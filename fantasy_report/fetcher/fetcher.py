import datetime
import pandas

from database import Database

from yfantasy_api.api import YahooFantasyApi


class Service():
    def __init__(self, league_id):
        self.fantasy_api = YahooFantasyApi(league_id, game_id='nhl')
        self.game_weeks = self.fantasy_api.game().game_weeks().get().game_weeks
        self.current_week = self.__parse_current_week()
        self.__db = Database()

    def fetch_latest_data(self):
        self.__populate_team_data()
        latest_week = self.__db.get_latest_week()
        for week in range(1, self.current_week):
            if latest_week and latest_week > week:
                print(f'Skipping as week {week} data is already up to date...')
                continue
            self.__populate_matchup_data(week)
            for team in range(1, 13):
                self.__populate_player_points(week, team)
                self.__populate_optimal_points(week, team)

    def __populate_team_data(self):
        teams = self.fantasy_api.league().teams().get().teams

        for t in teams:
            self.__db.upsert_team(t)

    def __populate_matchup_data(self, week):
        print(f'Getting matchup data for week {week}...')
        matchups = self.fantasy_api.league().scoreboard(week=week).get().matchups
        all_play = []
        for m in matchups:
            winner = list(filter(lambda x: x.team.info.team_key == m.winner_team_key, m.teams))[0]
            loser = list(filter(lambda x: x.team.info.team_key != m.winner_team_key, m.teams))[0]
            self.__db.upsert_weekly_result(winner, week, True, loser.team.info.team_id)
            self.__db.upsert_weekly_result(loser, week, False, winner.team.info.team_id)
            all_play.extend([winner, loser])

        all_play.sort(key=lambda x: x.team_points, reverse=True)
        for rank, weekly_result in enumerate(all_play):
            self.__db.upsert_all_play(weekly_result.team.info.team_id, week, rank)

    def __populate_player_points(self, week, team):
        print(f'Getting player data for week {week} and team {team}...')
        for d in self.__get_dates_from_week(week):
            players = self.fantasy_api.team(team).roster().stats(date=d.date()).get().players
            for p in players:
                self.__db.upsert_player(p)
                self.__db.upsert_stats(p, team, d.date(), week)

    def __populate_optimal_points(self, week, team):
        total_for_week = 0
        for d in self.__get_dates_from_week(week):
            total_for_week += self.__calculate_optimal_points(d.date(), team)
        self.__db.upsert_optimal_points(team, week, round(total_for_week, 2))

    def __calculate_optimal_points(self, day, team):
        c = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'C')]
        lw = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'LW')]
        rw = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'RW')]
        f = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'F')]
        d = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'D')]
        g = [(record[0], record[3]) for record in self.__db.get_players(day, team, 'G')]

        c_lw_rw = self.__calculate_optimal_forward_points(c, lw, rw, f, 0)
        c_rw_lw = self.__calculate_optimal_forward_points(c, lw, rw, f, 0)
        lw_c_rw = self.__calculate_optimal_forward_points(lw, c, rw, f, 1)
        lw_rw_c = self.__calculate_optimal_forward_points(lw, rw, c, f, 2)
        rw_c_lw = self.__calculate_optimal_forward_points(rw, c, lw, f, 1)
        rw_lw_c = self.__calculate_optimal_forward_points(rw, lw, c, f, 2)
        d_points = sum([x[1] for x in d][:5])
        g_points = sum([x[1] for x in g][:2])
        return max(c_lw_rw, c_rw_lw, lw_c_rw, lw_rw_c, rw_c_lw, rw_lw_c) + d_points + g_points

    def __calculate_optimal_forward_points(self, f1, f2, f3, f, c_position):
        f1 = f1[:3 if c_position == 0 else 2]
        used = [x[0] for x in f1]
        f2 = [i for i in filter(lambda x: x[0] not in used, f2)][:3 if c_position == 1 else 2]
        used += [x[0] for x in f2]
        f3 = [i for i in filter(lambda x: x[0] not in used, f3)][:3 if c_position == 2 else 2]
        used += [x[0] for x in f3]
        f = [i for i in filter(lambda x: x[0] not in used, f)][:2]
        forwards = f1 + f2 + f3 + f
        return sum([x[1] for x in forwards])

    def __get_dates_from_week(self, week):
        start = self.game_weeks[week - 1].start
        end = self.game_weeks[week - 1].end
        return pandas.date_range(start, end)

    def __parse_current_week(self):
        for w in self.game_weeks:
            start = datetime.datetime.strptime(w.start, "%Y-%m-%d")
            end = datetime.datetime.strptime(w.end, "%Y-%m-%d")
            today = datetime.datetime.today()
            if today >= start and today <= end:
                return int(w.week)


if __name__ == '__main__':
    fetcher = Service(17457)
    fetcher.fetch_latest_data()

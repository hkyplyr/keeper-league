from os import path
from sys import argv

from pandas import DataFrame
from pickle import dump, load
from prettytable import PrettyTable

from api import YahooFantasyApi


class ApiWrapper():
    def __init__(self, league_id, game_id):
        self.fantasy_api = YahooFantasyApi(league_id, game_id=game_id)

    def get_team_map_for_week(self, week):
        pickle_name = self.__get_pickle_name(week)
        if path.exists(pickle_name):
            with open(pickle_name, 'rb') as p:
                return load(p)

        team_dict = {}
        teams = self.fantasy_api.get_teams()
        for t in teams:
            if t == 'count':
                continue
            team = Team(teams[t])
            team_dict[team.team_name] = team

        matchup_data = []
        matchups = self.fantasy_api.get_scoreboard(week)[1]['scoreboard']['0']['matchups']
        for m in matchups:
            if m == 'count':
                continue
            matchup = Matchup(matchups[m])
            team_dict[matchup.w_team.team_name].add_matchup_data(matchup.w_pts, matchup.w_proj, matchup.w_perc, 1, 0)
            team_dict[matchup.l_team.team_name].add_matchup_data(matchup.l_pts, matchup.l_proj, matchup.l_perc, 0, 1)
            matchup_data.append(matchup)

        all_players = []
        for team in team_dict.values():
            team_players = []
            players = self.fantasy_api.get_stats_week(team.team_id, week)[1]['roster']['0']['players']
            for p in players:
                if p == 'count':
                    continue
                team_players.append(Player(players[p], team.team_name))
            all_players.extend(team_players)

            roster, remaining = self.__get_optimal_players(['QB'], 1, [], team_players)
            roster, remaining = self.__get_optimal_players(['RB'], 2, roster, remaining)
            roster, remaining = self.__get_optimal_players(['WR'], 2, roster, remaining)
            roster, remaining = self.__get_optimal_players(['TE'], 1, roster, remaining)
            roster, remaining = self.__get_optimal_players(['K'], 1, roster, remaining)
            roster, remaining = self.__get_optimal_players(['DEF'], 1, roster, remaining)
            roster, remaining = self.__get_optimal_players(['RB', 'WR', 'TE'], 1, roster, remaining)
            optimal_points = sum([player.points for player in roster])
            team_dict[team.team_name].add_optimal_points(optimal_points)

        with open(pickle_name, 'wb') as p:
            dump([team_dict, all_players, matchup_data], p)
        return team_dict, all_players, matchup_data

    def __get_optimal_players(self, position, number_to_take, roster, players):
        filtered = list(sorted(filter(lambda x: x.player_position in position, players),
                               key=lambda x: x.points, reverse=True))
        optimal = filtered[0:number_to_take]
        for player in optimal:
            players.remove(player)
            roster.append(player)
        return roster, players

    def __get_pickle_name(self, week):
        return f'pickles/week-{week}-{self.fantasy_api.league_id}.pickle'

class Player():
    def __init__(self, player_json, team_name):
        self.team_name = team_name
        self.player_name = self.__parse_player_name(player_json)
        self.player_position = self.__parse_player_position(player_json)
        self.selected_position = self.__parse_selected_position(player_json)
        self.points = self.__parse_player_points(player_json)

    def __repr__(self):
        return self.player_name

    def __parse_player_name(self, player_json):
        return player_json['player'][0][2]['name']['full']

    def __parse_player_position(self, player_json):
        for i in range(9, 14):
            if 'display_position' in player_json['player'][0][i]:
                return player_json['player'][0][i]['display_position']

    def __parse_selected_position(self, player_json):
        return player_json['player'][1]['selected_position'][1]['position']

    def __parse_player_points(self, player_json):
        if 'player_points' in player_json['player'][2]:
            player_json = player_json['player'][2]
        else:
            player_json = player_json['player'][3]
        return float(player_json['player_points']['total'])

class Matchup():
    def __init__(self, matchup_json):
        self.w_team, self.w_pts, self.w_proj, self.w_perc = self.__parse_team_data(matchup_json, True)
        self.l_team, self.l_pts, self.l_proj, self.l_perc = self.__parse_team_data(matchup_json, False)
        self.difference = self.w_pts - self.l_pts

    def __parse_winning_team_key(self, matchup_json):
        if 'winner_team_key' in matchup_json['matchup']:
            return matchup_json['matchup']['winner_team_key']

        team_one = matchup_json['matchup']['0']['teams']['0']['team']
        team_two = matchup_json['matchup']['0']['teams']['1']['team']
        if team_one[1]['win_probability'] > 0.5:
            return team_one[0][0]['team_key']
        else:
            return team_two[0][0]['team_key']

    def __parse_team_points(self, team_stats_json):
        return float(team_stats_json['team'][1]['team_points']['total'])

    def __parse_team_projections(self, team_stats_json):
        return float(team_stats_json['team'][1]['team_projected_points']['total'])

    def __parse_team_data(self, matchup_json, is_winner):
        winning_team_key = self.__parse_winning_team_key(matchup_json)
        teams = matchup_json['matchup']['0']['teams']
        for t in teams:
            if t == 'count':
                continue
            team = Team(teams[t])
            points = self.__parse_team_points(teams[t])
            projected = self.__parse_team_projections(teams[t])
            project_percentage = points / projected * 100

            if is_winner and team.team_key == winning_team_key:
                return team, points, projected, project_percentage
            elif not is_winner and team.team_key != winning_team_key:
                return team, points, projected, project_percentage


class Team():
    def __init__(self, team_json):
        self.team_id = self.__parse_team_id(team_json)
        self.team_name = self.__parse_team_name(team_json)
        self.team_key = self.__parse_team_key(team_json)
        self.faab_left = self.__parse_faab_left(team_json)

    def __repr__(self):
        return self.team_name

    def add_matchup_data(self, points, projection, projection_percentage, win, loss):
        self.points = points
        self.projection = projection
        self.projection_percentage = projection_percentage
        self.win = win
        self.loss = loss

    def add_optimal_points(self, optimal_points):
        self.optimal_points = optimal_points
        self.coach_rating = self.points / self.optimal_points * 100

    def __parse_team_id(self, team_json):
        return team_json['team'][0][1]['team_id']

    def __parse_team_name(self, team_json):
        return team_json['team'][0][2]['name'].replace('\xe2', '\'')

    def __parse_team_key(self, team_json):
        return team_json['team'][0][0]['team_key']

    def __parse_faab_left(self, team_json):
        potential_faab = team_json['team'][0][8]
        if 'faab_balance' in potential_faab:
            return potential_faab['faab_balance']
        else:
            return 0


class ReportWriter():
    def __init__(self, current_week, league_id, game_id='nfl'):
        self.current_week = int(current_week)
        self.api_wrapper = ApiWrapper(league_id, game_id=game_id)

    def run_report(self):
        reports = [self.__get_weekly_report(i)[0] for i in range(1, self.current_week + 1)]
        self.__calculate_allplay_and_luck(reports)

        self.__output_overall_report(reports)
        self.__output_power_report(reports)
        self.__output_weekly_report(reports, self.current_week)

        _, all_players, matchups = self.__get_weekly_report(self.current_week)
        self.__output_top_players(all_players)
        self.__output_bench_players(all_players)
        self.__output_matchup_data(matchups)

    def __calculate_top_players(self, players, on_bench=False):
        players = sorted(players, key=lambda x: x.points, reverse=True)
        qb = self.__calculate_top_player(players, 'QB', on_bench)
        rb = self.__calculate_top_player(players, 'RB', on_bench)
        wr = self.__calculate_top_player(players, 'WR', on_bench)
        te = self.__calculate_top_player(players, 'TE', on_bench)
        return [qb, rb, wr, te]

    def __calculate_top_player(self, players, position, on_bench):
        if on_bench:
            players = list(filter(lambda x: x.selected_position in ['BN', 'IR'], players))
        else:
            players = list(filter(lambda x: x.selected_position not in ['BN', 'IR'], players))
        return list(filter(lambda x: x.player_position == position, players))[0]

    def __output_matchup_data(self, matchups):
        matchups = list(sorted(matchups, key=lambda x: x.difference, reverse=True))
        blowout = matchups[0]
        closest = matchups[-1]
        print('\nClosest/Blowout Victories')
        print(f'{blowout.w_team} beat {blowout.l_team} by {self.__round(blowout.difference, 2)} points.')
        print(f'{closest.w_team} beat {closest.l_team} by {self.__round(closest.difference, 2)} points.')

    def __output_top_players(self, players):
        print('\nTop Players')
        players = self.__calculate_top_players(players)
        for player in players:
            print(f'{player.player_position} {player.player_name} scored {player.points} for {player.team_name}.')

    def __output_bench_players(self, players):
        print('\nTop Benchwarmers')
        players = self.__calculate_top_players(players, on_bench=True)
        for player in players:
            position = player.player_position
            print(f'{position} {player.player_name} scored {player.points} on {player.team_name}\'s bench.')

    def __output_overall_report(self, reports):
        print('\nOverall Standings')
        overall_report = sum(reports)
        self.__sort_report(overall_report, 'win', 'points')
        table = PrettyTable(field_names=['Team', 'Record', 'PF', 'FAAB'])
        for index, columns in overall_report.iterrows():
            record = self.__format_record(columns['win'], columns['loss'])
            table.add_row([index[1], record, self.__round(columns['points'], 2), index[3]])
        print(table)

    def __output_power_report(self, reports):
        print('\nPower Rankings')
        report = sum(reports)
        self.__calculate_power_ranks(report)
        self.__sort_report(report, 'power_rank', 'points')
        table = PrettyTable(field_names=['Team', 'All Play', 'Optimal', 'Coach %'])
        for index, columns in report.iterrows():
            record = self.__format_record(columns['all_win'], columns['all_loss'])
            optimal_points = self.__round(columns['optimal_points'], 2)
            coach_rating = self.__calculate_coach_rating(columns['points'], optimal_points)
            table.add_row([index[1], record, optimal_points, coach_rating])
        print(table)

    def __output_weekly_report(self, reports, week):
        print(f'\nWeek {week} Results')
        report = reports[week - 1]
        self.__sort_report(report, 'win', 'points')
        table = PrettyTable(field_names=['Team', 'W/L', 'PF', 'OPF', 'Coach %', 'Luck %', 'Proj %'])
        for index, columns in report.iterrows():
            win_or_loss = 'W' if columns['win'].astype(int) else 'L'
            points_for = self.__round(columns['points'], 2)
            optimal = self.__round(columns['optimal_points'], 2)
            coach_rating = self.__calculate_coach_rating(points_for, optimal)
            luck_rating = self.__calculate_luck(columns['luck_rank'], len(report), win_or_loss)
            proj_percentage = self.__round(columns['projection_percentage'] - 100, 1)
            table.add_row([index[1], win_or_loss, points_for, optimal, coach_rating, luck_rating, proj_percentage])
        print(table)

    def __calculate_luck(self, rank, num_of_teams, win_or_loss):
        multiplier = (1 / (num_of_teams - 1)) * 100
        if win_or_loss == 'W':
            return self.__round((rank - 1) * multiplier, 2)
        else:
            return self.__round((rank - num_of_teams) * multiplier, 2)

    def __get_weekly_report(self, week):
        team_map, all_players, matchups = self.api_wrapper.get_team_map_for_week(week)
        return self.__convert_to_dataframe(team_map), all_players, matchups

    def __convert_to_dataframe(self, data):
        data = {k: v.__dict__ for k, v in data.items()}
        return DataFrame.from_dict(data, orient='index').set_index(['team_id', 'team_name', 'team_key', 'faab_left'])

    def __format_record(self, win, loss):
        return f'({int(win)}-{int(loss)})'

    def __calculate_coach_rating(self, points, optimal):
        return self.__round(points / optimal * 100, 1)

    def __calculate_allplay_and_luck(self, reports):
        for report in reports:
            report['all_win'] = (report['points'].rank() - 1).astype(int)
            report['all_loss'] = (report['points'].rank(ascending=False) - 1).astype(int)
            report['luck_rank'] = (report['points'].rank(ascending=False)).astype(int)

    def __calculate_power_ranks(self, report):
        report['pf_rank'] = report['points'].rank()
        report['record_rank'] = report['win'].rank()
        report['ofp_rank'] = report['optimal_points'].rank()
        report['all_rank'] = report['all_win'].rank()
        report['power_rank'] = sum([report['pf_rank'], report['record_rank'], report['ofp_rank'], report['all_rank']])

    def __sort_report(self, report, *keys):
        report.sort_values(by=[*keys], inplace=True, ascending=False)

    def __round(self, value, digits):
        return round(value, ndigits=digits)

if __name__ == '__main__':
    writer = ReportWriter(argv[1], league_id=argv[2])
    writer.run_report()

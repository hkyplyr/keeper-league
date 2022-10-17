import sqlite3

from models import (
    PlayerAwards,
    PowerRankingsTeam,
    StandingsTeam,
    TeamAwards,
    WeeklyResultsTeam,
)


class Database:
    def __init__(self):
        self.__conn = sqlite3.connect("keeper_league.db")
        self.__init_db()

    def __execute(self, sql_statement_name, values={}):
        with open(f"keeper_league/sql/{sql_statement_name}.sql", "r") as f:
            cursor = self.__conn.cursor()
            cursor.execute(f.read(), values)
            self.__conn.commit()
            return cursor.fetchall()

    def __init_db(self):
        with open(f"keeper_league/sql/init.sql", "r") as f:
            for sql_statement in f.read().split(";"):
                self.__conn.cursor().execute(sql_statement)

    def get_last_updated_week(self):
        result = self.__execute("get_last_updated_week")[0][0]
        if result:
            return int(result)
        else:
            return 1

    def get_player_awards(self, week):
        return [
            PlayerAwards(row)
            for row in self.__execute("get_player_awards", {"week": week})
        ]

    def get_power_rankings(self, week):
        previous_ranks = {
            row[1]: row[0]
            for row in self.__execute("get_power_rankings", {"week": week - 1})
        }
        return [
            PowerRankingsTeam(row, previous_ranks)
            for row in self.__execute("get_power_rankings", {"week": week})
        ]

    def get_rolling_points_for(self, week):
        return self.__execute("get_rolling_points_for", {"week": week})

    def get_standings(self, week):
        return [
            StandingsTeam(row)
            for row in self.__execute("get_standings", {"week": week})
        ]

    def get_team_awards(self, week):
        return [
            TeamAwards(row) for row in self.__execute("get_team_awards", {"week": week})
        ]

    def get_weekly_results(self, week):
        return [
            WeeklyResultsTeam(row)
            for row in self.__execute("get_weekly_results", {"week": week})
        ]

    def insert_matchup(self, matchup):
        self.__execute("insert_matchup", matchup)

    def insert_optimal_points(self, optimal_points):
        self.__execute("insert_optimal_points", optimal_points)

    def insert_player(self, player):
        self.__execute("insert_player", player)

    def insert_team(self, team):
        self.__execute("insert_team", team)

    def insert_weekly_results(self, weekly_results):
        self.__execute("insert_weekly_results", weekly_results)

    def update_all_play(self, week):
        self.__execute("update_all_play", {"week": week})


if __name__ == "__main__":
    db = Database()

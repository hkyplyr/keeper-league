import os
import sqlite3

from sql import GET_MATCHUP_DATA, GET_ROLLING_REPORT, GET_STANDINGS, GET_TOP_PLAYER_FOR_TEAM, \
    GET_WEEK_REPORT_DATA, GET_YEAR_REPORT_DATA

class Database:
    def __init__(self):
        self.__conn = sqlite3.connect('sqlite.db')

    def __execute(self, sql_statement, params=(), fetch_one=False):
        cursor = self.__conn.cursor()
        cursor.execute(sql_statement, params)
        if fetch_one:
            return cursor.fetchone()
        else:
            return cursor.fetchall()

    def get_matchup_data(self, week):
        return self.__execute(GET_MATCHUP_DATA, (week,))

    def get_rolling_report(self, week):
        return self.__execute(GET_ROLLING_REPORT, (week,))

    def get_standings(self, week):
        return self.__execute(GET_STANDINGS, (week,))

    def get_top_players_for_team(self, week, team_name):
        return self.__execute(GET_TOP_PLAYER_FOR_TEAM, (week, team_name), fetch_one=True)

    def get_week_report_data(self, week):
        return self.__execute(GET_WEEK_REPORT_DATA, (week,))

    def get_year_report_data(self, week):
        return self.__execute(GET_YEAR_REPORT_DATA, (week,))

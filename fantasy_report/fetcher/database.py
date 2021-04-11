import os
import sqlite3

from sql import INIT_TABLES, GET_LATEST_WEEK, GET_PLAYERS_BY_POSITION, UPSERT_ALL_PLAY_RECORD, \
    UPSERT_OPTIMAL_POINTS, UPSERT_PLAYER, UPSERT_STATS, UPSERT_TEAM, UPSERT_WEEKLY_RESULTS

class Database:
    def __init__(self):
        self.__conn = sqlite3.connect('sqlite.db')
        self.__execute_insert(INIT_TABLES)

    def __execute_insert(self, sql_statement, params=()):
        for sql in sql_statement.split(';'):
            if sql.isspace():
                continue
            self.__conn.execute(sql, params)
        self.__conn.commit()

    def __execute_fetch(self, sql_statement, params=(), fetch_one=False):
        cursor = self.__conn.cursor()
        cursor.execute(sql_statement, params)
        if fetch_one:
            return cursor.fetchone()
        else:
            return cursor.fetchall()

    def get_latest_week(self):
        return self.__execute_fetch(GET_LATEST_WEEK, fetch_one=True)[0]

    def get_players(self, day, team, position):
        return self.__execute_fetch(GET_PLAYERS_BY_POSITION, (team, day, position))

    def upsert_team(self, team):
        self.__execute_insert(UPSERT_TEAM, (team.info.team_id, team.info.name))

    def upsert_weekly_result(self, weekly_results, week, win, opponent):
        params = (week, weekly_results.team.info.team_id, weekly_results.team_points,
                  weekly_results.team_projected_points, win, opponent)
        self.__execute_insert(UPSERT_WEEKLY_RESULTS, params)

    def upsert_all_play(self, team, week, wins):
        self.__execute_insert(UPSERT_ALL_PLAY_RECORD, (team, week, wins))

    def upsert_player(self, player):
        params = (player.player_id, player.full_name)
        self.__execute_insert(UPSERT_PLAYER, params)

    def upsert_stats(self, player, team, week, date):
        params = (player.player_id, team, ','.join(player.eligible_positions), date,
                  player.points, week)
        self.__execute_insert(UPSERT_STATS, params)

    def upsert_optimal_points(self, team, week, points):
        self.__execute_insert(UPSERT_OPTIMAL_POINTS, (team, week, points))

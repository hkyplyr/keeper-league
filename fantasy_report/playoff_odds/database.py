import sqlite3

from sql import GET_STANDINGS, GET_AVERAGE_POINTS

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

    def get_standings(self):
        return self.__execute(GET_STANDINGS)

    def get_rolling_points_for(self, week):
        return self.__execute(GET_AVERAGE_POINTS, (week,))

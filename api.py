from auth import AuthenticationService
import requests
import time
import sys

BASE_URL = 'https://fantasysports.yahooapis.com/fantasy/v2'


class YahooFantasyApi:
    def __init__(self, league_id, game_id='nhl'):
        self.league_id = league_id
        self.game_id = game_id
        self.auth_service = AuthenticationService()
        self.__set_tokens()

    def __set_tokens(self):
        self.access_token = self.auth_service.get_access_token()
        self.refresh_token = self.auth_service.get_refresh_token()
        self.expires_by = self.auth_service.get_expires_by()

    def __check_tokens(self):
        if time.time() > self.expires_by - 300:
            self.auth_service.refresh_tokens()
            self.__set_tokens()

    #############################
    # Yahoo Fantasy Api methods
    #############################
    def __get(self, path):
        self.__check_tokens()
        params = {'format': 'json'}
        headers = {'Authorization': 'Bearer {}'.format(self.access_token)}
        url = '{}/{}'.format(BASE_URL, path)

        time.sleep(1)

        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return response.json()['fantasy_content']
            else:
                print(response.status_code, response.text)
                sys.exit()
        except:
            print(sys.exc_info()[0])

    def __get_game_resource(self, sub_resource):
        path = 'game/{}/{}'.format(self.game_id, sub_resource)
        return self.__get(path)['game']

    def __get_league_resource(self, sub_resource):
        path = 'league/{}.l.{}/{}'.format(self.game_id, self.league_id, sub_resource)
        return self.__get(path)['league']

    def __get_player_resource(self, sub_resource, player_id):
        path = 'player/{}.p.{}/{}'.format(self.game_id, player_id, sub_resource)
        return self.__get(path)['player']

    def __get_team_resource(self, sub_resource, team_id):
        path = 'team/{}.l.{}.t.{}/{}'.format(self.game_id, self.league_id, team_id, sub_resource)
        return self.__get(path)['team']

    #############################
    # Public facing Api methods
    #############################
    def get_standings(self):
        return self.__get_league_resource('standings')

    def get_roster(self, team_id):
        return self.__get_team_resource('roster/players', team_id)[1]['roster']

    def get_scoreboard(self, week):
        return self.__get_league_resource('scoreboard;week={}'.format(week))

    def get_matchups(self, team_id, weeks_arr):
        weeks = ','.join(str(c) for c in weeks_arr)
        return self.__get_team_resource('matchups;weeks{}'.format(weeks), team_id)

    def get_stats(self, team_id, date):
        return self.__get_team_resource('roster;type=date;date={}/players/stats'.format(date), team_id)

    def get_stats_week(self, team_id, week):
        return self.__get_team_resource('roster;type=week;week={}/players/stats'.format(week), team_id)

    def get_teams(self):
        return self.__get_league_resource('teams')[1]['teams']

    def get_draft_results(self):
        return self.__get_league_resource('draftresults')[1]['draft_results']

    def get_player(self, player_id):
        return self.__get_player_resource('metadata', player_id)

    def get_players(self, start):
        return self.__get_league_resource('players;start={};type=season/ownership'.format(start))

    def get_keepers(self, start):
        return self.__get_league_resource('players;start={};status=K'.format(start))

    def get_transactions(self):
        return self.__get_league_resource('transactions')[1]['transactions']

    def get_game_weeks(self):
        return self.__get_game_resource('game_weeks')

    def get_stats_players(self, start, date):
        return self.__get_league_resource('players;start={};out=ownership/stats;type=date;date={}'.format(start, date))

    def get_stats_players_season(self, start):
        return self.__get_league_resource('players;start={};sort=AR/stats;type=season;season=2018'.format(start))

    def get_league_metadata(self):
        return self.__get_league_resource('metadata')

    def get_stats_players_test(self, start, count, date):
        return self.__get_league_resource('players;start={};count={};out=ownership/stats;type=date;date={}'
                                          .format(start, count, date))

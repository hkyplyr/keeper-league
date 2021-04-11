import sys

import os
import imgkit
import json
import pandas as pd
import plotly.express as px
from jinja2 import Environment, PackageLoader, select_autoescape

from database import Database

UP_ARROW = '#9650'
DOWN_ARROW = '#9660'
DASH = '#9644'

class Writer:
    def __init__(self, week):
        self.__db = Database()
        self.__week = int(week)
        self.__add_recap_file()

    def __add_recap_file(self):
        if os.path.exists(f'recaps/week-{self.__week}.json'):
            return

        if not os.path.exists('recaps'):
            os.mkdir('recaps')
        data = {team[1]['Team']: {'recap': ''} for team in self.__get_weekly_power_ranking().iterrows()}
        with open(f'recaps/week-{self.__week}.json', 'w') as f:
            json.dump(data, f, indent=4)

    def __get_standings(self, week=None):
        week = self.__week if week is None else week
        data = self.__db.get_standings(week)
        df = pd.DataFrame(data, columns=['Team', 'W', 'L', 'PF', 'OPF', 'PPF'])
        df['Coach%'] = round(df['PF'] / df['OPF'] * 100, 2)
        df.sort_values(by=['W', 'PF'], inplace=True, ascending=False)
        return df

    def __get_weekly_power_ranking(self, week=None):
        week = self.__week if week is None else week
        data = self.__db.get_rolling_report(week)
        df = pd.DataFrame(data, columns=['Team', 'Wins', 'Losses', 'All-Wins', 'All-Losses', 'All-Games', 'PF', 'OPF', 'PPF'])
        df['Coach%'] = self.__calculate_coach_rating(df)
        df['Proj%'] = self.__calculate_projection_percentage(df)
        df['Power Rank'] = df['PF'].rank() * 2 + df['All-Wins'].rank() + df['Wins'].rank() * 3
        df.sort_values(by=['Power Rank', 'PF'], inplace=True, ascending=False)
        return df

    def __calculate_coach_rating(self, df):
        return round(df['PF'] / df['OPF'] * 100, 2)

    def __calculate_projection_percentage(self, df):
        return round(df['PF'] / df['PPF'] * 100, 2)

    def __get_rank_change(self):
        ranks = {}
        last_week = self.__get_weekly_power_ranking(week=self.__week - 1)
        current_week = self.__get_weekly_power_ranking(week=self.__week)
        for i, team in enumerate(current_week.iterrows()):
            ranks[team[1]['Team']] = {'current': i + 1}
        for i, team in enumerate(last_week.iterrows()):
            last_rank = i + 1
            current_rank = ranks[team[1]['Team']]['current']
            ranks[team[1]['Team']]['last'] = last_rank
            ranks[team[1]['Team']]['changed'] = last_rank - current_rank
        return ranks

    def get_matchup_data(self):
        matchup_data = self.__db.get_matchup_data(self.__week)
        for data in matchup_data:
            print('{} ({}) defeated {} ({})'.format(data[0], data[1], data[3], data[2]))

        matchups_by_team = {}
        for data in matchup_data:
            matchups_by_team[data[0]] = {'won': 'W', 'pf': self.__round(data[1])}
            matchups_by_team[data[3]] = {'won': 'L', 'pf': self.__round(data[2])}
        return matchups_by_team

    def graph_power_rankings(self):
        dataframe_dict = {'Team': [], 'Week': [], 'Rank': []}

        weeks = list(range(1, self.__week + 1))
        plots = {}
        for w in range(1, self.__week + 1):
            report = self.__get_weekly_power_ranking(week=w)
            rank = 1
            for index, data in report.iterrows():
                dataframe_dict['Team'].append(data['Team'])
                dataframe_dict['Week'].append(w)
                dataframe_dict['Rank'].append(rank)
                rank += 1

        df = pd.DataFrame(data=dataframe_dict)
        figure = px.line(df, x='Week', y='Rank', color='Team', color_discrete_sequence=px.colors.qualitative.Dark24)
        figure['layout']['yaxis']['autorange'] = 'reversed'
        figure.update_layout(
            xaxis=dict(dtick=1),
            yaxis=dict(dtick=1),
            title=dict(text='Weekly Power Rankings', x=0.5, xanchor='center', yanchor='top')
        )
        figure.write_image('out/Weekly-Power-Rankings.png', width=600, height=400, scale=2)

    def graph_standings(self):
        dataframe_dict = {'Team': [], 'Week': [], 'Rank': []}

        weeks = list(range(1, self.__week + 1))
        plots = {}
        for w in range(1, self.__week + 1):
            report = self.__get_standings(week=w)
            rank = 1
            for index, data in report.iterrows():
                dataframe_dict['Team'].append(data['Team'])
                dataframe_dict['Week'].append(w)
                dataframe_dict['Rank'].append(rank)
                rank += 1

        df = pd.DataFrame(data=dataframe_dict)
        figure = px.line(df, x='Week', y='Rank', color='Team', color_discrete_sequence=px.colors.qualitative.Dark24)
        figure['layout']['yaxis']['autorange'] = 'reversed'
        figure.update_layout(
            xaxis=dict(dtick=1),
            yaxis=dict(dtick=1),
            title=dict(text='Weekly Standings', x=0.5, xanchor='center', yanchor='top')
        )
        figure.write_image('out/Weekly-Standings.png', width=600, height=400, scale=2)

    def __get_week_report_data(self):
        week_data = {}
        for data in self.__db.get_week_report_data(self.__week):
            week_data[data[0]] = {
                'week_pf': self.__round(data[1]),
                'week_win': 'W' if data[2] else 'L',
                'week_coach': self.__round(data[3] * 100)
            }
        for team in week_data.keys():
            top_player = self.__db.get_top_players_for_team(self.__week, team)
            week_data[team]['top_player'] = {
                'name': top_player[0],
                'points': self.__round(top_player[1])
            }
        return week_data

    def __get_year_report_data(self):
        year_data = {}
        for data in self.__db.get_year_report_data(self.__week):
            year_data[data[0]] = {
                'year_pf': self.__round(data[1]),
                'year_win': data[2],
                'year_loss': data[3],
                'year_coach': self.__round(data[4] * 100)
            }
        return year_data

    def __get_original_ranks(self):
        results = {}
        original_ranks = self.__get_weekly_power_ranking(week=1)
        for i, team in enumerate(original_ranks.iterrows()):
            results[team[1]['Team']] = i + 1
        return results

        results = {team[1]: team[0] for team in self.__db.get_teams()}
        return results

    def get_recaps(self):
        with open(f'recaps/week-{self.__week}.json', 'r') as f:
            return json.load(f)

    def output_power_rankings(self):
        env = Environment(
            loader=PackageLoader('fantasy_report', 'templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )

        reports = []
        year_data = self.__get_year_report_data()
        week_data = self.__get_week_report_data()
        rank_changes = self.__get_rank_change()
        recaps = self.get_recaps()
        original_ranks = self.__get_original_ranks()
        for team, ranks in rank_changes.items():
            team_data = year_data[team]
            team_data.update(week_data[team])
            team_data['original_rank'] = original_ranks[team]
            team_data['name'] = team
            team_data['rank'] = ranks['current']
            team_data['recap'] = recaps[team]['recap']
            if ranks['changed'] > 0:
                team_data['rank_change'] = UP_ARROW
            elif ranks['changed'] < 0:
                team_data['rank_change'] = DOWN_ARROW
            else:
                team_data['rank_change'] = DASH
            reports.append(team_data)

        template = env.get_template('template.html')
        rendered = template.render(teams=reports)
        with open('report.html', 'w') as f:
            f.write(rendered)
        imgkit.from_file('report.html', f'out/Power-Rankings-Week-{self.__week}.jpg',
                         options={'enable-local-file-access': '', 'quiet': ''})
        os.remove('report.html')

    def __round(self, value):
        return '{:.2f}'.format(value)


if __name__ == '__main__':
    w = Writer(sys.argv[1])
    w.output_power_rankings()
    w.graph_power_rankings()
    w.graph_standings()

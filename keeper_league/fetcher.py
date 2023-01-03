from datetime import datetime, timedelta
from models import (
    Player,
    Matchup,
    OptimalPoints,
    WeeklyResult,
    Team,
    db_session,
)
from yfantasy_api.api import YahooFantasyApi
from sqlalchemy import func
from tools import GetOptimalPoints
from update_all_play import update_all_play


def get_sorted_players(session, api, team_id, week, day):
    players = api.team(team_id).roster(date=day).stats().get().players

    for player in players:
        played = list(player.stats.values())[0] is not None
        session.merge(
            Player(
                id=player.id,
                team_id=team_id,
                week=week,
                date=day,
                name=player.name,
                image_url=player.image_url,
                positions=",".join([pos for pos in player.eligible_positions]),
                points=player.points,
                started=played and player.selected_position not in ["BN", "IR", "IR+"],
            )
        )
        session.commit()

    players = filter(lambda player: float(player.points) >= 0, players)
    players = sorted(players, key=lambda player: float(player.points), reverse=True)
    return list(players)


week = 12
api = YahooFantasyApi(6738, "nhl", timeout=2)
session = db_session()


def get_last_updated_week():
    week = session.query(func.max(Player.week)).one()[0]
    return 1 if not week else week


def daterange(start, end):
    start = datetime.strptime(start, "%Y-%m-%d")
    end = datetime.strptime(end, "%Y-%m-%d")
    num_of_days = (end - start).days + 1
    for d in range(num_of_days):
        yield (start + timedelta(d)).date()


def get_game_ranges():
    game_weeks = api.game().game_weeks().get().game_weeks
    return {int(gw.week): daterange(gw.start, gw.end) for gw in game_weeks}


game_ranges = get_game_ranges()


def inclusive_range(start, end):
    return range(start, end + 1)


for i in inclusive_range(get_last_updated_week(), week):
    matchups = api.league().scoreboard(week=i).get().matchups

    for matchup in matchups:
        winner = Team(
            id=matchup.winning_team.id,
            name=matchup.winning_team.name,
            image_url=matchup.winning_team.team_logos,
        )

        loser = Team(
            id=matchup.losing_team.id,
            name=matchup.losing_team.name,
            image_url=matchup.losing_team.team_logos,
        )

        session.merge(winner)
        session.merge(loser)

        session.merge(
            WeeklyResult(
                team_id=matchup.winning_team.id,
                week=i,
                winner=True,
                points_for=matchup.winning_team.points,
                projected_points_for=matchup.winning_team.projected_points,
            )
        )

        session.merge(
            WeeklyResult(
                team_id=matchup.losing_team.id,
                week=i,
                winner=False,
                points_for=matchup.losing_team.points,
                projected_points_for=matchup.losing_team.projected_points,
            )
        )

        session.merge(
            Matchup(
                winner_id=matchup.winning_team.id,
                loser_id=matchup.losing_team.id,
                week=i,
                victory_margin=float(matchup.winning_team.points)
                - float(matchup.losing_team.points),
            )
        )

        session.commit()

    teams = api.league().teams().get().teams
    for day in game_ranges.get(i):
        for team in teams:
            print(f"Getting players for {team.name} on {day}")
            players = get_sorted_players(session, api, team.id, i, day)
            optimal_points = GetOptimalPoints.get_optimal_points(players)

            session.merge(
                OptimalPoints(team_id=team.id, week=i, date=day, points=optimal_points)
            )

    session.commit()

    update_all_play(i)

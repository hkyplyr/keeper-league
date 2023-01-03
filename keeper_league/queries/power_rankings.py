from models import AllPlay, OptimalPoints, Player, Team, WeeklyResult, db_session
from sqlalchemy import Integer, and_, func
from tools import Formatting

session = db_session()


def optimal_points_subquery(week):
    return (
        session.query(
            OptimalPoints.week,
            OptimalPoints.team_id,
            func.sum(OptimalPoints.points).label("points"),
        )
        .filter(OptimalPoints.week == week)
        .group_by(OptimalPoints.team_id)
        .subquery()
    )


def season_optimal_points_subquery(week):
    return (
        session.query(
            OptimalPoints.team_id, func.sum(OptimalPoints.points).label("points")
        )
        .filter(OptimalPoints.week <= week)
        .group_by(OptimalPoints.team_id)
        .subquery()
    )


def season_results_subquery(week):
    return (
        session.query(
            WeeklyResult.team_id,
            func.sum(WeeklyResult.winner.cast(Integer)).label("wins"),
            func.sum(WeeklyResult.points_for).label("points_for"),
        )
        .filter(WeeklyResult.week <= week)
        .group_by(WeeklyResult.team_id)
        .subquery()
    )


def top_player_subquery():
    subquery = (
        session.query(
            Player.week,
            Player.team_id,
            Player.name,
            func.sum(Player.points).label("pf"),
        )
        .filter(Player.started)
        .group_by(Player.week, Player.team_id, Player.name)
        .subquery()
    )

    return (
        session.query(
            subquery.c.week,
            subquery.c.team_id,
            subquery.c.name,
            func.max(subquery.c.pf).label("pf"),
        )
        .group_by(subquery.c.week, subquery.c.team_id)
        .subquery()
    )


def all_play_subquery(week):
    return (
        session.query(AllPlay.team_id, func.sum(AllPlay.wins).label("all_win"))
        .group_by(AllPlay.team_id)
        .filter(AllPlay.week <= week)
        .subquery()
    )


def power_ranking(all_play, season_optimal_points, season_results):
    return (
        func.rank().over(order_by=all_play.c.all_win)
        + func.rank().over(order_by=season_optimal_points.c.points)
        + func.rank().over(order_by=season_results.c.points_for)
        + func.rank().over(order_by=season_results.c.wins)
    ).label("pr")


def get_power_rankings(week):
    previous_ranks = {
        r["team_id"]: r["rank"] for r in __get_power_rankings(max(1, week - 1))
    }

    return __get_power_rankings(week, previous_ranks)


def __get_power_rankings(week, previous_ranks={}):
    top_player = top_player_subquery()
    optimal_points = optimal_points_subquery(week)
    season_results = season_results_subquery(week)
    season_optimal_points = season_optimal_points_subquery(week)
    all_play = all_play_subquery(week)

    subquery = (
        session.query(
            power_ranking(all_play, season_optimal_points, season_results),
            Team.name.label("team_name"),
            Team.id.label("team_id"),
            WeeklyResult.winner,
            top_player.c.name.label("top_player_name"),
            top_player.c.pf.label("top_player_points"),
            WeeklyResult.points_for,
            ((WeeklyResult.points_for / optimal_points.c.points) * 100).label(
                "week_coach"
            ),
            season_results.c.points_for.label("points"),
            (
                (season_results.c.points_for / season_optimal_points.c.points) * 100
            ).label("year_coach"),
            all_play.c.all_win,
        )
        .join(WeeklyResult, Team.id == WeeklyResult.team_id)
        .join(
            top_player,
            and_(
                top_player.c.team_id == Team.id, top_player.c.week == WeeklyResult.week
            ),
        )
        .join(season_optimal_points, season_optimal_points.c.team_id == Team.id)
        .join(
            optimal_points,
            and_(
                optimal_points.c.team_id == Team.id,
                optimal_points.c.week == WeeklyResult.week,
            ),
        )
        .join(season_results, season_results.c.team_id == WeeklyResult.team_id)
        .join(all_play, all_play.c.team_id == Team.id)
        .filter(WeeklyResult.week <= week)
        .group_by(Team.name)
        .subquery()
    )

    result = session.query(
        func.row_number()
        .over(
            order_by=(
                subquery.c.pr.desc(),
                subquery.c.all_win.desc(),
                subquery.c.points.desc(),
            )
        )
        .label("rank"),
        subquery,
    )

    return [__build_row_power_ranking_row(r, previous_ranks) for r in result]


def __build_row_power_ranking_row(r, previous_ranks):
    return {
        "rank": r.rank,
        "team": r.team_name,
        "result": "W" if r.winner else "L",
        "points": Formatting.format_points(r.points_for),
        "top_player": f"{r.top_player_name} ({Formatting.format_points(r.top_player_points)})",
        "weekly_coach_percentage": Formatting.format_percentage(r.week_coach),
        "total_points": Formatting.format_points(r.points),
        "yearly_coach_percentage": Formatting.format_percentage(r.year_coach),
        "movement": previous_ranks.get(r.team_id, r.rank) - r.rank,
        "team_id": r.team_id,
    }

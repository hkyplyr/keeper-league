from models import AllPlay, OptimalPoints, Player, Team, WeeklyResult, db_session
from sqlalchemy import Integer, and_, func
from tools import Formatting

session = db_session()


def rank():
    return (
        func.row_number()
        .over(order_by=(wins().desc(), points_for().desc()))
        .label("rank")
    )


def team_name():
    return Team.name.label("team_name")


def games_played():
    return func.count(WeeklyResult.winner).label("gp")


def wins():
    return func.sum(WeeklyResult.winner.cast(Integer)).label("w")


def losses():
    return (func.count(WeeklyResult.winner) - func.sum(WeeklyResult.winner)).label("l")


def win_percentage():
    return ((1.0 * wins()) / (wins() + losses())).label("win_percentage")


def all_play_wins():
    return func.sum(AllPlay.wins).label("all_wins")


def all_play_losses():
    return func.sum(AllPlay.losses).label("all_losses")


def all_play_percentage():
    return ((1.0 * all_play_wins()) / (all_play_wins() + all_play_losses())).label(
        "all_percentage"
    )


def points_for():
    return func.sum(WeeklyResult.points_for).label("pf")


def coach_percentage(subquery):
    return (points_for() / func.sum(subquery.c.points) * 100).label("coach")


def luck_percentage():
    return (
        (
            (wins() * 1.0 / games_played())
            - (all_play_wins() * 1.0 / (all_play_wins() + all_play_losses()))
        )
        * 100
    ).label("luck")


def optimal_points_for(subquery):
    return func.sum(subquery.c.points).label("opf")


def optimal_points_subquery():
    return (
        session.query(
            OptimalPoints.week,
            OptimalPoints.team_id,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.week, OptimalPoints.team_id)
        .subquery()
    )


def get_standings(week):
    optimal_points = optimal_points_subquery()

    result = (
        session.query(
            rank(),
            team_name(),
            games_played(),
            wins(),
            losses(),
            win_percentage(),
            all_play_wins(),
            all_play_losses(),
            all_play_percentage(),
            points_for(),
            optimal_points_for(optimal_points),
            coach_percentage(optimal_points),
            luck_percentage(),
        )
        .join(WeeklyResult, Team.id == WeeklyResult.team_id)
        .join(
            optimal_points,
            and_(
                optimal_points.c.team_id == Team.id,
                optimal_points.c.week == WeeklyResult.week,
            ),
        )
        .join(
            AllPlay, and_(AllPlay.team_id == Team.id, AllPlay.week == WeeklyResult.week)
        )
        .filter(WeeklyResult.week <= week)
        .group_by(Team.name)
        .order_by(wins().desc(), points_for().desc())
    )

    return [__build_standings_row(r) for r in result]


def __build_standings_row(r):
    return {
        "rank": r.rank,
        "team": r.team_name,
        "record": f"({r.w}-{r.l})",
        "all_play": f"({r.all_wins}-{r.all_losses})",
        "points_for": Formatting.format_points(r.pf),
        "optimal_points_for": Formatting.format_points(r.opf),
        "coach_percentage": Formatting.format_percentage(r.coach),
        "luck_percentage": Formatting.format_percentage(r.luck),
    }

    # "win%": format_win_percentage(r.win_percentage),
    # "allWin%": format_win_percentage(r.all_percentage),

from models import AllPlay, Team, WeeklyResult, db_session
from sqlalchemy import func

session = db_session()


def all_play_wins():
    return (func.rank().over(order_by=WeeklyResult.points_for.asc()) - 1).label("w")


def all_play_losses():
    return (func.rank().over(order_by=WeeklyResult.points_for.desc()) - 1).label("l")


def update_all_play(week):
    result = (
        session.query(
            Team.id.label("team_id"),
            WeeklyResult.week,
            WeeklyResult.points_for,
            all_play_wins(),
            all_play_losses(),
        )
        .join(WeeklyResult, Team.id == WeeklyResult.team_id)
        .filter(WeeklyResult.week == week)
    )

    for r in result:
        session.merge(AllPlay(team_id=r.team_id, week=r.week, wins=r.w, losses=r.l))
    session.commit()

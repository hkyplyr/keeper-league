from models import Matchup, OptimalPoints, Team, WeeklyResult, db_session
from sqlalchemy import and_, func, literal
from tools import Formatting

session = db_session()


def highest_scorer(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            WeeklyResult.points_for.label("points"),
            literal(None).label("percentage"),
            literal("Highest Scorer").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(WeeklyResult.points_for.desc())
        .limit(1)
        .one()
    )


def lowest_scorer(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            WeeklyResult.points_for.label("points"),
            literal(None).label("percentage"),
            literal("Lowest Scorer").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(WeeklyResult.points_for.asc())
        .limit(1)
        .one()
    )


def biggest_blowout(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            Matchup.victory_margin.label("points"),
            literal(None).label("percentage"),
            literal("Biggest Blowout").label("label"),
        )
        .join(Matchup, Matchup.winner_id == Team.id)
        .filter(Matchup.week == week)
        .order_by(Matchup.victory_margin.desc())
        .limit(1)
        .one()
    )


def closest_victory(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            Matchup.victory_margin.label("points"),
            literal(None).label("percentage"),
            literal("Closest Victory").label("label"),
        )
        .join(Matchup, Matchup.winner_id == Team.id)
        .filter(Matchup.week == week)
        .order_by(Matchup.victory_margin.asc())
        .limit(1)
        .one()
    )


def overacheiving_team(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            literal(None).label("points"),
            (WeeklyResult.points_for / WeeklyResult.projected_points_for * 100).label(
                "percentage"
            ),
            literal("Overacheiving Team").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(
            (WeeklyResult.points_for / WeeklyResult.projected_points_for * 100).desc()
        )
        .limit(1)
        .one()
    )


def underacheiving_team(week):
    return (
        session.query(
            Team.name,
            Team.image_url,
            literal(None).label("points"),
            (WeeklyResult.points_for / WeeklyResult.projected_points_for * 100).label(
                "percentage"
            ),
            literal("Underacheiving Team").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .filter(WeeklyResult.week == week)
        .order_by(
            (WeeklyResult.points_for / WeeklyResult.projected_points_for * 100).asc()
        )
        .limit(1)
        .one()
    )


def best_coach(week):
    subquery = (
        session.query(
            OptimalPoints.team_id,
            OptimalPoints.week,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.team_id, OptimalPoints.week)
        .subquery()
    )

    return (
        session.query(
            Team.name,
            Team.image_url,
            literal(None).label("points"),
            (WeeklyResult.points_for / subquery.c.points * 100).label("percentage"),
            literal("Best Coach").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .join(
            subquery,
            and_(subquery.c.team_id == Team.id, subquery.c.week == WeeklyResult.week),
        )
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.points_for / subquery.c.points * 100).desc())
        .limit(1)
        .one()
    )


def worst_coach(week):
    subquery = (
        session.query(
            OptimalPoints.team_id,
            OptimalPoints.week,
            func.sum(OptimalPoints.points).label("points"),
        )
        .group_by(OptimalPoints.team_id, OptimalPoints.week)
        .subquery()
    )

    return (
        session.query(
            Team.name,
            Team.image_url,
            literal(None).label("points"),
            (WeeklyResult.points_for / subquery.c.points * 100).label("percentage"),
            literal("Worst Coach").label("label"),
        )
        .join(WeeklyResult, WeeklyResult.team_id == Team.id)
        .join(
            subquery,
            and_(subquery.c.team_id == Team.id, subquery.c.week == WeeklyResult.week),
        )
        .filter(WeeklyResult.week == week)
        .order_by((WeeklyResult.points_for / subquery.c.points * 100).asc())
        .limit(1)
        .one()
    )


def build_row(data):
    if data.points:
        value = f"{data.name} ({Formatting.format_points(data.points)})"

    if data.percentage:
        value = f"{data.name} ({Formatting.format_percentage(data.percentage)}%)"

    return {"label": data.label, "value": value, "image": data.image_url}


def get_awards(week):
    awards = [
        highest_scorer(week),
        biggest_blowout(week),
        overacheiving_team(week),
        best_coach(week),
        lowest_scorer(week),
        closest_victory(week),
        underacheiving_team(week),
        worst_coach(week),
    ]

    return [build_row(r) for r in awards]

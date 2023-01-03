from models import Player, Team, db_session
from sqlalchemy import and_, func, not_
from tools import Formatting

session = db_session()


def get_top_players(week):
    return __get_players(week, True)


def get_bottom_players(week):
    return __get_players(week, False)


def build_row(position, data):
    return {
        "position": position,
        "player_image": data.player_image,
        "team_image": data.team_image,
        "player": data.name,
        "points": Formatting.format_points(data.points),
        "avg_points": Formatting.format_points(data.avg_points, 1),
        "team": data.team_name,
    }


def __get_players(week, descending):
    forwards = __get_top_forwards(week, descending)
    defense = __get_top_defensemen(week, descending)
    goalie = __get_top_goalie(week, descending)

    players = forwards | defense | goalie
    return [
        build_row("C", players["C"]),
        build_row("LW", players["LW"]),
        build_row("RW", players["RW"]),
        build_row("D", players["D1"]),
        build_row("D", players["D2"]),
        build_row("G", players["G"]),
    ]


def __get_top_forwards(week, descending):
    all_top_forwards = [
        __do_get_top_forwards(week, "C", "LW", "RW", descending),
        __do_get_top_forwards(week, "C", "RW", "LW", descending),
        __do_get_top_forwards(week, "LW", "C", "RW", descending),
        __do_get_top_forwards(week, "LW", "RW", "C", descending),
        __do_get_top_forwards(week, "RW", "C", "LW", descending),
        __do_get_top_forwards(week, "RW", "LW", "C", descending),
    ]

    all_top_forwards.sort(key=lambda r: r[0], reverse=True)

    return all_top_forwards[0][1]


def __get_top_defensemen(week, descending):
    first = __get_top_player(week, "D", descending=descending)
    second = __get_top_player(week, "D", [first.id], descending)

    return {"D1": first, "D2": second}


def __get_top_goalie(week, descending):
    return {"G": __get_top_player(week, "G", descending=descending)}


def __do_get_top_forwards(
    week, first_position, second_position, third_position, descending
):
    first = __get_top_player(week, first_position, descending=descending)
    second = __get_top_player(week, second_position, [first.id], descending)
    third = __get_top_player(week, third_position, [first.id, second.id], descending)

    total_points = first.points + second.points + third.points
    return total_points, {
        first_position: first,
        second_position: second,
        third_position: third,
    }


def __get_top_player(week, position, used_ids=[], descending=False):
    result = (
        session.query(
            Player.team_id,
            Player.week,
            Player.id,
            Player.name,
            player_points(),
            (func.sum(Player.points) / func.count(Player.points)).label("avg_points"),
            Player.image_url.label("player_image"),
            Team.image_url.label("team_image"),
            Team.name.label("team_name"),
        )
        .join(Team, Team.id == Player.team_id)
        .filter(Player.week == week)
        .filter(Player.positions.like(f"%{position}%"))
        .filter(not_(Player.id.in_(used_ids)))
        .filter(Player.started)
        .group_by(Player.team_id, Player.week, Player.id, Player.name)
        .order_by(order_by(descending))
        .limit(1)
        .one()
    )

    return result


def order_by(descending):
    if descending:
        return player_points().desc()
    else:
        return player_points().asc()


def player_points():
    return func.sum(Player.points).label("points")

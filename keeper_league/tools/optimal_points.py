POSITIONS = {"C": 2, "LW": 2, "RW": 2, "F": 2, "D": 4, "G": 2}


def get_optimal_points(players):
    f = __get_optimal_forwards(players)
    d = __get_optimal_defensemen(players)
    g = __get_optimal_goalies(players)

    return f + d + g


def __get_optimal_forwards(players):
    return max(
        __do_get_optimal_forwards(players, "C", "LW", "RW", "F"),
        __do_get_optimal_forwards(players, "C", "RW", "LW", "F"),
        __do_get_optimal_forwards(players, "LW", "C", "RW", "F"),
        __do_get_optimal_forwards(players, "LW", "RW", "C", "F"),
        __do_get_optimal_forwards(players, "RW", "C", "LW", "F"),
        __do_get_optimal_forwards(players, "RW", "LW", "C", "F"),
    )


def __get_optimal_defensemen(players):
    total, _ = __get_optimal_by_position(players, "D")
    return total


def __get_optimal_goalies(players):
    total, _ = __get_optimal_by_position(players, "G")
    return total


def __do_get_optimal_forwards(players, first, second, third, fourth):
    first, used = __get_optimal_by_position(players, first)
    second, used = __get_optimal_by_position(players, second, used)
    third, used = __get_optimal_by_position(players, third, used)
    fourth, used = __get_optimal_by_position(players, fourth, used)

    return first + second + third + fourth


def __get_optimal_by_position(players, position, used=[]):
    number_of_spots = POSITIONS[position]

    players = list(
        filter(
            lambda player: player.id not in used
            and position in player.eligible_positions,
            players,
        )
    )[:number_of_spots]

    optimal_points = sum([float(player.points) for player in players])
    used_players = used + [player.id for player in players]

    return optimal_points, used_players

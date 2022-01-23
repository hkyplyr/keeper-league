from datetime import datetime, timedelta

from yfantasy_api.api import YahooFantasyApi, game
from database import Database

db = Database()


def get_sorted_players(api, team_id, week, day):
    players = api.team(team_id).roster(date=day).stats().get().players

    for player in players:
        db.insert_player(
            {
                "id": player.id,
                "team_id": team_id,
                "week": week,
                "date": day,
                "name": player.name,
                "image_url": player.image_url,
                "positions": ",".join(
                    [
                        pos for pos in player.eligible_positions
                    ]
                ),
                "points": player.points,
                "started": player.selected_position not in ["BN", "IR"],
            }
        )

    players = filter(lambda player: float(player.points) >= 0, players)
    players = sorted(players, key=lambda player: float(player.points), reverse=True)
    return list(players)


def get_optimal_position(players, position, number_of_spots, used):
    players = filter(lambda player: player.id not in used, players)
    players = list(filter(lambda player: position in player.eligible_positions, players))

    return [float(player.points) for player in players[:number_of_spots]], used + [
        player.id for player in players[:number_of_spots]
    ]


def get_c_lw_rw(players, used):
    c, used = get_optimal_position(players, "C", 2, used)
    lw, used = get_optimal_position(players, "LW", 2, used)
    rw, used = get_optimal_position(players, "RW", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


def get_c_rw_lw(players, used):
    c, used = get_optimal_position(players, "C", 2, used)
    rw, used = get_optimal_position(players, "RW", 2, used)
    lw, used = get_optimal_position(players, "LW", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


def get_lw_c_rw(players, used):
    lw, used = get_optimal_position(players, "LW", 2, used)
    c, used = get_optimal_position(players, "C", 2, used)
    rw, used = get_optimal_position(players, "RW", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


def get_lw_rw_c(players, used):
    lw, used = get_optimal_position(players, "LW", 2, used)
    rw, used = get_optimal_position(players, "RW", 2, used)
    c, used = get_optimal_position(players, "C", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


def get_rw_c_lw(players, used):
    rw, used = get_optimal_position(players, "RW", 2, used)
    c, used = get_optimal_position(players, "C", 2, used)
    lw, used = get_optimal_position(players, "LW", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


def get_rw_lw_c(players, used):
    rw, used = get_optimal_position(players, "RW", 2, used)
    lw, used = get_optimal_position(players, "LW", 2, used)
    c, used = get_optimal_position(players, "C", 2, used)
    f, used = get_optimal_position(players, "F", 2, used)
    return sum(c) + sum(lw) + sum(rw) + sum(f)


teams = {}
week = 5
api = YahooFantasyApi(4774, "nhl")


def daterange(start, end):
    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')
    num_of_days = (end - start).days + 1
    for d in range(num_of_days):
        yield (start + timedelta(d)).date()


def get_game_ranges():
    game_weeks = api.game().game_weeks().get().game_weeks
    return {
        int(gw.week): daterange(gw.start, gw.end)
        for gw in game_weeks
    }


game_ranges = get_game_ranges()


for i in range(db.get_last_updated_week(), week + 1):
    matchups = api.league().scoreboard(week=i).get().matchups

    for matchup in matchups:
        db.insert_team(
            {
                "id": matchup.winning_team.id,
                "name": matchup.winning_team.name,
                "image_url": matchup.winning_team.team_logos,
            }
        )

        db.insert_team(
            {
                "id": matchup.losing_team.id,
                "name": matchup.losing_team.name,
                "image_url": matchup.losing_team.team_logos,
            }
        )

        proj_points_perc = matchup.winning_team.points / matchup.winning_team.projected_points
        db.insert_weekly_results(
            {
                "team_id": matchup.winning_team.id,
                "week": i,
                "is_winner": True,
                "pf": matchup.winning_team.points,
                "ppf": matchup.winning_team.projected_points,
                "ppf_percentage": proj_points_perc,
            }
        )

        proj_points_perc = matchup.losing_team.points / matchup.losing_team.projected_points
        db.insert_weekly_results(
            {
                "team_id": matchup.losing_team.id,
                "week": i,
                "is_winner": False,
                "pf": matchup.losing_team.points,
                "ppf": matchup.losing_team.projected_points,
                "ppf_percentage": proj_points_perc,
            }
        )

        db.insert_matchup(
            {
                "winner_team": matchup.winning_team.id,
                "loser_team": matchup.losing_team.id,
                "week": i,
                "victory_margin": float(matchup.winning_team.points)
                - float(matchup.losing_team.points),
            }
        )

    teams = api.league().teams().get().teams
    for day in game_ranges.get(i):
        for team in teams:
            print(f'Getting players for {team.name} on {day}')
            players = get_sorted_players(api, team.id, i, day)
            g, used = get_optimal_position(players, "G", 2, [])
            d, used = get_optimal_position(players, "D", 4, used)
            rest = max(
                get_c_lw_rw(players, used),
                get_c_rw_lw(players, used),
                get_lw_c_rw(players, used),
                get_lw_rw_c(players, used),
                get_rw_c_lw(players, used),
                get_rw_lw_c(players, used),
            )
            db.insert_optimal_points(
                {
                    "team_id": team.id,
                    "week": i,
                    "date": day,
                    "points": sum(g + d + [rest]),
                }
            )

    for i in range(1, week + 1):
        db.update_all_play(i)

from yfantasy_api.api import YahooFantasyApi
from database import Database

db = Database()


def get_sorted_players(api, team_id, week):
    players = api.team(team_id).roster(week=week).stats().get().players

    for player in players:
        db.insert_player(
            {
                "id": player.id,
                "team_id": team_id,
                "week": week,
                "name": player.name,
                "image_url": player.image_url,
                "positions": ",".join(
                    [
                        pos
                        for pos in player.eligible_positions
                        if pos in ["QB", "RB", "WR", "TE", "DEF", "K"]
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


def get_rb_wr_te(players, used):
    rb, used = get_optimal_position(players, "RB", 2, used)
    wr, used = get_optimal_position(players, "WR", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_rb_te_wr(players, used):
    rb, used = get_optimal_position(players, "RB", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    wr, used = get_optimal_position(players, "WR", 2, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_wr_rb_te(players, used):
    wr, used = get_optimal_position(players, "WR", 2, used)
    rb, used = get_optimal_position(players, "RB", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


def get_wr_te_rb(players, used):
    wr, used = get_optimal_position(players, "WR", 2, used)
    te, used = get_optimal_position(players, "TE", 1, used)
    rb, used = get_optimal_position(players, "RB", 2, used)
    flx, used = get_optimal_position(players, "W/R/T", 1, used)
    return sum(rb) + sum(wr) + sum(te) + sum(flx)


teams = {}
week = 6
api = YahooFantasyApi(87025, "nfl")

for i in range(1, week + 1):
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
    for team in teams:
        players = get_sorted_players(api, team.id, i)
        qb, used = get_optimal_position(players, "QB", 1, [])
        dst, used = get_optimal_position(players, "DEF", 1, used)
        k, used = get_optimal_position(players, "K", 1, used)
        rest = max(
            get_rb_wr_te(players, used),
            get_rb_te_wr(players, used),
            get_wr_rb_te(players, used),
            get_wr_te_rb(players, used),
        )
        db.insert_optimal_points(
            {
                "team_id": team.id,
                "week": i,
                "points": sum(qb + dst + k + [rest]),
            }
        )

    for i in range(1, week + 1):
        db.update_all_play(i)

from yfantasy_api.api import YahooFantasyApi
from database import Database

db = Database()


def get_sorted_players(api, team_id, week):
    players = api.team(team_id).roster(week=week).stats(week=week).get().players

    for player in players:
        db.insert_player(
            {
                "id": player.player_id,
                "team_id": team_id,
                "week": week,
                "name": player.full_name,
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
    players = filter(lambda player: player.player_id not in used, players)
    players = list(filter(lambda player: position in player.eligible_positions, players))

    return [float(player.points) for player in players[:number_of_spots]], used + [
        player.player_id for player in players[:number_of_spots]
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
        team_one = None
        team_two = None
        for team in matchup.teams:
            if team_one is None:
                team_one = team
            elif team_two is None:
                team_two = team
            db.insert_team(
                {
                    "id": team.team.info.team_id,
                    "name": team.team.info.name,
                    "image_url": team.team.info.team_logos[0]["team_logo"]["url"],
                }
            )
            is_winner = team.team.info.team_key == matchup.winner_team_key
            points_for = float(team.team_points)
            proj_points_for = float(team.team_projected_points)
            proj_points_perc = points_for / proj_points_for
            db.insert_weekly_results(
                {
                    "team_id": team.team.info.team_id,
                    "week": i,
                    "is_winner": is_winner,
                    "pf": points_for,
                    "ppf": proj_points_for,
                    "ppf_percentage": proj_points_perc,
                }
            )
        if team_one.team.info.team_key == matchup.winner_team_key:
            db.insert_matchup(
                {
                    "winner_team": team_one.team.info.team_id,
                    "loser_team": team_two.team.info.team_id,
                    "week": i,
                    "victory_margin": float(team_one.team_points) - float(team_two.team_points),
                }
            )
        else:
            db.insert_matchup(
                {
                    "winner_team": team_two.team.info.team_id,
                    "loser_team": team_one.team.info.team_id,
                    "week": i,
                    "victory_margin": float(team_two.team_points) - float(team_one.team_points),
                }
            )

    teams = api.league().teams().get().teams
    for team in teams:
        players = get_sorted_players(api, team.info.team_id, i)
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
                "team_id": team.info.team_id,
                "week": i,
                "points": sum(qb + dst + k + [rest]),
            }
        )

    for i in range(1, week + 1):
        db.update_all_play(i)

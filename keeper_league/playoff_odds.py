from yfantasy_api.api import YahooFantasyApi
from database import Database
from statistics import mean, stdev
import math
import random
import copy

fantasy_api = YahooFantasyApi(87025, "nfl")
db = Database()

points_for = {}
for week in range(1, 11):
    for result in db.get_rolling_points_for(week):
        if result[0] not in points_for:
            points_for[result[0]] = {"pf": []}
        points_for[result[0]]["pf"].append(result[1])
for value in points_for.values():
    value["avg"] = mean(value["pf"][1:])
    value["std"] = stdev(value["pf"][1:])

standings = {}
for team in db.get_standings(5):
    team_data = {"w": team.wins, "l": team.losses, "pf": team.raw_pf}
    standings[team.name] = team_data

remaining_matchups = []
for week in range(1, 14 + 1):
    matchups = fantasy_api.league().scoreboard(week=week).get().matchups
    for m in matchups:
        if m.status == "postevent":
            continue
        team_one_info = m.teams[0].team.info
        team_two_info = m.teams[1].team.info
        matchup = {
            "team_one": {"id": team_one_info.team_id, "name": team_one_info.name},
            "team_two": {"id": team_two_info.team_id, "name": team_two_info.name},
        }
        remaining_matchups.append(matchup)


def random_bm():
    u = 0
    v = 0
    while u == 0:
        u = random.random()
    while v == 0:
        v = random.random()
    return math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)


def monte_carlo(team_variables, standings, matchups, iterations=10000):
    results = {}
    for team in standings:
        results[team] = [0] * 12

    for _ in range(iterations):
        final_standings = simulate_season(team_variables, standings, matchups)
        for team, value in final_standings.items():
            results[team][value - 1] += 1.0 / iterations * 100

    results = dict(sorted(results.items(), key=lambda x: sum(x[1][:6]), reverse=True))
    return results


def simulate_season(team_variables, standings, matchups):
    final_standings = copy.deepcopy(standings)
    for matchup in matchups:
        team_one = matchup["team_one"]["name"]
        team_two = matchup["team_two"]["name"]
        team_one_pf = (
            team_variables[team_one]["avg"] + random_bm() * team_variables[team_one]["std"]
        )
        team_two_pf = (
            team_variables[team_two]["avg"] + random_bm() * team_variables[team_two]["std"]
        )

        final_standings[team_one]["pf"] += team_one_pf
        final_standings[team_two]["pf"] += team_two_pf
        if team_one_pf > team_two_pf:
            final_standings[team_one]["w"] += 1
            final_standings[team_two]["l"] += 1
        elif team_one_pf < team_two_pf:
            final_standings[team_one]["l"] += 1
            final_standings[team_two]["w"] += 1
    final_standings = dict(
        sorted(final_standings.items(), key=lambda x: (x[1]["w"], x[1]["pf"]), reverse=True)
    )

    final_standings_prob = {}
    for i, standings in enumerate(final_standings.items()):
        final_standings_prob[standings[0]] = i + 1
    return final_standings_prob


headers = "Bye\tMake Playoffs\tTeam"
for team, result in monte_carlo(points_for, standings, remaining_matchups).items():
    if headers:
        print(headers)
        headers = None
    first = round(result[0], 1)
    second = round(result[1], 1)
    third = round(result[2], 1)
    fourth = round(result[3], 1)
    fifth = round(result[4], 1)
    sixth = round(result[5], 1)

    have_bye = round(sum(result[:2]), 1)
    make_playoffs = round(sum(result[:6]), 1)
    if make_playoffs:
        if have_bye == 100.0:
            have_bye = 100
        if make_playoffs == 100.0:
            make_playoffs = 100
        have_bye = f"{have_bye}%" if have_bye != 0.0 else "-"
        make_playoffs = f"{make_playoffs}%"

        team_record = f'({standings.get(team).get("w")}-{standings.get(team).get("l")})'
        print(f"{have_bye}\t\t{make_playoffs}\t{team} {team_record}")

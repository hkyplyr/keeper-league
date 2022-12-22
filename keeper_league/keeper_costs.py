from itertools import zip_longest
from yfantasy_api.api import YahooFantasyApi

import csv
import json
import os

api = YahooFantasyApi(6738, "nhl")

ordinal = lambda n: "%d%s" % (
    n,
    "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10 :: 4],
)


def trades():
    return api.league().transactions(ttype="trade").get().transactions


def draft_results():
    return api.league().draft_results().get().draft_results


def teams():
    return api.league().teams().get().teams


def roster(team_id):
    return api.team(team_id).roster().get().players


def draft_round(draft_pick):
    draft_round = draft_pick.round - 2
    return draft_round if draft_round > 0 else 0


def get_draft_costs():
    return {
        draft_pick.player.id: draft_round(draft_pick) for draft_pick in draft_results()
    }


def get_roster(team):
    players = [
        [player.name, draft_costs.get(player.id, 14)] for player in roster(team.id)
    ]

    return [[team.name, None]] + sorted(players, key=lambda x: (x[1], x[0]))


def get_initial_picks():
    initial_picks = {}
    for team in teams():
        initial_picks[team.name] = []

        for draft_round in range(1, 21):
            pick_key = (f"{ordinal(draft_round)} Round", draft_round)

            initial_picks[team.name].append(pick_key)

    return initial_picks


def determine_current_draft_picks():
    initial_picks = get_initial_picks()

    for trade in trades():
        for pick in trade.traded_picks:
            draft_round = int(pick.round)

            if pick.original_team_name == pick.source_team_name:
                initial_picks[pick.source_team_name].remove(
                    (f"{ordinal(draft_round)} Round", draft_round)
                )
                initial_picks[pick.destination_team_name].append(
                    (
                        f"{ordinal(draft_round)} Round ({pick.original_team_name})",
                        draft_round,
                    )
                )
            elif pick.original_team_name == pick.destination_team_name:
                initial_picks[pick.source_team_name].remove(
                    (
                        f"{ordinal(draft_round)} Round ({pick.original_team_name})",
                        draft_round,
                    )
                )
                initial_picks[pick.destination_team_name].append(
                    (f"{ordinal(draft_round)} Round", draft_round)
                )
            else:
                initial_picks[pick.source_team_name].remove(
                    (
                        f"{ordinal(draft_round)} Round ({pick.original_team_name})",
                        draft_round,
                    )
                )
                initial_picks[pick.destination_team_name].append(
                    (
                        f"{ordinal(draft_round)} Round ({pick.original_team_name})",
                        draft_round,
                    )
                )

    for picks in initial_picks.values():
        picks.sort(key=lambda x: (x[1], x[0]))

    return [
        [item for sublist in row for item in sublist]
        for row in zip(*initial_picks.values())
    ]


if __name__ == "__main__":
    token_content = json.loads(os.environ.get("TOKEN_FILE"))
    print(token_content.get("expires_by"))


    draft_costs = get_draft_costs()

    players_by_team = [get_roster(team) for team in teams()]
    rotated_players = zip_longest(*players_by_team, fillvalue=[None, None])
    picks = determine_current_draft_picks()

    with open("keeper-costs.csv", "w") as f:
        writer = csv.writer(f)

        for row in rotated_players:
            flattened = [item for sublist in row for item in sublist]
            writer.writerow(flattened)

        writer.writerows(picks)

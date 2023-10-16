import csv
import json
import os
from base64 import b64encode
from itertools import zip_longest

import requests
from nacl import encoding, public
from yfantasy_api.api import YahooFantasyApi

if not os.path.exists(".tokens.json"):
    with open(".tokens.json", "w") as f:
        f.write(os.environ.get("TOKEN_FILE"))

api = YahooFantasyApi(65227, "nhl")

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


def encrypt_token_data():
    data = json.dumps(
        {
            "access_token": api.access_token,
            "refresh_token": api.refresh_token,
            "expires_by": api.expires_by,
        }
    )

    public_key = os.environ.get("PUBLIC_KEY")
    public_key = public.PublicKey(
        public_key.encode("utf-8") + b"==", encoding.URLSafeBase64Encoder()
    )
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(data.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


def update_github_tokens():
    if os.environ.get("SHOULD_UPDATE_TOKENS") != "true":
        return

    url = (
        "https://api.github.com/repos/hkyplyr/keeper-league/actions/secrets/TOKEN_FILE"
    )
    payload = {
        "encrypted_value": encrypt_token_data(),
        "key_id": os.environ.get("PUBLIC_KEY_ID"),
    }

    access_token = os.environ.get("GH_ACCESS_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access_token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    requests.put(url, data=json.dumps(payload), headers=headers)


if __name__ == "__main__":

    draft_costs = get_draft_costs()

    players_by_team = [get_roster(team) for team in teams()]
    rotated_players = zip_longest(*players_by_team, fillvalue=[None, None])
    picks = determine_current_draft_picks()

    with open("docs/keeper-costs.csv", "w") as f:
        writer = csv.writer(f)

        for row in rotated_players:
            flattened = [item for sublist in row for item in sublist]
            writer.writerow(flattened)

        writer.writerows(picks)

    update_github_tokens()

import csv
import itertools

from yfantasy_api.api import YahooFantasyApi

api = YahooFantasyApi(4774, "nhl")


def __added_pick(pick, original_team):
    pick_round = int(pick.round)
    if pick.original_team_key == pick.destination_team_key:
        return __format_pick(pick_round)
    else:
        return __format_pick(pick_round, original_team)


def __calculate_draft_cost(player, draft_results):
    return max(0, draft_results.get(player.name, 16) - 2)


def __flatten(list_of_tuples):
    return [item for sublist in list_of_tuples for item in sublist]


def __format_pick(pick_round, original_team=None):
    return (__pick_name(pick_round, original_team), pick_round)


def __get_manager_name(team):
    manager_name = team.managers[0].name
    name = manager_name.split(" ")[0].capitalize()
    if name == "Prime":
        return "Kenzie"
    return name


def __get_players_for_team(team_id, draft_results):
    players = [
        (player.name, __calculate_draft_cost(player, draft_results))
        for player in api.team(team_id).roster().get().players
    ]

    return sorted(players, key=lambda x: x[1])


def __pick_name(pick_round, team=None):
    ordinals = {1: "st", 2: "nd", 3: "rd"}
    if pick_round % 100 // 10 != 1:
        suffix = ordinals.get(pick_round % 10, "th")
    else:
        suffix = "th"

    pick_name = f"{pick_round}{suffix} Round"
    if team:
        pick_name = f"{pick_name} ({team})"
    return pick_name


def __removed_pick(pick, original_team):
    pick_round = int(pick.round)
    if pick.original_team_key == pick.source_team_key:
        return __format_pick(pick_round)
    else:
        return __format_pick(pick_round, original_team)


def get_picks_by_team():
    teams = api.league().teams().get().teams
    team_managers = {team.key: __get_manager_name(team) for team in teams}

    initial_picks = {
        team.key: [(__pick_name(pick + 1), pick + 1) for pick in range(20)]
        for team in teams
    }

    for transaction in api.league().transactions().get().transactions:
        if transaction.type != "trade":
            continue

        for pick in transaction.traded_picks:
            original_team = team_managers.get(pick.original_team_key)
            added_pick = __added_pick(pick, original_team)
            removed_pick = __removed_pick(pick, original_team)

            initial_picks[pick.source_team_key].remove(removed_pick)
            initial_picks[pick.destination_team_key].append(added_pick)
            initial_picks[pick.destination_team_key].sort(key=lambda x: x[1])

    return initial_picks


def get_players_by_team():
    draft_results = {
        pick.player.name: pick.round
        for pick in api.league().draft_results().get().draft_results
    }

    return {
        __get_manager_name(team): __get_players_for_team(team.id, draft_results)
        for team in api.league().teams().get().teams
    }


def __combine_lists(data):
    combined = itertools.zip_longest(*data.values(), fillvalue=(None, None))
    return [__flatten(combined_list) for combined_list in combined]


def main():
    player_costs = get_players_by_team()
    picks = get_picks_by_team()

    headers = __flatten(map(lambda x: (x, None), player_costs.keys()))
    player_csv = __combine_lists(player_costs)
    picks_csv = __combine_lists(picks)

    with open("docs/keeper.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(player_csv)
        writer.writerows(picks_csv)


if __name__ == "__main__":
    main()

from yfantasy_api.api import YahooFantasyApi
import argparse
import csv
import itertools
from datetime import date

TEAM_MAP = {}

yfs = YahooFantasyApi(league_id=17457, game_id='nhl')

def get_todays_date():
    return str(date.today())

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', action='store_true', default=False, help='Output useful debug information')
args = parser.parse_args()


def __get_draft_costs():
    """Get drafted player keeper costs using the Yahoo Fantasy API.
    Return a map of player ids to their keeper costs.
    """
    draft_picks = yfs.league().draft_results().get().draft_results
    keeper_costs = {}
    for d in draft_picks:
        player_key = d.player_key
        cost = max(0, min(d.round - 2, 20))
        keeper_costs[player_key] = cost
    return keeper_costs


def __parse_manager_name(team_info):
    """Parse and format a manager's name from their team info JSON.
    If a manager has first and list name or is not capitalized, we
    drop the last name and capitalize the first name accordingly.

    Keyword arguments:
    team_info -- the JSON data containing the team and manager's info
    """
    return team_info[19]['managers'][0]['manager']['nickname'].split(' ', 1)[0].capitalize()


def __get_roster_costs(draft_costs, team_key):
    """Get keeper costs for each player on a given team's roster.
    If the player does not have a calculated keeper cost from the draft_costs
    map we default to 18th round.

    Keywor arguments:
    draft_costs -- the draft costs map, mapping a player to their cost
    team_id -- the id of the team to get the roster for
    """
    # TODO: add support for querying the team API by key
    team_id = team_key[14:]
    team_roster = yfs.team(team_id).roster().get().players
    team_map = __get_team_map()

    players = []
    for p in team_roster:
        player_key = p.player_key
        player_name = p.full_name
        players.append((player_name, draft_costs.get(player_key, 14)))
    return team_map[team_key], sorted(players, key=lambda x: (x[1], x[0]))


def __combine_lists(data, fillvalue=(None, None)):
    """Combine an arbitrary number of lists such that the first n
    values are the first values in each individual list, the next n
    values are the second value in each individual list and so on.

    If the lists are not the same length we use a default value to
    pad the resulting list.

    Keyword arguments:
    data -- the list of lists to be combined
    fillvalue -- the value to use to pad the list lengths
    """
    zipped = list(itertools.zip_longest(*data, fillvalue=fillvalue))
    for i, row in enumerate(zipped):
        zipped[i] = [item for sublist in row for item in sublist]
    return zipped


def __get_ordinal(value):
    """Provides the ordinal value for a given integer
    For example `1` returns 'st', `2` returns 'nd', etc.

    Keyword arguments:
    value -- the integer used to retrieve the ordinal
    """
    value = int(value)
    if value % 100 // 10 != 1:
        if value % 10 == 1:
            return "st"
        elif value % 10 == 2:
            return "nd"
        elif value % 10 == 3:
            return "rd"
        else:
            return "th"
    else:
        return "th"


def __generate_initial_picks():
    """Generate a map of lists of initial draft picks for each team.
    """
    picks_by_team = {}
    for team in yfs.league().teams().get().teams:
        team_key = team.info.team_key
        picks = []
        for pick in range(1, 21):
            picks.append((pick, team_key))
        picks_by_team[team_key] = picks
    return picks_by_team


def __get_updated_picks():
    """Update the list of initial picks by checking the list of transactions
    from the Yahoo Fantasy API. If a pick is traded we add the pick to the
    destination team's list and remove it from the source team's list.
    """
    initial_picks = __generate_initial_picks()
    transactions = yfs.league().transactions(ttype='trade').get().transactions
    for t in transactions:
        if t.type != 'trade':
            # Picks are only moved in a trade.
            continue

        if not t.traded_picks:
            # If a trade does not contain picks, we don't care.
            continue

        for p in t.traded_picks:
            source = p.source_team_key
            dest = p.destination_team_key
            # TODO: Fix yfantasy-api round to be an integer
            moved_pick = (int(p.round), p.original_team_key)
            initial_picks[source].remove(moved_pick)
            initial_picks[dest].append(moved_pick)

    return initial_picks


def __get_team_map():
    """Create or retrieve a map of team information (manager name),
    keyed by the team id.
    """
    if TEAM_MAP:
        return TEAM_MAP

    teams = yfs.league().teams().get().teams
    for t in teams:
        team_key = t.info.team_key
        manager = t.info.managers[0].nickname.split(' ', 1)[0].capitalize()
        TEAM_MAP[team_key] = manager
    return TEAM_MAP


def log(text_to_print, debug=args.debug):
    if debug:
        print(text_to_print)


def get_rosters_for_csv():
    """Retrieve the list of players for each team, formatted for printing
    in columns to a csv file.
    """
    keeper_costs = __get_draft_costs()
    headers = []
    rosters = []
    for team in yfs.league().teams().get().teams:
        name, costs = __get_roster_costs(keeper_costs, team.info.team_key)
        log(f'\n{name}')
        for player in costs:
            log(f'{player[0]}, {player[1]}')
        headers.append(name)
        headers.append(None)
        rosters.append(costs)
    return headers, __combine_lists(rosters)


def get_picks_for_csv():
    """Retrieve the list of draft picks for each team, formatted for printing
    in columns to a csv file.
    """
    team_map = __get_team_map()
    picks_by_team = __get_updated_picks()
    pick_matrix = []
    for team, picks in picks_by_team.items():
        pick_list = []
        sorted_picks = sorted(picks, key=lambda x: (x[0]))
        for pick in sorted_picks:
            text = f'{pick[0]}{__get_ordinal(pick[0])} Round'
            if pick[1] != team:
                text = text + f' ({team_map[pick[1]]})'
            pick_list.append((text, pick[0]))
        pick_matrix.append(pick_list)

    return __combine_lists(pick_matrix)


def output_csv(teams, rosters, picks, file_prefix='keepercosts'):
    """Output the provided data to a csv file.

    Keyword arguments:
    filename -- the name of the file to create/open for writing
    teams -- the list of team names to use as the header
    rosters -- the row-formatted lists of players with hteir keeper cost
    picks -- the row-formatted list of draft picks
    """
    todays_date = get_todays_date()
    filename = f'out/{file_prefix}-{todays_date}.csv'

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(teams)
        writer.writerows(rosters)
        writer.writerows(picks)
        writer.writerow([f'Data pulled on {todays_date}'])


if __name__ == '__main__':
    teams, rosters = get_rosters_for_csv()
    picks = get_picks_for_csv()
    output_csv(teams, rosters, picks)

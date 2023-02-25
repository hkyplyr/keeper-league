import json
import os
import sys

from database import Database
from queries import Awards, PowerRankings, Standings, Teams

colors = {
    1: "bg-gray-500",
    2: "bg-green-500",
    3: "bg-blue-500",
    4: "bg-violet-500",
    5: "bg-pink-500",
    6: "bg-red-500",
    7: "bg-purple-500",
    8: "bg-fuchsia-500",
    9: "bg-indigo-500",
    10: "bg-yellow-500",
    11: "bg-orange-500",
    12: "bg-teal-500",
}


def get_and_prepare_power_rankings(week):
    power_rankings = PowerRankings.get_power_rankings(week)
    for row in power_rankings:
        row["color"] = colors[row["team_id"]]
        row["writeup"] = ""

    return power_rankings


db = Database()


def get_week():
    if len(sys.argv) == 1:
        print("Must provide week")
        exit()

    week = int(sys.argv[1])
    last_updated_week = db.get_last_updated_week()
    if week <= 0 or week > last_updated_week:
        print("Provided week is invalid")
        exit()

    return week


if __name__ == "__main__":
    week = get_week()

    filepath = f"docs/data/week-{week}.json"
    if os.path.exists(filepath):
        print(f"{filepath} already exists, skipping...")
    else:
        data = {
            "standings": Standings.get_standings(week),
            "powerRankings": get_and_prepare_power_rankings(week),
            "awards": Awards.get_awards(week),
            "allStarTeam": Teams.get_top_players(week),
            "allBustTeam": Teams.get_bottom_players(week),
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent="    ")

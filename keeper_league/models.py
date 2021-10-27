class PlayerAwards:
    def __init__(self, row):
        self.player_name = row[0]
        self.player_image = row[1]
        self.points = format_points(row[2])
        self.team_name = row[3]
        self.team_image = row[4]
        self.award_name = row[5]

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.items() if "image" not in k})


class PowerRankingsTeam:
    def __init__(self, row, previous_ranks):
        self.rank = row[0]
        self.name = row[1]
        self.movement = self.__get_rank_movement(previous_ranks)
        self.record = format_record(row[2], row[3])
        self.pf = format_points(row[4])
        self.coach = format_percentage(row[5])

    def __get_rank_movement(self, previous_ranks):
        previous_rank = previous_ranks.get(self.name)
        if not previous_rank:
            return 0
        return previous_rank - self.rank

    def __repr__(self):
        return str(self.__dict__)


class StandingsTeam:
    def __init__(self, row):
        self.rank = row[0]
        self.name = row[1]
        self.wins = row[2]
        self.losses = row[3]
        self.record = format_record(row[2], row[3])
        self.raw_pf = row[4]
        self.pf = format_points(row[4])
        self.luck = format_percentage(row[5])

    def __repr__(self):
        return str(self.__dict__)


class TeamAwards:
    def __init__(self, row):
        self.team_one_name = row[0]
        self.team_one_image = row[1]
        self.team_two_name = row[2]
        self.team_two_image = row[3]
        self.points = format_points(row[4])
        self.percentage = format_percentage(row[5])
        self.award_name = row[6]

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.items() if "image" not in k})


class WeeklyResultsTeam:
    def __init__(self, row):
        self.rank = row[0]
        self.name = row[1]
        self.result = "W" if row[2] else "L"
        self.pf = format_points(row[3])
        self.opf = format_points(row[4])
        self.coach = format_percentage(row[5])

    def __repr__(self):
        return str(self.__dict__)


def format_percentage(percentage):
    if not percentage:
        return percentage

    formatted_percentage = "{:.1f}".format(percentage)
    if formatted_percentage == "100.0":
        return "100"
    return f"{formatted_percentage}"


def format_points(points):
    if not points:
        return points

    return "{:.2f}".format(points)


def format_record(wins, losses):
    return f"({wins}-{losses})"

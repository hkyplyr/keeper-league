def format_points(points, places=2):
    if places == 1:
        return "{:.1f}".format(points)
    else:
        return "{:.2f}".format(points)


def format_percentage(percentage):
    if percentage is None:
        return percentage

    formatted_percentage = "{:.1f}".format(percentage)
    if formatted_percentage == "100.0":
        return "100"
    return f"{formatted_percentage}"


def format_win_percentage(percentage):
    return "{:.3f}".format(percentage)

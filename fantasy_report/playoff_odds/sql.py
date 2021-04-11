GET_STANDINGS = """
    SELECT
        t.team_name,
        sum(wr.winner) AS wins,
        count(wr.winner) - sum(wr.winner) AS losses,
        sum(wr.points_for) AS pf,
        sum(op.points),
        sum(wr.projection)
    FROM teams t
    JOIN weekly_results wr ON t.id = wr.team_id
    JOIN optimal_points op ON op.team_id = wr.team_id AND op.week = wr.week
    JOIN all_play ap ON ap.team_id = op.team_id AND ap.week = op.week
    GROUP BY t.team_name
    ORDER BY wins DESC, pf DESC;
"""

GET_AVERAGE_POINTS = """
    SELECT
        t.team_name,
        wr.points_for
    FROM teams t
    JOIN weekly_results wr ON t.id = wr.team_id
    WHERE wr.week = ?
    GROUP BY t.team_name;
"""

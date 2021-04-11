GET_MATCHUP_DATA = """
    SELECT
        t1.team_name,
        wr.points_for,
        wr2.points_for,
        t2.team_name
    FROM weekly_results wr
    JOIN teams t1 ON t1.id = wr.team_id
    JOIN teams t2 ON t2.id = wr.opponent
    JOIN weekly_results wr2 ON wr2.team_id = wr.opponent AND wr.week = wr2.week
    WHERE wr.week = ?1 AND wr.winner = True
    ORDER BY wr.points_for DESC;
"""

GET_ROLLING_REPORT = """
    SELECT
        t.team_name as team_name,
        sum(wr.winner) as wins,
        count(wr.winner) - sum(wr.winner) as losses,
        sum(ap.wins) as all_win,
        count(ap.wins) * 11 - sum(ap.wins) as all_losses,
        count(ap.wins) * 11 as all_games,
        sum(wr.points_for) as pf,
        sum(op.points) as opf,
        sum(wr.projection) as ppf
    FROM teams t
    JOIN weekly_results wr ON t.id = wr.team_id
    JOIN optimal_points op ON (op.team_id = wr.team_id AND op.week = wr.week)
    JOIN all_play ap ON ap.team_id = op.team_id AND ap.week = op.week
    WHERE wr.week <= ?1
    GROUP BY t.team_name;
"""

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
    WHERE wr.week <= ?
    GROUP BY t.team_name
    ORDER BY wins DESC, pf DESC;
"""

GET_TOP_PLAYER_FOR_TEAM = """
    SELECT
        p.name,
        sum(s.points)
    FROM stats s
        JOIN players p ON s.player_id = p.id
        JOIN teams t ON t.id = s.team_id
    WHERE s.week = ?
    AND t.team_name = ?
    GROUP BY p.name, t.team_name
    ORDER BY sum(s.points) DESC
    LIMIT 1;
"""

GET_WEEK_REPORT_DATA = """
    SELECT 
        t.team_name,
        sum(w.points_for),
        sum(w.winner),
        sum(w.points_for) / sum(o.points)
    FROM weekly_results w
        JOIN teams t ON w.team_id = t.id
        JOIN optimal_points o ON o.team_id = t.id AND o.week = w.week
    WHERE w.week = ?
    GROUP BY t.team_name;
"""

GET_YEAR_REPORT_DATA = """
    SELECT 
        t.team_name,
        sum(w.points_for),
        sum(w.winner),
        count(w.winner) - sum(w.winner),
        sum(w.points_for) / sum(o.points)
    FROM weekly_results w
        JOIN teams t ON w.team_id = t.id
        JOIN optimal_points o ON o.team_id = t.id AND o.week = w.week
    WHERE w.week <= ?
    GROUP BY t.team_name;
"""
SELECT * FROM (
    SELECT t1.name, t1.image_url, t2.name, t2.image_url, m.victory_margin, NULL, "Biggest Blowout"
    FROM matchups m
    JOIN teams t1 ON t1.id = m.winner_team
    JOIN teams t2 ON t2.id = m.loser_team
    WHERE m.week = :week
    ORDER BY m.victory_margin DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t1.name, t1.image_url, t2.name, t2.image_url, m.victory_margin, NULL, "Closest Victory"
    FROM matchups m
    JOIN teams t1 ON t1.id = m.winner_team
    JOIN teams t2 ON t2.id = m.loser_team
    WHERE m.week = :week
    ORDER BY m.victory_margin
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, wr.pf, NULL, "Highest Scorer"
    FROM weekly_results wr
    JOIN teams t on t.id = wr.team_id
    WHERE wr.week = :week
    ORDER BY wr.pf DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, wr.pf, NULL, "Lowest Scorer"
    FROM weekly_results wr
    JOIN teams t on t.id = wr.team_id
    WHERE wr.week = :week
    ORDER BY wr.pf
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, NULL, (wr.pf / wr.ppf * 100), "Overacheiving Team"
    FROM weekly_results wr
    JOIN teams t on t.id = wr.team_id
    WHERE wr.week = :week
    ORDER BY (wr.pf / wr.ppf * 100) DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, NULL, (wr.pf / wr.ppf * 100), "Underacheiving Team"
    FROM weekly_results wr
    JOIN teams t on t.id = wr.team_id
    WHERE wr.week = :week
    ORDER BY (wr.pf / wr.ppf * 100)
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, NULL, (wr.pf / op.points * 100), "Best Coach"
    FROM weekly_results wr
    JOIN teams t ON t.id = wr.team_id
    JOIN optimal_points op ON op.team_id = wr.team_id AND op.week = wr.week
    WHERE wr.week = :week
    ORDER BY (wr.pf / op.points * 100) DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT t.name, t.image_url, NULL, NULL, NULL, (wr.pf / op.points * 100), "Worst Coach"
    FROM weekly_results wr
    JOIN teams t ON t.id = wr.team_id
    JOIN optimal_points op ON op.team_id = wr.team_id AND op.week = wr.week
    WHERE wr.week = :week
    ORDER BY (wr.pf / op.points * 100)
    LIMIT 1
)
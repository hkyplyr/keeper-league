SELECT
    ROW_NUMBER() OVER (
        ORDER BY wr.is_winner DESC, wr.pf DESC
    ) as rk,
    t.name,
    wr.is_winner,
    wr.pf,
    sum(op.points),
    (wr.pf / sum(op.points) * 100) as coach
FROM teams t
    JOIN weekly_results wr ON t.id = wr.team_id
    JOIN optimal_points op ON op.team_id = wr.team_id AND op.week = wr.week
WHERE op.week = :week
GROUP BY t.name, wr.is_winner, wr.pf
ORDER BY wr.is_winner DESC, wr.pf DESC;

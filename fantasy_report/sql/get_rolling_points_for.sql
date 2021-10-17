SELECT t.name, wr.pf
FROM teams t
JOIN weekly_results wr ON t.id = wr.team_id
WHERE wr.week = :week
GROUP BY t.name;
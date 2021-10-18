INSERT INTO all_play (team_id, week, all_win, all_loss)
SELECT
    t.id,
    wr.week,
    RANK() OVER (
        ORDER BY wr.pf
    ) - 1 all_win,
    RANK() OVER (
        ORDER BY wr.pf DESC
    ) - 1 all_loss
FROM weekly_results wr
JOIN teams t ON t.id = wr.team_id
WHERE week = :week
ON CONFLICT DO NOTHING;
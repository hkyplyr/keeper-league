SELECT 
    ROW_NUMBER() OVER (
        ORDER BY pr desc, all_win desc, points desc
    ) as rk,
    name, all_win, all_loss, points, coach, test_pf, test_opf
FROM (
SELECT
    (
        RANK() OVER (
        ORDER BY sum(ap.all_win)
    ) +
        RANK() OVER (
        ORDER BY sum(op.points)
    ) +
        RANK() OVER (
        ORDER BY sum(wr.pf)
    ) +
        RANK() OVER (
        ORDER BY sum(wr.is_winner)
    )
    ) as pr,
    t.name,
    sum(ap.all_win) as all_win,
    sum(ap.all_loss) as all_loss,
    sum(op.points) as points,
    (sum(wr.pf) / sum(op.points)) * 100 as coach,
    sum(wr.pf) as test_pf,
    sum(op.points) as test_opf
FROM teams t
    JOIN all_play ap ON 
        ap.team_id = t.id
    JOIN (SELECT team_id, week, sum(points) as points FROM optimal_points GROUP BY team_id, week) AS op
        ON op.team_id == ap.team_id AND op.week = ap.week
    JOIN weekly_results wr ON
        wr.team_id = op.team_id AND wr.week = op.week
WHERE wr.week <= :week
GROUP BY t.name)
ORDER BY pr desc, all_win desc, points desc;
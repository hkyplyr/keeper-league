SELECT
    ROW_NUMBER() OVER (
        ORDER BY sum(wr.is_winner) DESC, sum(wr.pf) DESC
    ) as rk,
    t.name,
    sum(wr.is_winner) as wins,
    count(wr.is_winner) - sum(wr.is_winner) as losses,
    sum(wr.pf),
    ((sum(wr.is_winner) * 1.0 / count(wr.is_winner)) - (sum(ap.all_win) * 1.0 / (sum(ap.all_win) + sum(ap.all_loss)))) * 100
FROM teams t
    JOIN weekly_results wr ON t.id = wr.team_id
    JOIN all_play ap ON ap.team_id = wr.team_id AND ap.week = wr.week
WHERE wr.week <= :week
GROUP BY t.name
ORDER BY sum(wr.is_winner) DESC, sum(wr.pf) DESC;
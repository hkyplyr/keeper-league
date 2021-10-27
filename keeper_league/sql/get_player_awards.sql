SELECT * FROM (
    SELECT p.name, p.image_url, sum(p.points), t.name, t.image_url, "Best Forward"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions NOT LIKE '%D%' AND positions NOT LIKE '%G%' AND started = True
    GROUP BY p.name, p.image_url, t.name, t.image_url
    ORDER BY sum(p.points) DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, sum(p.points), t.name, t.image_url, "Best Defencemen"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%D%' AND started = True
    GROUP BY p.name, p.image_url, t.name, t.image_url
    ORDER BY sum(p.points) DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, sum(p.points), t.name, t.image_url, "Best Goalie"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%G%' AND started = True
    GROUP BY p.name, p.image_url, t.name, t.image_url
    ORDER BY sum(p.points) DESC
    LIMIT 1
)
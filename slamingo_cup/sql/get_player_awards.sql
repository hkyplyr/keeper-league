SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Starting QB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%QB%' AND started = True
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Starting RB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%RB%' AND started = True
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Starting WR"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%WR%' AND started = True
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Starting TE"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%TE%' AND started = True
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Worst Starting QB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%QB%' AND started = True
    ORDER BY p.points
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Worst Starting RB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%RB%' AND started = True
    ORDER BY p.points
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Worst Starting WR"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%WR%' AND started = True
    ORDER BY p.points
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Worst Starting TE"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%TE%' AND started = True
    ORDER BY p.points
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Benched QB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%QB%' AND started = False
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Benched RB"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%RB%' AND started = False
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Benched WR"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%WR%' AND started = False
    ORDER BY p.points DESC
    LIMIT 1
) UNION ALL
SELECT * FROM (
    SELECT p.name, p.image_url, p.points, t.name, t.image_url, "Best Benched TE"
    FROM players p
    JOIN teams t on t.id = p.team_id
    WHERE week = :week AND positions LIKE '%TE%' AND started = False
    ORDER BY p.points DESC
    LIMIT 1
)
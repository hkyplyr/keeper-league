INSERT INTO players (id, team_id, week, name, image_url, positions, points, started)
VALUES (:id, :team_id, :week, :name, :image_url, :positions, :points, :started)
ON CONFLICT(id, team_id, week) DO UPDATE SET name = :name, image_url = :image_url, positions = :positions, points = :points, started = :started;
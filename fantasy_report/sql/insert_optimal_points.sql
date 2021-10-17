INSERT INTO optimal_points (team_id, week, points)
VALUES (:team_id, :week, :points)
ON CONFLICT(team_id, week) DO UPDATE SET points = :points;
INSERT INTO optimal_points (team_id, week, date, points)
VALUES (:team_id, :week, :date, :points)
ON CONFLICT(team_id, date) DO UPDATE SET points = :points;
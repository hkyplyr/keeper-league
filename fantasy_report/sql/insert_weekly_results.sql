INSERT INTO weekly_results (team_id, week, is_winner, pf, ppf, ppf_percentage)
VALUES (:team_id, :week, :is_winner, :pf, :ppf, :ppf_percentage)
ON CONFLICT(team_id, week) DO UPDATE SET is_winner = :is_winner, pf = :pf, ppf = :ppf, ppf_percentage = :ppf_percentage
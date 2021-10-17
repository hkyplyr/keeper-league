INSERT INTO matchups (winner_team, loser_team, week, victory_margin)
VALUES (:winner_team, :loser_team, :week, :victory_margin)
ON CONFLICT(winner_team, loser_team, week) DO UPDATE SET victory_margin = :victory_margin;
INIT_TABLES = """
    CREATE TABLE IF NOT EXISTS players (
        id int,
        name varchar,
        PRIMARY KEY (id)
    );

    CREATE TABLE IF NOT EXISTS teams (
        id int,
        team_name varchar,
        PRIMARY KEY (id)
    );

    CREATE TABLE IF NOT EXISTS weekly_results (
        week int,
        team_id int,
        points_for real,
        projection real,
        winner int,
        opponent int,
        PRIMARY KEY (week, team_id)
    );

    CREATE TABLE IF NOT EXISTS stats (
        player_id int,
        team_id int,
        positions varchar,
        game_date date,
        points real,
        week int,
        PRIMARY KEY (game_date, player_id)
    );

    CREATE TABLE IF NOT EXISTS optimal_points (
        team_id int,
        week int,
        points real,
        PRIMARY KEY (team_id, week)
    );

    CREATE TABLE IF NOT EXISTS all_play (
        team_id int,
        week int,
        wins int,
        PRIMARY KEY (team_id, week)
    );
"""

GET_LATEST_WEEK = """
    SELECT max(week) FROM weekly_results;
"""

GET_PLAYERS_BY_POSITION = """
    SELECT
        player_id,
        positions,
        game_date,
        points
    FROM stats
    WHERE team_id = ?
    AND game_date = ?
    AND instr(positions, ?) > 0
    AND points >= 0
    ORDER BY points DESC;
"""

UPSERT_ALL_PLAY_RECORD = """
    INSERT INTO all_play (team_id, week, wins)
    VALUES (?1, ?2, ?3)
    ON CONFLICT (team_id, week)
    DO UPDATE SET wins = ?3;
"""

UPSERT_OPTIMAL_POINTS = """
    INSERT INTO optimal_points (team_id, week, points)
    VALUES (?1, ?2, ?3)
    ON CONFLICT (team_id, week)
    DO UPDATE SET points = ?3;
"""

UPSERT_PLAYER = """
    INSERT INTO players (id, name)
    VALUES (?1, ?2)
    ON CONFLICT (id)
    DO UPDATE SET name = ?2;
"""

UPSERT_STATS = """
    INSERT INTO stats (
        player_id,
        team_id,
        positions,
        game_date,
        points,
        week)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING;
"""

UPSERT_TEAM = """
    INSERT INTO teams (id, team_name)
    VALUES (?1, ?2)
    ON CONFLICT (id)
    DO UPDATE SET team_name = ?2;
"""

UPSERT_WEEKLY_RESULTS = """
    INSERT INTO weekly_results (
        week,
        team_id,
        points_for,
        projection,
        winner,
        opponent)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT DO NOTHING;
"""

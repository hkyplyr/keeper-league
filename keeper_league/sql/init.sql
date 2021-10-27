CREATE TABLE IF NOT EXISTS teams (
    id integer PRIMARY KEY,
    name text NOT NULL,
    image_url text NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_results (
    team_id integer,
    week integer,
    is_winner boolean,
    pf real,
    ppf real,
    ppf_percentage real,
    PRIMARY KEY (team_id, week)
);

CREATE TABLE IF NOT EXISTS all_play (
    team_id integer,
    week integer,
    all_win integer,
    all_loss integer,
    PRIMARY KEY (team_id, week)
);

CREATE TABLE IF NOT EXISTS optimal_points (
    team_id integer,
    week integer,
    date text,
    points real,
    PRIMARY KEY (team_id, date)
);

CREATE TABLE IF NOT EXISTS players (
    id integer,
    team_id integer,
    date text,
    week integer,
    name text,
    image_url text,
    positions text,
    points real,
    started boolean,
    PRIMARY KEY (id, team_id, date)
);

CREATE TABLE IF NOT EXISTS matchups (
    winner_team integer,
    loser_team integer,
    week integer,
    victory_margin real,
    PRIMARY KEY (winner_team, loser_team, week)
);
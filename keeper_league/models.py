from sqlalchemy import create_engine
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import Session


Base = declarative_base()


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    image_url = Column(String(255))


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    date = Column(String(255), primary_key=True)
    week = Column(Integer)
    name = Column(String(255))
    image_url = Column(String(255))
    positions = Column(String(255))
    points = Column(Float)
    started = Column(Boolean)


class WeeklyResult(Base):
    __tablename__ = "weekly_results"

    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    week = Column(Integer, primary_key=True)
    winner = Column(Boolean)
    points_for = Column(Float)
    projected_points_for = Column(Float)

    team = relationship("Team")


class AllPlay(Base):
    __tablename__ = "all_play"

    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    week = Column(Integer, primary_key=True)
    wins = Column(Integer)
    losses = Column(Integer)


class OptimalPoints(Base):
    __tablename__ = "optimal_points"

    team_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    week = Column(Integer)
    date = Column(String(255), primary_key=True)
    points = Column(Float)


class Matchup(Base):
    __tablename__ = "matchups"

    winner_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    loser_id = Column(Integer, ForeignKey("teams.id"), primary_key=True)
    week = Column(Integer, primary_key=True)
    victory_margin = Column(Float)


def db_session():
    engine = create_engine("sqlite:///keeper_league.db", future=True)
    Base.metadata.create_all(engine)
    return Session(engine)

from models import db_session, Player
from sqlalchemy import func


class Database:
    def __init__(self):
        self.session = db_session()

    def get_last_updated_week(self):
        week = self.session.query(func.max(Player.week)).one()[0]
        return 1 if not week else week

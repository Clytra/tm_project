from typing import Dict, List, Union

from db import db
from datetime import datetime
import enum

ScoreJSON = Dict[str, Union[int, datetime, enumerate, int, int, int, int, int, int, int]]


class StatusEnum(enum.Enum):
    uczestnik = 0,
    rezerwa = 1,
    rezygnacja = 2,
    dyskwalifikacja = 3,
    oczekujący = 4


class ScoreModel(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer(), primary_key=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(StatusEnum), default=4)
    group1 = db.Column(db.Integer())
    group2 = db.Column(db.Integer())
    pz1 = db.Column(db.Integer())
    pz2 = db.Column(db.Integer())
    pz3 = db.Column(db.Integer())
    tb1 = db.Column(db.Integer())
    tb2 = db.Column(db.Integer())

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'), nullable=False)
    tournament_id = db.Column(db.Integer(), db.ForeignKey('tournaments.id'), nullable=False)
    user = db.relationship('UserModel')
    tournament = db.relationship('TournamentModel')

    def __init__(self, join_date: datetime, status: enumerate, group1: int, group2: int, pz1: int, pz2: int, pz3: int, tb1: int, tb2: int, user_id: int, tournament_id: int):
        self.join_date = join_date
        self.status = status
        self.group1 = group1
        self.group2 = group2
        self.pz1 = pz1
        self.pz2 = pz2
        self.pz3 = pz3
        self.tb1 = tb1
        self.tb2 = tb2
        self.user_id = user_id
        self.tournament_id = tournament_id

    def json(self) -> ScoreJSON:
        return {
            'id': self.id, 'join_date': self.join_date, 'status': self.status, 'group1': self.group1,
            'group2': self.group2, 'pz1': self.pz1, 'pz2': self.pz2,
            'pz3': self.pz3, 'tb1': self.tb1, 'tb2': self.tb2, 'user_id': self.user_id,
            'tournament_id': self.tournament_id
        }

    @classmethod
    def find_by_id(cls, _id: int) -> 'ScoreModel':
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls) -> List['ScoreModel']:
        return cls.query.all()

    def save_to_fb(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update_row(self) -> None:
        db.session.update(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

from typing import Dict, List, Union

from db import db
from datetime import date
from models.score import ScoreJSON

TournamentJSON = Dict[str, Union[int, str, str, str, date, List[ScoreJSON]]]


class TournamentModel(db.Model):
    __tablename__ = 'tournaments'

    id = db.Column(db.Integer(), primary_key=True)
    address = db.Column(db.String(80))
    city = db.Column(db.String(20))
    post_code = db.Column(db.String(10))
    date = db.Column(db.Date)

    scores = db.relationship('ScoreModel', lazy='dynamic')

    def __init__(self, address: str, city: str, post_code: str, date: date):
        self.address = address
        self.city = city
        self.post_code = post_code
        self.date = date

    def json(self) -> TournamentJSON:
        return {
            'id': self.id, 'address': self.address, 'city': self.city, 'post_code': self.post_code,
            'date': self.date, 'scores': [score.json() for score in self.scores.all()]
        }

    @classmethod
    def find_by_id(cls, _id: int) -> 'TournamentModel':
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls) -> List['TournamentModel']:
        return cls.query.all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def update_row(self) -> None:
        db.session.update(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

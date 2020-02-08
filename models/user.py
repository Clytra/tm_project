from typing import Dict, List, Union

from db import db
from models.score import ScoreJSON


UserJSON = Dict[str, Union[int, str, str, str, str, str, str, List[ScoreJSON]]]


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone_number = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    scores = db.relationship('ScoreModel', lazy='dynamic')

    def __init__(self, username: str, password: str, first_name: str, last_name: str, phone_number: str, email: str):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.email = email

    def json(self) -> UserJSON:
        return {
            'id': self.id, 'username': self.username, 'password': self.password, 'first_name': self.first_name,
            'last_name': self.last_name, 'phone_number': self.phone_number, 'email': self.email,
            'scores': [score.json() for score in self.scores.all()]
        }

    @classmethod
    def find_by_username(cls, username: str) -> 'UserModel':
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, id: int) -> 'UserModel':
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls) -> List['UserModel']:
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

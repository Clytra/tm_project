from flask_restful import Resource, reqparse
from datetime import datetime
from flask_jwt_extended import (
    jwt_required,
    get_jwt_claims,
    get_jwt_identity,
    jwt_optional,
    fresh_jwt_required,
)

from models.score import ScoreModel

BLANK_ERROR = "'{}' nie może być puste."
ITEM_NOT_FOUND = "Nie znaleziono rekordu."
ADMIN_PERMISSION = "Wymagane uprawnienia administratora."
ERROR_EDITING = "Wystąpił błąd podczas edycji danych."
ERROR_ADDING = "Wystąpił błąd podczas dodawania danych."
LOGIN_PERMISSION = "Aby uzyskać więcej informacji, należy się zalogować."


class Score(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=int, required=True, help=BLANK_ERROR.format('user_id'))
    parser.add_argument('tournament_id', type=int, required=True, help=BLANK_ERROR.format('tournament_id'))
    parser.add_argument('join_date', type=datetime, nullable=False)
    parser.add_argument('status', type=enumerate)
    parser.add_argument('group1', type=int)
    parser.add_argument('group2', type=int)
    parser.add_argument('pz1', type=int)
    parser.add_argument('pz2', type=int)
    parser.add_argument('pz3', type=int)
    parser.add_argument('tb1', type=int)
    parser.add_argument('tb2', type=int)

    @classmethod
    @jwt_required
    def get(cls, id: int):
        score = ScoreModel.find_by_id(id)
        if score:
            return score.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ADMIN_PERMISSION}, 401
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help=BLANK_ERROR.format('user_id'))
        parser.add_argument('tournament_id', type=int, required=True, help=BLANK_ERROR.format('tournament_id'))
        parser.add_argument('join_date', type=datetime, nullable=False, default=datetime.utcnow())
        parser.add_argument('status', type=enumerate, default=4)

        data = parser.parse_args()

        score = ScoreModel(**data)

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_ADDING}, 500

        return score.json(), 201

    @classmethod
    @jwt_required
    def put(cls, id: int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ADMIN_PERMISSION}, 401
        data = Score.parser.parse_args()
        score = ScoreModel.find_by_id(id)
        if score:
            score.group1 = data["group1"]
            score.group2 = data["group2"]
        else:
            score = ScoreModel(id, **data)

        try:
            score.save_to_db()
        except:
            return {"message": ERROR_EDITING}, 500

        return score.json(), 200


class ScoreList(Resource):
    @classmethod
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        scores = [score.json() for score in ScoreModel.find_all()]
        if user_id:
            return {'scores': scores}, 200
        return (
            {
                'scores': [score['id'] for score in scores],
                'message': LOGIN_PERMISSION,
            },
            200,
        )

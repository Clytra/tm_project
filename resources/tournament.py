from flask_jwt import jwt_required
from flask_jwt_extended import get_jwt_claims
from flask_restful import Resource, reqparse
from models.tournament import TournamentModel
from datetime import date

ITEM_NOT_FOUND = "Nie znaleziono rekordu."
ADMIN_PERMISSION = "Wymagane uprawnienia administratora."
ERROR_ADDING = "Wystąpił błąd podczas dodawania danych."
SUCCESS_DELETING = "Dane usunięto pomyślnie."
ERROR_EDITING = "Wystąpił błąd podczas edycji danych."

class Tournament(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('address', type=str, required=False)
    parser.add_argument('city', type=str, required=False)
    parser.add_argument('post_code', type=str, required=False)
    parser.add_argument('date', type=date, required=False)

    @classmethod
    def get(cls, id: int):

        tournament = TournamentModel.find_by_id(id)

        if tournament:
            return tournament.json(), 200
        return {"message": ITEM_NOT_FOUND}, 404

    @classmethod
    @jwt_required
    def post(cls):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ADMIN_PERMISSION}, 401
        data = Tournament.parser.parse_args()
        tournament = TournamentModel(**data)

        try:
            tournament.save_to_db()
        except:
            return {"message": ERROR_ADDING}, 500

        return tournament.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, id: int):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ADMIN_PERMISSION}, 401
        tournament = TournamentModel.find_by_id(id)

        if not tournament:
            return {"message": ITEM_NOT_FOUND}, 404
        tournament.delete_from_db()
        return {"message": SUCCESS_DELETING}, 200

    @classmethod
    @jwt_required
    def put(cls, address: str):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': ADMIN_PERMISSION}, 401
        data = Tournament.parser.parse_args()
        tournament = TournamentModel.find_by_name(address)

        if tournament:
            tournament.address = data["address"]
            tournament.city = data["city"]
            tournament.post_code = data["post_code"]
            tournament.post_code = data["date"]
        else:
            tournament = TournamentModel(id, **data)

        try:
            tournament.save_to_db()
        except:
            return {"message": ERROR_EDITING}, 500

        return tournament.json(), 200


class TournamentList(Resource):
    @classmethod
    def get(cls):
        return {"tournaments": [row.json() for row in TournamentModel.find_all()]}
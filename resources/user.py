from flask_blacklist import Blacklist
from flask_jwt import jwt_required
from flask_jwt_extended import get_jwt_identity, create_access_token, get_raw_jwt, create_refresh_token, \
    jwt_refresh_token_required
from flask_restful import Resource, reqparse
from flask import Flask, request, flash, redirect, url_for
from werkzeug.security import safe_str_cmp
from werkzeug.utils import secure_filename

from models.user import UserModel
from io import TextIOWrapper
import csv, io

BLANK_ERROR = "'{}' nie może być puste."
USER_NOT_FOUND = "Nie znaleziono użytkownika."
ERROR_INSERTING = "Wystąpił błąd podczas dodawania danych."
NAME_ALREADY_EXISTS = "Użytkownik o takim nicku już istnieje."
USER_DELETED = "Użytkownik został usunięty."
ERROR_EDITING = "Wystąpił błąd podczas edycji danych."
CREATED_SUCCESSFULLY = "Użytkownik został dodany pomyślnie."
USER_LOGGED_OUT = "Użytkownik został wylogowany."
INVALID_CREDENTIALS = "Niepoprawne dane logowania."
ERROR_IMPORT = "Wystąpił błąd podczas importu danych."


class User(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True, help=BLANK_ERROR.format('username'))
    parser.add_argument('password', type=str, required=True, help=BLANK_ERROR.format('password'))
    parser.add_argument('first_name', type=str, required=False)
    parser.add_argument('last_name', type=str, required=False)
    parser.add_argument('phone_number', type=str, required=True, help=BLANK_ERROR.format('phone_number'))
    parser.add_argument('email', type=str, required=True, help=BLANK_ERROR.format('email'))

    @classmethod
    def get(cls, id: int):

        user = UserModel.find_by_id(id)

        if user:
            return user.json(), 200
        return {"message": USER_NOT_FOUND}, 404

    @classmethod
    def delete(cls, id: int):

        user = UserModel.find_by_id(id)

        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200

    @classmethod
    def put(cls, id):

        data = User.parser.parse_args()
        user = UserModel.find_by_id(id)

        if user:
            user.username = data["username"]
            user.password = data['password']
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.phone_number = data["phone_number"]
            user.email = data["email"]
            user.admin = data['admin']
        else:
            user = UserModel(id, **data)

        try:
            user.save_to_db()
        except:
            return {"message": ERROR_EDITING}, 500

        return user.json(), 200


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = User.parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": NAME_ALREADY_EXISTS}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {"message": CREATED_SUCCESSFULLY}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help=BLANK_ERROR.format('username'))
        parser.add_argument('password', type=str, required=True, help=BLANK_ERROR.format('password'))
        data = parser.parse_args()

        user = UserModel.find_by_username(data["username"])
        user.username = data["username"]
        user.password = data["password"]

        if user and safe_str_cmp(user.password, data["password"]):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        return {"message": INVALID_CREDENTIALS}, 401


class UserList(Resource):
    @classmethod
    def get(cls):
        return {"users": [row.json() for row in UserModel.find_all()]}


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]
        user_id = get_jwt_identity()
        Blacklist.add(jti)
        return {"message:": USER_LOGGED_OUT}


class UserImport(Resource):
    @classmethod
    def post(cls):

        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimeter=';')
        for row in csv_reader:
            user = UserModel(username=row[0], password=row[1], first_name=row[2], last_name=row[3], phone_number=row[4],
                             email=row[5], admin=row[6])
            try:
                user.save_to_db()
            except:
                return {"message": ERROR_IMPORT}, 500

            return user.json(), 201


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200

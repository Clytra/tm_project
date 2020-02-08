from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from db import db
from blacklist import Blacklist
from resources.user import User, UserImport, UserList, UserRegister, UserLogin, UserLogout, TokenRefresh
from resources.tournament import Tournament, TournamentList
from resources.score import Score, ScoreList

UPLOAD_FOLDER = '///users.csv'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///terraM.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = [
    'access',
    'refresh',
]
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config["JWT_AUTH_URL_RULE"] = '/login'
app.secret_key = "test"


api = Api(app)


@app.before_first_request
def create_tables():

    db.create_all()

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(
        identity
):
    if (
        identity == 1
    ):
        return {'is_admin': True}
    return {'is_admin': False}

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return (
        decrypted_token['jti'] in Blacklist
    )

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({'message': 'Token wygasł', 'error': 'token wygasł'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(
        error
):
    return (
        jsonify(
            {'message': 'Signature verification failed', 'error': 'invalid_token'}
        ),
        401,
    )

@jwt.unauthorized_loader
def missing_token_callback(error):
    return (
        jsonify(
            {
                'description': 'Request does not contain an acces token',
                'error': 'authorization_required',
            }
        ),
        401,
    )

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return (
        jsonify(
            {'description': 'The token is not fresh', 'error': 'fresh_token_required'}
        ),
        401,
    )

@jwt.revoked_token_loader
def revoked_token_callback():
    return(
        jsonify(
            {'description':'The token has been revoked.', 'error': 'token_revoked'}
        ),
        401,
    )
api.add_resource(Tournament, "/api/tournament/<int:id>")
api.add_resource(TournamentList, "/api/tournaments")
api.add_resource(Score, "/api/score/<int:id>")
api.add_resource(ScoreList, "/api/scores")
api.add_resource(UserRegister, "/api/register")
api.add_resource(User, "/api/user/<int:id>")
api.add_resource(UserList, "/api/users")
api.add_resource(UserImport, "/api/import")
api.add_resource(UserLogin, "/api/login")
api.add_resource(UserLogout, "/api/logout")
api.add_resource(TokenRefresh, '/api/refresh')




if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
from datetime import datetime
import http.client

from flask_restx import Namespace, Resource, abort, fields

from users import config
from users.db import db
from users.models import UserModel
from users.token_validation import generate_token_header,\
    validate_token_header


api_namespace = Namespace('api', description='API operations')

model = {
    'user_id': fields.Integer(),
    'username': fields.String(),
    # DO NOT RETURN THE PASSWORD!!!
    'time_created': fields.DateTime(),
}
user_model = api_namespace.model('User', model)


def authentication_header_parser(value):
    username = validate_token_header(value, config.PUBLIC_KEY)
    if username is None:
        abort(401)
    return username


authentication_parser = api_namespace.parser()
authentication_parser.add_argument('Authorization', location='headers',
                                   type=str,
                                   help='Bearer Access Token')

login_parser = api_namespace.parser()
login_parser.add_argument('username', type=str, required=True,
                          help='Username', location='form')
login_parser.add_argument('password', type=str, required=True,
                          help='Password', location='form')


@api_namespace.route('/login/')
class UserLogin(Resource):

    @api_namespace.doc('login')
    @api_namespace.expect(login_parser)
    def post(self):
        """
        Login and return a valid Authorization header
        """
        args = login_parser.parse_args()

        # Search for the user
        user = (UserModel
                .query
                .filter(UserModel.username == args['username'])
                .first())
        if not user:
            return '', http.client.UNAUTHORIZED

        # Check the password
        # REMEMBER, THIS IS NOT SAFE. DO NOT STORE PASSWORDS IN PLAIN
        if user.password != args['password']:
            return '', http.client.UNAUTHORIZED

        # Generate the header
        header = generate_token_header(user.username, config.PRIVATE_KEY)
        return {'Authorized': header}, http.client.OK


@api_namespace.route('/signup/')
class UserCreate(Resource):

    @api_namespace.expect(login_parser)
    @api_namespace.marshal_with(user_model, code=http.client.CREATED)
    def post(self):
        """
        Create a new user
        """
        args = login_parser.parse_args()

        new_user = UserModel(username=args['username'],
                             password=args['password'],
                             time_created=datetime.utcnow())
        db.session.add(new_user)
        db.session.commit()

        result = api_namespace.marshal(new_user, user_model)

        return result, http.client.CREATED

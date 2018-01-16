from . import auth_blueprint
from flask.views import MethodView
from sqlalchemy import exc
from flask_bcrypt import Bcrypt
from flasgger import swag_from
from flask import make_response, request, jsonify
from app.models import User,Blacklist_Token

import validate

class RegistrationView(MethodView):
    """This class registers a new user."""
    @swag_from('/app/docs/register.yml')
    def post(self):
        post_data = request.data
        # Register the user
        email = post_data['email']
        password = post_data['password']
        security_question = post_data['security_question']
        security_answer = post_data['security_answer']
        if not email:
            return make_response(jsonify({"message": "Email is required"})),401
        if not validate.valid_email(email):
            return make_response(jsonify({"message": "Please enter correct email"})),401
        if not password:
            return make_response(jsonify({"message": "Password is required"})),401
        if not validate.valid_password(password):
            return make_response(jsonify({"message": "Please enter correct password"})),401
        if not security_question:
            return make_response(jsonify({"message": "Please enter response for the security question"})),401
        if not security_answer:
            return make_response(jsonify({"message": "Please enter response for the security answer"})),401
        if len(password) >= 6:
            result = User.query.filter_by(email=request.data['email']).first()
            try:
                user = User(email=email, password=password,
                    security_question=security_question, security_answer=security_answer)
                user.save()
                return jsonify({'message': 'You registered successfully.'}),201
            except exc.IntegrityError:
                return jsonify({'message': 'Email already exists. Please use another one'}),404
        return jsonify({'message':'Enter a password with more than 6 characters'}),401

class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""
    @swag_from('/app/docs/login.yml')
    def post(self):
        post_data = request.data
        email = post_data['email']
        password = post_data['password']
        if not email or not password:
            return make_response(jsonify({"message": "All fields are required"})),401
        if not validate.valid_email(email):
            return make_response(jsonify({"message": "Please enter correct email"})),401
        if not validate.valid_password(password):
            return make_response(jsonify({"message": "Please enter correct password"})),401
        # Get the user object using their email (unique to every user)
        user = User.query.filter_by(email = email).first()
        if user and user.password_is_valid(password):
            # Generate the access token. This will be used as the authorization header
            access_token = user.generate_token(user.user_id)
            if access_token:
                return jsonify({'message': 'You logged in successfully.',
                            'access_token': access_token.decode()}),200
            # User does not exist. Therefore, we return an error message
        return jsonify({'message': 'Invalid email or password, Please try again'}), 401

class LogoutView(MethodView):
    """This class logsout a user."""
    @swag_from('/app/docs/logout.yml')
    def post(self):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"message": "No token provided, Please login"}),401
        access_token = auth_header.split(" ")[1]
        if access_token:
            user_id = User.decode_token(access_token)
            if isinstance(user_id, int):
                token = Blacklist_Token(blacklist_token=access_token)
                token.save()
                return jsonify({'message': 'Your have been successfully logged out.'}),200
        return jsonify({'message': 'Please enter a valid token'}),401

class ChangePasswordView(MethodView):
    @swag_from('/app/docs/changepassword.yml')
    def post(self):
        post_data = request.data
    # Register the user
        email = post_data['email']
        new_password = post_data['new_password']
        security_question = post_data['security_question']
        security_answer = post_data['security_answer']
        user = User.query.filter_by(email=email,security_answer=security_answer).first()
        if user:
            user.password = Bcrypt().generate_password_hash(new_password).decode()
            user.save()
            return jsonify({'message': 'Your password has been reset.'}),201
        return jsonify({'message': 'User with email not found or wrong security answer,please try again'}),401

# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
changepassword_view = ChangePasswordView.as_view('changepassword_view')
# Define the rule for the registration url --->  /api/v1/auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/register',
    view_func=registration_view,
    methods=['POST'])
# Define the rule for the registration url --->  /api/v1/auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/login',
    view_func=login_view,
    methods=['POST'])
# Define the rule for the registration url --->  /api/v1/auth/change_passsword
auth_blueprint.add_url_rule(
    '/api/v1/auth/change_password',
    view_func=changepassword_view,
    methods=['POST'])
# Define the rule for the registration url --->  /api/v1/auth/logout
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/v1/auth/logout',
    view_func=logout_view,
    methods=['POST'])
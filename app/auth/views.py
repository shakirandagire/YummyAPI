from . import auth_blueprint
from flask.views import MethodView
from sqlalchemy import exc
from flask_bcrypt import Bcrypt
from flask import make_response, request, jsonify
from app.models import User,Blacklist_Token
import validate

class RegistrationView(MethodView):
    """This class registers a new user."""
    def post(self):
        """Handle POST request for this view.
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            type: string
            name: body
            required: true
            description: Register users
        responses:
          200:
            description: User registered
        """
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
                response = {'message': 'You registered successfully.'}
                # return a response notifying the user that they registered successfully
                return make_response(jsonify(response)), 201
            except exc.IntegrityError:
                return jsonify({'message': 'Email already exists. Please use another one'}),404
        return make_response(jsonify({'message':'Enter a password with more than 6 characters'})),401

class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""
    def post(self):
        """ Handle POST request for this view.
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            type: string
            name: body
            required: true
            description: Logging in user
        responses:
          200:
            description: User logged in successfully
        """
        # Get the user object using their email (unique to every user)
        user = User.query.filter_by(email=request.data['email']).first()

        if user and user.password_is_valid(request.data['password']):
            # Generate the access token. This will be used as the authorization header
            access_token = user.generate_token(user.user_id)

            if access_token:
                response = {
                    'message': 'You logged in successfully.',
                    'access_token': access_token.decode()
                }
                return make_response(jsonify(response)), 200
        else:
            # User does not exist. Therefore, we return an error message
            response = {
                'message': 'Invalid email or password, Please try again'
            }
            return make_response(jsonify(response)), 401


class LogoutView(MethodView):
    """This class logsout a user."""
    def post(self):
        """Handle the request for logout view.
        ---
        tags:
          - User Authentication
        security:
          - TokenHeader: []
        responses:
          200:
            description: User logged out successfully
        """
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
    def post(self):
        """
        Handle request to change password. Url ---> /api/v1/auth/change_password
        ---
        tags:
          - User Authentication
        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: Please enter email and old password before you input a new password
        security:
          - TokenHeader: []
        responses:
          200:
            description: Password successfully changed
        """
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
            response = {
                'message': 'Your password has been reset.'}
            return make_response(jsonify(response)),201
        else:
            response = jsonify({
                        'message': 'User with email not found or wrong security answer,please try again'
                    })
            return make_response(response), 401

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
    methods=['POST']
)
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
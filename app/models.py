from app import db
from flask_bcrypt import Bcrypt
import jwt
from flask import current_app
from datetime import datetime, timedelta

class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    security_question = db.Column(db.String(256), nullable=False)
    security_answer = db.Column(db.String(256), nullable=False)
    categories = db.relationship('Category', order_by='Category.category_id', cascade="all, delete-orphan", lazy ="dynamic")
 

    def __init__(self, email, password,security_question,security_answer):
        """Initialize the user with an email and a password."""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()
        self.security_question = security_question
        self.security_answer = security_answer

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(days=365),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            blacklist = Blacklist_Token.check_blacklist_token(auth_token=token)
            if blacklist:
                return 'Blacklisted token. Please log in'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

class Blacklist_Token(db.Model):
    """This class defines the blacklist table """
    __tablename__ = 'blacklists'
    # Define the columns of the users table, starting with the primary key
    token_id = db.Column(db.Integer, primary_key=True)
    blacklist_token = db.Column(db.String(256), nullable=False, unique=True)
    
    def __init__(self,blacklist_token):
        """Initialize the blacklisted token."""
        self.blacklist_token = blacklist_token

    def save(self):
        """Save a user to the database.
        This includes saving the blacklisted token.
        """
        db.session.add(self)
        db.session.commit()

    def check_blacklist_token(auth_token):
        result = Blacklist_Token.query.filter_by(blacklist_token = str(auth_token)).first()
        if result:
            return True
        else:
            return False

    def __repr__(self):
        return "<token_id: blacklist_token{}>".format(self.blacklist_token)

class Category(db.Model):
    """This class represents the category table."""

    __tablename__ = 'categories'

    category_id = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(255))
    recipes = db.relationship('Recipe', order_by='Recipe.recipe_id', cascade="all, delete-orphan", lazy='dynamic')
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    created_by = db.Column(db.Integer, db.ForeignKey(User.user_id))

    def __init__(self, categoryname, created_by):
        """initialize with name."""
        self.categoryname = categoryname
        self.created_by = created_by

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Category.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Category: {}>".format(self.categoryname)

class Recipe(db.Model):
    """ Models the recipe table """

    __tablename__ = 'recipes'
    recipe_id = db.Column(db.Integer, primary_key=True)
    recipename = db.Column(db.String(256))
    description = db.Column(db.Text)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                                onupdate=db.func.current_timestamp())
    category_identity = db.Column(db.Integer, db.ForeignKey(Category.category_id))


    def __init__(self, recipename, description, category_identity):
        self.recipename = recipename
        self.description = description
        self.category_identity = category_identity

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Recipe.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Recipe: {}>".format(self.recipename)
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from flasgger import Swagger
import validate

from instance.config import app_config


# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    
    from .models import Category, User, Recipe
    
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    swagger = Swagger(app, template= {"securityDefinitions": {

        "TokenHeader": {
            "type": "apiKey",
            "name":"Authorization",
            "in": "header"

        }
    }})

    @app.route('/api/v1/categories/', methods=['POST'])
    def addcategories():
        """
        Adding categories 
        ---
        tags:
          - Category

        parameters:
          - in: body
            type: string
            name: body
            required: true
            description: Enter Category data

        security:
          - TokenHeader: []

        responses:
          200:
            description: Category created successfully
                
            """

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    categoryname = str(request.data.get('categoryname', '')).title()

                    if not categoryname:
                        return make_response(jsonify({"message": "Please enter a categoryname"})),400

                    if not validate.valid_name(categoryname):     
                        return make_response(jsonify({"message": "Please enter valid categoryname with no numbers and special characters"})),400

                    result = Category.query.filter_by(categoryname = categoryname, created_by = user_id).first()

                    if result:
                        return make_response(jsonify({"message": "Category already exists"})),400
                    
                    category = Category(categoryname=categoryname, created_by=user_id)
                    category.save()
                    response = jsonify({
                        'message': 'Category ' + category.categoryname +' has been created',
                        'category_id': category.category_id,
                        'categoryname':category.categoryname,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'created_by': user_id
                    })

                    return make_response(response),201
            else:
                    message = user_id
                    response = {
                        'message': message
                    }
                    return make_response(jsonify(response)),401


    @app.route('/api/v1/categories/', methods=['GET'])
    def getcategories():
        """
        Getting all categories 
        ---
        tags:
          - Category

        parameters:
          - in: query
            type: string
            name: q
            required: false
            description: q is for searching categories

          - in: query
            type: integer
            name: page
            required: false
            description: page is the page number to be displayed

          - in: query
            type: integer
            name: per_page
            required: false
            description: per_page is the number of categories to be displayed on the page

        security:
          - TokenHeader: []

        responses:
          200:
            description: User categories displayed 
                
        """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated
                #                  
                page = int(request.args.get('page', 1))
                print(page)
                per_page = int(request.args.get('per_page', 30))
                q = str(request.args.get('q', '')).title()
                categories = Category.query.filter_by(
                    created_by=user_id).paginate(page=page, per_page=per_page)
                results = []
                if not categories:
                    return make_response(jsonify({'message': 'No categories available'})),400

                if q:
                    for category in categories.items:
                        if q in category.categoryname.title():
                            obj = {}
                            obj = {
                                'category_id': category.category_id,
                                'categoryname': category.categoryname,
                                'date_created': category.date_created,
                                'date_modified': category.date_modified,
                                'created_by': category.created_by
                            }
                            results.append(obj)
                else:
                    for category in categories.items:
                        obj = {}
                        obj = {
                            'category_id': category.category_id,
                            'categoryname': category.categoryname,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                        results.append(obj)

                if results:
                    return make_response(jsonify({'categories': results})),200
                else:
                    return make_response(jsonify({"message": "No categories found"})),400
            else:
                    message = user_id
                    response = {
                        'message': message
                    }
                    return make_response(jsonify(response)),401

           
    @app.route('/api/v1/categories/<int:category_id>', methods=['DELETE'])
    def deletecategory(category_id, **kwargs):
        """
        Delete category
        ---
        tags:
          - Category

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: deleting category

        security:
          - TokenHeader: []

        responses:
          200:
            description: Category deleted successfully
                
        """
     # retrieve a category using it's ID
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(category_id = category_id).first()
                if not category:
                    return make_response(jsonify({"message": "No categories found"})),404

                if request.method == 'DELETE':
                    category.delete()
                    return {
                    "message": "category {} deleted successfully".format(category.category_id) 
                }, 200
            else:
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)),401



    @app.route('/api/v1/categories/<int:category_id>', methods=['GET'])
    def getcategory_by_id(category_id, **kwargs):
        """
        Getting category by id
        ---
        tags:
          - Category

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: getting category by id

        security:
          - TokenHeader: []

        responses:
          200:
            description: Category gotten successfully 
                
        """
     # retrieve a category using it's ID
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
        
                category = Category.query.filter_by(created_by=user_id,category_id=category_id).first()
                if not category:
                    return make_response(jsonify({"message": "No categories found"})),400
                else:
                    response = jsonify({
                    'category_id': category.category_id,
                    'categoryname': category.categoryname,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified
                })
                response.status_code = 200
                return response
            else:
                message = user_id
                response = {
                    'message': message
                }
            return make_response(jsonify(response)),401

    @app.route('/api/v1/categories/<int:category_id>', methods=['PUT'])
    def editcategory(category_id, **kwargs):
        """
        Editing all categories 
        ---
        tags:
          - Category

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: getting the category id

          - in: body
            type: string
            name: body
            required: true
            description: editing categories

        security:
          - TokenHeader: []

        responses:
          200:
            description: Category edited successfully
                
        """
     # retrieve a category using it's ID
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                categoryname = str(request.data.get('categoryname', ''))

                if not categoryname:
                    return make_response(jsonify({"message": "Please enter a categoryname"})),400

                if not validate.valid_name(categoryname):     
                    return make_response(jsonify({"message": "Please enter valid categoryname with no numbers and special characters"})),400

                result = Category.query.filter_by(categoryname = categoryname, created_by = user_id).first()

                if result:
                    return make_response(jsonify({"message": "Category already exists"})),400
                
                category = Category.query.filter_by(created_by=user_id,category_id = category_id).first()
                if not category:
                    return make_response(jsonify({"message": "No categories found to edit"})),400
                else:                
                    category.categoryname = categoryname
                    category.save()
                    response = jsonify({
                        'message': 'Category ' + category.categoryname +' has been edited',
                        'category_id': category.category_id,
                        'categoryname': category.categoryname,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'created_by' : category.created_by
                    })
                    response.status_code = 200
                    return response
            else:
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)),401

    @app.route('/api/v1/categories/<int:category_id>/recipes', methods=['POST'])
    def addrecipes(category_id, **kwargs):
        """For creating recipes 
         
        ---
        tags:
          - Recipes

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: Enter category id

          - in: body
            type: string
            name: body
            required: true
            description: Recipes can be added

        security:
          - TokenHeader: []

        responses:
          200:
            description: Recipes created successfully
                
            """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(created_by = user_id,category_id = category_id).first()
                if not category:
                    return make_response(jsonify({"message": "No categories found"})),400
               
                if request.method == "POST":
                    recipename = str(request.data.get('recipename', '')).title()
                    description = str(request.data.get('description', '')).title()

                    if not recipename and not description:
                        return make_response(jsonify({"message" : "Enter valid recipename and description"})),400

                    if not validate.valid_name(recipename):     
                        return make_response(jsonify({"message" : "Please enter valid recipename with no numbers and special characters"})),400

                    result = Recipe.query.filter_by(recipename = recipename, category_identity = category_id).first()
                    if result:
                        return make_response(jsonify({"message" : "Recipe already exists"})),400

                    recipe = Recipe(recipename = recipename, description = description, category_identity = category_id)              
                    recipe.save()
                    response = jsonify({
                        'message': 'Recipe ' + recipe.recipename +' has been created',
                        'recipe':{
                            'recipe_id': recipe.recipe_id,
                            'recipename': recipe.recipename,
                            'description': recipe.description,
                            'date_created': recipe.date_created,
                            'date_modified': recipe.date_modified,
                            'category_identity': category_id,

                        }
                    })

                    response.status_code = 201
                    return response

            else:
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)),401

    @app.route('/api/v1/categories/<int:category_id>/recipes', methods=['GET'])
    def getrecipes(category_id, **kwargs):
        """For retrieving recipes
         
        ---
        tags:
          - Recipes

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: Enter category id

          - in: query
            type: string
            name: q
            required: false
            description: q is for searching categories

          - in: query
            type: integer
            name: page
            required: false
            description: page is the page number to be displayed

          - in: query
            type: integer
            name: per_page
            required: false
            description: per_page is the number of categories to be displayed on the page

        security:
          - TokenHeader: []

        responses:
          200:
            description: Recipes created successfully
                
            """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
                if not category:
                    return jsonify({'message': 'No recipe in the category found!!!'})

                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 5))
                q = str(request.args.get('q','')).title()
                recipes = Recipe.query.filter_by(category_identity = category_id).paginate(page=page, per_page=per_page)
                results = []

                if not recipes:
                    return jsonify({'message': 'No recipes found!!!'})
                if q:
                    for recipe in recipes.items:
                        if q in recipe.recipename.title():
                            obj = {}
                            obj = {
                            'recipe_id': recipe.recipe_id,
                            'recipename': recipe.recipename,
                            'description': recipe.description,
                            'date_created': recipe.date_created,
                            'date_modified': recipe.date_modified,
                            'category_identity': category_id
                            }
                            results.append(obj)
                else:
                    for recipe in recipes.items:
                        obj = {}
                        obj = {
                            'recipe_id': recipe.recipe_id,
                            'recipename': recipe.recipename,
                            'description': recipe.description,
                            'date_created': recipe.date_created,
                            'date_modified': recipe.date_modified,
                            'category_identity': category_id
                            
                        }
                        results.append(obj)
                
                if results:

                    return make_response(jsonify({'recipes': results})),200
                else:
                    return make_response(jsonify({"message": "No recipes found"})),404
            else:
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)),401

          
    @app.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
    def getrecipe_by_id(category_id, recipe_id, **kwargs):
        """For getting recipes by id
         
        ---
        tags:
          - Recipes

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: Enter category id

          - in: path
            type: integer
            name: recipe_id
            required: false
            description: Enter recipe id

        security:
          - TokenHeader: []

        responses:
          200:
            description: Recipes displayed
                
            """
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
                recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
                if not recipe:
                    return jsonify({"message": "No recipes found"}),404

                response = jsonify({
                    'recipe_id': recipe.recipe_id,
                    'recipename': recipe.recipename,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity': category_id
                })
                response.status_code = 200
                return response

    @app.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
    def editrecipe(category_id, recipe_id, **kwargs):
        """For editing recipes by id    
        ---
        tags:
          - Recipes

        parameters:

          - in: path
            type: integer
            name: category_id
            required: true
            description: Enter category id

          - in: path
            type: integer
            name: recipe_id
            required: true
            description: Enter recipe id

          - in: body
            name: body
            type: object
            required: true
            description: Enter the new recipe

        security:
          - TokenHeader: []

        responses:
          200:
            description: Recipes edited successfully
                
            """

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()

                recipename = str(request.data.get('recipename', '')).title()
                description = str(request.data.get('description', '')).title()

                if not recipename or not description:
                    return make_response(jsonify({"message" : "Enter valid recipename and description"})),400

                if not validate.valid_name(recipename):     
                    return make_response(jsonify({"message" : "Please enter valid recipename with no numbers and special characters"})),400

                result = Recipe.query.filter_by(recipename = recipename, category_identity = category_id).first()
                if result:
                    return make_response(jsonify({"message" : "Recipe already exists"})),400

                recipe = Recipe(recipename = recipename, description = description, category_identity = category_id)
    
                recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
                if not recipe:
                    return jsonify({"message": "No recipes found"}),404

                if request.method == 'PUT':
                    recipename = str(request.data.get('recipename', ''))
                    description = str(request.data.get('description', ''))
                    recipe.recipename = recipename
                    recipe.description = description
                    recipe.save()
                    response = jsonify({
                        'recipe_id': recipe.recipe_id,
                        'recipename': recipe.recipename,
                        'description': recipe.description,
                        'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,
                        'category_identity': category_id
                    })
                    response.status_code = 200
                    return response
        
    @app.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
    def deleterecipe(category_id, recipe_id, **kwargs):
        """For deleting recipes by id
         
        ---
        tags:
          - Recipes

        parameters:
          - in: path
            type: integer
            name: category_id
            required: true
            description: Enter category id

          - in: path
            type: integer
            name: recipe_id
            required: true
            description: Enter recipe id

        security:
          - TokenHeader: []

        responses:
          200:
            description: Recipes displayed
                
            """

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
                # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str): 
                category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
     
            recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
            if not recipe:
                return jsonify({"message": "No recipes found"}),400

            if request.method == 'DELETE':
                recipe.delete()
                return {
                    "message": "recipe {} deleted successfully".format(recipe.recipe_id)},200
    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
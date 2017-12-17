from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response

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

    @app.route('api/v1/categories/', methods=['POST', 'GET'])
    def categories():

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authenticated

                if request.method == "POST":
                    categoryname = str(request.data.get('categoryname', '')).strip()
                    if categoryname:
                        category = Category(categoryname = categoryname, created_by = user_id)
                        category.save()
                        response = jsonify({
                            'id': category.id,
                            'categoryname':category.categoryname,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': user_id
                        })

                        return make_response(response), 201

                # else:  GET                    
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 5))
                q = str(request.args.get('q', '')).lower()
                categories = Category.query.filter_by(
                    created_by=user_id).paginate(page=page, per_page=per_page)
                results = []
                if not categories:
                    return jsonify({'message': 'No categories available'})
                if q:
                    for category in categories.items:
                        if q in category.categoryname.lower():
                            obj = {}
                            obj = {
                                'id': category.id,
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
                            'id': category.id,
                            'categoryname': category.categoryname,
                            'date_created': category.date_created,
                            'date_modified': category.date_modified,
                            'created_by': category.created_by
                        }
                        results.append(obj)

                if results:
                    return jsonify({'categories': results})
                else:
                    return jsonify({"message": "No categories found"})
            else:
                    message = user_id
                    response = {
                        'message': message
                    }
                    return make_response(jsonify(response)), 401
        
    @app.route('api/v1/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def category_manipulation(id, **kwargs):
     # retrieve a category using it's ID
        category = Category.query.filter_by(id=id).first()
        if not category:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            category.delete()
            return {
            "message": "category {} deleted successfully".format(category.id) 
         }, 200

        elif request.method == 'PUT':
            categoryname = str(request.data.get('categoryname', ''))
            category.categoryname = categoryname
            category.save()
            response = jsonify({
                'id': category.id,
                'categoryname': category.categoryname,
                'date_created': category.date_created,
                'date_modified': category.date_modified,
                'created_by' : category.created_by
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': category.id,
                'categoryname': category.categoryname,
                'date_created': category.date_created,
                'date_modified': category.date_modified
            })
            response.status_code = 200
            return response
    
    @app.route('api/v1/categories/<int:id>/recipes', methods=['POST', 'GET'])
    def recipes(id, **kwargs):
        """For creating recipes and retrieving them"""
        Category.query.filter_by(id=id).first()
        if request.method == "POST":
            recipename = str(request.data.get('recipename', '')).strip()
            description = str(request.data.get('description', '')).strip()
            if recipename and description:
                recipe = Recipe(recipename =recipename, description=description, category_identity=id)
                recipe.save()
                response = jsonify({
                    'message': 'Recipe ' + recipe.recipename +' has been created',
                    'recipe':{
                        'id': recipe.id,
                        'recipename': recipe.recipename,
                        'description': recipe.description,
                        'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,
                        'category_identity': id

                    }
                })

            response.status_code = 201
            return response

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', '')).lower()
        recipes = Recipe.query.filter_by(category_identity = id).paginate(page=page, per_page=per_page)
        results = []

        # if not recipes:
        #     return jsonify({'message': 'No recipes !!!'})

        if q:
            for recipe in recipes.items:
                if q in recipe.recipename.lower():
                    obj = {}
                    obj = {
                    'id': recipe.id,
                    'recipename': recipe.recipename,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity': id
                    }
                    results.append(obj)
        else:
            for recipe in recipes.items:
                obj = {}
                obj = {
                    'id': recipe.id,
                    'recipename': recipe.recipename,
                    'description': recipe.description,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'category_identity': id
                    
                }
                results.append(obj)
            return make_response(jsonify(results)), 200
        
        if results:

            return jsonify({'recipes': results})
        else:
            return jsonify({"message": "No recipes found"}),404

          
    @app.route('api/v1/categories/<int:id>/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
    def recipe_manipulation(id, recipe_id, **kwargs):
        Category.query.filter_by(id=id).first()
     
        recipe = Recipe.query.filter_by(id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            recipe.delete()
            return {
                "message": "recipe {} deleted successfully".format(recipe.id)
            }, 200

        elif request.method == 'PUT':
            recipename = str(request.data.get('recipename', ''))
            description = str(request.data.get('description', ''))
            recipe.recipename = recipename
            recipe.description = description
            recipe.save()
            response = jsonify({
                'id': recipe.id,
                'recipename': recipe.recipename,
                'description': recipe.description,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'category_identity': id
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': recipe.id,
                'recipename': recipe.recipename,
                'description': recipe.description,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'category_identity': id
            })
            response.status_code = 200
            return response
    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
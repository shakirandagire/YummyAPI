from . import recipe
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from flasgger import Swagger
import validate
from app.models import User,Recipe,Category

@recipe.route('/api/v1/categories/<int:category_id>/recipes', methods=['POST'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
            # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str): 
            category = Category.query.filter_by(created_by = user_id,category_id = category_id).first()
            if not category:
                return make_response(jsonify({"message": "No categories found"})),400           
            if request.method == "POST":
                recipename = str(request.data.get('recipename', '')).lower()
                description = str(request.data.get('description', '')).lower()
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
                        'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                        'description': recipe.description,'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,'category_identity': category_id,
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

@recipe.route('/api/v1/categories/<int:category_id>/recipes', methods=['GET'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
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
            q = str(request.args.get('q','')).lower()           
            recipes = Recipe.query.filter_by(category_identity = category_id).paginate(page=page, per_page=per_page,error_out=False)
            results = []
            if not recipes:
                return jsonify({'message': 'No recipes found!!!'})
            if q:
                for recipe in recipes.items:
                    if q in recipe.recipename.lower():
                        obj = {}
                        obj = {
                        'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                        'description': recipe.description,'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,'category_identity': category_id
                        }
                        results.append(obj)
            else:
                for recipe in recipes.items:
                    obj = {}
                    obj = {
                        'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                        'description': recipe.description,'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified,'category_identity': category_id   
                    }
                    results.append(obj)

            if len(results) <= 0:
                return jsonify({"message": "No recipes found"}), 404
            
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

        
@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401

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
                'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                'description': recipe.description,'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,'category_identity': category_id
            })
            response.status_code = 200
            return response

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
            # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str): 
            category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
            recipename = str(request.data.get('recipename', '')).lower()
            description = str(request.data.get('description', '')).lower()
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
                    'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                    'description': recipe.description,'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,'category_identity': category_id
                })
                response.status_code = 200
                return response
    
@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
            # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str): 
            category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
        recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
        if not recipe:
            return jsonify({"message": "No recipes found"}),404
        if request.method == 'DELETE':
            recipe.delete()
            return {
                "message": "recipe {} deleted successfully".format(recipe.recipe_id)},200
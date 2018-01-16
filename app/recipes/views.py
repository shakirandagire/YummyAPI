from . import recipe
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response
from flasgger import swag_from
import validate
from app.models import User,Recipe,Category,Blacklist_Token
from functools import wraps
from app.categories.views import authentication

@recipe.route('/api/v1/categories/<int:category_id>/recipes', methods=['POST'])
@authentication
@swag_from('/app/docs/addrecioes.yml')
def addrecipes(user_id,category_id, **kwargs):
    category = Category.query.filter_by(created_by = user_id,category_id = category_id).first()
    if not category:
        return make_response(jsonify({"message": "No categories found"})),400
    if request.method == "POST":
        recipename = str(request.data.get('recipename', '')).lower()
        recipe_description = str(request.data.get('recipe_description', '')).lower()
        instructions = str(request.data.get('instructions', '')).lower()
        if not recipename and not recipe_description and not instructions:
            return jsonify({"message" : "All fields are required"}),400
        if not validate.valid_name(recipename):
            return jsonify({"message" : "Please enter valid recipename with no spaces, numbers and special characters"}),400
        result = Recipe.query.filter_by(recipename = recipename, category_identity = category_id).first()
        if result:
            return make_response(jsonify({"message" : "Recipe already exists"})),400
        recipe = Recipe(recipename = recipename,recipe_description = recipe_description, category_identity = category_id)
        recipe.save()
        return jsonify({
            'message': 'Recipe ' + recipe.recipename +' has been created',
            'recipe':{
                'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                'recipe_description': recipe.recipe_description,'instructions': instructions,
                'date_created': recipe.date_created,'date_modified': recipe.date_modified,
                'category_identity': category_id}}),201

@recipe.route('/api/v1/categories/<int:category_id>/recipes', methods=['GET'])
@authentication
@swag_from('/app/docs/getrecipes.yml')
def getrecipes(user_id,category_id, **kwargs):
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
                'recipe_description': recipe.recipe_description,'instructions': instructions,
                'date_created': recipe.date_created,'date_modified': recipe.date_modified,
                'category_identity': category_id
                }
                results.append(obj)
    for recipe in recipes.items:
        obj = {}
        obj = {
            'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
            'recipe_description': recipe.recipe_description,'instructions': recipe.instructions,
            'date_created': recipe.date_created,'date_modified': recipe.date_modified,
            'category_identity': category_id
        }
        results.append(obj)
    if len(results) <= 0:
        return jsonify({"message": "No recipes found"}), 404
    if results:
        return make_response(jsonify({'recipes': results})),200
    return make_response(jsonify({"message": "No recipes found"})),404    

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@authentication
@swag_from('/app/docs/getrecipesbyid.yml')
def getrecipe_by_id(user_id,category_id, recipe_id, **kwargs):
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "No recipes found"}),404
    return jsonify({
            'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
            'recipe_description': recipe.recipe_description,'instructions': recipe.instructions,
            'date_created': recipe.date_created,'date_modified': recipe.date_modified,
            'category_identity': category_id }),200

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
@authentication
@swag_from('/app/docs/editrecipes.yml')
def editrecipe(user_id,category_id, recipe_id, **kwargs):
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipename = str(request.data.get('recipename', '')).lower()
    recipe_description = str(request.data.get('recipe_description', '')).lower()
    instructions = str(request.data.get('instructions', '')).lower()
    if not recipename or not recipe_description or not instructions:
        return make_response(jsonify({"message" : "All fields are required"})),400
    if not validate.valid_name(recipename):
        return make_response(jsonify({"message" : "Please enter valid recipename with no numbers and special characters"})),400
    result = Recipe.query.filter_by(recipename = recipename, category_identity = category_id).first()
    if result:
        return make_response(jsonify({"message" : "Recipe already exists"})),400
    recipe = Recipe(recipename = recipename, recipe_description = recipe_description, category_identity = category_id)
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "No recipes found"}),404
    if request.method == 'PUT':
        recipename = str(request.data.get('recipename', '')).lower()
        recipe_description = str(request.data.get('recipe_description', '')).lower()
        instructions = str(request.data.get('instructions', '')).lower()
        recipe.recipename = recipename
        recipe.recipe_description = recipe_description
        recipe.instructions = instructions
        recipe.save()
        return jsonify({
            'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
            'recipe_description': recipe.recipe_description,'date_created': recipe.date_created,
            'date_modified': recipe.date_modified,'category_identity': category_id}),200

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
@authentication
def deleterecipe(user_id,category_id, recipe_id, **kwargs):
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "No recipes found"}),404
    if request.method == 'DELETE':
        recipe.delete()
        return {
            "message": "recipe {} deleted successfully".format(recipe.recipe_id)},200
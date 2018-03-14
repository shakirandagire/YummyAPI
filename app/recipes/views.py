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
@swag_from('/app/docs/addrecipes.yml')
def addrecipes(user_id,category_id, **kwargs):
    """Function for adding recipes """
    category = Category.query.filter_by(created_by = user_id,category_id = category_id).first()
    if not category:
        return make_response(jsonify({"message": "No categories found"})),404
    if request.method == "POST":
        recipename = str(request.data.get('recipename', '')).strip().title()
        recipe_description = str(request.data.get('recipe_description', '')).strip().title()
        instructions = str(request.data.get('instructions', '')).title()
        if not recipename and not recipe_description or not instructions:
            return jsonify({"message" : "All fields are required"}),400
        if not validate.valid_name(recipename):
            return jsonify({"message" : "Please enter valid recipename with no spaces, numbers and special characters"}),400
        result = Recipe.query.filter_by(recipename = recipename, category_identity = category_id).first()
        if result:
            return make_response(jsonify({"message" : "Recipe already exists"})),409
        recipe = Recipe(recipename = recipename,recipe_description = recipe_description, instructions=instructions, category_identity = category_id)
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
    """Function for getting all recipes in a category,searching,pagination """
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    if not category:
        return jsonify({'message': 'Category not found!!!'})
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = str(request.args.get('q', '')).lower()
    recipes = Recipe.query.filter_by(
        category_identity = category_id).filter(Recipe.recipename.ilike('%'+q+'%')).paginate(page=page, per_page=per_page,error_out=False)
    if recipes.total <= 0:
        return jsonify({"message": "No recipes found for this search"}),404 
    if recipes.items:
        results = []
        for recipe in recipes.items:
            obj = {
                'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
                'recipe_description': recipe.recipe_description,'instructions': recipe.instructions,
                'date_created': recipe.date_created,'date_modified': recipe.date_modified,
                'category_identity': category_id }
            results.append(obj)
        return jsonify({'recipes': results}),200
    return make_response(jsonify({"message": "No recipes avaliable on this page"})),404

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@authentication
@swag_from('/app/docs/getrecipesbyid.yml')
def getrecipe_by_id(user_id,category_id, recipe_id, **kwargs):
    """Function for getting specific recipe in a category"""
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "Recipe not found"}),404
    return jsonify({
            'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
            'recipe_description': recipe.recipe_description,'instructions': recipe.instructions,
            'date_created': recipe.date_created,'date_modified': recipe.date_modified,
            'category_identity': category_id }),200

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
@authentication
@swag_from('/app/docs/editrecipes.yml')
def editrecipe(user_id,category_id, recipe_id, **kwargs):
    """Function for editing recipes in a category"""
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipename = str(request.data.get('recipename', '')).title()
    recipe_description = str(request.data.get('recipe_description', '')).title()
    instructions = str(request.data.get('instructions', '')).lower()
    if not recipename or not recipe_description or not instructions:
        return make_response(jsonify({"message" : "All fields are required"})),400
    if not validate.valid_name(recipename):
        return make_response(jsonify({"message" : "Please enter valid recipename with no numbers and special characters"})),400
    result = Recipe.query.filter_by(recipename = recipename,recipe_description =recipe_description,instructions=instructions, category_identity = category_id).first()
    if result:
        return make_response(jsonify({"message" : "Recipe already exists"})),409
    recipe = Recipe(recipename = recipename, recipe_description = recipe_description, instructions = instructions, category_identity = category_id)
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "Recipe not found to edit"}),404
    if request.method == 'PUT':
        recipename = str(request.data.get('recipename', '')).title()
        recipe_description = str(request.data.get('recipe_description', '')).title()
        instructions = str(request.data.get('instructions', '')).title()
        recipe.recipename = recipename
        recipe.recipe_description = recipe_description
        recipe.instructions = instructions
        recipe.save()
        return jsonify({'recipe_id': recipe.recipe_id,'recipename': recipe.recipename,
            'recipe_description': recipe.recipe_description,'instructions': recipe.instructions,
            'date_created': recipe.date_created,'date_modified': recipe.date_modified,
            'category_identity': category_id}),201

@recipe.route('/api/v1/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
@authentication
@swag_from('/app/docs/deleterecipes.yml')
def deleterecipe(user_id,category_id, recipe_id, **kwargs):
    """Function for deleting recipes in a category"""
    category = Category.query.filter_by(created_by = user_id,category_id=category_id).first()
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return jsonify({"message": "Recipe not found to delete"}),404
    if request.method == 'DELETE':
        recipe.delete()
        return {
            "message": "recipe {} deleted successfully".format(recipe.recipename)},200
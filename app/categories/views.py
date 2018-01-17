from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response,url_for

from . import category
import validate
from app.models import User,Recipe,Category,Blacklist_Token
from functools import wraps
from flasgger import swag_from

def authentication(func):
    """Function to handle the user authentication"""
    @wraps(func)
    def auth(*args,**kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return jsonify({"message": "No token provided, Please login"}),401
        access_token = auth_header.split()[1]
        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                return func(user_id,*args,**kwargs)
            return jsonify({'message': user_id}),401
        return jsonify({"message": "Please login"}),401
    return auth

@category.route('/api/v1/categories/', methods=['POST'])
@authentication
@swag_from('/app/docs/addcategories.yml')
def addcategories(user_id):
    """Function for adding categories"""
    if request.method == "POST":
        categoryname = str(request.data.get('categoryname', '')).strip().lower()
        category_description = str(request.data.get('category_description', '')).strip().lower()
        if not categoryname or not category_description:
            return jsonify({"message": "All fields are required"}),400
        if not validate.valid_name(categoryname):
            return make_response(jsonify({"message": "Please enter valid categoryname with no spaces, numbers and special characters"})),400
        result = Category.query.filter_by(categoryname = categoryname,created_by = user_id).first()
        if result:
            return make_response(jsonify({"message": "Category already exists"})),409
        category = Category(categoryname = categoryname,  category_description = category_description, created_by=user_id)
        category.save()
        return jsonify({
            'message': 'Category ' + category.categoryname +' has been created',
            'category_id': category.category_id,'categoryname':category.categoryname,
            'category_description':category.category_description,'date_created': category.date_created,
            'date_modified': category.date_modified,'created_by': user_id}), 201
        

@category.route('/api/v1/categories/', methods=['GET'])
@swag_from('/app/docs/getcategories.yml')
@authentication
def getcategories(user_id):
    """Function for getting all categories,searching,pagination """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    q = str(request.args.get('q', ''))
    categories = Category.query.filter_by(
        created_by=user_id).filter(Category.categoryname.ilike('%'+q+'%')).paginate(page=page, per_page=per_page,error_out=False)
    if categories.total <= 0:
        return jsonify({"message": "No category found for this search"}),404 
    if categories.items:
        results = []
        for category in categories.items:
            obj = {
                'category_id': category.category_id,'categoryname': category.categoryname,
                'date_created': category.date_created,'date_modified': category.date_modified,
                'category_description':category.category_description,'created_by': category.created_by,
                'recipes':url_for("recipes.getrecipes",category_id=category.category_id,_external=True)}
            results.append(obj)
        return jsonify({'categories': results}),200
    return make_response(jsonify({"message": "No categories avaliable on this page"})),404

@category.route('/api/v1/categories/<int:category_id>', methods=['DELETE'])
@authentication
@swag_from('/app/docs/deletecategories.yml')
def deletecategory(user_id,category_id, **kwargs):
    """Function for deleting a category"""
    category = Category.query.filter_by(category_id = category_id).first()
    if not category:
        return make_response(jsonify({"message": "Category not found to delete"})),404
    if request.method == 'DELETE':
        category.delete()
        return {"message": "category {} deleted successfully".format(category.category_id)},200

@category.route('/api/v1/categories/<int:category_id>', methods=['GET'])
@authentication
@swag_from('/app/docs/getcategoriesbyid.yml')
def getcategory_by_id(user_id,category_id, **kwargs):
    """Function for getting a single category """
    category = Category.query.filter_by(created_by=user_id,category_id=category_id).first()
    if not category:
        return make_response(jsonify({"message": "Category not found"})),404
    return jsonify({
    'category_id': category.category_id,'categoryname': category.categoryname,
    'category_description':category.category_description,'date_created': category.date_created,
    'date_modified': category.date_modified,
    'recipes':url_for("recipes.getrecipes",category_id=category.category_id,_external=True)}),200

@category.route('/api/v1/categories/<int:category_id>', methods=['PUT'])
@authentication
@swag_from('/app/docs/editcategories.yml')
def editcategory(user_id,category_id, **kwargs):
    """Function for editing a category """
    categoryname = str(request.data.get('categoryname', '')).lower()
    category_description = str(request.data.get('category_description', '')).lower()
    if not categoryname and not category_description:
        return make_response(jsonify({"message": "All fields are required"})),400
    if not validate.valid_name(categoryname):
        return make_response(jsonify({"message": "Please enter valid categoryname with no numbers and special characters"})),400
    result = Category.query.filter_by(categoryname = categoryname, created_by = user_id).first()
    if result:
        return make_response(jsonify({"message": "Category already exists"})),409
    category = Category.query.filter_by(created_by=user_id,category_id = category_id).first()
    if not category:
        return make_response(jsonify({"message": "Category not found to edit"})),404
    category.categoryname = categoryname
    category.category_description = category_description
    category.save()
    return jsonify({
        'message': 'Category ' + category.categoryname +' has been edited',
        'category_id': category.category_id,'categoryname': category.categoryname,
        'category_description':category.category_description,'date_created': category.date_created,
        'date_modified': category.date_modified,'created_by' : category.created_by }),201

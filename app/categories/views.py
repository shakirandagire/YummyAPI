from . import category

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify, abort, make_response,url_for
import validate
from app.models import User,Recipe,Category

@category.route('/api/v1/categories/', methods=['POST'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # Go ahead and handle the request, the user is authenticated
            if request.method == "POST":
                categoryname = str(request.data.get('categoryname', '')).lower()
                if not categoryname:
                    return make_response(jsonify({"message": "Please enter a categoryname"})),404
                if not validate.valid_name(categoryname):
                    return make_response(jsonify({"message": "Please enter valid categoryname with no spaces, numbers and special characters"})),404
                result = Category.query.filter_by(categoryname = categoryname, created_by = user_id).first()
                if result:
                    return make_response(jsonify({"message": "Category already exists"})),404
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

@category.route('/api/v1/categories/', methods=['GET'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            # Go ahead and handle the request, the user is authenticated
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            q = str(request.args.get('q', '')).lower()
            categories = Category.query.filter_by(
                created_by=user_id).paginate(page=page, per_page=per_page,error_out=False)
            results = []
            if not categories:
                return make_response(jsonify({'message': 'No category available'})),404
            if q:
                for category in categories.items:
                    if q in category.categoryname.lower():
                        obj = {}
                        obj = {
                            'category_id': category.category_id,'categoryname': category.categoryname,
                            'date_created': category.date_created,'date_modified': category.date_modified,
                            'created_by': category.created_by,
                            'recipes':url_for("recipes.getrecipes",category_id=category.category_id,_external=True)}
                        results.append(obj)
            else:
                for category in categories.items:
                    obj = {}
                    obj = {
                        'category_id': category.category_id,'categoryname': category.categoryname,
                        'date_created': category.date_created,'date_modified': category.date_modified,
                        'created_by': category.created_by,
                        'recipes':url_for("recipes.getrecipes",category_id=category.category_id,_external=True)
                    }
                    results.append(obj)
            if len(results) <= 0:
                return jsonify({"message": "No category on this page"}), 404

            if results:
                return make_response(jsonify({'categories': results})),200
            else:
                return make_response(jsonify({"message": "No category found"})),404
        else:
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)),401
            
@category.route('/api/v1/categories/<int:category_id>', methods=['DELETE'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
            # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.query.filter_by(category_id = category_id).first()
            if not category:
                return make_response(jsonify({"message": "No category found to delete"})),404
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

@category.route('/api/v1/categories/<int:category_id>', methods=['GET'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
    access_token = auth_header.split(" ")[1]
    if access_token:
            # Attempt to decode the token and get the User ID
        user_id = User.decode_token(access_token)
        if not isinstance(user_id, str):
            category = Category.query.filter_by(created_by=user_id,category_id=category_id).first()
            if not category:
                return make_response(jsonify({"message": "No category found"})),400
            else:
                response = jsonify({
                'category_id': category.category_id,'categoryname': category.categoryname,
                'date_created': category.date_created,'date_modified': category.date_modified
            })
            response.status_code = 200
            return response
        else:
            message = user_id
            response = {
                'message': message
            }
        return make_response(jsonify(response)),401

@category.route('/api/v1/categories/<int:category_id>', methods=['PUT'])
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
    if auth_header is None:
        return jsonify({"message": "No token provided, Please login"}),401
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
                return make_response(jsonify({"message": "No category found to edit"})),400
            else:
                category.categoryname = categoryname
                category.save()
                response = jsonify({
                    'message': 'Category ' + category.categoryname +' has been edited',
                    'category_id': category.category_id,'categoryname': category.categoryname,
                    'date_created': category.date_created,'date_modified': category.date_modified,
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


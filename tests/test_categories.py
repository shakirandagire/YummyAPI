import unittest
import os
import json
from app import create_app, db
from app.models import Category, Recipe, User

class CategoryTestCase(unittest.TestCase):
    """This class represents the category test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'categoryname': 'salad'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

    def register_user(self, email="user@test.com", password="test1234",security_question="testquestion",security_answer="testanswer"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password,
            'security_question': security_question,
            'security_answer':security_answer
        }
        return self.client().post('/api/v1/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/api/v1/auth/login', data=user_data)


    def test_category_creation(self):
        """Test API can create a category (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('salad', str(res.data))

    def test_category_creation_without_categoryname(self):
        """Test API cannot create a category without categoryname (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        empty_category = {"categoryname": ""}
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = empty_category)
        self.assertEqual(res.status_code, 404)
    

    def test_category_already_exists(self):
        """Test API cannot create a category that already exists"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"Rice"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        self.assertEqual(res.status_code, 404)

    def test_category_cannot_entered_with_spaces(self):
        """Test API cannot create a category with spaces"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":" "}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)

        self.assertEqual(res.status_code, 404)

    def test_category_cannot_entered_with_numbers(self):
        """Test API cannot create a category with numbers"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname": "44555666"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=category)

        self.assertEqual(res.status_code, 404)

    def test_category_cannot_entered_with_special_character(self):
        """Test API cannot create a category with special_character"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname": "@#$"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=category)
        self.assertEqual(res.status_code, 404)

    def test_api_can_get_all_categories(self):
        """Test API can get categories (GET request)."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        res = self.client().get(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('salad', str(res.data))

    def test_api_cannot_get_categories_that_donot_exist(self):
        """Test API cannot get categories that donot exist(GET request)."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"noodles"}
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        res1 = self.client().get(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        self.assertEqual(res1.status_code, 404)

    def test_category_can_be_got_by_q(self):
        """Test API can get a category by q"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token), data = self.category)
        res1 = self.client().get(
            '/api/v1/categories/?q=salad',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res1.status_code, 200)
        self.assertIn('salad', str(res1.data))

    def test_category_not_avaiable_to_get_by_q(self):
        """Test API cannot get a wrong category by q"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token), data = self.category)
        res = self.client().get(
            '/api/v1/categories/?q=lunch',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 404)

    def test_category_can_be_got_by_pagination(self):
        """Test API can get a category by pagination"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token), data = self.category)
        res = self.client().get(
            '/api/v1/categories/?page=1&per_page=1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('salad', str(res.data))

    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data =self.category)
        print('post rv',rv)
        results = json.loads(rv.data.decode())
        print('post res data', results)
        result = self.client().get(
            '/api/v1/categories/1'.format(results['category_id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('salad', str(result.data))

    def test_category_can_be_edited(self):
        """Test API can edit an existing category. (PUT request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'breakfast'})
        results = json.loads(rv.data.decode())
        rv = self.client().put(
            '/api/v1/categories/1'.format(results['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={"categoryname": "lunch"})
        self.assertEqual(rv.status_code, 200)
        

    def test_new_category_doesnot_exists(self):
        """Test API cannot edit a new category with name that already exists"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"rice"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        res1 = self.client().put(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        self.assertEqual(res1.status_code, 400)
        
    def test_edited_category_cannot_be_entered_with_spaces(self):
        """Test API cannot create a new category with spaces"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"   "}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().put(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)

        self.assertEqual(res.status_code, 400)


    def test_edited_category_cannot_be_entered_with_numbers(self):
        """Test API cannot create a new category with numbers"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname": "44555666"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().put(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)

        self.assertEqual(res.status_code, 400)


    def test_edited_category_cannot_be_entered_with_special_character(self):
        """Test API cannot create a new category with special_character"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname": "@#$"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().put(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)

        self.assertEqual(res.status_code, 400)


    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""

        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'breakfast'})
        results = json.loads(rv.data.decode())
        res = self.client().delete(
            '/api/v1/categories/1'.format(results['category_id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().delete(
            '/api/v1/categories/1'.format(results['category_id']),
        headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)


class RecipeTestCase(unittest.TestCase):
    """This class represents the recipes test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'categoryname': 'salad'}
        self.recipe = {'recipename': 'biryani', 'description': 'put rice in the water'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234",security_question="testquestion",security_answer="testanswer"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password,
            'security_question': security_question,
            'security_answer':security_answer
        }
        return self.client().post('/api/v1/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/api/v1/auth/login', data=user_data)

    def test_recipe_creation(self):
        """Test API can create a recipe (POST request)"""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('salad', str(res.data))
        headers=dict(Authorization="Bearer " + access_token),
        result = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.recipe)
        self.assertEqual(res.status_code, 201)
        self.assertIn('biryani', str(result.data))

    def test_recipe_already_exists_in_a_category(self):
        """Test API cannot create a recipe that already exists in the category"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"rice"}
        recipe = {"recipename" : "boiled rice" , "description" : "put rice in water"}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)
        result = self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)

        result2 = self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data =recipe)
        self.assertEqual(result2.status_code, 400)

    def test_recipes_cannot_entered_with_spaces(self):
        """Test API cannot create a recipe with spaces"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"rice"}
        recipe = {"recipename" : " " , "description" : " "}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=category)

        result=self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)
        self.assertEqual(result.status_code, 400)

    def test_recipes_cannot_entered_with_numbers(self):
        """Test API cannot create a recipe with numbers"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
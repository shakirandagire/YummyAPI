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
        self.category = {'categoryname': 'Salad'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
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
        self.assertIn('Salad', str(res.data))

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
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Salad', str(res.data))

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
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/api/v1/categories/?q=Salad',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Salad', str(res.data))

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
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/api/v1/categories/?page=1&per_page=1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Salad', str(res.data))
    
    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/api/v1/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Salad', str(result.data))

    def test_category_can_be_edited(self):
        """Test API can edit an existing category. (PUT request)"""

        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'Breakfast'})
        results = json.loads(rv.data.decode())
        self.assertEqual(rv.status_code, 201)

        rv = self.client().put(
            '/api/v1/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={"categoryname": "Lunch"})
        self.assertEqual(rv.status_code, 200)

        results = self.client().get(
            '/api/v1/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Lunch', str(results.data))

    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""

        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'Breakfast'})
        self.assertEqual(rv.status_code, 201)

        results = json.loads(rv.data.decode())


        res = self.client().delete(
            '/api/v1/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().delete(
            '/api/v1/categories/{}'.format(results['id']),
        headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


class RecipeTestCase(unittest.TestCase):
    """This class represents the recipes test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'categoryname': 'Salad'}
        self.recipe = {'recipename': 'biryani', 'description': 'put rice in the water'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
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
        self.assertIn('Salad', str(res.data))

        result = self.client().post('/api/v1/categories/1/recipes', data = self.recipe)
        self.assertEqual(res.status_code, 201)
        self.assertIn("biryani", str(result.data))

    def test_api_can_get_all_recipes(self):
        """Test API can get a recipe (GET request)."""
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
        self.assertIn('Salad', str(res.data))

        res = self.client().post('/api/v1/categories/1/recipes', data = self.recipe)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/v1/categories/1/recipes')
        self.assertEqual(res.status_code, 200)
        self.assertIn('biryani', str(res.data))

    def test_recipe_can_be_got_by_q(self):
        """Test API can create a category (POST request)"""      
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token), data = self.category)
        self.assertEqual(res.status_code, 201)

        result = self.client().post('/api/v1/categories/1/recipes', data = self.recipe)
        self.assertEqual(res.status_code, 201)
    
        result = self.client().get(
            '/api/v1/categories/1/recipes/?q=biryani',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.recipe)
              
    def test_recipe_can_be_got_by_pagination(self):
        """Test API can create a category (POST request)"""      
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token), data = self.category)
        self.assertEqual(res.status_code, 201)

        result = self.client().post('/api/v1/categories/1/recipes', data = self.recipe)
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/api/v1/categories/1/recipes/?page=1&per_page=1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.recipe)
      
    
    def test_api_can_get_recipe_by_id(self):
        """Test API can get a single recipe by using it's id."""
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
        self.assertIn('Salad', str(res.data))

        rv = self.client().post('/api/v1/categories/1/recipes', data=self.recipe)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/categories/1/recipes/1')
        self.assertEqual(result.status_code, 200)
        self.assertIn('biryani', str(result.data))

    def test_recipe_can_be_edited(self):
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
        self.assertIn('Salad', str(res.data))

        """Test API can edit an existing recipe. (PUT request)"""
        rv = self.client().post(
            '/api/v1/categories/1/recipes',
            data={'recipename': 'biryani' , 'description':'put rice in water'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/api/v1/categories/1/recipes/1',
            data={
                "recipename": "chicken steak", "description": " put chicken in grill"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/api/v1/categories/1/recipes/1')
        # self.assertIn('chicken steak', 'put chicken in grill',str(results.data))

    def test_recipe_deletion(self):
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
        self.assertIn('Salad', str(res.data))

        """Test API can delete an existing recipe. (DELETE request)."""
        rv = self.client().post(
            '/api/v1/categories/1/recipes',
            data={'recipename': 'biryani', 'description': 'put rice in water'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/api/v1/categories/1/recipes/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/api/v1/categories/1/recipes/1')
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
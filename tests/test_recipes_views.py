import unittest
import os
import json
from app import create_app, db
from app.models import Category, Recipe, User


class RecipeTestCase(unittest.TestCase):
    """This class represents the recipes test case"""
    
    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'categoryname': 'salad', 'category_description': 'Yummy Salad Recipes'}
        self.recipe = {'recipename': 'biryani', 'recipe_description': 'put rice in the water', 
                       'instructions': '1. Put water in saucepan, 2. Put rice and salt'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234",
                      security_question="testquestion",security_answer="testanswer"):
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
        category = {"categoryname":"rice", 'category_description': 'Yummy Salad Recipes'}
        recipe = {"recipename" : "boiled rice" , "recipe_description" : "put rice in water",
                  'instructions': '1. Put water in saucepan, 2. Put rice and salt'}
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
        category = {"categoryname":"rice", 'category_description': 'Yummy Salad Recipes'}
        recipe = {"recipename" : " " , "recipe_description" : " ", 'instructions': ' '}
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
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"rice", 'category_description': 'Yummy Salad Recipes'}
        recipe = {"recipename" : "23456754" , "recipe_description" : "put water", 
                 'instructions': '1. Put water in saucepan, 2. Put rice and salt'}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=category)

        res1 = self.client().post(
              '/api/v1/categories/1/recipes', 
              headers=dict(Authorization="Bearer " + access_token),
              data = recipe)
        self.assertEqual(res1.status_code, 400)

    def test_category_cannot_entered_with_special_character(self):
        """Test API cannot create a category with special_character"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category = {"categoryname":"rice", 'category_description': 'Yummy Salad Recipes'}
        recipe = {"recipename" : "$$##@!" , "recipe_description" : "put water",
                  'instructions': '1. Put water in saucepan, 2. Put rice and salt'}
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data = category)

        res1 = self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)
        self.assertEqual(res1.status_code, 400)

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
        # # self.assertEqual(res.status_code, 201)
        # self.assertIn('salad', str(res.data))

        res1= self.client().post('/api/v1/categories/1/recipes', 
              headers=dict(Authorization="Bearer " + access_token),
              data = self.recipe)
        # self.assertEqual(res1.status_code, 201)
        res2 = self.client().get('/api/v1/categories/1/recipes',
               headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res2.status_code, 200)
        self.assertIn('biryani', str(res2.data))

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
            headers=dict(Authorization="Bearer " + access_token), 
            data = self.category)
        self.assertEqual(res.status_code, 201)

        result = self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data = self.recipe)
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
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)
        self.assertEqual(res.status_code, 201)

        result = self.client().post(
                '/api/v1/categories/1/recipes',
                headers=dict(Authorization="Bearer " + access_token),
                data = self.recipe)
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
        self.assertIn('salad', str(res.data))

        rv = self.client().post(
            '/api/v1/categories/1/recipes', 
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token))
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
        self.assertIn('salad', str(res.data))

        """Test API can edit an existing recipe. (PUT request)"""
        rv = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data={'recipename': 'biryani' , 'recipe_description':'put rice in water', 
                  'instructions': '1. Put water in saucepan, 2. Put rice and salt'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "recipename": "chicken steak", "recipe_description": " put chicken in grill",
                'instructions': '1. Put chicken on the grill, 2. Put spices'
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
                '/api/v1/categories/1/recipes/1',
                headers=dict(Authorization="Bearer " + access_token)
        )

    def test_edited_recipe_cannot_be_entered_with_spaces(self):
        """Test API cannot create a new recipe with spaces"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        recipe = {"recipename": "  ", "recipe_description": " put chicken in grill",
                  'instructions': '1. Put chicken on the grill, 2. Put spices'}
            
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)

        res1 = self.client().put(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)

        self.assertEqual(res1.status_code, 400)


    def test_edited_recipe_cannot_be_entered_with_numbers(self):
        """Test API cannot create a new recipe with numbers"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        recipe = {"recipename": "123456", "recipe_description": " put chicken in grill",
                  'instructions': '1. Put chicken on the grill, 2. Put spices'}
            
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)

        res1 = self.client().put(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)

        self.assertEqual(res1.status_code, 400)

    def test_edited_recipe_cannot_be_entered_with_special_character(self):
        """Test API cannot create a new recipe with special_character"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        recipe = {"recipename": "$%^#@!", "description": " put chicken in grill",
                  'instructions': '1. Put chicken on the grill, 2. Put spices'}
            
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = self.category)

        res1 = self.client().put(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token),
            data = recipe)

        self.assertEqual(res1.status_code, 400)


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
        self.assertIn('salad', str(res.data))

        """Test API can delete an existing recipe. (DELETE request)."""
        rv = self.client().post(
            '/api/v1/categories/1/recipes',
            headers=dict(Authorization="Bearer " + access_token),
            data={'recipename': 'biryani', 'description': 'put rice in water',
                  'instructions': '1. Put water in saucepan, 2. Put rice and salt'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete(
            '/api/v1/categories/1/recipes/1',
            headers=dict(Authorization="Bearer " + access_token)
        )
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 400
        result = self.client().get(
                '/api/v1/categories/1/recipes/1',
                headers=dict(Authorization="Bearer " + access_token))
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
import unittest
import os
import json
from app import create_app, db

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
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)


    def test_category_creation(self):
        """Test API can create a category (POST request)"""      
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Salad', str(res.data))

    def test_api_can_get_all_categories(self):
        """Test API can get categories (GET request)."""

        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        
        res = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Salad', str(res.data))

    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/categories/{}'.format(results['id']),
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
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'Breakfast'})
        results = json.loads(rv.data.decode())
        self.assertEqual(rv.status_code, 201)

        rv = self.client().put(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={"categoryname": "Lunch"})
        self.assertEqual(rv.status_code, 200)

        results = self.client().get(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Lunch', str(results.data))

    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""

        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'categoryname': 'Breakfast'})
        self.assertEqual(rv.status_code, 201)

        results = json.loads(rv.data.decode())


        res = self.client().delete(
            '/categories/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().delete(
            '/categories/{}'.format(results['id']),
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
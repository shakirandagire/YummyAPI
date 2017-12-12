import unittest
import json
from app import create_app, db

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.test_data = {
            'email': 'shakira@ndagire.com',
            'password': '1234567'
        }

        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        res = self.client().post('/auth/register', data=self.test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "You registered successfully.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):  
        res = self.client().post('/auth/register', data=self.test_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/auth/register', data=self.test_data)
        self.assertEqual(second_res.status_code, 202)
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/auth/register', data=self.test_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/auth/login', data=self.test_data)
        result = json.loads(login_res.data.decode())
        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        not_a_user = {
            'email': 'new@user.com',
            'password': 'nope'
        }
        res = self.client().post('/auth/login', data=not_a_user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Invalid email or password, Please try again")
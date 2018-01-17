import unittest
import json
from app import create_app, db

class AuthTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '1234567',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        self.login_test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '1234567'
        }
        with self.app.app_context():
             db.create_all()

    def test_registration(self):
        """Test that API can register user"""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "You registered successfully.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that API cannot register existing user"""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        second_res = self.client().post('/api/v1/auth/register', data=self.test_data)
        self.assertEqual(second_res.status_code, 404)
        result = json.loads(second_res.data.decode())
        self.assertEqual(result['message'], "Email already exists. Please use another one")

    def test_user_enters_no_email_when_registering(self):
        """Test that API cannot register user with no email"""
        test_data = {
            'email': '',
            'password': '1234567',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "All fields are required")

    def test_user_enters_no_password_when_registering(self):
        """Test that API cannot register user with no password"""
        test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "All fields are required")

    def test_user_enters_invalid_email_when_registering(self):
        """Test that API cannot register user with invalid email"""
        test_data = {
            'email': 'shakirandagire',
            'password': '1234567',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Please enter correct email")

    def test_user_enters_invalid_password_when_registering(self):
        """Test that API cannot register user with invalid password"""
        test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '$%TGVG^&U&*',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Please enter correct password")

    def test_user_enters_no_security_question_when_registering(self):
        """Test that API cannot register user no security question"""
        test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '1234567',
            'security_question':'',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code,401)
        self.assertEqual(result['message'], "All fields are required")

    def test_user_enters_no_security_answer_when_registering(self):
        """Test that API cannot register user no security answer"""
        test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '1234567',
            'security_question':'favorite dog',
            'security_answer':''
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "All fields are required")

    def test_user_password(self):
        """Test that API cannot register with password less than 6 characters"""
        test_data = {
            'email': 'shakira1@ndagire.com',
            'password': '12345',
            'security_question':'favorite dog',
            'security_answer':'tuti'
        }
        res = self.client().post('/api/v1/auth/register', data=test_data)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Enter a password with more than 6 characters")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/v1/auth/login', data=self.login_test_data)
        result = json.loads(login_res.data.decode())
        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered user cannot login."""
        not_a_user = {
            'email': 'new@user.com',
            'password': 'nope'
        }
        res = self.client().post('/api/v1/auth/login', data=not_a_user)
        result = json.loads(res.data.decode())
        self.assertEqual(res.status_code, 401)
        self.assertEqual(result['message'], "Invalid email or password, Please try again")

    def test_user_logout(self):
        """Test registered user can logout."""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        login_res = self.client().post('/api/v1/auth/login', data=self.login_test_data)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res1 = self.client().post(
            '/api/v1/auth/logout',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res1.status_code, 200)

    def test_user_cannot_logout_with_wrong_token(self):
        """Test registered user can logout with wrong token."""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        login_res = self.client().post('/api/v1/auth/login', data=self.login_test_data)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res1 = self.client().post(
            '/api/v1/auth/logout',
            headers=dict(Authorization="Bearer " + " "))
        self.assertEqual(res1.status_code, 401)

    def test_user_cannot_be_granted_access(self):
        """Test that user cannot be granted access without a token."""
        res = self.client().post('/api/v1/auth/register', data=self.test_data)
        login_res = self.client().post('/api/v1/auth/login', data=self.login_test_data)
        result = json.loads(login_res.data.decode())
        access_token = result['access_token']
        res1 = self.client().post(
            '/api/v1/categories/')
        self.assertEqual(res1.status_code, 401)

    def test_change_password(self):
        """Test user can reset password"""
        res1 = self.client().post('/api/v1/auth/register', data=self.test_data)
        new_test_data = {'email': 'shakira1@ndagire.com',
                    'new_password': '12345678910',
                    'security_question':'favorite dog',
                    'security_answer':'tuti'}
        res2 = self.client().post(
            '/api/v1/auth/change_password',
            data=new_test_data)
        self.assertEqual(res2.status_code, 201)
        result = json.loads(res2.data.decode())
        self.assertEqual(result['message'], "Your password has been reset.")

    def test_user_cannot_change_password_with_wrong_email(self):
        """Test user can reset password"""
        res1 = self.client().post('/api/v1/auth/register', data=self.test_data)
        new_test_data = {'email': 'shakira2@ndagire.com',
                    'new_password': '12345678910',
                    'security_question':'favorite dog',
                    'security_answer':'tuti'}
        res2 = self.client().post(
            '/api/v1/auth/change_password',
            data=new_test_data)
        self.assertEqual(res2.status_code, 401)

    def test_user_cannot_change_password_with_wrong_security_answer(self):
        """Test user can reset password"""
        res1 = self.client().post('/api/v1/auth/register', data=self.test_data)
        new_test_data = {'email': 'shakira1@ndagire.com',
                    'new_password': '12345678910',
                    'security_question':'favorite dog',
                    'security_answer':'tuti11'}
        res2 = self.client().post(
            '/api/v1/auth/change_password',
            data=new_test_data)
        self.assertEqual(res2.status_code, 401)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()




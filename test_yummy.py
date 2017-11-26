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
        self.category = {'categoryname': 'Brunch'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_category_creation(self):
        """Test API can create a category (POST request)"""
        res = self.client().post('/categories/', data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Brunch', str(res.data))

    def test_api_can_get_all_categories(self):
        """Test API can get categories (GET request)."""
        res = self.client().post('/categories/', data=self.category)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/categories/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Brunch', str(res.data))

    def test_api_can_get_category_by_id(self):
        """Test API can get a single category by using it's id."""
        rv = self.client().post('/categories/', data=self.category)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/categories/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Brunch', str(result.data))

    def test_category_can_be_edited(self):
        """Test API can edit an existing category. (PUT request)"""
        rv = self.client().post(
            '/categories/',
            data={'categoryname': 'Breakfast'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/categories/1',
            data={
                "categoryname": "Breakfast and Lunch"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/categories/1')
        self.assertIn('and Lunch', str(results.data))

    def test_category_deletion(self):
        """Test API can delete an existing category. (DELETE request)."""
        rv = self.client().post(
            '/categories/',
            data={'categoryname': 'Breakfast'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/categories/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/categories/1')
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
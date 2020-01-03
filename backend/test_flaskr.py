import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is a question?',
            'answer': 'Errh...',
            'category': 'Art',
            'difficulty': 5

        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_create_question(self):
        self.client().post('/questions', json=self.new_question)
        response = self.client().post('/questions', json=self.new_question)
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(body.get('success'))

    def test_get_questions(self):
        response = self.client().get('/questions')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.get('success'))
        self.assertIn('questions', body.keys())
        self.assertIn('total_questions', body.keys())
        self.assertIn('categories', body.keys())

    def test_delete_question(self):
        question = Question.query.order_by(desc(Question.id)).first()

        response = self.client().delete(f'/questions/{question.id}')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.get('success'))
        self.assertEqual(body.get('deleted'), question.id)

    def test_404_error_if_page_out_of_range(self):
        response = self.client().get('/questions?page=1000000')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(body.get('success'))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

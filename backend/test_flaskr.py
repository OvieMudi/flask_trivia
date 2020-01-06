import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

from flaskr import create_app
from models import setup_db, Question, Category
from environs import Env

env = Env()
env.read_env('.config.env')


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = env.str('TEST_DATABASE_URI')
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            self.quiz1 = Question('question1?', 'answer1', '4', 3)
            self.quiz2 = Question('question2?', 'answer2', '4', 3)
            self.quiz3 = Question('question3?', 'answer3', '4', 3)
            self.quiz1.insert()
            self.quiz2.insert()
            self.quiz3.insert()

            self.new_question = {
                'id': self.quiz3.format()['id'],
                'question': self.quiz3.question,
                'answer': self.quiz3.answer,
                'category': self.quiz3.category,
                'difficulty': self.quiz3.difficulty
            }

            self.search_term = self.quiz3.question

            self.play_quiz_payload = {
                'previous_questions': [self.quiz2.id, self.quiz3.id],
                'quiz_category': '0'
            }

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.quiz1.delete()
            self.quiz2.delete()
            self.quiz3.delete()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_all_categories(self):
        response = self.client().get('/categories')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.get('success'))
        self.assertIn('categories', body.keys())

    def test_get_questions_by_categories(self):
        response = self.client().get('/categories/1/questions')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.get('success'))
        self.assertIn('current_category', body.keys())

    def test_create_question(self):
        self.client().post('/questions', json=self.new_question)
        response = self.client().post('/questions', json=self.new_question)
        body = json.loads(response.data)
        self.new_question['id'] = body.get('question')['id']

        self.assertEqual(response.status_code, 201)
        self.assertTrue(body.get('success'))

    def test_get_all_questions(self):
        response = self.client().get('/questions')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(body.get('success'))
        self.assertIn('questions', body.keys())
        self.assertIn('total_questions', body.keys())
        self.assertIn('categories', body.keys())

    def test_search_questions(self):
        with self.app.app_context():
            response = self.client().post(
                '/questions', json={'searchTerm': self.search_term})
            body = json.loads(response.data)

            self.assertTrue(body.get('success'))
            self.assertIn('questions', body.keys())
            self.assertIn('total_questions', body.keys())

    def test_play_quiz(self):
        with self.app.app_context():
            response = self.client().post('/quizzes', json=self.play_quiz_payload)
            body = json.loads(response.data)

            self.assertTrue(body.get('success'))
            self.assertIn('question', body.keys())
            self.assertIn('available_questions', body.keys())

    def test_delete_question(self):

        with self.app.app_context():
            question_id = self.new_question['id']

            response = self.client().delete(f'/questions/{question_id}')
            body = json.loads(response.data)

            self.assertEqual(response.status_code, 200)
            self.assertTrue(body.get('success'))
            self.assertEqual(body.get('deleted'), question_id)

    def test_400_error(self):
        response = self.client().post('/questions', json={})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(body.get('success'))

    def test_404_error_if_page_out_of_range(self):
        response = self.client().get('/questions?page=1000000')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(body.get('success'))

    def test_405_error(self):
        response = self.client().post('/questions/1', json={})
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 405)
        self.assertFalse(body.get('success'))

    def test_500_error(self):
        response = self.client().post('/quizzes')
        body = json.loads(response.data)

        self.assertEqual(response.status_code, 500)
        self.assertFalse(body.get('success'))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

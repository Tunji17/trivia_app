import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_login = ''  # insert database username and password in this format username:password
        self.database_path = "postgres://{}@{}/{}".format(self.database_login, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))
        self.assertTrue(len(data['questions']))

    def test_create_question(self):
        payload = {
            'question': 'who am i',
            'answer': 'i am tunji',
            'difficulty': 1,
            'category': 3,
        }
        response = self.client().post('/questions', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)

    def test_search_question(self):
        payload = {
            'searchTerm': 'what is',
        }
        response = self.client().post('/questions', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_categories(self):
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_delete_question(self):
        res = self.client().delete('/questions/6')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 6).one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['deleted'], 6)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete('/books/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
    
    def test_play_quiz_all_categories(self):
        payload = {
            'previous_questions': [10],
            'quiz_category': {'type': 'click', 'id': 0}
        }
        response = self.client().post('/quizzes', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['question']))

    def test_play_quiz_single_category(self):
        payload = {
            'previous_questions': [10],
            'quiz_category': {'type': 'science', 'id': 1}
        }
        response = self.client().post('/quizzes', json=payload)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['question']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

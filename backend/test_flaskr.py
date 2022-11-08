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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["totalQuestions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_get_invalid_page(self):
        result = self.client().get('/questions?page=1000')
        data = json.loads(result.data)
        self.assertNotEqual(result.status_code, 400)
        self.assertEqual(data['success'], True)

    def test_get_categories(self):
        result = self.client().get('/categories')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_delete_questions(self):
        result = self.client().get('/questions/1000')
        data = json.loads(result.data)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable resource')

    def test_add_questions(self):
        new_question = {
            'question': 'what is your number',
            'answer': '456',
            'difficulty': 1,
            'category': 1
        }
        result = self.client().get('/questions', json=new_question)
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)

    def test_questions_in_category(self):
        result = self.client().get('/categories/1/questions')
        data = json.loads(result.data)
        self.assertEqual(result.status_code, 200)

    def test_question_not_in_category(self):
        result = self.client().get('/categories/1000/questions')
        self.assertEqual(result.status_code, 404)

    def test_search_questions(self):
        search = {
            'searchTerm': "i"
        }
        result = self.client().post('/search', json=search)
        self.assertEqual(result.status_code, 200)

    def test_search_not_found(self):
        search = {
            'searchTerm': "Expecto patronam for dementors"
        }
        result = self.client().post('/search', json=search)
        self.assertEqual(result.status_code, 422)

    def test_quiz_sucess(self):
        quiz = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'Science',
                'id': 'A'
            }
        }
        result = self.client().post('/quizzes', json=quiz)
        data = json.loads(result.data)
        self.assertEqual(data['success'], True)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()

from crypt import methods
from operator import le
import os
import re
from sre_parse import CATEGORIES
from traceback import print_tb
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_data(request, selection):
    """helper function to paginate data"""
    page = request.args.get('page', 1, type=int)
    start = (page -1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    
    formatted_data = [s.format() for s in selection]
    formatted_data = formatted_data[start:end]
    return formatted_data
    
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resource={r"/api/*": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response
    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        """Endpoint to get all available categories"""
        categories = Category.query.all()
        formatted_category = {}
        for c in categories:
            formatted_category[c.id] = c.type
        return jsonify({
            'success': True,
            'categories': formatted_category
        })

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        """endpoint to retreive all questions from the DB
        and return 10 questions per page"""
        try:
            questions = Question.query.all()
            categories = Category.query.all()
            cat = {}
            for c in categories:
                cat[c.id] = c.type
            formatted_questions = paginate_data(request, questions)
            
            return jsonify ({
                'success': True,
                'questions': formatted_questions,
                'totalQuestions': len(formatted_questions),
                'categories': cat,
                'currentCategory': 'History'
            })
        except Exception as e:
            print(e)
            abort(400)
    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['GET', 'DELETE'])
    def delete_question(question_id):
        """Endpoint to delete question by id"""
        try:
            # returns one question if the id mathches else returns none
            question = Question.query.filter(question_id == Question.id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            all_questions = Question.query.all()
            current_question = paginate_data(request, all_questions)
            return jsonify({
                "success": True
            })
        except:
            abort(422)


    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        """End point which adds a new question"""
        #Getting the body of the request
        body = request.get_json()
        try:
            new_question = body.get('question')
            new_answer = body.get('answer')
            new_difficulty = body.get('difficulty')
            new_category = body.get('category')
            
            new = Question(question=new_question, answer=new_answer,
                           difficulty=new_difficulty, category=new_category)
            new.insert()
            return jsonify({
                'success': True
            })
        except:
            abort(422)

    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/search', methods=['POST'])
    def search_question():
        """Endpoint to search a question"""
        body = request.get_json()
        try:
            #Fetching the searchTerm from the body
            search_term = body.get('searchTerm', None)
            
            search_result = Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
            if len(search_result) == 0:
                abort(404)
            questions = paginate_data(request, search_result)
            return jsonify({
                'success': True,
                'questions': questions,
                'totalQuestions': len(search_result),
                'currentCategory': 'Entertainment'
            })
        except:
            abort(422)

    """
    Create a GET endpoint to get questions based on category.
    """
    @app.route('/categories/<int:cat_id>/questions')
    def get_question_by_category(cat_id):
        """Endpoint to get questions by category"""
        try:
            #Fetch the category type using the id
            cat = Category.query.filter(Category.id == cat_id).one_or_none()
            question = Question.query.filter_by(category=str(cat_id)).all()
            formatted_question = paginate_data(request, question)
            print(formatted_question)    
            return jsonify({
                "success": True,
                'questions': formatted_question,
                'currentCategory': str(cat.type),
                'totalQuestions': len(question)
            })
        except:
            abort(404)
    
    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST', 'GET'])
    def play_quiz():
        """Endpoint to play the quiz"""
        body = request.get_json()
        try:
            #fetch data from the previous question
            previous_question = body.get('previous_questions')
            quiz_category = body.get('quiz_category')
            
            current_category = Category.query.filter_by(type=str(quiz_category['type'])).one_or_none()
            if current_category is None:
                question = Question.query.all()
            else:
                question = Question.query.filter_by(category=str(quiz_category['id'])).all()
            
            random_index = random.randint(0, len(question) - 1)
            random_question = question[random_index]
            #Until the question isn't in previous question keep generatng randome nums
            while random_question.id in previous_question:
                random_index = random.randint(0, len(question) - 1)
                random_question = question[random_index]
            return jsonify({
                'success': True,
                "question": {
                    'id': random_question.id,
                    'question': random_question.question,
                    'answer': random_question.answer,
                    'difficulty': random_question.difficulty,
                    'category': random_question.category
                }
            })
        except:
            abort(422)

    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Page not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable_recource(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Unprocessable resource"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    @app.errorhandler(405)
    def invalid_method(error):
        return jsonify({
            "success": False,
            'error': 405,
            "message": "Invalid method!"
        }), 405
    
    return app

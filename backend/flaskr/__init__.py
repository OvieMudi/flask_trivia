import os
from math import ceil
from sys import exc_info
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_results(results):
    page = request.args.get('page', 1, int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    return results[start:end]


def fetch_categories():
    categories = Category.query.all()
    formated_categories = [category.format() for category in categories]
    return formated_categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)

    # '''
    # @TODO: Use the after_request decorator to set Access-Control-Allow
    # '''
    @app.after_request
    def access_control_headers(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,POST,PATCH,DELETE,OPTIONS')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
        try:
            formated_categories = fetch_categories()

            return jsonify({
                'categories': formated_categories
            })

        except:
            print(exc_info())
            abort(422)

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    @app.route('/questions')
    def get_questions():
        try:
            questions = Question.query.all()
            formated_questions = [question.format() for question in questions]
            paginated_questions = paginate_results(formated_questions)

            if request.args.get('page', 1, int) > ceil(len(questions)/QUESTIONS_PER_PAGE):
                return handle_404_error('Out of range')

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(questions),
                'categories': fetch_categories(),
                'current_categories': None
            })

        except:
            print(exc_info)
            abort(422)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()
            question.delete()

            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            print(exc_info())
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        search_term = body.get('searchTerm', None)
        if search_term:
            try:
                questions = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()
                formated_questions = [question.format()
                                      for question in questions]
                paginated_questions = paginate_results(formated_questions)

                return jsonify({
                    'questions': paginated_questions,
                    'total_questions': len(formated_questions),
                    'current_category': None
                })

            except:
                abort(422)

        else:
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            for value in (question, answer, difficulty, category):
                if not value:
                    print(value)
                    return handle_400_error(f'Null or invalid syntax in request data: {value}')

            try:
                new_question = Question(
                    question,
                    answer,
                    category,
                    difficulty
                )

                new_question.insert()

                return jsonify({
                    'success': True,
                    'message': 'created'
                }), 201

            except:
                print(exc_info())
                abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def handle_400_error(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': error or 'Null or invalid syntax in request data.'
        }), 400

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': error or "Requested page not found"
        }), 404

    @app.errorhandler(422)
    def handle_422_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Cannot process request."
        }), 422

    return app

import os
from math import ceil
from sys import exc_info, path
from flask import Flask, request, abort, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

print(path)


def paginate_results(results):
    page = request.args.get('page', 1, int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    return results[start:end]


def fetch_categories():
    categories = Category.query.all()
    formated_categories = [category.format() for category in categories]
    return formated_categories


def fetch_questions():
    questions = Question.query.all()
    formated_questions = [question.format() for question in questions]
    return formated_questions


def fetch_questions_filter_by_category(category_id):
    questions = Question.query.filter(
        Question.category == str(category_id)).all()
    formated_questions = [category.format() for category in questions]
    return formated_questions


def handle_path_params_validation(param):
    try:
        int(param)
        pass

    except Exception as ex:
        print(ex)
        abort(400)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins.
    Delete the sample route after completing the TODOs
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

    @app.route('/')
    def get_index():
        return redirect(url_for('get_questions'))

    @app.route('/categories')
    def get_categories():
        try:
            formated_categories = fetch_categories()

            return jsonify({
                'success': True,
                'categories': formated_categories
            })

        except Exception as ex:
            print(ex)

    @app.route('/questions')
    def get_questions():
        try:
            formated_questions = fetch_questions()
            paginated_questions = paginate_results(formated_questions)

            if request.args.get('page', 1, int) > ceil(
                    len(formated_questions)/QUESTIONS_PER_PAGE):
                return handle_404_error('Out of range')

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(formated_questions),
                'categories': fetch_categories(),
                'current_categories': None
            })

        except Exception as ex:
            print(exc_info)
            abort(422)

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
        except Exception as ex:
            print(ex)
            abort(422)

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
                    'success': True,
                    'questions': paginated_questions,
                    'total_questions': len(formated_questions),
                    'current_category': None
                })

            except Exception as ex:
                abort(422)

        else:
            question = body.get('question', None)
            answer = body.get('answer', None)
            difficulty = body.get('difficulty', None)
            category = body.get('category', None)

            for value in (question, answer, difficulty, category):
                if not value:
                    print(value)
                    return handle_400_error(
                        f'Null or invalid syntax in request data: {value}')

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
                    'message': 'created',
                    'question': new_question.format()
                }), 201

            except Exception as ex:
                print(ex)
                abort(422)

    @app.route('/categories/<category_id>/questions')
    def get_questions_by_id(category_id):
        handle_path_params_validation(category_id)

        try:
            formated_questions = fetch_questions_filter_by_category(
                category_id)
            paginated_questions = paginate_results(formated_questions)

            return jsonify({
                'success': True,
                'questions': paginated_questions,
                'total_questions': len(formated_questions),
                'current_category': category_id
            })

        except Exception as ex:
            print(ex)
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def quiz_questions():
        body = request.get_json()

        if not body:
            abort(500)

        else:
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)

            try:
                questions = None
                selected_question = None

                if bool(int(quiz_category)):
                    questions = fetch_questions_filter_by_category(
                        quiz_category)

                else:
                    questions = fetch_questions()

                available_questions = [
                    question for question in questions if question.get(
                        'id') not in previous_questions]

                selected_question = random.choice(
                    available_questions) if len(available_questions) else None

                return jsonify({
                    'success': True,
                    'question': selected_question,
                    'available_questions': available_questions
                })

            except Exception as ex:
                print(ex)
                abort(422)

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
            'message': 'Null or invalid syntax in request.'
        }), 400

    @app.errorhandler(404)
    def handle_404_error(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': "Requested page not found"
        }), 404

    @app.errorhandler(405)
    def handle_405_error(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': "Method not allowed"
        }), 405

    @app.errorhandler(422)
    def handle_422_error(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': "Cannot process request."
        }), 422

    @app.errorhandler(500)
    def handle_500_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': "Internal server error"
        }), 500

    return app

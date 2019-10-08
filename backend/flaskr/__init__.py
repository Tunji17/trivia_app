import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from pprint import pprint
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response

    @app.route('/categories')
    def get_categories():
        all_categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in all_categories]
        return jsonify({
          'categories': formatted_categories,
        })

    @app.route('/questions')
    def get_questions():
        page = request.args.get('page', 1, int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        skip = start + QUESTIONS_PER_PAGE
        all_questions = Question.query.order_by(Question.id).all()
        formatted_questions = [question.format() for question in all_questions]
        total_questions = len(formatted_questions)
        paginated_result = formatted_questions[start:skip]
        all_categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in all_categories]
        return jsonify({
          'questions': paginated_result,
          'total_questions': total_questions,
          'categories': formatted_categories,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
              'deleted': question_id,
            })
        except:
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        data = request.get_json()
        new_question = data.get('question', None)
        question_answer = data.get('answer', None)
        question_difficulty = data.get('difficulty', None)
        question_category = data.get('category', None)
        search_term = data.get('searchTerm')
        if search_term:
            search_response = Question.query.filter((Question.question.ilike("%{}%".format(search_term)))).all()
            formatted_search_result = [question.format() for question in search_response]
            total_questions = len(formatted_search_result)
            return jsonify({
              'questions': formatted_search_result,
              'total_questions': total_questions,
            })
        try:
            question = Question(
              question=new_question,
              answer=question_answer,
              difficulty=question_difficulty,
              category=question_category,
            )
            question.insert()
            return jsonify({
              'status_code': 200
            })
        except:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        result = Question.query.filter_by(category=category_id).all()
        formatted_result = [question.format() for question in result]
        total_questions = len(formatted_result)
        return jsonify({
          'questions': formatted_result,
          'total_questions': total_questions,
        })

    def get_random_row():
        max_model_id = Question.query.order_by(Question.id.desc())[0].id
        random_id = random.randrange(0, max_model_id)
        random_row = Question.query.get(random_id)
        if random_row is None:
            return ''
        formatted_random_row = random_row.format()
        return formatted_random_row

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')
        if quiz_category['id'] == 0:
            question = get_random_row()
            if previous_questions:
                while (question['id'] == previous_questions[0]):
                    question = get_random_row()
            return jsonify({
                'question': question,
            })
        else:
            category_questions = Question.query.filter_by(category=quiz_category['id']).all()
            formatted_category_questions = [question.format() for question in category_questions]
            true_random = random.SystemRandom()
            question = true_random.choice(formatted_category_questions)
            if previous_questions:
                counter = 0
                while (question['id'] == previous_questions[counter]):
                    question = true_random.choice(formatted_category_questions)
                    counter += 1
            return jsonify({
                'question': question,
            })

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 400,
          "message": "bad request"
          }), 400
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          "success": False,
          "error": 404,
          "message": "resource not found"
          }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          "success": False,
          "error": 422,
          "message": "unprocessable"
          }), 422

    @app.errorhandler(500)
    def bad_request(error):
        return jsonify({
          "success": False,
          "error": 500,
          "message": "Internal server error"
          }), 500

    return app

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, core
from sqlalchemy import func
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page-1)*QUESTIONS_PER_PAGE
  end = start+QUESTIONS_PER_PAGE
  formatted_selection = [item.format() for item in selection]
  return formatted_selection[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route("/categories")
  def retrieve_categories():
    all_categories = Category.query.order_by(Category.id).all()
    categories = {category.id: category.type for category in all_categories}
    if len(categories) == 0:
        abort(404)
    else:
        return jsonify({
            "success": True,
            "categories": categories
        })
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
  @app.route("/questions")
  def retrieve_questions():
    questions = Question.query.order_by(Question.id).all()
    paginated_questions = paginate(request, questions)
    all_categories = Category.query.order_by(Category.id).all()
    categories = {category.id:category.type for category in all_categories}
    if len(paginated_questions) == 0:
      abort(404)
    else:
      return jsonify({
        "success": True,
        "questions": paginated_questions,
        "total_questions": len(questions),
        "current_category": None,
        "categories": categories,
      })
  '''

  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route("/questions/<int:question_id>", methods=["DELETE"])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      
      if question is None:
        abort(404)
        
      question.delete()

      return jsonify({
        "success": True,
        "deleted": question_id              
      })
    except:
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
  @app.route("/questions", methods=["POST"])
  def add_question():
    try:
      body = request.get_json()

      if 'question' not in body or 'answer' not in body or 'difficulty' not in body or 'category' not in body:
        abort(422)

      question = body.get('question')
      answer = body.get('answer')
      difficulty = int(body.get('difficulty'))
      category = int(body.get('category'))
      question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
      question.insert()

      return jsonify({
          "success": True,
          "created": question.id    
      })
    except:
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
  @app.route("/questions/search", methods=["POST"])
  def search_questions():
    body = request.get_json()
    searchTerm = body.get('searchTerm','')

    questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
    paginated_questions = paginate(request, questions)

    if len(paginated_questions) == 0:
      abort(404)
    else:
      return jsonify({
          "success": True,
          "questions": paginated_questions,
          "total_questions": len(questions),
          'current_category': None
      })
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route("/categories/<int:category_id>/questions")
  def retrieve_category_questions(category_id):
    try:
      questions = Question.query.order_by(Question.id).filter_by(category=category_id).all()
      paginatedQuestions = paginate(request, questions)
      all_categories = Category.query.order_by(Category.id).all()
      categories = {category.id:category.type for category in all_categories}
      if len(paginatedQuestions) == 0:
        abort(404)
      else:
        return jsonify({
          "success": True,
          "questions": paginatedQuestions,
          "total_questions": len(questions),
          "current_category": category_id,
          "categories": categories,
        })
    except:
      abort(404)
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
  @app.route("/quizzes", methods=["POST"])
  def play_quiz():
    try:
      body = request.get_json()
      
      previous_questions = body.get('previous_questions',[])
      quiz_category = body.get('quiz_category')
      category_id = int(quiz_category.get('id'))      
    
      if category_id > 0:
        question = Question.query.filter(Question.category==int(category_id)).filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()
      else:
        question = Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).first()    
      
      formatted_question = None 
      if question:
        formatted_question = question.format()

      return jsonify({
          "success": True,
          "question": formatted_question,
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
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
      "message": "resource is not found"
    }), 404

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "method is not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
    }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
    }), 500
  
  return app

    
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resourses={r'/*':{'origins':'*'}})
  
  @app.after_request
  def after_request (response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Headers','GET,POST,PATCH,DELET,OPTIONS')
    return response

  def paginate (request,selection):
    page =request.args.get('page',1,type=int)
    start=(page -1 )*QUESTIONS_PER_PAGE
    end= start+QUESTIONS_PER_PAGE
    question=[q.format() for q in selection]
    current_qs=question[start:end ]
    return current_qs
  
 
  @app.route('/categories',methods=['GET'])
  def get_all_categories():
    try:
      categories =Category.query.all()
      if (len(categories)==0):abort(404)
      categories_dict={category.id:  category.type for category in Category.query.all()}
      
      return jsonify({
      'success':True,
      'categories':categories_dict
      }),200
    except Exception:
      abort(422)



  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions=Question.query.order_by(Question.id).all()
    total_questions=len(questions)
    current_qs=paginate(request,questions)
    if (len(current_qs)==0):abort(404)

    categories =Category.query.order_by(Category.id).all()
    if (len(categories)==0):abort(404)

    categories_dict={category.id:  category.type for category in categories}

    return jsonify({
      'success':True,
      'questions':current_qs,
      'total_questions':total_questions,
      'categories':categories_dict,       
    }),200


  @app.route("/questions/<int:qID>", methods=['DELETE'])
  def delete_question(qID):
    try:
      question=Question.query.filter_by(id=qID).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
        'success':True,
        'deleted':qID
      }),200

    except Exception:
      abort(422)

  @app.route("/questions", methods=['POST'])
  def post_question():
    try:
      data=request.get_json()
      question =data.get('question',None)
      answer =data.get('answer',None)
      difficulty =data.get('difficulty',None)
      category =data.get('category',None)
      if not (question and answer and difficulty and category):
        return abort(422)
      
      question=Question(question=question,answer=answer,difficulty=difficulty,category=category)
      question.insert()

      return jsonify({
        'success':True,
        'id':question.id,
        'created':question.question,
        'message':'Question successfully created!',
      }),200
    except Exception:
      abort (422)
  
  @app.route('/questions/search',methods=['POST'])
  def search_questions():
    data= request.get_json()
    search_term= data.get('searchTerm',None)
    if not search_term:
      abort(422)
    try:
      search_results=Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      if len(search_results) ==0:
        abort(404)
      current_qs=paginate(request,search_results)
      
      return jsonify({
        'success':True,
        'questions':current_qs,
        'total_questions':len(search_results),
      }),200
    except Exception:
      abort(404)
  
  @app.route('/categories/<int:id>/questions')
  def get_questions_by_category(id):
    category = Category.query.filter_by(id=id).one_or_none()

    if (category is None):
        abort(400)

    selection = Question.query.filter_by(category=category.id).all()

    paginated = paginate(request, selection)

    return jsonify({
        'success': True,
        'questions': paginated,
        'total_questions': len(Question.query.all()),
        'current_category': category.type
    })

  
  @app.route("/quizzes",methods=["POST"])
  def play_quiz():
    try:
      data = request.get_json()

      prev_qs = data.get('previous_questions')

      category = data.get('quiz_category')

      if (category) is None or (prev_qs) is None:
        abort(400)

      
      if (int (category['id'] )== 0):
          questions = Question.query.all()
      else:
          questions = Question.query.filter_by(category=category['id']).all()

      if not questions:
        abort(404)
      total = len(questions)
      new_question = questions[random.randrange(0, len(questions), 1)]
      def Is_Used(question):
            used_befor = False
            for pre_q in prev_qs:
                if (pre_q == question.id):
                    used_befor = True
            return used_befor

      while (Is_Used(new_question)):
          new_question = questions[random.randrange(0, len(questions), 1)]
          if new_question is None:
            return jsonify({
            'success': True
            })

      return jsonify({
            'success': True,
            'question': new_question.format()
        })
    except Exception:
      abort(400)

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':"Resource Not Found"
    }),404
  
  @app.errorhandler(422)
  def Unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':"Unprocessable Entity"
    }),422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':"Bad Request"
    }),400
  
  return app

    
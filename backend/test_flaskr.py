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
        self.database_path = "postgresql://{}@{}/{}".format('postgres', 'localhost:5432', self.database_name)
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

   
    def test_get_all_categories(self):
        response = self.client().get('/categories')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(data['categories']))


    def test_404_request_not_exist_category(self):
        response = self.client().get('/categories/111111')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource Not Found')
    

    def test_get_paginated_question(self):
        response = self.client().get('/questions')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
         self.assertIn('questions', data)
        self.assertIn('total_questions', data)
        self.assertEqual(len(data['questions']),10)
    
    
    def test_404_request_question_with_valid_page(self):
        response = self.client().get('/questions?page=500')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource Not Found')


    def test_delete_question(self):
        new_question={
            "answer": "Apollo 13", 
            "category": 5, 
            "difficulty": 4,
            "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"
        }
        question= Question(question=new_question['question'], answer=new_question['answer'],difficulty=new_question['difficulty'],category=new_question['category'])
        question.insert()
        
        qID= question.id
        Q_befor=Question.query.all()

        response = self.client().delete('/questions/{}'.format(qID))
        data=json.loads(response.data)
        Q_after=Question.query.all()
        question=Question.query.filter(Question.id==qID).one_or_none()

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],qID)
        self.assertTrue(len(Q_befor)>len(Q_after))
        self.assertEqual(question,None)
    
    def test_404_delete_Not_Exist_question(self):
        response = self.client().delete('/questions/484sdf53')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource Not Found')

    def test_422_delete_question_twice(self):
        question= Question(question="this question for test deleting twice ", answer="this answer for test also",category=1,difficulty=1)
        question.insert()
        qID=question.id
        self.client().delete('/questions/{}'.format(qID))
        response = self.client().delete('/questions/{}'.format(qID))
        data=json.loads(response.data)

        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unprocessable Entity')


  
    def test_post_question(self):
        new_question={
            'question': "this new question for test the creating option ",
            'answer':"this answer for test also",
            'category':1,
            'difficulty':1
        }
        Q_befor=Question.query.all()
        response = self.client().post('/questions',json=new_question)
        data=json.loads(response.data)
        Q_after=Question.query.all()
        new_question = Question.query.filter_by(id=data['id']).one_or_none()


        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(len(Q_after)>len(Q_befor))
        self.assertIsNotNone(new_question )
        self.assertEqual(data['message'], 'Question successfully created!')


    
    def test_422_post_question_with_invalid_data(self):
        new_question={
            'question': None,
            'answer':None,
            'category':1,
            'difficulty':1
        }
        response = self.client().post('/questions',json=new_question)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unprocessable Entity')
    

    def test_search_questions(self):
        search_Term={'searchTerm':'Body'}
        response = self.client().post('/questions/search',json=search_Term)
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertIsNotNone(data['questions'])
        self.assertIsNotNone(data['total_questions'])


    def test_422_search_question_with_Invalid_data(self):
        search_Term={'searchTerm':''}
        response = self.client().post('/questions/search',json=search_Term)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Unprocessable Entity')

    def test_get_catogery_questions(self):
        response = self.client().get('/categories/6/questions')
        data=json.loads(response.data)

        self.assertEqual(response.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertNotEqual(len(data['questions']),0)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])


    def test_404_get_catogery_questions_with_invalid_data(self):
         
        response = self.client().get('/categories/c/questions')
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Resource Not Found')
    
    def test_play_quiz(self):
        new_quiz= {'previous_questions': [4],
                          'quiz_category': {'type': 'Geography', 'id': '3'}}

        response = self.client().post('/quizzes', json=new_quiz)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'],3)
        self.assertNotEqual(data['question']['id'],3)

    def test_400_play_quiz_with_invalid_data(self):
        new_quiz={'previous_questions':[]}
        response = self.client().post('/quizzes',json=new_quiz)
        data=json.loads(response.data)
        
        self.assertEqual(response.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'Bad Request')
    
    
    
    





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
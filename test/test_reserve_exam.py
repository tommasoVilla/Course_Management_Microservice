import unittest
from pymongo import MongoClient
from app import app

mongo_client = MongoClient()


class TestReserveExam(unittest.TestCase):

    # To make the test some default documents are stored in the db
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        exams = db.exams
        students = db.students
        exams.insert_one({"course": "IdCorso:re39ur32",
                          "call": 1,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": []})
        exams.insert_one({"course": "IdCorso:re39ur33",
                          "call": 1,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": []})
        students.insert_one({"name": "John Doe",
                             "username": "student_username",
                             "courses": ["IdCorso:re39ur32"]})

    # Testing standard case: the student is registered to the exam
    def test_reserve_exam_success(self):
        exam_id = str(mongo_client.course_management.exams.find_one({"course": "IdCorso:re39ur32"})['_id'])
        response = self.app.put('/course_management/api/v1.0/exams/' + exam_id + '/students/student_username')
        self.assertEqual(200, response.status_code)

    # Testing the following scenario: the user requires to make a reservation for a student that does not exist
    def test_not_found_student(self):
        exam_id = str(mongo_client.course_management.exams.find_one({"course": "IdCorso:re39ur32"})['_id'])
        response = self.app.put('/course_management/api/v1.0/exams/' + exam_id + '/students/not_exist')
        pass_condition = 404 == response.status_code and response.json['error'] == 'Student Not Found'
        self.assertEqual(True, pass_condition)

    # Testing the following scenario: the user requires to make a reservation for an exam that does not exist.
    def test_not_found_exam(self):
        response = self.app.put(
            '/course_management/api/v1.0/exams/aaaaaaaaaaaaaaaaaaaaaaaa/students/student_username')
        pass_condition = 404 == response.status_code and response.json['error'] == 'Exam Not Found'
        self.assertEqual(True, pass_condition)

    # Testing reservation of a student already registered to the exam
    def test_conflict_student(self):
        exam_id = str(mongo_client.course_management.exams.find_one({"course": "IdCorso:re39ur32"})['_id'])
        self.app.put(
            '/course_management/api/v1.0/exams/' + exam_id + '/students/student_username')
        response = self.app.put(
            '/course_management/api/v1.0/exams/' + exam_id + '/students/student_username')
        self.assertEqual(409, response.status_code)

    # Testing reservation of a student that is not registered to the course
    def test_not_subscribed_student(self):
        exam_id = str(mongo_client.course_management.exams.find_one({"course": "IdCorso:re39ur33"})['_id'])
        response = self.app.put('/course_management/api/v1.0/exams/' + exam_id + '/students/student_username')
        self.assertEqual(403, response.status_code)

    # The data store is cleaned up after the execution of the test
    def tearDown(self):
        db = mongo_client.course_management
        exams = db.exams
        students = db.students
        exams.delete_one({"course": "IdCorso:re39ur32"})
        exams.delete_one({"course": "IdCorso:re39ur33"})
        students.delete_one({"username": "student_username"})

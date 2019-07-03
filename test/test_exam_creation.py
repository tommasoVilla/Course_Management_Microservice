import unittest
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestCExamCreation(unittest.TestCase):

    # To make the test a default exam is added to the data store
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        exams = db.exams
        exams.insert_one({"course": "IdCorso:re39ur32",
                          "call": 1,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": []})

    # Testing standard case: an user complete the exam creation
    def test_insert_exam(self):
        exam = {"course": "IdCorso1:re39ur32",
                "call": 2,
                "date": "24-11-2020",
                "startTime": "10:30",
                "room": "A1",
                "expirationDate": "20-11-2020",
                "students": []}

        response = self.app.post('/course_management/api/v1.0/exams', json=exam)
        self.assertEqual(201, response.status_code)

    # Testing creation attempt of a exam that is in conflict with the one already in the data store
    def test_conflict_exam(self):
        conflict_exam = {"course": "IdCorso:re39ur32",
                         "call": 1,
                         "date": "12-03-2019",
                         "startTime": "9:30",
                         "room": "A5",
                         "expirationDate": "10-03-2019",
                         "students": []}
        response = self.app.post('/course_management/api/v1.0/exams', json=conflict_exam)
        self.assertEqual(409, response.status_code)

    # Testing forwarding of a request with wrong fields (specifically date has a bad format)
    def test_bad_request(self):
        bad_exam = {"course": "IdCorso3:re39ur32",
                    "call": 4,
                    "date": "1-15-2020",
                    "startTime": "16:30",
                    "room": "A3",
                    "expirationDate": "20-11-2020",
                    "students": []}
        response = self.app.post('/course_management/api/v1.0/exams', json=bad_exam)
        self.assertEqual(400, response.status_code)

    # The data store is cleaned up after the execution of the test: the created exams are removed
    def tearDown(self):
        db = mongo_client.course_management
        exams = db.exams
        exams.delete_one({"course": "IdCorso:re39ur32"})
        exams.delete_one({"course": "IdCorso1:re39ur32"})

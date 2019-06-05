import unittest

from bson import ObjectId
from pymongo import MongoClient

from app import app

mongo_client = MongoClient()


class TestUnsubscribeStudent(unittest.TestCase):

    # To make the test default documents are stored into the db
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        db = mongo_client.course_management
        courses = db.courses
        courses.insert_one({"_id": ObjectId("bbbbbbbbbbbbbbbbbbbbbbbb"),
                            "name": "corso1",
                            "department": "dipartimento",
                            "teacher": "docente",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [{"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                         {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})
        courses.insert_one({"_id": ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'),
                            "name": "corso2",
                            "department": "dipartimento",
                            "teacher": "docente",
                            "year": "2019-2020",
                            "semester": 2,
                            "description": "descrizione",
                            "schedule": [
                                {"day": "lun", "startTime": "09:00", "endTime": "10:30", "room": "A1"},
                                {"day": "mar", "startTime": "10:30", "endTime": "11:30", "room": "C6"}]})
        students = db.students
        students.insert_one({"name": "John Doe",
                             "username": "student_username",
                             "courses": [ObjectId('aaaaaaaaaaaaaaaaaaaaaaaa'), ObjectId('bbbbbbbbbbbbbbbbbbbbbbbb')]})
        exams = db.exams
        exams.insert_one({"course": "bbbbbbbbbbbbbbbbbbbbbbbb",
                          "call": 1,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": ["student_username", "other_student"]})
        exams = db.exams
        exams.insert_one({"course": "bbbbbbbbbbbbbbbbbbbbbbbb",
                          "call": 2,
                          "date": "21-03-2019",
                          "startTime": "10:30",
                          "room": "A1",
                          "expirationDate": "20-03-2019",
                          "students": ["student_username", "other_student"]})

    # Testing standard case: the courses is added to the student
    def test_unsubscribe_student_success(self):
        response = self.app.delete(
            '/course_management/api/v1.0/students/student_username/courses/bbbbbbbbbbbbbbbbbbbbbbbb')
        cond1 = response.status_code == 200
        cond2 = "bbbbbbbbbbbbbbbbbbbbbbbb" not in response.json['courses']
        exams = mongo_client.course_management.exams.find({"course": "bbbbbbbbbbbbbbbbbbbbbbbb"})
        cond3 = "student_username" not in exams[0]["students"] and "student_username" not in exams[1]["students"]
        pass_condition = cond1 and cond2 and cond3
        self.assertEqual(True, pass_condition)

    # The data store is cleaned up after the execution of the test
    def tearDown(self):
        db = mongo_client.course_management
        courses = db.courses
        students = db.students
        exams = db.exams
        courses.delete_one({"name": "corso1"})
        courses.delete_one({"name": "corso2"})
        students.delete_one({"username": "student_username"})
        exams.delete_many({"course": "bbbbbbbbbbbbbbbbbbbbbbbb"})

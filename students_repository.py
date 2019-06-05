from bson import ObjectId
from pymongo.errors import PyMongoError

"""
This module provides functions that handle the interaction with courses persistence layer.
The persistence layer is a Mongo data-store.
"""


class StudentsRepositoryException(Exception):
    pass


def serialize_student(student):
    """
    Convert the given student (dictionary) in an other dictionary that can be "jsonified"
    :param student:
    :return: the "jsonifiable" student
    """
    student['id'] = str(student.pop('_id'))
    if 'courses' in student:
        student['courses'] = list(map(str, student['courses']))
    return student


def add_course_to_student(db_client, student_dict, course_dict):
    """
    Add a course to a student. Only the id of the course is embedded in the student document for a lower replication.
    :param db_client: instance of MongoClient used to make requests to the data store
    :param student_dict: student to be updated
    :param course_dict: course to be added
    :return: the updated student, None if the student is already registered to the course
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to students collection
        students = db.students
        # Check if the student is already registered to the course
        if 'courses' in student_dict:
            student_courses = student_dict['courses']
            if course_dict['id'] in student_courses:
                return None
        # Add the course
        result = students.update_one({"username": student_dict['username']},
                                     {"$push": {"courses": ObjectId(course_dict['id'])}})
        if result.modified_count != 1:  # Something unexpected went wrong
            raise StudentsRepositoryException()
        updated_student = students.find_one({"username": student_dict['username']})
        return serialize_student(updated_student)
    except PyMongoError:
        raise StudentsRepositoryException()


def find_student_by_username(db_client, student_username):
    """
    Search in the data store for a student with the provided username
    :param db_client: instance of MongoClient used to make requests to the data store
    :param student_username: username of the student to be searched
    :return: the user having the given username if a matching one exists, None otherwise
    """
    try:
        # Access to course_management db
        db = db_client.course_management
        # Access to students collection
        students = db.students

        matching_student = students.find_one({'username': student_username})
        if matching_student is None:
            return None
        return serialize_student(matching_student)

    except PyMongoError:
        raise StudentsRepositoryException()


def add_student(db_client, student_dict):
    """
    Add the given student to the data store using the given db_client
    :param db_client: instance of MongoClient used to make requests to the data store
    :param student_dict: dictionary representing the student to be added to the data store
    :return: the added student, None if a conflict occurred
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to students collection
        students = db.students

        # Check if the student is in conflict with an existent one having the same username
        conflictual_student = students.find_one({'username': student_dict['username']})

        if conflictual_student is not None:
            return None

        # Make the insert
        insert_result = students.insert_one(student_dict)

        if insert_result.inserted_id is None:
            raise StudentsRepositoryException()

        return serialize_student(student_dict)

    except PyMongoError:
        raise StudentsRepositoryException()


def unsubscribe_from_course(db_client, student_dict, course_dict):
    """
    Remove the student from the given course. If some exam reservation exist for the student, these are removed too.
    :param db_client: instance of MongoClient used to make requests to the data store
    :param student_dict: dictionary representing the student to unsubscribe
    :param course_dict: dictionary representing the course to be removed from the student
    :return: the updated student
    """
    try:

        # Access to course_management db
        db = db_client.course_management
        # Access to students collection
        students = db.students
        # Access to exams collection
        exams = db.exams

        with db_client.start_session() as s:
            s.start_transaction()
            # remove the course from the student document
            students.update_one({"username": student_dict['username']},
                                {"$pull": {"courses": ObjectId(course_dict['id'])}})
            # remove the student from the exam documents
            exams.update_many({"course": course_dict['id']}, {"$pull": {"students": student_dict["username"]}})
            s.commit_transaction()

        updated_student = students.find_one({"username": student_dict['username']})
        return serialize_student(updated_student)

    except PyMongoError:
        raise StudentsRepositoryException()

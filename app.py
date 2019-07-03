import json

from flask import Flask, request, abort, make_response, jsonify
import logging
import os
import pymongo
from courses_repository import add_course, CoursesRepositoryException, find_course, find_course_by_id, \
    find_courses_by_ids, remove_course
from exam_repository import find_exam_by_course_id, ExamsRepositoryException, add_exam, find_exam_by_id, \
    add_student_to_exam
from request_parsing import trim, is_valid_year, is_valid_schedule, is_valid_time, is_valid_date
from sqshandler import push_on_queue, SqsHandlerException
from students_repository import add_student, StudentsRepositoryException, find_student_by_username, \
    add_course_to_student, unsubscribe_from_course

app = Flask(__name__)
# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# Instantiate MongoClient for the interaction with the Mongo data-store
client = pymongo.MongoClient(os.getenv('MONGO_URL', ''))


# client = pymongo.MongoClient()


@app.route('/')
def health_check():
    return '', 200


@app.route('/course_management/api/v1.0/exams/<string:exam_id>/students/<string:student_username>', methods=['PUT'])
def reserve_exam(exam_id, student_username):
    """
    This function exports the url for reserve an exam for a student
    :param exam_id: identifier of the exam that the student has to be added too
    :param student_username: identifier of the student that requires the reservation
    """
    try:
        exam = find_exam_by_id(client, exam_id)
        if exam is None:
            logger.error("Exam Not Found")
            abort(make_response(jsonify({'error': "Exam Not Found"}), 404))
        student = find_student_by_username(client, student_username)
        if student is None:
            logger.error("Student Not Found")
            abort(make_response(jsonify({'error': "Student Not Found"}), 404))
        # Only the students registered to the course are allowed to make the reservation
        if not exam['course'] in student['courses']:
            logger.error("Student not registered to the course")
            abort(make_response(jsonify({'error': "Not Registered To Course"}), 403))
        updated_exam = add_student_to_exam(client, exam, student)
        if updated_exam is None:
            abort(409)  # Conflict - The student has already been registered
        return jsonify(updated_exam), 200  # Ok
    except ExamsRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/exams/<string:course>', methods=['GET'])
def get_exam_by_course(course):
    """
    This function exports the url to find an exam by course id.
    The content of the request is url-encoded and contains the id of the course of the exams to find.
    :param course: id of the course of the exams to search
    """

    # Check format of the request, responding with HTTP Bad Request in case of failed validation.
    if trim(course) == "":
        abort(400)

    # Check if exams of the course matching with the given id course exist in the data store
    try:
        exams = find_exam_by_course_id(client, course)
        if exams is None:
            abort(404)  # Not found
        return jsonify(exams), 200  # Found
    except ExamsRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/exams', methods=['POST'])
def create_exam():
    """
        This function exports the url used to send a exam creation request.
        The content of the request is a json string representing the exam information.
        Course and call are used as a composite key
    """
    check_exam_creation_body(request)
    exam = {'course': request.json['course'],
            'call': request.json['call'],
            'date': request.json['date'],
            'startTime': request.json['startTime'],
            'expirationDate': request.json['expirationDate'],
            'room': request.json['room'],
            'students': []}

    try:
        added_exam = add_exam(client, exam)
        if added_exam is None:
            abort(409)  # Conflict
        return jsonify(added_exam), 201  # Created
    except ExamsRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/courses/<string:by>/<string:string>', methods=['GET'])
def get_course_by(by, string):
    """
    This function exports the endpoint to find a course by name or by teacher name.
    The content of the request is endpoint-encoded and contains the type of searching and the sequence to find.
    :param by: type of searching. Can be "name" or "teacher"
    :param string: sequence to search in the fields of the courses
    """

    # Check format of the request, responding with HTTP Bad Request in case of failed validation.
    if (by != "name" and by != "teacher") or not trim(string).isalnum:
        abort(400)

    # Check if courses matching with the given sequence exist in the data store
    try:
        courses = find_course(client, by, string)
        if courses is None:
            abort(404)  # Not found
        return jsonify(courses), 200  # Found
    except CoursesRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/courses', methods=['POST'])
def create_course():
    """
        This function exports the endpoint used to send a course creation request.
        The content of the request is a json string representing the course information.
        Name, Department, Teacher and Year are used as a composite key
    """
    check_course_creation_body(request)
    course = {'name': request.json['name'],
              'department': request.json['department'],
              'teacher': request.json['teacher'],
              'year': request.json['year'],
              'semester': request.json['semester'],
              'description': request.json['description'],
              'schedule': request.json['schedule']}

    try:
        added_course = add_course(client, course)
        if added_course is None:
            abort(409)  # Conflict
        return jsonify(added_course), 201  # Created
    except CoursesRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/courses/<string:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """
        This function exports the endpoint used to send a course deletion request.
    """
    try:
        course = find_course_by_id(client, course_id)
        if course is None:
            logger.error("Course Not Found")
            abort(make_response(jsonify({'error': "Course Not Found"}), 404))
        remove_course(client, course)
        return '', 200
    except CoursesRepositoryException:
        abort(500)


@app.route('/course_management/api/v1.0/students', methods=['POST'])
def create_student():
    """
        This function exports the endpoint used to send a student creation request.
        The content of the request is a JSON string representing the information about the student: username and name
        The username is unique inside the data store
    """
    check_student_creation_body(request)
    student = {'name': request.json['name'],
               'username': request.json['username']}
    try:
        added_student = add_student(client, student)
        if added_student is None:
            abort(409)
        return jsonify(added_student), 201  # Created
    except StudentsRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/students/<string:student_username>/courses/<string:course_id>', methods=['PUT'])
def register_student_to_course(student_username, course_id):
    """
    This function exports the endpoint used to add the course with the given id to the student with the provided username.
    """
    try:
        student = find_student_by_username(client, student_username)
        if student is None:
            logger.error("Student Not Found")
            abort(make_response(jsonify({'error': "Student Not Found"}), 404))
        course = find_course_by_id(client, course_id)
        if course is None:
            logger.error("Course Not Found")
            abort(make_response(jsonify({'error': "Course Not Found"}), 404))
        updated_student = add_course_to_student(client, student, course)
        if updated_student is None:
            abort(409)  # Conflict - The course has already been added
        return jsonify(updated_student), 200  # Ok
    except StudentsRepositoryException:
        abort(500)  # Internal Server Error


@app.route('/course_management/api/v1.0/courses/students/<string:student_username>', methods=['GET'])
def get_student_courses(student_username):
    """
    This function exports the endpoint used to find the courses which a student is subscribed to.
    :param student_username: username of the student
    """
    try:
        student = find_student_by_username(client, student_username)
        if student is None:
            logger.error("Student Not Found")
            abort(make_response(jsonify({'error': "Student Not Found"}), 404))
        if 'courses' not in student:
            logger.error("Courses Not Found")
            abort(make_response(jsonify({'error': "Courses Not Found"}), 404))
        elif len(student['courses']) == 0:
            logger.error("Courses Not Found")
            abort(make_response(jsonify({'error': "Courses Not Found"}), 404))
        else:
            courses = find_courses_by_ids(client, student['courses'])
            return jsonify(courses), 200  # Ok

    except StudentsRepositoryException or CoursesRepositoryException:
        abort(500)


@app.route('/course_management/api/v1.0/students/<string:student_username>/courses/<string:course_id>',
           methods=['DELETE'])
def delete_student_from_course(student_username, course_id):
    """
    This function exports the endpoint used to delete the student's subscription to a course.
    :param student_username: username of the subscribed student
    :param course_id: identifier of the course to unsubscribe to
    """
    try:
        student = find_student_by_username(client, student_username)
        if student is None:
            logger.error("Student Not Found")
            abort(make_response(jsonify({'error': "Student Not Found"}), 404))
        course = find_course_by_id(client, course_id)
        if course is None:
            logger.error("Course Not Found")
            abort(make_response(jsonify({'error': "Course Not Found"}), 404))
        updated_student = unsubscribe_from_course(client, student, course)
        return jsonify(updated_student), 200

    except StudentsRepositoryException or CoursesRepositoryException:
        abort(500)


@app.route('/course_management/api/v1.0/courses/<string:course_id>/notification', methods=['POST'])
def push_course_notification(course_id):
    """
        This function exports the endpoint used to publish a notification about a course
        :param course_id: identifier of the course to which the notification is associated
        """
    if not request.json:
        abort(400)  # Bad Request
    if 'message' not in request.json:
        abort(400)  # Bad Request
    course = find_course_by_id(client, course_id)
    if course is None:
        logger.error("Course Not Found")
        abort(make_response(jsonify({'error': 'Course Not Found'}), 404))
    # the notification is published on a message queue that will be consumed asynchronously by
    # notification management microservice

    notification_message = {'name': course['name'],
                            'department': course['department'],
                            'year': course['year'],
                            'message': request.json['message']}
    try:
        push_on_queue(json.dumps(notification_message), os.getenv('QUEUE_NAME', 'NotificationQueue.fifo'))
        return '', 200  # Ok
    except SqsHandlerException:
        abort(500)  # Internal Server Error


def check_exam_creation_body(body_request):
    """
    Check the correctness of the given exam information
    """
    if not body_request.json:
        abort(400)  # Bad Request
    if 'course' not in body_request.json:
        abort(400)
    if 'call' not in body_request.json or not body_request.json['call'] in range(1, 7):
        abort(400)
    if 'room' not in body_request.json or not body_request.json['room'].isalnum():
        abort(400)
    if 'startTime' not in body_request.json or not is_valid_time(body_request.json['startTime']):
        abort(400)
    if 'date' not in body_request.json or not is_valid_date(body_request.json['date']):
        abort(400)
    if 'expirationDate' not in body_request.json or not is_valid_date(body_request.json['expirationDate']):
        abort(400)


def check_student_creation_body(body_request):
    """
    Check the correctness of the given student information
    """
    if not body_request.json:
        abort(400)
    if 'name' not in body_request.json or not trim(body_request.json['name']).isalnum():
        abort(400)
    # The username must be not-empty and without blank spaces
    if 'username' not in body_request.json or body_request.json['username'] == "" or trim(body_request.json['username']) \
            != body_request.json['username']:
        abort(400)


def check_course_creation_body(body_request):
    """
    Check the correctness of the given course information
    """
    if not body_request.json:
        abort(400)  # Bad Request
    if 'name' not in body_request.json or not trim(body_request.json['name']).isalnum():
        abort(400)
    if 'department' not in body_request.json or not trim(body_request.json['department']).isalpha():
        abort(400)
    if 'teacher' not in body_request.json or not trim(body_request.json['teacher']).isalpha():
        abort(400)
    if 'year' not in body_request.json or not is_valid_year(body_request.json['year']):
        abort(400)
    if 'semester' not in body_request.json or not body_request.json['semester'] in [1, 2]:
        abort(400)
    if 'description' not in body_request.json:
        abort(400)
    if 'schedule' not in body_request.json or not is_valid_schedule(body_request.json['schedule']):
        abort(400)


@app.errorhandler(404)
def not_found(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(409)
def conflict(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Conflict - The resource already exists'}), 409)


@app.errorhandler(500)
def internal_server_error(error):
    logger.error(error)
    return make_response(jsonify({'error': 'Internal Server Error'}), 500)


if __name__ == '__main__':
    host = os.getenv('LISTEN_IP', '0.0.0.0')
    port = int(os.getenv('LISTEN_PORT', '5000'))
    app.run(host=host, port=port, threaded=True)

from flask import Blueprint, request, jsonify
from extensions import db
from .models import Course, Student

courses_bp = Blueprint(
    "courses",
    __name__,
    url_prefix="/api/courses"
)


@courses_bp.route("/", methods=["GET"])
def get_courses():

    courses = Course.query.all()

    return jsonify(
        [course.to_dict() for course in courses]
    )


@courses_bp.route("/", methods=["POST"])
def create_course():

    data = request.get_json()

    course = Course(
        name=data["name"],
        code=data["code"],
        credits=data["credits"],
        department_id=data["department_id"]
    )

    db.session.add(course)
    db.session.commit()

    return jsonify(course.to_dict()), 201


@courses_bp.route("/<int:id>", methods=["GET"])
def get_course(id):

    course = Course.query.get_or_404(id)

    return jsonify(course.to_dict())


@courses_bp.route("/<int:id>", methods=["PUT"])
def update_course(id):

    course = Course.query.get_or_404(id)

    data = request.get_json()

    course.name = data["name"]
    course.code = data["code"]
    course.credits = data["credits"]
    course.department_id = data["department_id"]

    db.session.commit()

    return jsonify(course.to_dict())


@courses_bp.route("/<int:id>", methods=["DELETE"])
def delete_course(id):

    course = Course.query.get_or_404(id)

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "message": "Course deleted"
    })


@courses_bp.route("/<int:id>/students/", methods=["GET"])
def course_students(id):

    course = Course.query.get_or_404(id)

    students = Student.query.join(Student.enrollments)\
        .filter_by(course_id=course.id).all()

    return jsonify(
        [student.to_dict() for student in students]
    )
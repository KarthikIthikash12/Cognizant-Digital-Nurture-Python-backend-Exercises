from extensions import db


class Department(db.Model):

    __tablename__ = "department"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    head_of_dept = db.Column(db.String(100))
    budget = db.Column(db.Float)

    courses = db.relationship(
        "Course",
        back_populates="department",
        cascade="all, delete"
    )

    students = db.relationship(
        "Student",
        back_populates="department",
        cascade="all, delete"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "head_of_dept": self.head_of_dept,
            "budget": self.budget
        }


class Course(db.Model):

    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    credits = db.Column(db.Integer)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id")
    )

    department = db.relationship(
        "Department",
        back_populates="courses"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="course"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "credits": self.credits,
            "department_id": self.department_id
        }


class Student(db.Model):

    __tablename__ = "student"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(100), unique=True)
    enrollment_year = db.Column(db.Integer)

    department_id = db.Column(
        db.Integer,
        db.ForeignKey("department.id")
    )

    department = db.relationship(
        "Department",
        back_populates="students"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "department_id": self.department_id,
            "enrollment_year": self.enrollment_year
        }


class Enrollment(db.Model):

    __tablename__ = "enrollment"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("student.id")
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("course.id")
    )

    enrollment_date = db.Column(db.Date)
    grade = db.Column(db.String(10))

    student = db.relationship(
        "Student",
        back_populates="enrollments"
    )

    course = db.relationship(
        "Course",
        back_populates="enrollments"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "course_id": self.course_id,
            "enrollment_date": str(self.enrollment_date) if self.enrollment_date else None,
            "grade": self.grade
        }
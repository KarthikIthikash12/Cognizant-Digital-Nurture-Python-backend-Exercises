from flask import Flask, jsonify

app = Flask(__name__)

courses = [
    {"id": 1, "name": "Python"},
    {"id": 2, "name": "Java"},
    {"id": 3, "name": "Machine Learning"}
]


@app.route("/api/courses/<int:id>")
def get_course(id):

    for course in courses:

        if course["id"] == id:
            return jsonify(course)

    return jsonify({"message": "Course not found"}), 404


if __name__ == "__main__":
    app.run(port=5001, debug=True)
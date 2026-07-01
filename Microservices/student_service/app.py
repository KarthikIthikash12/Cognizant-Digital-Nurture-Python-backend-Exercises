from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

students = [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Alice"}
]


@app.route("/api/students/<int:id>/enroll", methods=["POST"])
def enroll(id):

    data = request.get_json()

    course_id = data["course_id"]

    try:

        response = requests.get(
            f"http://127.0.0.1:5001/api/courses/{course_id}"
        )

    except requests.exceptions.ConnectionError:

        return jsonify({
            "message": "Course Service unavailable"
        }), 503

    if response.status_code != 200:

        return jsonify({
            "message": "Course not found"
        }), 404

    return jsonify({
        "message": f"Student {id} enrolled successfully"
    })


if __name__ == "__main__":
    app.run(port=5002, debug=True)
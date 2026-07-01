from flask import Flask, request
import requests

app = Flask(__name__)


@app.route("/api/courses/<path:path>", methods=["GET"])
def course_proxy(path):

    response = requests.get(
        f"http://127.0.0.1:5001/api/courses/{path}"
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


@app.route("/api/students/<path:path>", methods=["POST"])
def student_proxy(path):

    response = requests.request(
        method=request.method,
        url=f"http://127.0.0.1:5002/api/students/{path}",
        json=request.get_json()
    )

    return (
        response.content,
        response.status_code,
        response.headers.items()
    )


if __name__ == "__main__":
    app.run(port=5000, debug=True)
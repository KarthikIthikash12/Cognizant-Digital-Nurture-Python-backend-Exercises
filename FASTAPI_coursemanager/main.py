from datetime import datetime, timedelta

from jose import JWTError, jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from fastapi import Depends

from fastapi.middleware.cors import CORSMiddleware
from schemas import UserRegister, UserResponse
from security import get_password_hash
from fastapi import (
    FastAPI,
    HTTPException,
    status,
    BackgroundTasks,
    Response,
    Request
)

from fastapi.responses import JSONResponse

from schemas import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    StudentResponse
)

app = FastAPI(
    title="Course Management API",
    description="API for managing courses, students and enrollments.",
    version="1.0.0",
    contact={
        "name": "Karthik",
        "email": "karthik@example.com"
    }
)
SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 Authorization Code Flow:
# Redirects users to a login provider (Google, GitHub etc.)
# which returns an authorization code before issuing tokens.
#
# This project instead uses a simple JWT login:
# user sends email/password directly,
# server verifies credentials,
# server returns JWT.
# API Versioning
# URL Versioning: /api/v1/courses/
# Header Versioning:
# Accept: application/vnd.api+json;version=1

courses = []
users = []

students = [
    {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@gmail.com",
        "course_id": 1
    },
    {
        "id": 2,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@gmail.com",
        "course_id": 1
    }
]

from security import verify_password


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired token"
    )

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    for user in users:

        if user["email"] == email:
            return user

    raise credentials_exception
def send_confirmation_email(student_email: str):
    print(f"Sending confirmation to {student_email}")


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):

    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "ERROR",
                "message": str(exc.detail),
                "field": None
            }
        }
    )


@app.get("/")
async def root():
    return {"message": "API running"}
@app.post(
    "/api/v1/auth/login/",
    tags=["Authentication"]
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    for user in users:

        if (
            user["email"] == form_data.username
            and verify_password(
                form_data.password,
                user["hashed_password"]
            )
        ):

            token = create_access_token(
                {
                    "sub": user["email"]
                }
            )

            return {
                "access_token": token,
                "token_type": "bearer"
            }

    raise HTTPException(
        status_code=401,
        detail="Invalid credentials"
    )

@app.post(
    "/api/v1/courses/",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Courses"],
    summary="Create Course",
    response_description="Course created successfully"
)
async def create_course(
    course: CourseCreate,
    response: Response,
    current_user=Depends(get_current_user)
):

    new_course = {
        "id": len(courses) + 1,
        **course.model_dump()
    }

    courses.append(new_course)

    response.headers["Location"] = f"/api/v1/courses/{new_course['id']}/"

    return new_course


@app.get(
    "/api/v1/courses/",
    tags=["Courses"],
    summary="Get All Courses"
)
async def get_courses(
    page: int = 1,
    page_size: int = 2,
    search: str = ""
):

    filtered = [
        c for c in courses
        if search.lower() in c["name"].lower()
        or search.lower() in c["code"].lower()
    ]

    total = len(filtered)

    start = (page - 1) * page_size
    end = start + page_size

    results = filtered[start:end]

    next_page = None
    previous_page = None

    if end < total:
        next_page = f"/api/v1/courses/?page={page+1}&page_size={page_size}"

    if page > 1:
        previous_page = f"/api/v1/courses/?page={page-1}&page_size={page_size}"

    return {
        "count": total,
        "next": next_page,
        "previous": previous_page,
        "results": results
    }


@app.get(
    "/api/v1/courses/{id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Get Course"
)
async def get_course(id: int):

    for course in courses:
        if course["id"] == id:
            return course

    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Course with id {id} does not exist",
                "field": None
            }
        }
    )


@app.put(
    "/api/v1/courses/{id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Update Course"
)
async def update_course(
    id: int,
    course: CourseCreate
):

    for c in courses:

        if c["id"] == id:

            c.update(course.model_dump())

            return c

    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Course with id {id} does not exist",
                "field": None
            }
        }
    )


@app.patch(
    "/api/v1/courses/{id}",
    response_model=CourseResponse,
    tags=["Courses"],
    summary="Partially Update Course"
)
async def patch_course(
    id: int,
    course: CourseUpdate
):

    for c in courses:

        if c["id"] == id:

            updates = course.model_dump(exclude_unset=True)

            c.update(updates)

            return c

    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Course with id {id} does not exist",
                "field": None
            }
        }
    )
@app.post(
    "/api/v1/auth/register/",
    response_model=UserResponse,
    status_code=201,
    tags=["Authentication"]
)
async def register_user(user: UserRegister):

    for u in users:

        if u["email"] == user.email:

            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

    hashed = get_password_hash(user.password)

    new_user = {
        "id": len(users) + 1,
        "email": user.email,
        "hashed_password": hashed,
        "is_active": True
    }

    users.append(new_user)

    return {
        "id": new_user["id"],
        "email": new_user["email"],
        "is_active": new_user["is_active"]
    }

@app.delete(
    "/api/v1/courses/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Courses"],
    summary="Delete Course"
)
async def delete_course(
    id:int,
    current_user=Depends(get_current_user)
):

    for i, course in enumerate(courses):

        if course["id"] == id:

            courses.pop(i)

            return

    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Course with id {id} does not exist",
                "field": None
            }
        }
    )


@app.get(
    "/api/v1/courses/{id}/students/",
    response_model=list[StudentResponse],
    tags=["Courses"],
    summary="Get Students Enrolled in Course"
)
async def get_students(id: int):

    return [
        s for s in students
        if s["course_id"] == id
    ]


@app.post(
    "/api/enrollments/",
    status_code=status.HTTP_201_CREATED,
    tags=["Enrollments"],
    summary="Create Enrollment",
    response_description="Enrollment created successfully"
)
async def create_enrollment(
    background_tasks: BackgroundTasks
):

    student_email = "john@gmail.com"

    background_tasks.add_task(
        send_confirmation_email,
        student_email
    )

    return {
        "message": "Enrollment created successfully"
    }
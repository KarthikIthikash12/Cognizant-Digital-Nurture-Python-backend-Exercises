
# TASK 1: Understanding the Request-Response Cycle in Django




# STEP 1: Journey of a GET /api/courses/ Request Through Django


# 1. BROWSER
#    The user's browser sends an HTTP GET request to: GET /api/courses/
#    This travels over the internet to the server running Django.

# 2. WEB SERVER (e.g., Gunicorn / Nginx)
#    The web server receives the raw HTTP request and forwards it to Django
#    via WSGI (or ASGI). This is the entry point into the Django application.

# 3. MIDDLEWARE (Request Phase) ← ENTERS HERE FIRST
#    Before the request reaches the URL router, it passes through the
#    MIDDLEWARE stack (top to bottom). Each middleware can:
#      - Inspect or modify the request
#      - Short-circuit the cycle and return a response early
#    Example: SecurityMiddleware checks HTTPS, AuthenticationMiddleware
#    attaches the user object to `request.user`.

# 4. URL ROUTER (urls.py)
#    Django's URL dispatcher (URLconf) reads the request path: /api/courses/
#    It scans urlpatterns list (defined in urls.py) using regex or path()
#    converters to find a matching pattern.
#
#    Example:
#      urlpatterns = [
#          path('api/courses/', views.CourseListView.as_view()),
#      ]
#
#    If no match is found → Django returns a 404 response.
#    If matched → the associated View is called.

# 5. VIEW (views.py)
#    The matched view function or class-based view is invoked with the
#    request object (and any URL parameters).
#    The View acts as the CONTROLLER — it contains the business logic:
#      - Reads query parameters or request data
#      - Calls the Model to fetch/save data
#      - Decides what response to return
#
#    Example:
#      class CourseListView(APIView):
#          def get(self, request):
#              courses = Course.objects.all()   ← calls the Model
#              serializer = CourseSerializer(courses, many=True)
#              return Response(serializer.data)

# 6. MODEL (models.py) + DATABASE
#    The View calls the Model layer to interact with the database.
#    Django's ORM translates Python calls into SQL queries.
#
#    Example ORM call:       Course.objects.all()
#    Translated SQL:         SELECT * FROM courses_course;
#
#    The database executes the query and returns rows.
#    Django maps those rows back into Python Model instances.

# 7. TEMPLATE (optional for APIs, used in HTML responses)
#    For traditional HTML views, the View passes data to a Template.
#    The Template engine renders the HTML with the context data.
#    For REST APIs (e.g., Django REST Framework), a serializer is used
#    instead of a template, and JSON is returned directly.

# 8. RESPONSE OBJECT
#    The View returns an HttpResponse (or DRF Response) object containing:
#      - Status code (e.g., 200 OK)
#      - Headers (Content-Type, etc.)
#      - Body (JSON data or HTML)

# 9. MIDDLEWARE (Response Phase)
#    The response travels back UP through the middleware stack (bottom to top).
#    Each middleware can inspect or modify the response before it leaves Django.
#    Example: GZipMiddleware compresses the response body here.

# 10. BROWSER RECEIVES RESPONSE
#     The web server sends the HTTP response back to the browser.
#     The browser renders the page or the JavaScript processes the JSON.

#
# FULL CYCLE SUMMARY:
#
#  Browser
#    │
#    ▼
#  Web Server (Nginx/Gunicorn)
#    │
#    ▼
#  Middleware Stack (request phase: top → bottom)
#    │
#    ▼
#  URL Router (urls.py)  →  404 if no match
#    │
#    ▼
#  View (views.py)  ←→  Model (models.py)  ←→  Database
#    │
#    ▼
#  Template (templates/) or Serializer (for APIs)
#    │
#    ▼
#  HttpResponse object
#    │
#    ▼
#  Middleware Stack (response phase: bottom → top)
#    │
#    ▼
#  Browser receives final response
#



# STEP 2: Where Middleware Sits + Two Built-in Django Middleware Classes


# WHERE MIDDLEWARE SITS:
#   Middleware wraps around the entire request-response cycle.
#   It sits BETWEEN the web server and the URL router (on the way in),
#   and BETWEEN the view response and the web server (on the way out).
#   Think of it as a series of layers (like an onion) around your core app.
#
#   Django processes middleware in ORDER (top to bottom for requests,
#   bottom to top for responses), as listed in settings.py:
#
#   MIDDLEWARE = [
#       'django.middleware.security.SecurityMiddleware',       # 1st in, last out
#       'django.contrib.sessions.middleware.SessionMiddleware',
#       'django.middleware.common.CommonMiddleware',
#       'django.middleware.csrf.CsrfViewMiddleware',
#       'django.contrib.auth.middleware.AuthenticationMiddleware',
#       ...
#   ]

# ── BUILT-IN MIDDLEWARE #1: SecurityMiddleware ────────────────────────────────
#   Class:   django.middleware.security.SecurityMiddleware
#   Purpose: Enforces various HTTP security policies on every request/response.
#   What it does:
#     - Redirects HTTP requests to HTTPS (if SECURE_SSL_REDIRECT = True)
#     - Sets the HTTP Strict-Transport-Security (HSTS) header to tell
#       browsers to always use HTTPS for this domain
#     - Sets X-Content-Type-Options: nosniff to prevent MIME-type sniffing
#     - Sets X-XSS-Protection header to enable browser XSS filtering
#     - Removes the Referrer-Policy header leaking sensitive URL info
#   When it runs: On every request (inbound) and every response (outbound).

# ── BUILT-IN MIDDLEWARE #2: AuthenticationMiddleware ─────────────────────────
#   Class:   django.contrib.auth.middleware.AuthenticationMiddleware
#   Purpose: Associates the currently logged-in user with each incoming request.
#   What it does:
#     - Reads the session cookie from the request
#     - Looks up the corresponding user in the database (via SessionMiddleware)
#     - Attaches the User object to request.user
#     - If no valid session exists, request.user is set to AnonymousUser
#   Why it matters: Every view can then access request.user to check
#     authentication status and permissions without repeating login logic.
#   When it runs: On every inbound request, before the view is called.


# STEP 3: WSGI vs ASGI


# ── WHAT IS WSGI? 
#   WSGI = Web Server Gateway Interface
#   Defined in PEP 3333. It is the traditional Python standard for web apps.
#
#   Key characteristics:
#     - SYNCHRONOUS: handles one request at a time per worker process/thread
#     - Each request blocks until a response is returned
#     - Simple and well-supported (Gunicorn, uWSGI are popular WSGI servers)
#     - Cannot handle long-lived connections like WebSockets natively
#
#   Django uses WSGI by default.
#   Entry point file: myproject/wsgi.py
#   Called via:       gunicorn myproject.wsgi:application

# ── WHAT IS ASGI? 
#   ASGI = Asynchronous Server Gateway Interface
#   The modern successor to WSGI, designed for async Python (PEP 492+).
#
#   Key characteristics:
#     - ASYNCHRONOUS: can handle many concurrent connections with a single
#       process using Python's async/await (asyncio)
#     - Supports long-lived connections: WebSockets, Server-Sent Events (SSE),
#       HTTP/2, and background tasks
#     - Handled by servers like Uvicorn, Daphne, or Hypercorn
#
#   Entry point file: myproject/asgi.py
#   Called via:       uvicorn myproject.asgi:application

# ── WHICH DOES DJANGO USE BY DEFAULT? ────────────────────────────────────────
#   Django uses WSGI by default.
#   When you run `django-admin startproject`, both wsgi.py and asgi.py are
#   created, but the default runserver and deployment configs point to WSGI.

# ── WHEN WOULD YOU SWITCH TO ASGI? ──────────────────────────────────────────
#   Switch to ASGI when your application needs:
#     1. WebSockets — e.g., real-time chat, live notifications, dashboards
#     2. Server-Sent Events (SSE) — e.g., live data feeds, progress bars
#     3. High concurrency with I/O-bound tasks — e.g., calling external APIs
#        from many simultaneous users without spawning many OS threads
#     4. Async views — when using `async def` views in Django 3.1+
#     5. Django Channels — the library for WebSocket support requires ASGI
#
#   Example scenario: Building a live auction site where prices update in
#   real time for all connected browsers → use ASGI + Django Channels.



# STEP 4: MVC Pattern and Django's MVT


# ── THE MVC PATTERN (Traditional) ────────────────────────────────────────────
#   MVC = Model – View – Controller
#   A classic architectural pattern used by many frameworks (Rails, Laravel, etc.)
#
#   MODEL:
#     - Represents the data and business logic
#     - Communicates with the database
#     - Knows nothing about how data is displayed
#
#   VIEW:
#     - The presentation layer — what the user sees
#     - Renders data (usually as HTML) passed from the Controller
#     - Contains no business logic
#
#   CONTROLLER:
#     - The middleman / traffic director
#     - Receives user input (HTTP requests)
#     - Calls the Model to get data
#     - Passes data to the View for rendering
#     - Returns the final response

# ── DJANGO'S MVT PATTERN 
#   Django calls its pattern MVT = Model – View – Template
#   The letters are similar but the roles shift slightly from classic MVC.
#
#   MODEL  (models.py)
#     → Same as MVC's Model.
#     → Defines data structure, interacts with the database via Django ORM.
#     → Example: class Course(models.Model): title = models.CharField(...)
#
#   VIEW   (views.py)
#     → Corresponds to MVC's CONTROLLER (NOT MVC's View — confusing but true!)
#     → Contains business logic: receives the request, queries the Model,
#       selects a Template, and returns an HttpResponse.
#     → Example: def course_list(request): courses = Course.objects.all() ...
#
#   TEMPLATE  (templates/*.html)
#     → Corresponds to MVC's VIEW.
#     → The presentation layer: renders HTML using Django template language.
#     → Receives context data from the View and displays it.
#     → Example: {% for course in courses %} <li>{{ course.title }}</li> {% endfor %}
#
#   Django itself acts as the CONTROLLER in the traditional MVC sense —
#   specifically the URL dispatcher (urls.py) routes requests to the right View.

# ── SIDE-BY-SIDE MAPPING 
#
#   MVC Component    │  Django MVT Equivalent  │  Django File
#   ─────────────────┼─────────────────────────┼───────────────
#   Model            │  Model                  │  models.py
#   Controller       │  View                   │  views.py
#   View             │  Template               │  templates/*.html
#   (Framework core) │  URL Dispatcher         │  urls.py
#


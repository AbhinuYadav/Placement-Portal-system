# backend/app.py
from flask import Flask, jsonify
from flask_security import Security
from flask_restful import Api
from flask_cors import CORS
from datetime import datetime
from flask_security import utils  # for password hashing
from extension import cache, init_extension

from controllers.database import db
from controllers.config import Config
from controllers.user_datastore import user_datastore
from controllers.models import Role

from mail import mail, init_mail
from celery_app import celery  # import the configured celery instance

import socket
import redis
import os

# Force IPv4 for socket connections
socket.getaddrinfo('127.0.0.1', 6379)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    security = Security(app, user_datastore)

    api = Api(app, prefix='/api')

    # Initialize mail
    init_mail(app)
    init_extension(app)

    # Create exports folder
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)

    # --- Celery configuration with Flask app context ---
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    with app.app_context():
        db.create_all()

        # Create roles
        admin_role = user_datastore.find_or_create_role(
            name='admin',
            description='Institute Placement Cell Administrator'
        )
        company_role = user_datastore.find_or_create_role(
            name='company',
            description='Registered Company'
        )
        student_role = user_datastore.find_or_create_role(
            name='student',
            description='Student Seeking Placement'
        )

        # Create admin user if not exists
        if not user_datastore.find_user(email='admin@placement.edu'):
            hashed_password = utils.hash_password("Admin@123")
            admin = user_datastore.create_user(
                email="admin@placement.edu",
                password=hashed_password,
                roles=[admin_role]
            )
            print("Admin user created: admin@placement.edu / Admin@123")
            print(f"Password hash: {hashed_password[:50]}...")

        db.session.commit()

    return app, api


app, api = create_app()

# --- Test Redis connection ---
try:
    r = redis.Redis(host='127.0.0.1', port=6379, db=1, socket_connect_timeout=5)
    r.ping()
    print(" Redis is reachable")
except Exception as e:
    print(f" Redis not reachable: {e}")
    
# --- Test Celery connection ---
print("\n" + "="*50)
print("CELERY CONNECTION TEST")
print("="*50)
try:
    conn = celery.connection()
    conn.connect()
    print(" Celery can connect to Redis!")
    conn.release()
except Exception as e:
    print(f" Celery cannot connect: {e}")
print("="*50 + "\n")

# Debug: Print beat schedule to verify
print("\n=== BEAT SCHEDULE FROM CELERY ===")
beat_schedule = celery.conf.beat_schedule
if beat_schedule:
    for name, config in beat_schedule.items():
        print(f" {name}: {config['task']} at {config['schedule']}")
else:
    print(" No beat schedule found!")
print("="*50 + "\n")

# ===== CRITICAL FIX: Import tasks AFTER Celery is configured =====
import tasks
# =================================================================

# Configure CORS
CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
])

# -------------------- SIMPLE CELERY TEST ROUTE --------------------
@celery.task
def simple_test_task():
    print(" Simple test task executed!")
    return "OK"

@app.route('/test-celery-simple', methods=['GET'])
def test_celery_simple():
    try:
        task = simple_test_task.delay()
        return jsonify({'success': True, 'task_id': task.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ----------------------------------------------------------------

# Root endpoint
@app.route('/')
def index():
    return {
        'name': 'Placement Portal API',
        'version': '1.0',
        'status': 'running',
        'auth_method': 'Flask-Security-Too (pbkdf2_sha512)',
        'endpoints': {
            'auth': '/api/login, /api/register, /api/logout, /api/check-email, /api/profile, /api/change-password',
            'test': '/api/test/student, /api/test/company, /api/test/admin, /api/test/any'
        }
    }, 200

# Health check
@app.route('/health', methods=['GET'])
def health():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }, 200

# Import and register authentication APIs
from controllers.authentication_apis import (
    LoginAPI, LogoutAPI, RegisterAPI, CheckEmailAPI,
    ProfileAPI, ChangePasswordAPI,
    TestStudentAPI, TestCompanyAPI, TestAdminAPI, TestAnyAPI
)

api.add_resource(LoginAPI, '/login')
api.add_resource(LogoutAPI, '/logout')
api.add_resource(RegisterAPI, '/register')
api.add_resource(CheckEmailAPI, '/check-email')
api.add_resource(ProfileAPI, '/profile')
api.add_resource(ChangePasswordAPI, '/change-password')
api.add_resource(TestStudentAPI, '/test/student')
api.add_resource(TestCompanyAPI, '/test/company')
api.add_resource(TestAdminAPI, '/test/admin')
api.add_resource(TestAnyAPI, '/test/any')

# Import CRUD APIs
from controllers.crud_apis import (
    AdminDashboardAPI,
    AdminCompanyListAPI, AdminCompanyDetailAPI,
    AdminCompanyApproveAPI, AdminCompanyRejectAPI,
    AdminCompanyBlacklistAPI, AdminCompanyActivateAPI,
    AdminDriveListAPI, AdminDriveDetailAPI,
    AdminDriveApproveAPI, AdminDriveRejectAPI, AdminDriveCloseAPI,
    AdminStudentListAPI, AdminStudentDetailAPI,
    AdminStudentBlacklistAPI, AdminStudentActivateAPI,
    AdminSearchAPI, AdminApplicationsAPI, AdminGenerateMonthlyReportAPI,
    AdminTaskStatusAPI,

    StudentProfileAPI,
    StudentDriveListAPI, StudentDriveDetailAPI, StudentApplyAPI,
    StudentApplicationListAPI, StudentApplicationDetailAPI,
    StudentDashboardAPI, StudentHistoryAPI, StudentDeleteApplicationAPI,
    StudentExportApplicationsAPI,

    CompanyProfileAPI,
    CompanyDriveCreateAPI,
    CompanyDriveListAPI,
    CompanyDriveDetailAPI,
    CompanyApplicationListAPI,
    CompanyApplicationShortlistAPI,
    CompanyApplicationSelectAPI,
    CompanyApplicationRejectAPI,
    CompanyInterviewScheduleAPI,
    CompanyDashboardAPI,
    CompanyApplicationsAPI,
    CompanyApplicationDetailAPI
)

# -------------------- REGISTER ADMIN APIS --------------------
api.add_resource(AdminDashboardAPI, '/admin/dashboard')
api.add_resource(AdminApplicationsAPI, '/admin/applications')
api.add_resource(AdminCompanyListAPI, '/admin/companies')
api.add_resource(AdminCompanyDetailAPI, '/admin/companies/<int:company_id>')
api.add_resource(AdminCompanyApproveAPI, '/admin/companies/<int:company_id>/approve')
api.add_resource(AdminCompanyRejectAPI, '/admin/companies/<int:company_id>/reject')
api.add_resource(AdminCompanyBlacklistAPI, '/admin/companies/<int:company_id>/blacklist')
api.add_resource(AdminCompanyActivateAPI, '/admin/companies/<int:company_id>/activate')
api.add_resource(AdminDriveListAPI, '/admin/drives')
api.add_resource(AdminDriveDetailAPI, '/admin/drives/<int:drive_id>')
api.add_resource(AdminDriveApproveAPI, '/admin/drives/<int:drive_id>/approve')
api.add_resource(AdminDriveRejectAPI, '/admin/drives/<int:drive_id>/reject')
api.add_resource(AdminDriveCloseAPI, '/admin/drives/<int:drive_id>/close')
api.add_resource(AdminStudentListAPI, '/admin/students')
api.add_resource(AdminStudentDetailAPI, '/admin/students/<int:student_id>')
api.add_resource(AdminStudentBlacklistAPI, '/admin/students/<int:student_id>/blacklist')
api.add_resource(AdminStudentActivateAPI, '/admin/students/<int:student_id>/activate')
api.add_resource(AdminSearchAPI, '/admin/search')
api.add_resource(AdminGenerateMonthlyReportAPI, '/admin/reports/monthly')
api.add_resource(AdminTaskStatusAPI, '/admin/tasks/<string:task_id>')

# -------------------- REGISTER STUDENT APIS --------------------
api.add_resource(StudentProfileAPI, '/student/profile')
api.add_resource(StudentDashboardAPI, '/student/dashboard')
api.add_resource(StudentDriveListAPI, '/student/drives')
api.add_resource(StudentDriveDetailAPI, '/student/drives/<int:drive_id>')
api.add_resource(StudentApplyAPI, '/student/drives/<int:drive_id>/apply')
api.add_resource(StudentApplicationListAPI, '/student/applications')
api.add_resource(StudentApplicationDetailAPI, '/student/applications/<int:application_id>')
api.add_resource(StudentHistoryAPI, '/student/history')
api.add_resource(StudentDeleteApplicationAPI, '/student/applications/<int:application_id>')
api.add_resource(StudentExportApplicationsAPI, '/student/export/applications')

# -------------------- REGISTER COMPANY APIS --------------------
api.add_resource(CompanyProfileAPI, '/company/profile')
api.add_resource(CompanyDashboardAPI, '/company/dashboard')
api.add_resource(CompanyDriveCreateAPI, '/company/drives')
api.add_resource(CompanyDriveListAPI, '/company/drives')
api.add_resource(CompanyDriveDetailAPI, '/company/drives/<int:drive_id>')
api.add_resource(CompanyApplicationListAPI, '/company/drives/<int:drive_id>/applications')
api.add_resource(CompanyApplicationShortlistAPI, '/company/applications/<int:application_id>/shortlist')
api.add_resource(CompanyApplicationSelectAPI, '/company/applications/<int:application_id>/select')
api.add_resource(CompanyApplicationRejectAPI, '/company/applications/<int:application_id>/reject')
api.add_resource(CompanyInterviewScheduleAPI, '/company/applications/<int:application_id>/schedule-interview')
api.add_resource(CompanyApplicationsAPI, '/company/applications')
api.add_resource(CompanyApplicationDetailAPI, '/company/applications/<int:application_id>')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'message': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {'success': False, 'message': 'Internal server error'}, 500

if __name__ == "__main__":
    app.run(debug=True)
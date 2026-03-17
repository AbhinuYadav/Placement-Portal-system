''' # backend/controllers/authentication_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, auth_token_required, roles_required, roles_accepted, login_user, logout_user, current_user
from datetime import datetime

from controllers.user_datastore import user_datastore
from controllers.database import db
from controllers.models import Student, Company, Role

import re

# Helper functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


class CheckEmailAPI(Resource):
    """Check if email is available for registration"""
    def post(self):
        credentials = request.get_json()

        if not credentials:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        
        email = credentials.get('email')

        if not email:
            return make_response(jsonify({'message': 'Email is required.'}), 400)
        
        user = user_datastore.find_user(email=email)
        
        return make_response(jsonify({'available': user is None}), 200)


class RegisterAPI(Resource):
    """Register a new user (student or company)"""
    def post(self):
        data = request.get_json()

        if not data:
            return make_response(jsonify({'message': 'Registration data is required.'}), 400)
        
        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role')
        profile_data = data.get('profile', {})

        # Validate required fields
        if not email or not password or not role_name:
            return make_response(jsonify({'message': 'Email, password and role are required.'}), 400)
        
        # Validate email format
        if not validate_email(email):
            return make_response(jsonify({'message': 'Invalid email format.'}), 400)
        
        # Validate password strength
        is_valid, pwd_msg = validate_password(password)
        if not is_valid:
            return make_response(jsonify({'message': pwd_msg}), 400)
        
        # Validate role
        if role_name not in [Role.STUDENT, Role.COMPANY]:
            return make_response(jsonify({'message': 'Role must be either "student" or "company".'}), 400)
        
        # Check if user exists
        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': 'Email already registered.'}), 409)
        
        # Get role object
        role = user_datastore.find_role(role_name)
        if not role:
            return make_response(jsonify({'message': f'Role {role_name} not found.'}), 400)
        
        # Create user
        user = user_datastore.create_user(
            email=email,
            password=utils.hash_password(password),
            active=True
        )
        
        # Add role
        user_datastore.add_role_to_user(user, role_name)
        
        # Create profile based on role
        if role_name == Role.STUDENT:
            # Validate student fields
            required_student_fields = ['name', 'roll_number', 'branch', 'cgpa', 'graduation_year']
            missing = [f for f in required_student_fields if f not in profile_data]
            if missing:
                db.session.delete(user)
                db.session.commit()
                return make_response(jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400)
            
            student = Student(
                user_id=user.id,
                name=profile_data['name'],
                roll_number=profile_data['roll_number'],
                branch=profile_data['branch'],
                cgpa=float(profile_data['cgpa']),
                graduation_year=int(profile_data['graduation_year']),
                phone=profile_data.get('phone'),
                alternate_email=profile_data.get('alternate_email')
            )
            db.session.add(student)
            message = "Student registered successfully"
            
        elif role_name == Role.COMPANY:
            # Validate company fields
            required_company_fields = ['company_name', 'hr_name', 'hr_email']
            missing = [f for f in required_company_fields if f not in profile_data]
            if missing:
                db.session.delete(user)
                db.session.commit()
                return make_response(jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400)
            
            company = Company(
                user_id=user.id,
                company_name=profile_data['company_name'],
                hr_name=profile_data['hr_name'],
                hr_email=profile_data['hr_email'],
                hr_phone=profile_data.get('hr_phone'),
                website=profile_data.get('website'),
                industry=profile_data.get('industry'),
                location=profile_data.get('location'),
                company_description=profile_data.get('description'),
                approval_status='pending'
            )
            db.session.add(company)
            message = "Company registered successfully. Pending admin approval."
        
        db.session.commit()

        return make_response(jsonify({
            'message': message,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': role_name
            }
        }), 201)


class LoginAPI(Resource):
    """Login user and return auth token"""
    def post(self):
        login_data = request.get_json()

        if not login_data:
            return make_response(jsonify({'message': 'Login credentials are required.'}), 400)
        
        email = login_data.get('email')
        password = login_data.get('password')
        
        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required.'}), 400)
        
        user = user_datastore.find_user(email=email)

        if not user:
            return make_response(jsonify({'message': 'Invalid email or password.'}), 401)
        
        if not utils.verify_password(password, user.password):
            return make_response(jsonify({'message': 'Invalid email or password.'}), 401)
        
        if not user.active:
            return make_response(jsonify({'message': 'Account is deactivated. Contact admin.'}), 401)
        
        # Check company approval status
        if user.is_company and user.company_profile:
            if user.company_profile.approval_status == 'pending':
                return make_response(jsonify({'message': 'Company registration pending admin approval'}), 403)
            elif user.company_profile.approval_status == 'rejected':
                return make_response(jsonify({'message': 'Company registration was rejected'}), 403)
            elif user.company_profile.is_blacklisted:
                return make_response(jsonify({'message': 'Company has been blacklisted'}), 403)
        
        # Check if student is blacklisted
        if user.is_student and user.student_profile:
            if user.student_profile.is_blacklisted:
                return make_response(jsonify({'message': 'Account has been blacklisted'}), 403)
        
        # Login user (Flask-Login)
        login_user(user)
        
        # Update login stats
        user.last_login_at = datetime.utcnow()
        user.current_login_at = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        user.last_login_ip = request.remote_addr
        user.current_login_ip = request.remote_addr
        db.session.commit()
        
        # Generate auth token
        auth_token = user.get_auth_token()
        
        # Get profile
        profile = user.get_profile()

        return make_response(jsonify({
            'message': 'Login successful.',
            'auth_token': auth_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.get_role_name(),
                'profile': profile.to_dict() if profile and hasattr(profile, 'to_dict') else {}
            }
        }), 200)


class LogoutAPI(Resource):
    """Logout current user"""
    @auth_token_required
    def post(self):
        logout_user()
        return make_response(jsonify({'message': 'Logout successful.'}), 200)


class ProfileAPI(Resource):
    """Get current user profile"""
    @auth_token_required
    def get(self):
        user = current_user
        profile = user.get_profile()
        
        return make_response(jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.get_role_name(),
                'active': user.active,
                'last_login': user.last_login_at.isoformat() if user.last_login_at else None,
                'login_count': user.login_count,
                'profile': profile.to_dict() if profile and hasattr(profile, 'to_dict') else {}
            }
        }), 200)


class ChangePasswordAPI(Resource):
    """Change user password"""
    @auth_token_required
    def post(self):
        data = request.get_json()
        user = current_user

        if not data:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return make_response(jsonify({'message': 'All fields are required.'}), 400)
        
        if new_password != confirm_password:
            return make_response(jsonify({'message': 'New passwords do not match.'}), 400)
        
        # Validate new password
        is_valid, pwd_msg = validate_password(new_password)
        if not is_valid:
            return make_response(jsonify({'message': pwd_msg}), 400)
        
        # Verify current password
        if not utils.verify_password(current_password, user.password):
            return make_response(jsonify({'message': 'Current password is incorrect.'}), 401)
        
        # Change password
        user.password = utils.hash_password(new_password)
        db.session.commit()

        return make_response(jsonify({'message': 'Password changed successfully.'}), 200)


class TestStudentAPI(Resource):
    """Test endpoint for students only"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        return make_response(jsonify({
            'message': 'You have student access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestCompanyAPI(Resource):
    """Test endpoint for companies only"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        return make_response(jsonify({
            'message': 'You have company access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestAdminAPI(Resource):
    """Test endpoint for admin only"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        return make_response(jsonify({
            'message': 'You have admin access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestAnyAPI(Resource):
    """Test endpoint for any authenticated user"""
    @auth_token_required
    def get(self):
        return make_response(jsonify({
            'message': f'You are authenticated as {current_user.get_role_name()}',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)
''' 
# backend/controllers/authentication_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import utils, auth_token_required, roles_required, roles_accepted, login_user, logout_user, current_user
from datetime import datetime

from controllers.user_datastore import user_datastore
from controllers.database import db
from controllers.models import Student, Company, Role

import re

# Helper functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if len(password) > 100:  # Reasonable max length
        return False, "Password cannot be longer than 100 characters"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"


class CheckEmailAPI(Resource):
    """Check if email is available for registration"""
    def post(self):
        credentials = request.get_json()

        if not credentials:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        
        email = credentials.get('email')

        if not email:
            return make_response(jsonify({'message': 'Email is required.'}), 400)
        
        user = user_datastore.find_user(email=email)
        
        return make_response(jsonify({'available': user is None}), 200)


class RegisterAPI(Resource):
    """Register a new user (student or company)"""
    def post(self):
        data = request.get_json()

        if not data:
            return make_response(jsonify({'message': 'Registration data is required.'}), 400)
        
        email = data.get('email')
        password = data.get('password')
        role_name = data.get('role')
        profile_data = data.get('profile', {})

        # Validate required fields
        if not email or not password or not role_name:
            return make_response(jsonify({'message': 'Email, password and role are required.'}), 400)
        
        # Validate email format
        if not validate_email(email):
            return make_response(jsonify({'message': 'Invalid email format.'}), 400)
        
        # Validate password strength
        is_valid, pwd_msg = validate_password(password)
        if not is_valid:
            return make_response(jsonify({'message': pwd_msg}), 400)
        
        # Validate role
        if role_name not in [Role.STUDENT, Role.COMPANY]:
            return make_response(jsonify({'message': 'Role must be either "student" or "company".'}), 400)
        
        # Check if user exists
        if user_datastore.find_user(email=email):
            return make_response(jsonify({'message': 'Email already registered.'}), 409)
        
        # Get role object
        role = user_datastore.find_role(role_name)
        if not role:
            return make_response(jsonify({'message': f'Role {role_name} not found.'}), 400)
        
        # Create user with pbkdf2_sha512 (configured in config.py)
        user = user_datastore.create_user(
            email=email,
            password=utils.hash_password(password),  # Will use pbkdf2_sha512
            active=True
        )
        
        # Add role
        user_datastore.add_role_to_user(user, role_name)
        
        # Create profile based on role
        if role_name == Role.STUDENT:
            # Validate student fields
            required_student_fields = ['name', 'roll_number', 'branch', 'cgpa', 'graduation_year']
            missing = [f for f in required_student_fields if f not in profile_data]
            if missing:
                db.session.delete(user)
                db.session.commit()
                return make_response(jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400)
            
            student = Student(
                user_id=user.id,
                name=profile_data['name'],
                roll_number=profile_data['roll_number'],
                branch=profile_data['branch'],
                cgpa=float(profile_data['cgpa']),
                graduation_year=int(profile_data['graduation_year']),
                phone=profile_data.get('phone'),
                alternate_email=profile_data.get('alternate_email')
            )
            db.session.add(student)
            message = "Student registered successfully"
            
        elif role_name == Role.COMPANY:
            # Validate company fields
            required_company_fields = ['company_name', 'hr_name', 'hr_email']
            missing = [f for f in required_company_fields if f not in profile_data]
            if missing:
                db.session.delete(user)
                db.session.commit()
                return make_response(jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400)
            
            company = Company(
                user_id=user.id,
                company_name=profile_data['company_name'],
                hr_name=profile_data['hr_name'],
                hr_email=profile_data['hr_email'],
                hr_phone=profile_data.get('hr_phone'),
                website=profile_data.get('website'),
                industry=profile_data.get('industry'),
                location=profile_data.get('location'),
                company_description=profile_data.get('description'),
                approval_status='pending'
            )
            db.session.add(company)
            message = "Company registered successfully. Pending admin approval."
        
        db.session.commit()

        return make_response(jsonify({
            'message': message,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': role_name
            }
        }), 201)


class LoginAPI(Resource):
    """Login user and return auth token"""
    def post(self):
        login_data = request.get_json()

        if not login_data:
            return make_response(jsonify({'message': 'Login credentials are required.'}), 400)
        
        email = login_data.get('email')
        password = login_data.get('password')
        
        if not email or not password:
            return make_response(jsonify({'message': 'Email and password are required.'}), 400)
        
        user = user_datastore.find_user(email=email)

        if not user:
            return make_response(jsonify({'message': 'Invalid email or password.'}), 401)
        
        # Verify password using pbkdf2_sha512 (from config)
        if not utils.verify_password(password, user.password):
            return make_response(jsonify({'message': 'Invalid email or password.'}), 401)
        
        if not user.active:
            return make_response(jsonify({'message': 'Account is deactivated. Contact admin.'}), 401)
        
        # Check company approval status
        if user.is_company and user.company_profile:
            if user.company_profile.approval_status == 'pending':
                return make_response(jsonify({'message': 'Company registration pending admin approval'}), 403)
            elif user.company_profile.approval_status == 'rejected':
                return make_response(jsonify({'message': 'Company registration was rejected'}), 403)
            elif user.company_profile.is_blacklisted:
                return make_response(jsonify({'message': 'Company has been blacklisted'}), 403)
        
        # Check if student is blacklisted
        if user.is_student and user.student_profile:
            if user.student_profile.is_blacklisted:
                return make_response(jsonify({'message': 'Account has been blacklisted'}), 403)
        
        # Login user (Flask-Login)
        login_user(user)
        
        # Update login stats
        user.last_login_at = datetime.utcnow()
        user.current_login_at = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
        user.last_login_ip = request.remote_addr
        user.current_login_ip = request.remote_addr
        db.session.commit()
        
        # Generate auth token
        auth_token = user.get_auth_token()
        
        # Get profile
        profile = user.get_profile()

        return make_response(jsonify({
            'message': 'Login successful.',
            'auth_token': auth_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.get_role_name(),
                'profile': profile.to_dict() if profile and hasattr(profile, 'to_dict') else {}
            }
        }), 200)


class LogoutAPI(Resource):
    """Logout current user"""
    @auth_token_required
    def post(self):
        logout_user()
        return make_response(jsonify({'message': 'Logout successful.'}), 200)


class ProfileAPI(Resource):
    """Get current user profile"""
    @auth_token_required
    def get(self):
        user = current_user
        profile = user.get_profile()
        
        return make_response(jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.get_role_name(),
                'active': user.active,
                'last_login': user.last_login_at.isoformat() if user.last_login_at else None,
                'login_count': user.login_count,
                'profile': profile.to_dict() if profile and hasattr(profile, 'to_dict') else {}
            }
        }), 200)


class ChangePasswordAPI(Resource):
    """Change user password"""
    @auth_token_required
    def post(self):
        data = request.get_json()
        user = current_user

        if not data:
            return make_response(jsonify({'message': 'Request body is required.'}), 400)
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not current_password or not new_password or not confirm_password:
            return make_response(jsonify({'message': 'All fields are required.'}), 400)
        
        if new_password != confirm_password:
            return make_response(jsonify({'message': 'New passwords do not match.'}), 400)
        
        # Validate new password
        is_valid, pwd_msg = validate_password(new_password)
        if not is_valid:
            return make_response(jsonify({'message': pwd_msg}), 400)
        
        # Verify current password
        if not utils.verify_password(current_password, user.password):
            return make_response(jsonify({'message': 'Current password is incorrect.'}), 401)
        
        # Change password using pbkdf2_sha512
        user.password = utils.hash_password(new_password)
        db.session.commit()

        return make_response(jsonify({'message': 'Password changed successfully.'}), 200)


class TestStudentAPI(Resource):
    """Test endpoint for students only"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        return make_response(jsonify({
            'message': 'You have student access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestCompanyAPI(Resource):
    """Test endpoint for companies only"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        return make_response(jsonify({
            'message': 'You have company access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestAdminAPI(Resource):
    """Test endpoint for admin only"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        return make_response(jsonify({
            'message': 'You have admin access!',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)


class TestAnyAPI(Resource):
    """Test endpoint for any authenticated user"""
    @auth_token_required
    def get(self):
        return make_response(jsonify({
            'message': f'You are authenticated as {current_user.get_role_name()}',
            'user': current_user.email,
            'role': current_user.get_role_name()
        }), 200)
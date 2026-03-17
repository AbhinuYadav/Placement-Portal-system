# backend/controllers/crud_apis.py
from flask_restful import Resource
from flask import request, jsonify, make_response
from flask_security import auth_token_required, roles_required, roles_accepted, current_user
from controllers.database import db
from controllers.models import (
    User, Student, Company, PlacementDrive, 
    Application, Role
)
from sqlalchemy import or_
from datetime import datetime, timedelta
from celery_app import celery
from tasks import export_student_applications,generate_monthly_report, send_new_drive_notification
from flask import send_file
import os
from celery.result import AsyncResult
from extension import cache



class CompanyProfileAPI(Resource):
    """Company profile CRUD operations"""
    
    @auth_token_required
    @roles_required('company')
    def get(self):
        """Get company profile"""
        user = current_user
        if not user.company_profile:
            return make_response(jsonify({'message': 'Company profile not found'}), 404)
        
        return make_response(jsonify({
            'profile': user.company_profile.to_dict()
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def put(self):
        """Update company profile"""
        user = current_user
        data = request.get_json()
        
        if not user.company_profile:
            return make_response(jsonify({'message': 'Company profile not found'}), 404)
        
        company = user.company_profile
        
        # Update fields
        if data.get('company_name'):
            company.company_name = data['company_name']
        if data.get('hr_name'):
            company.hr_name = data['hr_name']
        if data.get('hr_email'):
            company.hr_email = data['hr_email']
        if data.get('hr_phone'):
            company.hr_phone = data['hr_phone']
        if data.get('website'):
            company.website = data['website']
        if data.get('industry'):
            company.industry = data['industry']
        if data.get('location'):
            company.location = data['location']
        if data.get('description'):
            company.company_description = data['description']
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Company profile updated successfully',
            'profile': company.to_dict()
        }), 200)


class StudentProfileAPI(Resource):
    """Student profile CRUD operations"""
    
    @auth_token_required
    @roles_required('student')
    def get(self):
        """Get student profile"""
        user = current_user
        if not user.student_profile:
            return make_response(jsonify({'message': 'Student profile not found'}), 404)
        
        return make_response(jsonify({
            'profile': user.student_profile.to_dict()
        }), 200)
    
    @auth_token_required
    @roles_required('student')
    def put(self):
        """Update student profile"""
        user = current_user
        data = request.get_json()
        
        if not user.student_profile:
            return make_response(jsonify({'message': 'Student profile not found'}), 404)
        
        student = user.student_profile
        
        # Update fields
        if data.get('phone'):
            student.phone = data['phone']
        if data.get('alternate_email'):
            student.alternate_email = data['alternate_email']
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Student profile updated successfully',
            'profile': student.to_dict()
        }), 200)


class PlacementDriveAPI(Resource):
    """Placement drive CRUD operations"""
    
    @auth_token_required
    def get(self, drive_id=None):
        """Get all drives or specific drive"""
        if drive_id:
            drive = PlacementDrive.query.get(drive_id)
            if not drive:
                return make_response(jsonify({'message': 'Drive not found'}), 404)
            return make_response(jsonify({'drive': drive.to_dict()}), 200)
        
        # Filter based on role
        if current_user.is_admin:
            drives = PlacementDrive.query.all()
        elif current_user.is_company:
            drives = PlacementDrive.query.filter_by(company_id=current_user.company_profile.id).all()
        else:  # student
            drives = PlacementDrive.query.filter_by(status='approved').all()
        
        return make_response(jsonify({
            'drives': [drive.to_dict() for drive in drives]
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def post(self):
        """Create new placement drive"""
        data = request.get_json()
        
        required_fields = ['drive_name', 'job_title', 'application_deadline']
        missing = [f for f in required_fields if f not in data]
        if missing:
            return make_response(jsonify({'message': f'Missing fields: {", ".join(missing)}'}), 400)
        
        drive = PlacementDrive(
            company_id=current_user.company_profile.id,
            drive_name=data['drive_name'],
            job_title=data['job_title'],
            job_description=data.get('job_description', ''),
            eligibility_criteria=data.get('eligibility_criteria', ''),
            min_cgpa=data.get('min_cgpa'),
            allowed_branches=data.get('allowed_branches', ''),
            application_deadline=datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00')),
            drive_date=datetime.fromisoformat(data['drive_date'].replace('Z', '+00:00')) if data.get('drive_date') else None,
            status='pending'
        )
        
        db.session.add(drive)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Placement drive created successfully. Pending admin approval.',
            'drive': drive.to_dict()
        }), 201)
    
    @auth_token_required
    @roles_required('company')
    def put(self, drive_id):
        """Update placement drive"""
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return make_response(jsonify({'message': 'Drive not found'}), 404)
        
        # Check ownership
        if drive.company_id != current_user.company_profile.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only update if pending
        if drive.status != 'pending':
            return make_response(jsonify({'message': 'Can only update pending drives'}), 400)
        
        data = request.get_json()
        
        if data.get('drive_name'):
            drive.drive_name = data['drive_name']
        if data.get('job_title'):
            drive.job_title = data['job_title']
        if data.get('job_description'):
            drive.job_description = data['job_description']
        if data.get('eligibility_criteria'):
            drive.eligibility_criteria = data['eligibility_criteria']
        if data.get('min_cgpa'):
            drive.min_cgpa = data['min_cgpa']
        if data.get('allowed_branches'):
            drive.allowed_branches = data['allowed_branches']
        if data.get('application_deadline'):
            drive.application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
        if data.get('drive_date'):
            drive.drive_date = datetime.fromisoformat(data['drive_date'].replace('Z', '+00:00'))
        
        drive.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Drive updated successfully',
            'drive': drive.to_dict()
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def delete(self, drive_id):
        """Delete placement drive"""
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return make_response(jsonify({'message': 'Drive not found'}), 404)
        
        # Check ownership
        if drive.company_id != current_user.company_profile.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only delete if pending
        if drive.status != 'pending':
            return make_response(jsonify({'message': 'Can only delete pending drives'}), 400)
        
        db.session.delete(drive)
        db.session.commit()
        
        return make_response(jsonify({'message': 'Drive deleted successfully'}), 200)


class ApplicationAPI(Resource):
    """Application CRUD operations"""
    
    @auth_token_required
    def get(self, application_id=None):
        """Get applications"""
        if application_id:
            app = Application.query.get(application_id)
            if not app:
                return make_response(jsonify({'message': 'Application not found'}), 404)
            
            # Check authorization
            if current_user.is_student and app.student_id != current_user.student_profile.id:
                return make_response(jsonify({'message': 'Unauthorized'}), 403)
            if current_user.is_company and app.drive.company_id != current_user.company_profile.id:
                return make_response(jsonify({'message': 'Unauthorized'}), 403)
            
            return make_response(jsonify({'application': app.to_dict()}), 200)
        
        # List applications based on role
        if current_user.is_student:
            apps = Application.query.filter_by(student_id=current_user.student_profile.id).all()
        elif current_user.is_company:
            apps = Application.query.join(PlacementDrive).filter(
                PlacementDrive.company_id == current_user.company_profile.id
            ).all()
        else:  # admin
            apps = Application.query.all()
        
        return make_response(jsonify({
            'applications': [app.to_dict() for app in apps]
        }), 200)
    
    @auth_token_required
    @roles_required('student')
    def post(self):
        """Apply to a drive"""
        data = request.get_json()
        drive_id = data.get('drive_id')
        
        if not drive_id:
            return make_response(jsonify({'message': 'Drive ID is required'}), 400)
        
        drive = PlacementDrive.query.get(drive_id)
        
        if not drive:
            return make_response(jsonify({'message': 'Drive not found'}), 404)
        
        if drive.status != 'approved':
            return make_response(jsonify({'message': 'Drive is not open for applications'}), 400)
        
        # Check if already applied
        existing = Application.query.filter_by(
            student_id=current_user.student_profile.id,
            drive_id=drive_id
        ).first()
        
        if existing:
            return make_response(jsonify({'message': 'Already applied to this drive'}), 400)
        
        application = Application(
            student_id=current_user.student_profile.id,
            drive_id=drive_id,
            status='applied'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201)
    
    # ==================== HELPER FUNCTIONS ====================

def get_current_student():
    """Get current student profile"""
    if not current_user.is_student:
        return None
    return current_user.student_profile

def get_current_company():
    """Get current company profile"""
    if not current_user.is_company:
        return None
    return current_user.company_profile

def is_branch_eligible(student_branch, allowed_branches_str):
    """
    Check if student branch matches any allowed branch with common variations
    Returns: Boolean (True if eligible, False if not)
    """
    if not allowed_branches_str:
        return True  # No branch restriction means all branches allowed
    
    # ===== COMMON BRANCH MAPPINGS =====
    branch_mappings = {
        # Computer Science variations
        'computer science': ['cse', 'computer science', 'cs', 'comp', 'comp sci', 'computer', 'computers'],
        'cse': ['cse', 'computer science', 'cs', 'comp', 'comp sci', 'computer', 'computers'],
        
        # Information Technology variations
        'information technology': ['it', 'information technology', 'info tech', 'i.t.', 'infotech', 'information tech'],
        'it': ['it', 'information technology', 'info tech', 'i.t.', 'infotech', 'information tech'],
        
        # Electronics variations
        'electronics': ['ece', 'electronics', 'electronics and communication', 
                        'electronics & communication', 'electronics and communications',
                        'electronics & comm', 'electronics and telecommunication',
                        'electronics & telecommunication', 'entc', 'ex tc', 'electronics engineering'],
        'ece': ['ece', 'electronics', 'electronics and communication', 
                'electronics & communication', 'electronics and communications',
                'electronics & comm', 'electronics and telecommunication',
                'electronics & telecommunication', 'entc', 'ex tc', 'electronics engineering'],
        
        # Electrical variations
        'electrical': ['eee', 'electrical', 'electrical and electronics', 
                       'electrical & electronics', 'electrical engineering', 'power'],
        'eee': ['eee', 'electrical', 'electrical and electronics', 
                'electrical & electronics', 'electrical engineering', 'power'],
        
        # Mechanical variations
        'mechanical': ['mech', 'mechanical', 'mechanical engineering', 'mech engg', 'mechanicals'],
        'mech': ['mech', 'mechanical', 'mechanical engineering', 'mech engg', 'mechanicals'],
        
        # Civil variations
        'civil': ['civil', 'civil engineering', 'civil engg', 'civil eng'],
        
        # Biotechnology variations
        'biotechnology': ['biotech', 'biotechnology', 'bio tech', 'bio-technology', 'bio'],
        'biotech': ['biotech', 'biotechnology', 'bio tech', 'bio-technology', 'bio'],
        
        # Instrumentation variations
        'instrumentation': ['instrumentation', 'instrumentation engineering', 'instru', 'ice'],
        
        # Production variations
        'production': ['production', 'production engineering', 'prod', 'industrial'],
        'industrial': ['industrial', 'industrial engineering', 'prod', 'production'],
        
        # Chemical variations
        'chemical': ['chemical', 'chemical engineering', 'chem'],
    }
    
    # Normalize inputs
    student_branch_lower = student_branch.lower().strip()
    allowed_branches = [b.strip().lower() for b in allowed_branches_str.split(',')]
    
    print(f"🔍 Branch check: '{student_branch}' against allowed: {allowed_branches}")
    
    # ===== CHECK 1: Direct match =====
    if student_branch_lower in allowed_branches:
        print(f"✅ Direct match found")
        return True
    
    # ===== CHECK 2: Check if student branch is a variation of any allowed branch =====
    for allowed in allowed_branches:
        # Check if this allowed branch has mappings
        if allowed in branch_mappings:
            if student_branch_lower in branch_mappings[allowed]:
                print(f"✅ Student branch matches mapping for '{allowed}'")
                return True
        
        # Check if any mapping key matches the allowed branch
        for key, variations in branch_mappings.items():
            if allowed in variations or key in allowed:
                if student_branch_lower in variations or student_branch_lower == key:
                    print(f"✅ Student branch matches variation of '{key}'")
                    return True
    
    # ===== CHECK 3: Partial matching =====
    for allowed in allowed_branches:
        # Check if allowed branch is contained in student branch
        if allowed in student_branch_lower and len(allowed) > 2:
            print(f"✅ Allowed branch '{allowed}' found in student branch")
            return True
        
        # Check if student branch is contained in allowed branch
        if student_branch_lower in allowed and len(student_branch_lower) > 2:
            print(f"✅ Student branch found in allowed branch '{allowed}'")
            return True
    
    # ===== CHECK 4: Abbreviation matching =====
    if len(student_branch_lower) <= 5:  # Short abbreviation like CSE, ECE, IT
        for allowed in allowed_branches:
            allowed_words = allowed.replace('-', ' ').replace('&', ' ').split()
            for word in allowed_words:
                if word.startswith(student_branch_lower) and len(student_branch_lower) >= 2:
                    print(f"✅ Abbreviation match")
                    return True
    
    print(f"❌ No match found")
    return False


# ==================== ADMIN APIS ====================

class AdminDashboardAPI(Resource):
    """Admin dashboard with statistics"""
    @auth_token_required
    @roles_required('admin')
    def get(self):

        cached_result = cache.get("admin_dashboard")
        if cached_result:
            print("✅ Admin dashboard cache HIT")
            return make_response(jsonify(cached_result), 200)
        
        print("❌ Admin dashboard cache MISS")

        # Get counts
        total_students = Student.query.count()
        total_companies = Company.query.count()
        total_drives = PlacementDrive.query.count()
        total_applications = Application.query.count()
        
        # Pending approvals
        pending_companies = Company.query.filter_by(approval_status='pending').count()
        pending_drives = PlacementDrive.query.filter_by(status='pending').count()
        
        # Recent activities
        recent_applications = Application.query.order_by(
            Application.applied_at.desc()
        ).limit(5).all()
        
        recent_drives = PlacementDrive.query.order_by(
            PlacementDrive.created_at.desc()
        ).limit(5).all()

        result={
            'stats': {
                'total_students': total_students,
                'total_companies': total_companies,
                'total_drives': total_drives,
                'total_applications': total_applications,
                'pending_companies': pending_companies,
                'pending_drives': pending_drives
            },
            'recent_applications': [
                {
                    'id': app.id,
                    'student_name': app.student.name,
                    'drive_name': app.drive.drive_name,
                    'company_name': app.drive.company.company_name,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat()
                } for app in recent_applications
            ],
            'recent_drives': [
                {
                    'id': drive.id,
                    'drive_name': drive.drive_name,
                    'company_name': drive.company.company_name,
                    'status': drive.status,
                    'created_at': drive.created_at.isoformat()
                } for drive in recent_drives
            ]
        }

        cache.set("admin_dashboard", result, timeout=300)
        
        return make_response(jsonify(result), 200)


class AdminCompanyListAPI(Resource):
    """List all companies with filters"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        # Get query parameters
        status = request.args.get('status')  # pending, approved, rejected
        search = request.args.get('search')
        
        query = Company.query
        
        if status:
            query = query.filter_by(approval_status=status)
        
        if search:
            query = query.filter(
                or_(
                    Company.company_name.contains(search),
                    Company.hr_name.contains(search),
                    Company.hr_email.contains(search)
                )
            )
        
        companies = query.order_by(Company.created_at.desc()).all()
        
        return make_response(jsonify({
            'companies': [company.to_dict() for company in companies]
        }), 200)


class AdminCompanyDetailAPI(Resource):
    """View company details"""
    @auth_token_required
    @roles_required('admin')
    def get(self, company_id):
        company = Company.query.get_or_404(company_id)
        
        # Get company's drives
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        
        return make_response(jsonify({
            'company': company.to_dict(),
            'drives': [
                {
                    'id': drive.id,
                    'drive_name': drive.drive_name,
                    'job_title': drive.job_title,
                    'status': drive.status,
                    'created_at': drive.created_at.isoformat(),
                    'application_count': drive.applications.count()
                } for drive in drives
            ]
        }), 200)


class AdminCompanyApproveAPI(Resource):
    """Approve a company"""
    @auth_token_required
    @roles_required('admin')
    def post(self, company_id):
        company = Company.query.get_or_404(company_id)
        
        if company.approval_status != 'pending':
            return make_response(jsonify({
                'message': f'Company already {company.approval_status}'
            }), 400)
        
        company.approval_status = 'approved'
        company.approved_at = datetime.utcnow()
        company.approved_by = current_user.id
        db.session.commit()

        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (company approved)")
        
        return make_response(jsonify({
            'message': 'Company approved successfully',
            'company': company.to_dict()
        }), 200)


class AdminCompanyRejectAPI(Resource):
    """Reject a company"""
    @auth_token_required
    @roles_required('admin')
    def post(self, company_id):
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        company = Company.query.get_or_404(company_id)
        
        if company.approval_status != 'pending':
            return make_response(jsonify({
                'message': f'Company already {company.approval_status}'
            }), 400)
        
        company.approval_status = 'rejected'
        company.rejection_reason = reason
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Company rejected',
            'company': company.to_dict()
        }), 200)


class AdminCompanyBlacklistAPI(Resource):
    """Blacklist a company"""
    @auth_token_required
    @roles_required('admin')
    def post(self, company_id):
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        company = Company.query.get_or_404(company_id)
        company.is_blacklisted = True
        company.blacklist_reason = reason
        company.blacklisted_at = datetime.utcnow()
        company.blacklisted_by = current_user.id
        
        # Also deactivate user
        user = User.query.get(company.user_id)
        if user:
            user.active = False
        
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (company blacklisted)")

        return make_response(jsonify({
            'message': 'Company blacklisted',
            'company': company.to_dict()
        }), 200)


class AdminCompanyActivateAPI(Resource):
    """Remove blacklist from company"""
    @auth_token_required
    @roles_required('admin')
    def post(self, company_id):
        company = Company.query.get_or_404(company_id)
        company.is_blacklisted = False
        company.blacklist_reason = None
        company.blacklisted_at = None
        company.blacklisted_by = None
        
        # Reactivate user
        user = User.query.get(company.user_id)
        if user:
            user.active = True
        
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (company activated)")

        return make_response(jsonify({
            'message': 'Company activated',
            'company': company.to_dict()
        }), 200)


class AdminDriveListAPI(Resource):
    """List all drives with filters"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        status = request.args.get('status')  # pending, approved, rejected, closed
        company_id = request.args.get('company_id')
        
        query = PlacementDrive.query
        
        if status:
            query = query.filter_by(status=status)
        
        if company_id:
            query = query.filter_by(company_id=company_id)
        
        drives = query.order_by(PlacementDrive.created_at.desc()).all()
        
        return make_response(jsonify({
            'drives': [
                {
                    'id': drive.id,
                    'drive_name': drive.drive_name,
                    'job_title': drive.job_title,
                    'company_name': drive.company.company_name,
                    'status': drive.status,
                    'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                    'created_at': drive.created_at.isoformat(),
                    'application_count': drive.applications.count()
                } for drive in drives
            ]
        }), 200)


class AdminDriveDetailAPI(Resource):
    """View drive details"""
    @auth_token_required
    @roles_required('admin')
    def get(self, drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Get applications
        applications = Application.query.filter_by(drive_id=drive.id).all()
        
        return make_response(jsonify({
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'eligibility_criteria': drive.eligibility_criteria,
                'min_cgpa': drive.min_cgpa,
                'allowed_branches': drive.allowed_branches,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'status': drive.status,
                'created_at': drive.created_at.isoformat(),
                'company': drive.company.to_dict() if drive.company else None
            },
            'applications': [
                {
                    'id': app.id,
                    'student_name': app.student.name,
                    'student_roll': app.student.roll_number,
                    'student_cgpa': app.student.cgpa,
                    'student_branch': app.student.branch,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat()
                } for app in applications
            ],
            'statistics': {
                'total': len(applications),
                'applied': sum(1 for a in applications if a.status == 'applied'),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected'),
                'rejected': sum(1 for a in applications if a.status == 'rejected')
            }
        }), 200)


class AdminDriveApproveAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self, drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        if drive.status != 'pending':
            return make_response(jsonify({'message': f'Drive already {drive.status}'}), 400)
        
        drive.status = 'approved'
        drive.approved_at = datetime.utcnow()
        drive.approved_by = current_user.id
        db.session.commit()
        
        # Trigger notification task for eligible students
        send_new_drive_notification.delay(drive.id)
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (drive approved)")

        return make_response(jsonify({
            'message': 'Drive approved successfully. Students will be notified.',
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'status': drive.status
            }
        }), 200)
# ==================== ADMIN APPLICATIONS API ====================

class AdminApplicationsAPI(Resource):
    """Get all applications with filters for admin"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        try:
            # Get query parameters
            status = request.args.get('status')
            search = request.args.get('search')
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            
            # Start query
            query = Application.query
            
            # Filter by status
            if status:
                query = query.filter(Application.status == status)
            
            # Search by student name or company name
            if search:
                query = query.join(Student).join(PlacementDrive).join(Company).filter(
                    db.or_(
                        Student.name.ilike(f'%{search}%'),
                        Company.company_name.ilike(f'%{search}%')
                    )
                )
            
            # Order by most recent first
            query = query.order_by(Application.applied_at.desc())
            
            # Paginate
            paginated = query.paginate(page=page, per_page=per_page, error_out=False)
            
            # Format response
            applications = []
            for app in paginated.items:
                applications.append({
                    'id': app.id,
                    'student_id': app.student_id,
                    'student_name': app.student.name if app.student else 'N/A',
                    'student_roll': app.student.roll_number if app.student else 'N/A',
                    'student_branch': app.student.branch if app.student else 'N/A',
                    'student_cgpa': app.student.cgpa if app.student else 'N/A',
                    'drive_id': app.drive_id,
                    'drive_name': app.drive.drive_name if app.drive else 'N/A',
                    'job_title': app.drive.job_title if app.drive else 'N/A',
                    'company_id': app.drive.company_id if app.drive else None,
                    'company_name': app.drive.company.company_name if app.drive and app.drive.company else 'N/A',
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                    'interview_date': app.interview_date.isoformat() if app.interview_date else None,
                })
            
            return make_response(jsonify({
                'success': True,
                'applications': applications,
                'pagination': {
                    'current_page': paginated.page,
                    'last_page': paginated.pages,
                    'per_page': paginated.per_page,
                    'total': paginated.total,
                    'from': (paginated.page - 1) * paginated.per_page + 1 if paginated.total > 0 else 0,
                    'to': min(paginated.page * paginated.per_page, paginated.total)
                }
            }), 200)
            
        except Exception as e:
            print(f"Error in AdminApplicationsAPI: {str(e)}")
            return {'success': False, 'message': str(e)}, 500

class AdminDriveRejectAPI(Resource):
    """Reject a placement drive"""
    @auth_token_required
    @roles_required('admin')
    def post(self, drive_id):
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        if drive.status != 'pending':
            return make_response(jsonify({
                'message': f'Drive already {drive.status}'
            }), 400)
        
        drive.status = 'rejected'
        # You might want to add a rejection_reason field to PlacementDrive model
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (drive rejected)")

        return make_response(jsonify({
            'message': 'Drive rejected',
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'status': drive.status
            }
        }), 200)


class AdminDriveCloseAPI(Resource):
    """Close an approved drive"""
    @auth_token_required
    @roles_required('admin')
    def post(self, drive_id):
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        if drive.status != 'approved':
            return make_response(jsonify({
                'message': 'Only approved drives can be closed'
            }), 400)
        
        drive.status = 'closed'
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (drive closed)")

        return make_response(jsonify({
            'message': 'Drive closed successfully',
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'status': drive.status
            }
        }), 200)


class AdminStudentListAPI(Resource):
    """List all students"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        branch = request.args.get('branch')
        year = request.args.get('year')
        search = request.args.get('search')
        
        query = Student.query
        
        if branch:
            query = query.filter_by(branch=branch)
        
        if year:
            query = query.filter_by(graduation_year=year)
        
        if search:
            query = query.filter(
                or_(
                    Student.name.contains(search),
                    Student.roll_number.contains(search)
                )
            )
        
        students = query.order_by(Student.roll_number).all()
        
        return make_response(jsonify({
            'students': [student.to_dict() for student in students],
            'total': len(students)
        }), 200)


class AdminStudentDetailAPI(Resource):
    """View student details"""
    @auth_token_required
    @roles_required('admin')
    def get(self, student_id):
        student = Student.query.get_or_404(student_id)
        
        # Get student's applications
        applications = Application.query.filter_by(student_id=student.id).all()
        
        return make_response(jsonify({
            'student': student.to_dict(),
            'applications': [
                {
                    'id': app.id,
                    'drive_name': app.drive.drive_name,
                    'company_name': app.drive.company.company_name,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat()
                } for app in applications
            ],
            'statistics': {
                'total_applications': len(applications),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected')
            }
        }), 200)


class AdminStudentBlacklistAPI(Resource):
    """Blacklist a student"""
    @auth_token_required
    @roles_required('admin')
    def post(self, student_id):
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        student = Student.query.get_or_404(student_id)
        student.is_blacklisted = True
        student.blacklist_reason = reason
        student.blacklisted_at = datetime.utcnow()
        student.blacklisted_by = current_user.id
        
        # Deactivate user
        user = User.query.get(student.user_id)
        if user:
            user.active = False
        
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (student blacklisted)")

        return make_response(jsonify({
            'message': 'Student blacklisted',
            'student': student.to_dict()
        }), 200)


class AdminStudentActivateAPI(Resource):
    """Remove blacklist from student"""
    @auth_token_required
    @roles_required('admin')
    def post(self, student_id):
        student = Student.query.get_or_404(student_id)
        student.is_blacklisted = False
        student.blacklist_reason = None
        student.blacklisted_at = None
        student.blacklisted_by = None
        
        # Reactivate user
        user = User.query.get(student.user_id)
        if user:
            user.active = True
        
        db.session.commit()
        
        cache.delete("admin_dashboard")
        print("🗑️ Admin dashboard cache cleared (student activated)")

        return make_response(jsonify({
            'message': 'Student activated',
            'student': student.to_dict()
        }), 200)


class AdminSearchAPI(Resource):
    """Global search for admin"""
    @auth_token_required
    @roles_required('admin')
    def get(self):
        query = request.args.get('q', '')
        
        if len(query) < 2:
            return make_response(jsonify({
                'message': 'Search query too short'
            }), 400)
        
        results = {
            'companies': [],
            'students': [],
            'drives': []
        }
        
        # Search companies
        companies = Company.query.filter(
            or_(
                Company.company_name.contains(query),
                Company.hr_name.contains(query),
                Company.hr_email.contains(query)
            )
        ).limit(5).all()
        
        results['companies'] = [
            {
                'id': c.id,
                'name': c.company_name,
                'type': 'company',
                'status': c.approval_status
            } for c in companies
        ]
        
        # Search students
        students = Student.query.filter(
            or_(
                Student.name.contains(query),
                Student.roll_number.contains(query)
            )
        ).limit(5).all()
        
        results['students'] = [
            {
                'id': s.id,
                'name': s.name,
                'roll': s.roll_number,
                'type': 'student'
            } for s in students
        ]
        
        # Search drives
        drives = PlacementDrive.query.filter(
            PlacementDrive.drive_name.contains(query)
        ).limit(5).all()
        
        results['drives'] = [
            {
                'id': d.id,
                'name': d.drive_name,
                'company': d.company.company_name,
                'type': 'drive',
                'status': d.status
            } for d in drives
        ]
        
        return make_response(jsonify(results), 200)

class AdminGenerateMonthlyReportAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def post(self):
        """Manually trigger monthly report generation"""
        try:
            task = generate_monthly_report.delay()
            return make_response(jsonify({
                'task_id': task.id,
                'message': 'Monthly report generation started'
            }), 202)
        except Exception as e:
            return make_response(jsonify({'error': str(e)}), 500)
        
class AdminTaskStatusAPI(Resource):
    @auth_token_required
    @roles_required('admin')
    def get(self, task_id):
        """Check status of any admin task"""
        task_result = AsyncResult(task_id, app=celery)
        response = {'task_id': task_id, 'state': task_result.state}
        
        if task_result.state == 'SUCCESS':
            response['result'] = task_result.info
        elif task_result.state == 'FAILURE':
            response['error'] = str(task_result.info)
        
        return make_response(jsonify(response), 200)

# ==================== STUDENT APIS ====================

class StudentExportStatusAPI(Resource):
    @auth_token_required
    def get(self, task_id):
        """Get status of an export task"""
        task_result = AsyncResult(task_id, app=celery)
        
        response = {'task_id': task_id, 'state': task_result.state}
        
        if task_result.state == 'PENDING':
            response['status'] = 'Task is pending...'
        elif task_result.state == 'FAILURE':
            response['status'] = str(task_result.info)  # exception
        elif task_result.state == 'SUCCESS':
            # Return the result info (including file path, etc.)
            response['info'] = task_result.info
        else:
            response['status'] = str(task_result.info) if task_result.info else ''
        
        return make_response(jsonify(response), 200)


class StudentExportDownloadAPI(Resource):
    @auth_token_required
    def get(self, task_id):
        """Download the exported file for a completed task"""
        task_result = AsyncResult(task_id, app=celery)
        
        if task_result.state != 'SUCCESS':
            return make_response(jsonify({'error': 'Export not ready or failed'}), 404)
        
        info = task_result.info
        if not info or info.get('status') != 'success':
            return make_response(jsonify({'error': 'Export failed'}), 404)
        
        # Verify ownership: the task must belong to the current user
        if info.get('student_id') != current_user.id:
            return make_response(jsonify({'error': 'Access denied'}), 403)
        
        file_path = info.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return make_response(jsonify({'error': 'File not found'}), 404)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=info.get('filename', 'export.csv'),
            mimetype='text/csv'
        )

class StudentExportApplicationsAPI(Resource):
    @auth_token_required
    @roles_required('student')
    def post(self):
        """Start export of student applications (async)"""
        student = get_current_student()
        if not student:
            return make_response(jsonify({'message': 'Student profile not found'}), 404)
        
        try:
            task = export_student_applications.delay(student.id)
            return make_response(jsonify({
                'task_id': task.id,
                'message': 'Export started. You will receive an email when complete.'
            }), 202)
        except Exception as e:
            print(f"❌ Export error: {e}")
            return make_response(jsonify({'message': str(e)}), 500)

class StudentDeleteApplicationAPI(Resource):
    """Delete/withdraw an application completely"""
    @auth_token_required
    @roles_required('student')
    def delete(self, application_id):
        student = get_current_student()
        application = Application.query.get_or_404(application_id)
        
        # Check ownership - only the student who applied can delete
        if application.student_id != student.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Optional: Check if deadline has passed
        if application.drive.application_deadline and application.drive.application_deadline < datetime.utcnow():
            return make_response(jsonify({
                'message': 'Cannot delete application after deadline'
            }), 400)
        
        # Optional: Check if company has already shortlisted/selected
        if application.status != 'applied':
            return make_response(jsonify({
                'message': f'Cannot delete application with status: {application.status}'
            }), 400)
        
        # Delete the application completely
        db.session.delete(application)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Application deleted successfully'
        }), 200)

class StudentProfileAPI(Resource):
    """Get/Update student profile"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        if not student:
            return make_response(jsonify({'message': 'Student profile not found'}), 404)
        
        return make_response(jsonify({
            'profile': student.to_dict()
        }), 200)
    
    @auth_token_required
    @roles_required('student')
    def put(self):
        student = get_current_student()
        if not student:
            return make_response(jsonify({'message': 'Student profile not found'}), 404)
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('phone'):
            student.phone = data['phone']
        if data.get('alternate_email'):
            student.alternate_email = data['alternate_email']
        
        student.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Profile updated successfully',
            'profile': student.to_dict()
        }), 200)

'''
class StudentDriveListAPI(Resource):
    """List all approved drives available to student"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        
        # Get all approved drives
        drives = PlacementDrive.query.filter_by(status='approved').all()
        
        # Filter by eligibility (simplified - you can enhance this)
        eligible_drives = []
        for drive in drives:
            # Check CGPA eligibility
            if drive.min_cgpa and student.cgpa < drive.min_cgpa:
                continue
            
            # Check branch eligibility (if specified)
            if drive.allowed_branches:
                branches = drive.allowed_branches.split(',')
                if student.branch not in branches:
                    continue
            
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first() is not None
            
            eligible_drives.append({
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'company_name': drive.company.company_name,
                'company_id': drive.company.id,
                'job_description': drive.job_description[:200] + '...' if drive.job_description else '',
                'eligibility_criteria': drive.eligibility_criteria,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'already_applied': already_applied
            })
        
        return make_response(jsonify({
            'drives': eligible_drives,
            'count': len(eligible_drives)
        }), 200)
'''

class StudentDriveListAPI(Resource):
    """List all approved drives available to student"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        
        # Get all approved drives (don't filter by eligibility here)
        drives = PlacementDrive.query.filter_by(status='approved').all()
        
        result_drives = []
        for drive in drives:
            # Skip if company is blacklisted
            if drive.company.is_blacklisted:
                continue
            
            # Check CGPA eligibility
            cgpa_eligible = not drive.min_cgpa or student.cgpa >= drive.min_cgpa
            
            # Check branch eligibility using our function
            branch_eligible = True
            if drive.allowed_branches:
                branch_eligible = is_branch_eligible(student.branch, drive.allowed_branches)
            
            # Check if already applied
            already_applied = Application.query.filter_by(
                student_id=student.id,
                drive_id=drive.id
            ).first() is not None
            
            # Check deadline
            deadline_active = True
            if drive.application_deadline and drive.application_deadline < datetime.utcnow():
                deadline_active = False
            
            # Overall eligibility
            is_eligible = cgpa_eligible and branch_eligible and deadline_active
            
            result_drives.append({
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'company_name': drive.company.company_name,
                'company_id': drive.company.id,
                'job_description': drive.job_description[:200] + '...' if drive.job_description else '',
                'eligibility_criteria': drive.eligibility_criteria,
                'min_cgpa': drive.min_cgpa,
                'allowed_branches': drive.allowed_branches,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'already_applied': already_applied,
                # ✅ ADD ELIGIBILITY OBJECT (same as detail view)
                'eligibility': {
                    'cgpa_eligible': cgpa_eligible,
                    'branch_eligible': branch_eligible,
                    'deadline_active': deadline_active,
                    'is_eligible': is_eligible,
                    'already_applied': already_applied
                }
            })
        
        return make_response(jsonify({
            'drives': result_drives,
            'count': len(result_drives)
        }), 200)
'''
class StudentDriveDetailAPI(Resource):
    """View specific drive details"""
    @auth_token_required
    @roles_required('student')
    def get(self, drive_id):
        student = get_current_student()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check if drive is approved
        if drive.status != 'approved':
            return make_response(jsonify({'message': 'Drive not available'}), 404)
        
        # Check if already applied
        application = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        return make_response(jsonify({
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'eligibility_criteria': drive.eligibility_criteria,
                'min_cgpa': drive.min_cgpa,
                'allowed_branches': drive.allowed_branches,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'company': {
                    'id': drive.company.id,
                    'name': drive.company.company_name,
                    'website': drive.company.website,
                    'industry': drive.company.industry,
                    'location': drive.company.location,
                    'description': drive.company.company_description
                }
            },
            'eligibility_status': {
                'cgpa_eligible': not drive.min_cgpa or student.cgpa >= drive.min_cgpa,
                'branch_eligible': not drive.allowed_branches or student.branch in drive.allowed_branches.split(','),
                'already_applied': application is not None
            },
            'application': application.to_dict() if application else None
        }), 200)
'''
class StudentDriveDetailAPI(Resource):
    """View specific drive details"""
    @auth_token_required
    @roles_required('student')
    def get(self, drive_id):
        student = get_current_student()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check if drive is approved
        if drive.status != 'approved':
            return make_response(jsonify({'message': 'Drive not available'}), 404)
        
        # Check if already applied
        application = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        # Check CGPA eligibility
        cgpa_eligible = not drive.min_cgpa or student.cgpa >= drive.min_cgpa
        
        # Check branch eligibility using our function
        branch_eligible = True
        if drive.allowed_branches:
            branch_eligible = is_branch_eligible(student.branch, drive.allowed_branches)
        
        # Check deadline
        deadline_active = True
        if drive.application_deadline and drive.application_deadline < datetime.utcnow():
            deadline_active = False
        
        # Overall eligibility
        is_eligible = cgpa_eligible and branch_eligible and deadline_active
        
        return make_response(jsonify({
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'eligibility_criteria': drive.eligibility_criteria,
                'min_cgpa': drive.min_cgpa,
                'allowed_branches': drive.allowed_branches,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'company': {
                    'id': drive.company.id,
                    'name': drive.company.company_name,
                    'website': drive.company.website,
                    'industry': drive.company.industry,
                    'location': drive.company.location,
                    'description': drive.company.company_description
                },
                # ✅ ADD ELIGIBILITY OBJECT (same as list view)
                'eligibility': {
                    'cgpa_eligible': cgpa_eligible,
                    'branch_eligible': branch_eligible,
                    'deadline_active': deadline_active,
                    'is_eligible': is_eligible,
                    'already_applied': application is not None
                }
            },
            'application': application.to_dict() if application else None
        }), 200)

'''
class StudentApplyAPI(Resource):
    """Apply to a drive"""
    @auth_token_required
    @roles_required('student')
    def post(self, drive_id):
        student = get_current_student()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check if drive is approved
        if drive.status != 'approved':
            return make_response(jsonify({'message': 'Drive not available for applications'}), 400)
        
        # Check deadline
        if drive.application_deadline and drive.application_deadline < datetime.utcnow():
            return make_response(jsonify({'message': 'Application deadline has passed'}), 400)
        
        # Check if already applied
        existing = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        if existing:
            return make_response(jsonify({'message': 'Already applied to this drive'}), 400)
        
        # Check eligibility (basic checks)
        if drive.min_cgpa and student.cgpa < drive.min_cgpa:
            return make_response(jsonify({'message': 'CGPA below eligibility criteria'}), 400)
        
        if drive.allowed_branches:
            branches = drive.allowed_branches.split(',')
            if student.branch not in branches:
                return make_response(jsonify({'message': 'Branch not eligible'}), 400)
        
        # Create application
        application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status='applied'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Successfully applied to drive',
            'application': application.to_dict()
        }), 201)
'''
class StudentApplyAPI(Resource):
    """Apply to a drive"""
    @auth_token_required
    @roles_required('student')
    def post(self, drive_id):
        student = get_current_student()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check if drive is approved
        if drive.status != 'approved':
            return make_response(jsonify({'message': 'Drive not available for applications'}), 400)
        
        # Check deadline
        if drive.application_deadline and drive.application_deadline < datetime.utcnow():
            return make_response(jsonify({'message': 'Application deadline has passed'}), 400)
        
        # Check if already applied
        existing = Application.query.filter_by(
            student_id=student.id,
            drive_id=drive.id
        ).first()
        
        if existing:
            return make_response(jsonify({'message': 'Already applied to this drive'}), 400)
        
        # Check CGPA eligibility
        if drive.min_cgpa and student.cgpa < drive.min_cgpa:
            return make_response(jsonify({'message': f'CGPA below eligibility criteria. Required: {drive.min_cgpa}'}), 400)
        
        # ✅ USE THE NEW BRANCH MAPPING FUNCTION
        if drive.allowed_branches:
            if not is_branch_eligible(student.branch, drive.allowed_branches):
                return make_response(jsonify({
                    'message': f'Branch not eligible. Your branch: {student.branch}, Allowed: {drive.allowed_branches}'
                }), 400)
        
        # Create application
        application = Application(
            student_id=student.id,
            drive_id=drive.id,
            status='applied'
        )
        
        db.session.add(application)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Successfully applied to drive',
            'application': application.to_dict()
        }), 201)

class StudentApplicationListAPI(Resource):
    """List all applications of current student"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        
        applications = Application.query.filter_by(
            student_id=student.id
        ).order_by(Application.applied_at.desc()).all()
        
        return make_response(jsonify({
            'applications': [
                {
                    'id': app.id,
                    'drive_id': app.drive_id,
                    'drive_name': app.drive.drive_name,
                    'company_name': app.drive.company.company_name,
                    'status': app.status,
                    'applied_at': app.applied_at.isoformat(),
                    'updated_at': app.updated_at.isoformat() if app.updated_at else None,
                    'interview_date': app.interview_date.isoformat() if app.interview_date else None
                } for app in applications
            ],
            'statistics': {
                'total': len(applications),
                'applied': sum(1 for a in applications if a.status == 'applied'),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected'),
                'rejected': sum(1 for a in applications if a.status == 'rejected')
            }
        }), 200)


class StudentApplicationDetailAPI(Resource):
    """View specific application details"""
    @auth_token_required
    @roles_required('student')
    def get(self, application_id):
        student = get_current_student()
        
        application = Application.query.get_or_404(application_id)
        
        # Check ownership
        if application.student_id != student.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        return make_response(jsonify({
            'application': {
                'id': application.id,
                'status': application.status,
                'applied_at': application.applied_at.isoformat(),
                'updated_at': application.updated_at.isoformat() if application.updated_at else None,
                'drive': {
                    'id': application.drive.id,
                    'drive_name': application.drive.drive_name,
                    'job_title': application.drive.job_title,
                    'company_name': application.drive.company.company_name
                },
                'interview': {
                    'date': application.interview_date.isoformat() if application.interview_date else None,
                    'notes': application.interview_notes
                } if application.interview_date else None
            }
        }), 200)


class StudentDashboardAPI(Resource):
    """Student dashboard with overview"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        
        # Get applications
        applications = Application.query.filter_by(student_id=student.id).all()
        
        # Get upcoming drives (next 7 days)
        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'approved',
            PlacementDrive.application_deadline >= datetime.utcnow(),
            PlacementDrive.application_deadline <= datetime.utcnow() + timedelta(days=7)
        ).limit(5).all()
        
        # Get recent applications
        recent_applications = Application.query.filter_by(
            student_id=student.id
        ).order_by(Application.applied_at.desc()).limit(5).all()
        
        return make_response(jsonify({
            'student': student.to_dict(),
            'statistics': {
                'total_applications': len(applications),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected'),
                'rejected': sum(1 for a in applications if a.status == 'rejected'),
                'pending': sum(1 for a in applications if a.status == 'applied')
            },
            'upcoming_deadlines': [
                {
                    'id': d.id,
                    'drive_name': d.drive_name,
                    'company_name': d.company.company_name,
                    'deadline': d.application_deadline.isoformat()
                } for d in upcoming_drives
            ],
            'recent_applications': [
                {
                    'id': a.id,
                    'drive_name': a.drive.drive_name,
                    'company_name': a.drive.company.company_name,
                    'status': a.status,
                    'applied_at': a.applied_at.isoformat()
                } for a in recent_applications
            ]
        }), 200)


class StudentHistoryAPI(Resource):
    """Placement history for student"""
    @auth_token_required
    @roles_required('student')
    def get(self):
        student = get_current_student()
        
        # Get all applications with final status
        applications = Application.query.filter_by(
            student_id=student.id
        ).order_by(Application.applied_at.desc()).all()
        
        return make_response(jsonify({
            'history': [
                {
                    'id': a.id,
                    'drive_name': a.drive.drive_name,
                    'company_name': a.drive.company.company_name,
                    'job_title': a.drive.job_title,
                    'applied_at': a.applied_at.isoformat(),
                    'final_status': a.status,
                    'selected_at': a.selected_at.isoformat() if a.selected_at else None,
                    'interview_date': a.interview_date.isoformat() if a.interview_date else None
                } for a in applications
            ],
            'summary': {
                'total_applications': len(applications),
                'selections': sum(1 for a in applications if a.status == 'selected'),
                'placements_by_company': {}
            }
        }), 200)


# ==================== COMPANY APIS ====================

class CompanyProfileAPI(Resource):
    """Get and update company profile"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = get_current_company()
        if not company:
            return make_response(jsonify({'message': 'Company profile not found'}), 404)
        
        return make_response(jsonify({
            'profile': company.to_dict()
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def put(self):
        company = get_current_company()
        if not company:
            return make_response(jsonify({'message': 'Company profile not found'}), 404)
        
        data = request.get_json()
        
        # Update allowed fields
        if data.get('hr_name'):
            company.hr_name = data['hr_name']
        if data.get('hr_email'):
            company.hr_email = data['hr_email']
        if data.get('hr_phone'):
            company.hr_phone = data['hr_phone']
        if data.get('website'):
            company.website = data['website']
        if data.get('industry'):
            company.industry = data['industry']
        if data.get('location'):
            company.location = data['location']
        if data.get('description'):
            company.company_description = data['description']
        
        company.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Profile updated successfully',
            'profile': company.to_dict()
        }), 200)


class CompanyDriveCreateAPI(Resource):
    """Create a new placement drive"""
    @auth_token_required
    @roles_required('company')
    def post(self):
        company = get_current_company()
        
        # Check if company is approved
        if company.approval_status != 'approved':
            return make_response(jsonify({
                'message': 'Your company is not approved yet. Cannot create drives.'
            }), 403)
        
        data = request.get_json()
        
        # Validate required fields
        required = ['drive_name', 'job_title', 'job_description', 'application_deadline']
        missing = [f for f in required if f not in data]
        if missing:
            return make_response(jsonify({
                'message': f'Missing fields: {", ".join(missing)}'
            }), 400)
        
        # Create drive
        drive = PlacementDrive(
            company_id=company.id,
            drive_name=data['drive_name'],
            job_title=data['job_title'],
            job_description=data['job_description'],
            eligibility_criteria=data.get('eligibility_criteria', ''),
            min_cgpa=data.get('min_cgpa'),
            allowed_branches=data.get('allowed_branches'),
            application_deadline=datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00')),
            drive_date=datetime.fromisoformat(data['drive_date'].replace('Z', '+00:00')) if data.get('drive_date') else None,
            status='pending'  # Needs admin approval
        )
        
        db.session.add(drive)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Drive created successfully. Pending admin approval.',
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'status': drive.status
            }
        }), 201)


class CompanyDriveListAPI(Resource):
    """List all drives created by the company"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = get_current_company()
        
        drives = PlacementDrive.query.filter_by(
            company_id=company.id
        ).order_by(PlacementDrive.created_at.desc()).all()
        
        return make_response(jsonify({
            'drives': [
                {
                    'id': d.id,
                    'drive_name': d.drive_name,
                    'job_title': d.job_title,
                    'status': d.status,
                    'application_deadline': d.application_deadline.isoformat() if d.application_deadline else None,
                    'created_at': d.created_at.isoformat(),
                    'application_count': d.applications.count(),
                    'shortlisted_count': d.applications.filter_by(status='shortlisted').count(),
                    'selected_count': d.applications.filter_by(status='selected').count()
                } for d in drives
            ]
        }), 200)


class CompanyDriveDetailAPI(Resource):
    """View details of a specific drive"""
    @auth_token_required
    @roles_required('company')
    def get(self, drive_id):
        company = get_current_company()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check ownership
        if drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        return make_response(jsonify({
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'job_description': drive.job_description,
                'eligibility_criteria': drive.eligibility_criteria,
                'min_cgpa': drive.min_cgpa,
                'allowed_branches': drive.allowed_branches,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'drive_date': drive.drive_date.isoformat() if drive.drive_date else None,
                'status': drive.status,
                'created_at': drive.created_at.isoformat(),
                'approved_at': drive.approved_at.isoformat() if drive.approved_at else None
            }
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def put(self, drive_id):
        """Update drive (only if pending)"""
        company = get_current_company()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check ownership
        if drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only update if pending
        if drive.status != 'pending':
            return make_response(jsonify({
                'message': 'Can only update pending drives'
            }), 400)
        
        data = request.get_json()
        
        # Update fields
        if data.get('drive_name'):
            drive.drive_name = data['drive_name']
        if data.get('job_title'):
            drive.job_title = data['job_title']
        if data.get('job_description'):
            drive.job_description = data['job_description']
        if data.get('eligibility_criteria'):
            drive.eligibility_criteria = data['eligibility_criteria']
        if data.get('min_cgpa'):
            drive.min_cgpa = data['min_cgpa']
        if data.get('allowed_branches'):
            drive.allowed_branches = data['allowed_branches']
        if data.get('application_deadline'):
            drive.application_deadline = datetime.fromisoformat(data['application_deadline'].replace('Z', '+00:00'))
        if data.get('drive_date'):
            drive.drive_date = datetime.fromisoformat(data['drive_date'].replace('Z', '+00:00'))
        
        drive.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Drive updated successfully',
            'drive': {
                'id': drive.id,
                'drive_name': drive.drive_name,
                'status': drive.status
            }
        }), 200)
    
    @auth_token_required
    @roles_required('company')
    def delete(self, drive_id):
        """Delete drive (only if pending)"""
        company = get_current_company()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check ownership
        if drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only delete if pending
        if drive.status != 'pending':
            return make_response(jsonify({
                'message': 'Can only delete pending drives'
            }), 400)
        
        db.session.delete(drive)
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Drive deleted successfully'
        }), 200)


class CompanyApplicationListAPI(Resource):
    """List all applications for a specific drive"""
    @auth_token_required
    @roles_required('company')
    def get(self, drive_id):
        company = get_current_company()
        drive = PlacementDrive.query.get_or_404(drive_id)
        
        # Check ownership
        if drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Get filter from query params
        status = request.args.get('status')  # applied, shortlisted, selected, rejected
        
        query = Application.query.filter_by(drive_id=drive.id)
        if status:
            query = query.filter_by(status=status)
        
        applications = query.order_by(Application.applied_at).all()
        
        return make_response(jsonify({
            'drive_name': drive.drive_name,
            'job_title': drive.job_title,
            'total_applications': len(applications),
            'applications': [
                {
                    'id': a.id,
                    'student_id': a.student.id,
                    'student_name': a.student.name,
                    'student_roll': a.student.roll_number,
                    'student_branch': a.student.branch,
                    'student_cgpa': a.student.cgpa,
                    'student_email': a.student.user.email,
                    'student_phone': a.student.phone,
                    'status': a.status,
                    'applied_at': a.applied_at.isoformat(),
                    'has_resume': bool(a.student.resume_path)
                } for a in applications
            ],
            'statistics': {
                'applied': sum(1 for a in applications if a.status == 'applied'),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected'),
                'rejected': sum(1 for a in applications if a.status == 'rejected')
            }
        }), 200)


class CompanyApplicationShortlistAPI(Resource):
    """Shortlist a student for interview"""
    @auth_token_required
    @roles_required('company')
    def post(self, application_id):
        company = get_current_company()
        application = Application.query.get_or_404(application_id)
        
        # Check drive ownership
        if application.drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only shortlist applied students
        if application.status != 'applied':
            return make_response(jsonify({
                'message': f'Student already {application.status}'
            }), 400)
        
        application.status = 'shortlisted'
        application.shortlisted_at = datetime.utcnow()
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Student shortlisted successfully',
            'application': {
                'id': application.id,
                'student_name': application.student.name,
                'status': application.status
            }
        }), 200)


class CompanyApplicationSelectAPI(Resource):
    """Select a student (final selection)"""
    @auth_token_required
    @roles_required('company')
    def post(self, application_id):
        company = get_current_company()
        application = Application.query.get_or_404(application_id)
        
        # Check drive ownership
        if application.drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        # Can only select shortlisted students
        if application.status != 'shortlisted':
            return make_response(jsonify({
                'message': 'Student must be shortlisted first'
            }), 400)
        
        application.status = 'selected'
        application.selected_at = datetime.utcnow()
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Student selected successfully',
            'application': {
                'id': application.id,
                'student_name': application.student.name,
                'status': application.status
            }
        }), 200)


class CompanyApplicationRejectAPI(Resource):
    """Reject a student"""
    @auth_token_required
    @roles_required('company')
    def post(self, application_id):
        company = get_current_company()
        application = Application.query.get_or_404(application_id)
        
        # Check drive ownership
        if application.drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        data = request.get_json() or {}
        reason = data.get('reason', 'No reason provided')
        
        application.status = 'rejected'
        application.rejected_at = datetime.utcnow()
        application.rejection_reason = reason
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Student rejected',
            'application': {
                'id': application.id,
                'student_name': application.student.name,
                'status': application.status
            }
        }), 200)


class CompanyInterviewScheduleAPI(Resource):
    """Schedule interview for a student"""
    @auth_token_required
    @roles_required('company')
    def post(self, application_id):
        company = get_current_company()
        application = Application.query.get_or_404(application_id)
        
        # Check drive ownership
        if application.drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        data = request.get_json()
        
        if not data or not data.get('interview_date'):
            return make_response(jsonify({
                'message': 'Interview date is required'
            }), 400)
        
        application.interview_date = datetime.fromisoformat(data['interview_date'].replace('Z', '+00:00'))
        application.interview_notes = data.get('notes', '')
        application.updated_at = datetime.utcnow()
        db.session.commit()
        
        return make_response(jsonify({
            'message': 'Interview scheduled successfully',
            'application': {
                'id': application.id,
                'student_name': application.student.name,
                'interview_date': application.interview_date.isoformat()
            }
        }), 200)

'''
class CompanyDashboardAPI(Resource):
    """Company dashboard with statistics"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = get_current_company()
        
        # Get all drives
        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        drive_ids = [d.id for d in drives]
        
        # Get all applications for company's drives
        applications = Application.query.filter(
            Application.drive_id.in_(drive_ids)
        ).all() if drive_ids else []
        
        # Upcoming interviews
        upcoming_interviews = [
            a for a in applications 
            if a.interview_date and a.interview_date >= datetime.utcnow()
        ]
        
        return make_response(jsonify({
            'company': company.to_dict(),
            'statistics': {
                'total_drives': len(drives),
                'pending_drives': sum(1 for d in drives if d.status == 'pending'),
                'active_drives': sum(1 for d in drives if d.status == 'approved'),
                'total_applications': len(applications),
                'shortlisted': sum(1 for a in applications if a.status == 'shortlisted'),
                'selected': sum(1 for a in applications if a.status == 'selected')
            },
            'recent_applications': [
                {
                    'id': a.id,
                    'student_name': a.student.name,
                    'drive_name': a.drive.drive_name,
                    'status': a.status,
                    'applied_at': a.applied_at.isoformat()
                } for a in sorted(applications, key=lambda x: x.applied_at, reverse=True)[:5]
            ],
            'upcoming_interviews': [
                {
                    'id': a.id,
                    'student_name': a.student.name,
                    'drive_name': a.drive.drive_name,
                    'interview_date': a.interview_date.isoformat()
                } for a in upcoming_interviews[:5]
            ]
        }), 200)
'''
class CompanyDashboardAPI(Resource):
    """Company dashboard with statistics and recent items"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = get_current_company()
        
        # Get all drives
        drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(
            PlacementDrive.created_at.desc()
        ).all()
        drive_ids = [d.id for d in drives]
        
        # Get all applications for company's drives
        applications = Application.query.filter(
            Application.drive_id.in_(drive_ids)
        ).all() if drive_ids else []
        
        # Calculate statistics
        total_applications = len(applications)
        shortlisted = sum(1 for a in applications if a.status == 'shortlisted')
        selected = sum(1 for a in applications if a.status == 'selected')
        rejected = sum(1 for a in applications if a.status == 'rejected')
        
        # Upcoming interviews
        upcoming_interviews = [
            a for a in applications 
            if a.interview_date and a.interview_date >= datetime.utcnow()
        ]
        
        # Get recent drives (last 5)
        recent_drives = []
        for drive in drives[:5]:
            recent_drives.append({
                'id': drive.id,
                'drive_name': drive.drive_name,
                'job_title': drive.job_title,
                'status': drive.status,
                'application_deadline': drive.application_deadline.isoformat() if drive.application_deadline else None,
                'created_at': drive.created_at.isoformat() if drive.created_at else None,
                'application_count': Application.query.filter_by(drive_id=drive.id).count()
            })
        
        # Get recent applications (last 5)
        recent_applications = []
        sorted_apps = sorted(applications, key=lambda x: x.applied_at, reverse=True)[:5]
        for app in sorted_apps:
            recent_applications.append({
                'id': app.id,
                'student_name': app.student.name,
                'student_roll': app.student.roll_number,
                'drive_id': app.drive_id,
                'drive_name': app.drive.drive_name,
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'interview_date': app.interview_date.isoformat() if app.interview_date else None
            })
        
        return make_response(jsonify({
            'company': company.to_dict(),
            'statistics': {
                'total_drives': len(drives),
                'pending_drives': sum(1 for d in drives if d.status == 'pending'),
                'approved_drives': sum(1 for d in drives if d.status == 'approved'),
                'active_drives': sum(1 for d in drives if d.status == 'approved'),
                'total_applications': total_applications,
                'shortlisted': shortlisted,
                'selected': selected,
                'rejected': rejected
            },
            # ✅ Add these fields that your frontend expects
            'recent_drives': recent_drives,
            'recent_applications': recent_applications,
            'upcoming_interviews': [
                {
                    'id': a.id,
                    'student_name': a.student.name,
                    'drive_name': a.drive.drive_name,
                    'interview_date': a.interview_date.isoformat() if a.interview_date else None
                } for a in upcoming_interviews[:5]
            ]
        }), 200)

class CompanyApplicationsAPI(Resource):
    """List all applications across all drives of the company"""
    @auth_token_required
    @roles_required('company')
    def get(self):
        company = get_current_company()
        
        # Get query parameters for filtering
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        drive_id = request.args.get('drive_id')
        status = request.args.get('status')
        search = request.args.get('search')
        
        # Base query - all applications for company's drives
        query = Application.query.join(PlacementDrive).filter(
            PlacementDrive.company_id == company.id
        )
        
        # Apply filters
        if drive_id:
            query = query.filter(Application.drive_id == drive_id)
        
        if status:
            query = query.filter(Application.status == status)
        
        if search:
            query = query.join(Student).filter(
                Student.name.ilike(f'%{search}%')
            )
        
        # Order by most recent first
        query = query.order_by(Application.applied_at.desc())
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Format response
        applications = []
        for app in paginated.items:
            applications.append({
                'id': app.id,
                'student_id': app.student.id,
                'student_name': app.student.name,
                'student_roll': app.student.roll_number,
                'student_branch': app.student.branch,
                'student_cgpa': app.student.cgpa,
                'student_email': app.student.user.email,
                'student_phone': app.student.phone,
                'drive_id': app.drive_id,
                'drive_name': app.drive.drive_name,
                'job_title': app.drive.job_title,
                'status': app.status,
                'applied_at': app.applied_at.isoformat() if app.applied_at else None,
                'interview_date': app.interview_date.isoformat() if app.interview_date else None,
                'has_resume': bool(app.student.resume_path)
            })
        
        return make_response(jsonify({
            'success': True,
            'applications': applications,
            'pagination': {
                'current_page': paginated.page,
                'last_page': paginated.pages,
                'per_page': paginated.per_page,
                'total': paginated.total,
                'from': (paginated.page - 1) * paginated.per_page + 1 if paginated.total > 0 else 0,
                'to': min(paginated.page * paginated.per_page, paginated.total)
            }
        }), 200)
    
class CompanyApplicationDetailAPI(Resource):
    """Get details of a specific application"""
    @auth_token_required
    @roles_required('company')
    def get(self, application_id):
        company = get_current_company()
        application = Application.query.get_or_404(application_id)
        
        # Check if this application belongs to company's drive
        if application.drive.company_id != company.id:
            return make_response(jsonify({'message': 'Unauthorized'}), 403)
        
        return make_response(jsonify({
            'success': True,
            'application': {
                'id': application.id,
                'student_id': application.student.id,
                'student_name': application.student.name,
                'student_roll': application.student.roll_number,
                'student_branch': application.student.branch,
                'student_cgpa': application.student.cgpa,
                'student_email': application.student.user.email,
                'student_phone': application.student.phone,
                'drive_id': application.drive_id,
                'drive_name': application.drive.drive_name,
                'job_title': application.drive.job_title,
                'job_description': application.drive.job_description,
                'eligibility_criteria': application.drive.eligibility_criteria,
                'min_cgpa': application.drive.min_cgpa,
                'allowed_branches': application.drive.allowed_branches,
                'application_deadline': application.drive.application_deadline.isoformat() if application.drive.application_deadline else None,
                'drive_date': application.drive.drive_date.isoformat() if application.drive.drive_date else None,
                'drive_status': application.drive.status,
                'status': application.status,
                'applied_at': application.applied_at.isoformat() if application.applied_at else None,
                'interview_date': application.interview_date.isoformat() if application.interview_date else None,
                'interview_notes': application.interview_notes,
                'rejection_reason': application.rejection_reason,
                'shortlisted_at': application.shortlisted_at.isoformat() if application.shortlisted_at else None,
                'selected_at': application.selected_at.isoformat() if application.selected_at else None,
                'rejected_at': application.rejected_at.isoformat() if application.rejected_at else None,
                'has_resume': bool(application.student.resume_path)
            }
        }), 200)
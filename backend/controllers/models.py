# backend/controllers/models.py
from controllers.database import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime

# Association table for roles and users
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Pre-defined role constants
    ADMIN = 'admin'
    COMPANY = 'company'
    STUDENT = 'student'


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=True)
    
    # Flask-Security-Too required fields
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=True)
    
    # Flask-Security-Too trackable fields
    last_login_at = db.Column(db.DateTime)
    current_login_at = db.Column(db.DateTime)
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    
    # ✅ FIXED: Added foreign_keys to specify which column to use
    student_profile = db.relationship(
        'Student', 
        backref='user', 
        uselist=False, 
        cascade='all, delete-orphan',
        foreign_keys='Student.user_id'  # Explicitly specify the foreign key
    )
    
    company_profile = db.relationship(
        'Company', 
        backref='user', 
        uselist=False, 
        cascade='all, delete-orphan',
        foreign_keys='Company.user_id'  # Explicitly specify the foreign key
    )
    
    @property
    def is_admin(self):
        return any(role.name == Role.ADMIN for role in self.roles)
    
    @property
    def is_company(self):
        return any(role.name == Role.COMPANY for role in self.roles)
    
    @property
    def is_student(self):
        return any(role.name == Role.STUDENT for role in self.roles)
    
    def get_role_name(self):
        """Get the primary role name"""
        if self.roles:
            return self.roles[0].name
        return None
    
    def get_profile(self):
        """Get role-specific profile"""
        if self.is_student:
            return self.student_profile
        elif self.is_company:
            return self.company_profile
        return None
    
    def __repr__(self):
        return f'<User {self.email}>'


class Student(db.Model):
    __tablename__ = 'student'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Personal Info
    name = db.Column(db.String(255), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)
    
    # Contact
    phone = db.Column(db.String(20))
    alternate_email = db.Column(db.String(255))
    
    # Resume
    resume_path = db.Column(db.String(255))
    resume_filename = db.Column(db.String(255))
    resume_uploaded_at = db.Column(db.DateTime)
    
    # Status
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(500))
    blacklisted_at = db.Column(db.DateTime)
    blacklisted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('Application', backref='student', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'roll_number': self.roll_number,
            'branch': self.branch,
            'cgpa': self.cgpa,
            'graduation_year': self.graduation_year,
            'phone': self.phone,
            'email': self.user.email if self.user else None,
            'has_resume': bool(self.resume_path),
            'is_blacklisted': self.is_blacklisted
        }
    
    def __repr__(self):
        return f'<Student {self.roll_number}: {self.name}>'


class Company(db.Model):
    __tablename__ = 'company'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    
    # Company Info
    company_name = db.Column(db.String(255), nullable=False)
    company_description = db.Column(db.Text)
    
    # HR Contact
    hr_name = db.Column(db.String(255), nullable=False)
    hr_email = db.Column(db.String(255), nullable=False)
    hr_phone = db.Column(db.String(20))
    
    # Company Details
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    
    # Status
    approval_status = db.Column(db.String(50), default='pending')  # pending, approved, rejected
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    rejection_reason = db.Column(db.String(500))
    
    is_blacklisted = db.Column(db.Boolean, default=False)
    blacklist_reason = db.Column(db.String(500))
    blacklisted_at = db.Column(db.DateTime)
    blacklisted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    drives = db.relationship('PlacementDrive', backref='company', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'hr_name': self.hr_name,
            'hr_email': self.hr_email,
            'hr_phone': self.hr_phone,
            'website': self.website,
            'industry': self.industry,
            'location': self.location,
            'approval_status': self.approval_status,
            'is_blacklisted': self.is_blacklisted
        }
    
    def __repr__(self):
        return f'<Company {self.company_name}>'


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    
    # Drive Details
    drive_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.Text)
    
    # Eligibility
    eligibility_criteria = db.Column(db.Text)
    min_cgpa = db.Column(db.Float)
    allowed_branches = db.Column(db.String(500))  # Comma-separated
    
    # Dates
    application_deadline = db.Column(db.DateTime, nullable=False)
    drive_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, closed
    approved_at = db.Column(db.DateTime)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    applications = db.relationship('Application', backref='drive', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'drive_name': self.drive_name,
            'job_title': self.job_title,
            'company_name': self.company.company_name if self.company else None,
            'application_deadline': self.application_deadline.isoformat() if self.application_deadline else None,
            'status': self.status,
            'application_count': self.applications.count()
        }
    
    def __repr__(self):
        return f'<PlacementDrive {self.drive_name}>'


class Application(db.Model):
    __tablename__ = 'application'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    
    # Application Details
    status = db.Column(db.String(50), default='applied')  # applied, shortlisted, selected, rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Interview Details
    interview_date = db.Column(db.DateTime)
    interview_notes = db.Column(db.Text)
    
    # Selection Details
    shortlisted_at = db.Column(db.DateTime)
    selected_at = db.Column(db.DateTime)
    rejected_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.String(500))
    
    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_name': self.student.name if self.student else None,
            'drive_name': self.drive.drive_name if self.drive else None,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }
    
    def __repr__(self):
        return f'<Application {self.id}>'
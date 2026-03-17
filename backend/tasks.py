# backend/tasks.py
from celery_app import celery
from datetime import datetime, timedelta
import csv
import os
from controllers.database import db
from controllers.models import Company, Student, PlacementDrive, Application, User, Role
from mail import send_email
from flask import current_app

# Helper to get admin emails
def get_admin_emails():
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admins = User.query.filter(User.roles.contains(admin_role)).all()
        return [admin.email for admin in admins if admin.email]
    return []

# -------------------- DAILY REMINDERS (for upcoming deadlines) --------------------
@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    """
    Send reminders to students about upcoming application deadlines.
    Runs daily at configured time (9 AM).
    """
    print("📧 Daily reminders task started")

    # Find drives with deadlines in the next 2 days
    now = datetime.utcnow()
    day_after = now + timedelta(days=2)

    upcoming_drives = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.application_deadline >= now,
        PlacementDrive.application_deadline <= day_after
    ).all()

    if not upcoming_drives:
        print("No upcoming deadlines in the next 2 days")
        return "No upcoming deadlines"

    # Get all active students
    students = Student.query.filter_by(is_blacklisted=False).all()
    if not students:
        print("No students to notify")
        return "No students"

    # Build email content
    drive_list_html = "<ul>"
    for drive in upcoming_drives:
        company_name = drive.company.company_name if drive.company else "Unknown Company"
        deadline_str = drive.application_deadline.strftime('%Y-%m-%d %H:%M UTC')
        drive_list_html += f"<li><strong>{drive.drive_name}</strong> at {company_name}<br>"
        drive_list_html += f"Job Title: {drive.job_title}<br>"
        drive_list_html += f"Eligibility: {drive.eligibility_criteria or 'Not specified'}<br>"
        drive_list_html += f"Deadline: {deadline_str}</li><br>"
    drive_list_html += "</ul>"

    subject = "🔔 Reminder: Upcoming Placement Drive Deadlines"
    html_body = f"""
    <h2>Upcoming Application Deadlines</h2>
    <p>The following drives have deadlines within the next 2 days:</p>
    {drive_list_html}
    <p>Log in to the placement portal to apply or view details.</p>
    <hr>
    <p><em>Placement Cell</em></p>
    """

    # Send to each student
    sent_count = 0
    for student in students:
        if student.user and student.user.email:
            success, _ = send_email(subject, student.user.email, html_body)
            if success:
                sent_count += 1

    print(f"Sent reminders to {sent_count} students about {len(upcoming_drives)} drives")
    return f"Sent reminders to {sent_count} students"

# -------------------- NEW DRIVE NOTIFICATION --------------------
@celery.task(name="tasks.send_new_drive_notification")
def send_new_drive_notification(drive_id):
    """
    Send notification to all eligible students when a new drive is approved.
    """
    print(f"📢 New drive notification task started for drive ID: {drive_id}")
    
    drive = PlacementDrive.query.get(drive_id)
    if not drive or drive.status != 'approved':
        print(f"Drive {drive_id} not found or not approved")
        return "Drive not available"
    
    # Get all eligible students (not blacklisted)
    students = Student.query.filter_by(is_blacklisted=False).all()
    if not students:
        print("No students to notify")
        return "No students"
    
    company_name = drive.company.company_name if drive.company else "Unknown Company"
    
    subject = f"🎉 New Placement Drive: {drive.drive_name} at {company_name}"
    html_body = f"""
    <h2>New Placement Drive Announced!</h2>
    <h3>{drive.drive_name}</h3>
    <p><strong>Company:</strong> {company_name}</p>
    <p><strong>Job Title:</strong> {drive.job_title}</p>
    <p><strong>Job Description:</strong><br>{drive.job_description or 'Not specified'}</p>
    <p><strong>Eligibility Criteria:</strong> {drive.eligibility_criteria or 'Not specified'}</p>
    <p><strong>Minimum CGPA:</strong> {drive.min_cgpa or 'Not specified'}</p>
    <p><strong>Allowed Branches:</strong> {drive.allowed_branches or 'All branches'}</p>
    <p><strong>Application Deadline:</strong> {drive.application_deadline.strftime('%Y-%m-%d %H:%M UTC') if drive.application_deadline else 'Not specified'}</p>
    <p><strong>Drive Date:</strong> {drive.drive_date.strftime('%Y-%m-%d') if drive.drive_date else 'To be announced'}</p>
    <hr>
    <p>Log in to the placement portal to apply!</p>
    <p><em>Placement Cell</em></p>
    """
    
    sent_count = 0
    for student in students:
        if student.user and student.user.email:
            success, _ = send_email(subject, student.user.email, html_body)
            if success:
                sent_count += 1
    
    print(f"Sent new drive notifications to {sent_count} students")
    return f"Notified {sent_count} students about new drive"

# -------------------- MONTHLY REPORT (30-day rolling) --------------------
@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    """
    Generate monthly placement activity report for admin.
    Covers the last 30 days from today.
    """
    return _generate_monthly_report_logic()

def _generate_monthly_report_logic():
    """
    Core logic for monthly report generation - covers LAST 30 DAYS from today
    Used by both scheduled task and manual trigger
    """
    print("📊 Monthly report task started")

    # Calculate date range: last 30 days from today
    end_dt = datetime.utcnow()  # Today
    start_dt = end_dt - timedelta(days=30)  # 30 days ago

    print(f"📅 Report period: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')} (Last 30 days)")

    # 1. Number of Drives Conducted (Approved drives created in last 30 days)
    drives_count = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.created_at >= start_dt,
        PlacementDrive.created_at <= end_dt
    ).count()
    print(f"✅ Approved drives created: {drives_count}")

    # 2. Number of Students Applied (Applications with status 'applied' in last 30 days)
    applications_count = Application.query.filter(
        Application.status == 'applied',
        Application.applied_at >= start_dt,
        Application.applied_at <= end_dt
    ).count()
    print(f"✅ Applications with status 'applied': {applications_count}")

    # 3. Number of Students Selected (Applications with status 'selected' in last 30 days)
    selections_count = Application.query.filter(
        Application.status == 'selected',
        Application.selected_at >= start_dt,
        Application.selected_at <= end_dt
    ).count()
    print(f"✅ Selections with status 'selected': {selections_count}")

    # Get top companies by selections in last 30 days
    top_companies = db.session.query(
        Company.company_name,
        db.func.count(Application.id).label('selection_count')
    ).join(PlacementDrive, Company.id == PlacementDrive.company_id
    ).join(Application, PlacementDrive.id == Application.drive_id
    ).filter(
        Application.status == 'selected',
        Application.selected_at >= start_dt,
        Application.selected_at <= end_dt
    ).group_by(Company.id, Company.company_name
    ).order_by(db.desc('selection_count')
    ).limit(5).all()

    # Format month name for display (use current month)
    month_name = end_dt.strftime('%B %Y')
    
    # Top companies table
    top_companies_html = ""
    if top_companies:
        top_companies_html = "<h3>Top Companies by Selections (Last 30 Days)</h3><table border='1' cellpadding='5' style='border-collapse: collapse;'><tr><th>Company</th><th>Selections</th></tr>"
        for company, count in top_companies:
            top_companies_html += f"<tr><td>{company}</td><td>{count}</td></tr>"
        top_companies_html += "</table>"
    else:
        top_companies_html = "<p>No selections recorded in the last 30 days.</p>"

    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            h2 {{ color: #333; }}
            table {{ width: 50%; margin-bottom: 20px; }}
            th {{ background-color: #4CAF50; color: white; }}
            td, th {{ padding: 8px; text-align: left; }}
        </style>
    </head>
    <body>
        <h2>Monthly Placement Report - {month_name}</h2>
        <p><strong>Period:</strong> {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')} (Last 30 Days)</p>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse;">
            <tr style="background-color: #f2f2f2;"><th>Metric</th><th>Count</th></tr>
            <tr><td><strong>Drives Conducted (Approved)</strong></td><td>{drives_count}</td></tr>
            <tr><td><strong>Students Applied</strong></td><td>{applications_count}</td></tr>
            <tr><td><strong>Students Selected</strong></td><td>{selections_count}</td></tr>
        </table>
        <br>
        {top_companies_html}
        <p><em>Report generated by Placement Portal on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</em></p>
    </body>
    </html>
    """

    # Send to all admins
    admin_emails = get_admin_emails()
    subject = f"Monthly Placement Report - {month_name} (Last 30 Days)"

    sent_count = 0
    for email in admin_emails:
        if email:  # Make sure email is not None
            success, _ = send_email(subject, email, html_report)
            if success:
                sent_count += 1
                print(f"✅ Report sent to {email}")
            else:
                print(f"❌ Failed to send to {email}")

    print(f"📊 Monthly report sent to {sent_count} admins")
    return {
        'status': 'success',
        'message': f'Report sent to {sent_count} admins',
        'data': {
            'month': month_name,
            'period': {
                'from': start_dt.strftime('%Y-%m-%d'),
                'to': end_dt.strftime('%Y-%m-%d')
            },
            'drives_conducted': drives_count,
            'students_applied': applications_count,
            'students_selected': selections_count,
            'top_companies': [(company, int(count)) for company, count in top_companies]
        }
    }

# -------------------- EXPORT STUDENT APPLICATIONS --------------------
@celery.task(name="tasks.export_student_applications", bind=True)
def export_student_applications(self, student_id):
    """
    Export all applications of a student to a CSV file.
    Returns success message only (no status/download endpoints needed).
    """
    print(f"\n📁 Export task started for student {student_id} (task id: {self.request.id})")

    export_folder = current_app.config['EXPORT_FOLDER']
    os.makedirs(export_folder, exist_ok=True)

    try:
        student = Student.query.get(student_id)
        if not student:
            raise ValueError(f"Student with id {student_id} not found")

        applications = Application.query.filter_by(student_id=student_id).all()

        if applications:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"student_{student_id}_applications_{timestamp}.csv"
            file_path = os.path.join(export_folder, filename)

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'Student ID',
                    'Student Name',
                    'Company',
                    'Drive Title',
                    'Application Status',
                    'Applied Date',
                    'Interview Date'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for app in applications:
                    drive = app.drive
                    company = drive.company if drive else None
                    writer.writerow({
                        'Student ID': student.roll_number or student.id,
                        'Student Name': student.name,
                        'Company': company.company_name if company else 'N/A',
                        'Drive Title': drive.drive_name if drive else 'N/A',
                        'Application Status': app.status,
                        'Applied Date': app.applied_at.strftime('%Y-%m-%d %H:%M:%S') if app.applied_at else '',
                        'Interview Date': app.interview_date.strftime('%Y-%m-%d %H:%M:%S') if app.interview_date else ''
                    })

            print(f"✅ CSV file created: {file_path}")

        # Send email notification to student
        if student.user and student.user.email:
            subject = "Your Applications Export is Ready"
            if not applications:
                body = "<p>You have no applications to export.</p>"
            else:
                body = f"""
                <p>Your applications have been exported successfully.</p>
                <p>Total applications: {len(applications)}</p>
                <p>The CSV file has been generated. You can download it from your dashboard.</p>
                """
            send_email(subject, student.user.email, body)

        print(f"✅ Export task completed for student {student_id}")
        return f"Export completed for student {student_id}"

    except Exception as e:
        print(f"❌ Export task failed: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)
        raise

# Keep existing test task
@celery.task(name="tasks.test_task")
def test_task():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n🧪 TEST TASK EXECUTED at {current_time}")
    return f"Test task completed at {current_time}"
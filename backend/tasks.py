import csv
import os
from datetime import date, datetime, timedelta

from extensions import celery
from models import Student, Drive, Application, Company
from notifications import send_gchat_message, send_email
from flask import current_app


@celery.task(name='tasks.send_deadline_reminders')
def send_deadline_reminders():
    """Send reminders for drives with approaching deadlines and scheduled interviews."""
    window = current_app.config['REMINDER_WINDOW_DAYS']
    today = date.today()
    cutoff = today + timedelta(days=window)

    sent = 0

   
    open_drives = Drive.query.filter_by(status='Approved').all()
    upcoming = [d for d in open_drives if d.deadline and today <= _parse(d.deadline) <= cutoff]

    for drive in upcoming:
        applied_student_ids = {a.student_id for a in drive.applications}
        for student in Student.query.filter_by(is_blacklisted=0).all():
            if student.id in applied_student_ids:
                continue
            if not student.email:
                continue 
            eligible, _ = drive.is_eligible(student)
            if not eligible:
                continue

            subject = f"Deadline Reminder: {drive.drive_name} closes soon"
            html = f"""
            <p>Hi {student.name},</p>
            <p>The drive <strong>{drive.drive_name}</strong> ({drive.jobtitle}) at
            <strong>{drive.company.cname}</strong> closes on <strong>{drive.deadline}</strong>.
            You're eligible for it but haven't applied yet — apply before it's too late!</p>
            <p>- Placement Cell</p>
            """
            send_email(student.email, subject, html)
            sent += 1

    
    interview_apps = Application.query.filter_by(status='Interview').all()
    for appl in interview_apps:
        if not appl.interview_date or not appl.student.email:
            continue
        idate = _parse(appl.interview_date)
        if today <= idate <= cutoff:
            subject = f"Interview Reminder: {appl.drive.drive_name}"
            html = f"""
            <p>Hi {appl.student.name},</p>
            <p>Your interview for <strong>{appl.drive.drive_name}</strong> at
            <strong>{appl.drive.company.cname}</strong> is scheduled on
            <strong>{appl.interview_date}</strong>.</p>
            <p>All the best!</p>
            <p>- Placement Cell</p>
            """
            send_email(appl.student.email, subject, html)
            sent += 1

    return f"Sent {sent} reminders ({len(upcoming)} drives closing soon, {len(interview_apps)} interviews checked)"


def _parse(d_str):
    try:
        return datetime.strptime(d_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return date.max


@celery.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    """Generate a monthly placement activity report."""
    today = date.today()
    first_of_month = today.replace(day=1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)

    drives_conducted = Drive.query.filter(
        Drive.deadline >= str(last_month_start), Drive.deadline <= str(last_month_end)
    ).count()
    apps_last_month = Application.query.filter(
        Application.applied_date >= str(last_month_start),
        Application.applied_date <= str(last_month_end)
    ).all()
    selected = [a for a in apps_last_month if a.status == 'Selected']

    html = f"""
    <h2>Monthly Placement Activity Report</h2>
    <p>Period: {last_month_start} to {last_month_end}</p>
    <ul>
        <li>Drives conducted: {drives_conducted}</li>
        <li>Students applied: {len(apps_last_month)}</li>
        <li>Students selected: {len(selected)}</li>
        <li>Total registered students: {Student.query.count()}</li>
        <li>Total registered companies: {Company.query.count()}</li>
    </ul>
    """
    admin_email = current_app.config['ADMIN_EMAIL']
    send_email(admin_email, f"Placement Report — {last_month_start.strftime('%B %Y')}", html)
    return f"Report generated for {last_month_start} to {last_month_end}, sent to {admin_email}"


@celery.task(name='tasks.export_applications_csv')
def export_applications_csv(student_id: int):
    """User-triggered async job — exports student's application history to CSV."""
    student = Student.query.get(student_id)
    if not student:
        raise ValueError('Student not found')

    export_dir = current_app.config['EXPORT_FOLDER']
    os.makedirs(export_dir, exist_ok=True)
    filename = f"applications_{student.id}_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])
        for a in student.applications:
            writer.writerow([
                student.id,
                a.drive.company.cname if a.drive and a.drive.company else '',
                a.drive.drive_name if a.drive else '',
                a.status,
                a.applied_date,
            ])

    send_gchat_message(f"[{student.name}] Your application export is ready: {filename}")
    return filename
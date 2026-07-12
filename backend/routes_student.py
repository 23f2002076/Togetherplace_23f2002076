import os
from datetime import date
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from extensions import db, cache
from models import Student, Drive, Application

student_bp = Blueprint('student', __name__, url_prefix='/api/student')


def mystudent():
    uid = int(get_jwt_identity())
    return Student.query.filter_by(user_id=uid).first()


@student_bp.get('/me')
@jwt_required()
def get_me():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    return jsonify(mystudent().to_dict())


@student_bp.put('/me')
@jwt_required()
def update_me():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    data = request.form if request.form else (request.json or {})

    if 'cgpa' in data:
        try:
            cgpa = float(data['cgpa'])
        except (TypeError, ValueError):
            return jsonify({'error': 'cgpa number me daalo'}), 400
        if cgpa < 0 or cgpa > 10:
            return jsonify({'error': 'cgpa 0 se 10 ke beech honi chahiye'}), 400
        stud.cgpa = cgpa

    for f in ('name', 'email', 'phone', 'department', 'skills', 'backlogs'):
        if f in data:
            setattr(stud, f, data[f])

    if 'resume' in request.files:
        resumefile = request.files['resume']
        if resumefile.filename:
            fname = secure_filename(str(stud.user_id) + '_' + resumefile.filename)
            resumefile.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fname))
            stud.resume_name = fname

    db.session.commit()
    return jsonify(stud.to_dict())


# student ke liye saari approved drives, eligible hai ya nahi wo bhi bata do
@student_bp.get('/drives')
@jwt_required()
def open_drives():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()

    # raw drive list cache kar rahe hai (30 sec), eligibility har student ke liye alag hai
    # isliye wo cache ke bahar nikal ke fresh calculate karte hai
    cached = cache.get('open_drives_list')
    if cached is None:
        drives = Drive.query.filter_by(status='Approved').all()
        cache.set('open_drives_list', [d.id for d in drives], timeout=30)
    else:
        drives = [Drive.query.get(did) for did in cached]
        drives = [d for d in drives if d is not None]

    already_ids = {a.drive_id for a in stud.applications}

    result = []
    for d in drives:
        item = d.to_dict()
        ok, reason = d.is_eligible(stud)
        item['is_eligible'] = ok
        item['eligibility_reason'] = reason
        item['already_applied'] = d.id in already_ids
        result.append(item)
    return jsonify(result)


@student_bp.get('/drives/<int:did>')
@jwt_required()
def view_drive(did):
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    drv = Drive.query.get_or_404(did)
    already = Application.query.filter_by(student_id=stud.id, drive_id=did).first() is not None
    ok, reason = drv.is_eligible(stud)
    item = drv.to_dict()
    item.update({'already_applied': already, 'is_eligible': ok, 'eligibility_reason': reason})
    return jsonify(item)


@student_bp.post('/drives/<int:did>/apply')
@jwt_required()
def apply_drive(did):
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    drv = Drive.query.get_or_404(did)

    if drv.status != 'Approved':
        return jsonify({'error': 'ye drive abhi open nahi hai'}), 400
    if drv.deadline and drv.deadline < str(date.today()):
        return jsonify({'error': 'application deadline nikal gayi'}), 400
    if Application.query.filter_by(student_id=stud.id, drive_id=did).first():
        return jsonify({'error': 'aap already apply kar chuke ho isme'}), 409

    # yaha asli eligibility check hota hai - cgpa, backlog, branch sab
    ok, reason = drv.is_eligible(stud)
    if not ok:
        return jsonify({'error': f'eligible nahi ho: {reason}'}), 403

    appl = Application(student_id=stud.id, drive_id=did, applied_date=str(date.today()), status='Applied')
    db.session.add(appl)
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    return jsonify(appl.to_dict()), 201


@student_bp.get('/applications')
@jwt_required()
def my_applications():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    return jsonify([a.to_dict() for a in stud.applications])


@student_bp.get('/history')
@jwt_required()
def history():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    return jsonify([a.to_dict() for a in stud.applications])


@student_bp.get('/placements')
@jwt_required()
def placements():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    stud = mystudent()
    return jsonify([p.to_dict() for p in stud.placements])


# --- yaha se celery wala async CSV export shuru hota hai ---

@student_bp.post('/export/csv')
@jwt_required()
def trigger_export():
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    from tasks import export_applications_csv
    stud = mystudent()
    task = export_applications_csv.delay(stud.id)
    return jsonify({'task_id': task.id, 'message': 'export shuru ho gaya, thoda ruko'}), 202


@student_bp.get('/export/status/<task_id>')
@jwt_required()
def export_status(task_id):
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    from tasks import celery
    task = celery.AsyncResult(task_id)
    out = {'state': task.state}
    if task.state == 'SUCCESS':
        out['filename'] = task.result
    elif task.state == 'FAILURE':
        out['error'] = str(task.info)
    return jsonify(out)


@student_bp.get('/export/download/<filename>')
@jwt_required()
def download_export(filename):
    if get_jwt()['role'] != 'student':
        return jsonify({'error': 'sirf student access kar sakta hai'}), 403
    return send_from_directory(current_app.config['EXPORT_FOLDER'], filename, as_attachment=True)

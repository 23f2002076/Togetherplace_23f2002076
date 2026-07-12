from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from extensions import db, cache
from models import Company, Drive, Application, Placement

company_bp = Blueprint('company', __name__, url_prefix='/api/company')


# logged in company ka profile nikalne ka helper, har route me use hoga
def mycompany():
    uid = int(get_jwt_identity())
    return Company.query.filter_by(user_id=uid).first()


@company_bp.get('/me')
@jwt_required()
def get_me():
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    return jsonify(mycompany().to_dict())


@company_bp.put('/me')
@jwt_required()
def update_me():
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    data = request.json or {}
    for f in ('cname', 'hr', 'website', 'industry'):
        if f in data:
            setattr(comp, f, data[f])
    db.session.commit()
    return jsonify(comp.to_dict())


@company_bp.get('/drives')
@jwt_required()
def my_drives():
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    return jsonify([d.to_dict(include_company=False) for d in Drive.query.filter_by(company_id=comp.id).all()])


@company_bp.post('/drives')
@jwt_required()
def create_drive():
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()

    # admin se approval liye bina drive nahi bana sakti company
    if comp.approval != 'Approved':
        return jsonify({'error': 'pehle admin approval lo'}), 403

    data = request.json or {}
    if not data.get('drive_name') or not data.get('jobtitle') or not data.get('deadline'):
        return jsonify({'error': 'drive_name, jobtitle aur deadline zaruri hai'}), 400
    if data['deadline'] < str(date.today()):
        return jsonify({'error': 'deadline past me nahi ho sakti'}), 400

    drv = Drive(
        company_id=comp.id,
        drive_name=data.get('drive_name'),
        jobtitle=data.get('jobtitle'),
        jobdescription=data.get('jobdescription'),
        eligible=data.get('eligible'),
        min_cgpa=float(data.get('min_cgpa') or 0),
        max_backlogs=int(data.get('max_backlogs') or 99),
        eligible_branches=data.get('eligible_branches', ''),
        skills_required=data.get('skills_required'),
        experience=data.get('experience'),
        deadline=data.get('deadline'),
        salary=data.get('salary'),
        location=data.get('location'),
    )
    db.session.add(drv)
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('open_drives_list')
    return jsonify(drv.to_dict()), 201


@company_bp.put('/drives/<int:did>')
@jwt_required()
def edit_drive(did):
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    drv = Drive.query.get_or_404(did)
    if drv.company_id != comp.id:
        return jsonify({'error': 'ye drive aapki nahi hai'}), 403

    data = request.json or {}
    for f in ('drive_name', 'jobtitle', 'jobdescription', 'eligible', 'skills_required',
              'experience', 'deadline', 'salary', 'location', 'eligible_branches'):
        if f in data:
            setattr(drv, f, data[f])
    if 'min_cgpa' in data:
        drv.min_cgpa = float(data['min_cgpa'] or 0)
    if 'max_backlogs' in data:
        drv.max_backlogs = int(data['max_backlogs'] or 99)
    db.session.commit()
    cache.delete('open_drives_list')
    return jsonify(drv.to_dict())


@company_bp.post('/drives/<int:did>/close')
@jwt_required()
def close_drive(did):
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    drv = Drive.query.get_or_404(did)
    if drv.company_id != comp.id:
        return jsonify({'error': 'ye drive aapki nahi hai'}), 403
    drv.status = 'Closed'
    db.session.commit()
    cache.delete('open_drives_list')
    return jsonify({'message': 'drive band kardi'})


@company_bp.delete('/drives/<int:did>')
@jwt_required()
def delete_drive(did):
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    drv = Drive.query.get_or_404(did)
    if drv.company_id != comp.id:
        return jsonify({'error': 'ye drive aapki nahi hai'}), 403
    Application.query.filter_by(drive_id=did).delete()
    db.session.delete(drv)
    db.session.commit()
    cache.delete('admin_dashboard_stats')
    cache.delete('open_drives_list')
    return jsonify({'message': 'drive delete ho gayi'})


@company_bp.get('/drives/<int:did>/applicants')
@jwt_required()
def view_applicants(did):
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    drv = Drive.query.get_or_404(did)
    if drv.company_id != comp.id:
        return jsonify({'error': 'ye drive aapki nahi hai'}), 403

    apps = Application.query.filter_by(drive_id=did).all()
    result = []
    for a in apps:
        item = a.to_dict()
        item['student'] = a.student.to_dict()
        result.append(item)
    return jsonify(result)


@company_bp.put('/applications/<int:app_id>')
@jwt_required()
def update_appstatus(app_id):
    if get_jwt()['role'] != 'company':
        return jsonify({'error': 'sirf company access kar sakti hai'}), 403
    comp = mycompany()
    appl = Application.query.get_or_404(app_id)
    if appl.drive.company_id != comp.id:
        return jsonify({'error': 'ye application aapki drive ki nahi hai'}), 403

    data = request.json or {}
    newstatus = data.get('status')
    allowed = {'Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected'}
    if newstatus not in allowed:
        return jsonify({'error': f'status ye hona chahiye: {allowed}'}), 400

    appl.status = newstatus
    if 'interview_date' in data:
        appl.interview_date = data['interview_date']
    if 'feedback' in data:
        appl.feedback = data['feedback']

    # student final select hua to placement record bhi bana do, history ke liye chahiye
    if newstatus == 'Selected':
        already = Placement.query.filter_by(student_id=appl.student_id, drive_id=appl.drive_id).first()
        if not already:
            db.session.add(Placement(
                student_id=appl.student_id,
                company_id=comp.id,
                drive_id=appl.drive_id,
                position=appl.drive.jobtitle,
                salary=appl.drive.salary,
                joining_date=data.get('joining_date', ''),
                created_at=str(date.today()),
            ))

    db.session.commit()
    return jsonify(appl.to_dict())

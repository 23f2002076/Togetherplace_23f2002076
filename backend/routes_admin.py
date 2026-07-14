from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt

from extensions import db, cache
from models import User, Student, Company, Drive, Application

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def clear_dash_cache():
    cache.delete('admin_dashboard_stats')


@admin_bp.get('/dashboard')
@jwt_required()
@cache.cached(timeout=30, key_prefix='admin_dashboard_stats')
def dashboard():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403

    return jsonify({
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_drives': Drive.query.count(),
        'total_applications': Application.query.count(),
        'pending_companies': [c.to_dict() for c in Company.query.filter_by(approval='Pending').all()],
        'pending_drives': [d.to_dict() for d in Drive.query.filter_by(status='Pending').all()],
    })


@admin_bp.get('/students')
@jwt_required()
def list_students():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403
    return jsonify([s.to_dict() for s in Student.query.all()])


@admin_bp.get('/companies')
@jwt_required()
def list_companies():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403
    return jsonify([c.to_dict() for c in Company.query.all()])


@admin_bp.get('/drives')
@jwt_required()
def list_drives():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403
    return jsonify([d.to_dict() for d in Drive.query.all()])


@admin_bp.get('/applications')
@jwt_required()
def list_applications():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403
    return jsonify([a.to_dict() for a in Application.query.all()])


@admin_bp.get('/search')
@jwt_required()
def search():
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can access this'}), 403

    q = request.args.get('q', '')
    stype = request.args.get('type', 'student')
    if stype == 'student':
        found = Student.query.filter(
            Student.name.like(f'%{q}%') | Student.email.like(f'%{q}%') | Student.phone.like(f'%{q}%')
        ).all()
    else:
        found = Company.query.filter(Company.cname.like(f'%{q}%')).all()
    return jsonify([r.to_dict() for r in found])


@admin_bp.post('/company/<int:cid>/approve')
@jwt_required()
def approve_comp(cid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    comp = Company.query.get_or_404(cid)
    comp.approval = 'Approved'
    db.session.commit()
    clear_dash_cache()
    return jsonify({'message': 'company approved'})


@admin_bp.post('/company/<int:cid>/reject')
@jwt_required()
def reject_comp(cid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    comp = Company.query.get_or_404(cid)
    comp.approval = 'Rejected'
    db.session.commit()
    clear_dash_cache()
    return jsonify({'message': 'company rejected'})


@admin_bp.post('/company/<int:cid>/blacklist')
@jwt_required()
def blacklist_comp(cid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    comp = Company.query.get_or_404(cid)
    comp.is_blacklisted = 1
    db.session.commit()
    return jsonify({'message': 'company blacklisted'})


@admin_bp.post('/company/<int:cid>/unblacklist')
@jwt_required()
def unblacklist_comp(cid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    comp = Company.query.get_or_404(cid)
    comp.is_blacklisted = 0
    db.session.commit()
    return jsonify({'message': 'company unblacklisted'})


@admin_bp.delete('/company/<int:cid>')
@jwt_required()
def delete_comp(cid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    comp = Company.query.get_or_404(cid)
    user = User.query.get(comp.user_id)
    
    for drv in comp.drives:
        Application.query.filter_by(drive_id=drv.id).delete()
        db.session.delete(drv)
    db.session.delete(comp)
    if user:
        db.session.delete(user)
    db.session.commit()
    clear_dash_cache()
    return jsonify({'message': 'company deleted'})


@admin_bp.post('/student/<int:sid>/blacklist')
@jwt_required()
def blacklist_stud(sid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    stud = Student.query.get_or_404(sid)
    stud.is_blacklisted = 1
    db.session.commit()
    return jsonify({'message': 'student blacklisted'})


@admin_bp.post('/student/<int:sid>/unblacklist')
@jwt_required()
def unblacklist_stud(sid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    stud = Student.query.get_or_404(sid)
    stud.is_blacklisted = 0
    db.session.commit()
    return jsonify({'message': 'student unblacklisted'})


@admin_bp.put('/student/<int:sid>')
@jwt_required()
def edit_stud(sid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    stud = Student.query.get_or_404(sid)
    data = request.json or {}
    if 'cgpa' in data:
        try:
            cgpa = float(data['cgpa'])
        except (TypeError, ValueError):
            return jsonify({'error': 'cgpa must be a number'}), 400
        if cgpa < 0 or cgpa > 10:
            return jsonify({'error': 'cgpa must be between 0 and 10'}), 400
        stud.cgpa = cgpa
    for f in ('name', 'email', 'phone', 'department', 'skills', 'backlogs'):
        if f in data:
            setattr(stud, f, data[f])
    db.session.commit()
    return jsonify(stud.to_dict())


@admin_bp.delete('/student/<int:sid>')
@jwt_required()
def delete_stud(sid):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    stud = Student.query.get_or_404(sid)
    user = User.query.get(stud.user_id)
    Application.query.filter_by(student_id=sid).delete()
    db.session.delete(stud)
    if user:
        db.session.delete(user)
    db.session.commit()
    clear_dash_cache()
    return jsonify({'message': 'student deleted'})


@admin_bp.post('/drive/<int:did>/approve')
@jwt_required()
def approve_driv(did):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    drv = Drive.query.get_or_404(did)
    drv.status = 'Approved'
    db.session.commit()
    clear_dash_cache()
    cache.delete('open_drives_list')
    return jsonify({'message': 'drive approved'})


@admin_bp.post('/drive/<int:did>/reject')
@jwt_required()
def reject_driv(did):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    drv = Drive.query.get_or_404(did)
    drv.status = 'Rejected'
    db.session.commit()
    clear_dash_cache()
    return jsonify({'message': 'drive rejected'})



@admin_bp.delete('/drive/<int:did>')
@jwt_required()
def delete_driv(did):
    if get_jwt()['role'] != 'admin':
        return jsonify({'error': 'only admin can perform this action'}), 403
    drv = Drive.query.get_or_404(did)
    Application.query.filter_by(drive_id=did).delete()
    db.session.delete(drv)
    db.session.commit()
    clear_dash_cache()
    cache.delete('open_drives_list')
    return jsonify({'message': 'drive has been deleted'})
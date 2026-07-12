import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import create_access_token

from extensions import db
from models import User, Student, Company

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


# student register karega yaha se, form ya json dono chalega
@auth_bp.post('/register/student')
def register_student():
    data = request.form if request.form else request.json or {}

    uname = data.get('username', '').strip()
    pwd = data.get('password', '')
    if not uname or not pwd:
        return jsonify({'error': 'username aur password dono chahiye'}), 400

    # duplicate username check
    if User.query.filter_by(username=uname).first():
        return jsonify({'error': 'ye username already liya hua hai'}), 409

    # cgpa 0-10 ke beech honi chahiye warna galat data chala jayega
    try:
        cgpa = float(data.get('cgpa') or 0)
    except ValueError:
        return jsonify({'error': 'cgpa number me daalo'}), 400
    if cgpa < 0 or cgpa > 10:
        return jsonify({'error': 'cgpa 0 se 10 ke beech honi chahiye'}), 400

    newuser = User(username=uname, role='student')
    newuser.set_password(pwd)
    db.session.add(newuser)
    db.session.flush()  # id abhi ke liye chahiye

    stud = Student(
        user_id=newuser.id,
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        department=data.get('department'),
        cgpa=cgpa,
        backlogs=int(data.get('backlogs') or 0),
        skills=data.get('skills'),
    )

    # resume file aya hai to save kardo
    if 'resume' in request.files:
        resumefile = request.files['resume']
        if resumefile.filename:
            fname = secure_filename(uname + '_' + resumefile.filename)
            resumefile.save(os.path.join(current_app.config['UPLOAD_FOLDER'], fname))
            stud.resume_name = fname

    db.session.add(stud)
    db.session.commit()
    return jsonify({'message': 'Registration ho gaya, ab login karlo'}), 201


# company register karegi, admin approval baad me lagega login pe
@auth_bp.post('/register/company')
def register_company():
    data = request.form if request.form else request.json or {}

    uname = data.get('username', '').strip()
    pwd = data.get('password', '')
    if not uname or not pwd:
        return jsonify({'error': 'username aur password dono chahiye'}), 400
    if User.query.filter_by(username=uname).first():
        return jsonify({'error': 'ye username already liya hua hai'}), 409

    newuser = User(username=uname, role='company')
    newuser.set_password(pwd)
    db.session.add(newuser)
    db.session.flush()

    comp = Company(
        user_id=newuser.id,
        cname=data.get('cname'),
        hr=data.get('hr'),
        website=data.get('website'),
        industry=data.get('industry'),
    )
    db.session.add(comp)
    db.session.commit()
    return jsonify({'message': 'Registration ho gaya, admin approval ka wait karo'}), 201


@auth_bp.post('/login')
def login():
    data = request.json or request.form
    uname = data.get('username', '').strip()
    pwd = data.get('password', '')

    user = User.query.filter_by(username=uname).first()
    if not user or not user.check_password(pwd):
        return jsonify({'error': 'username ya password galat hai'}), 401

    # blacklist wale student ko andar mat aane do
    if user.role == 'student' and user.student and user.student.is_blacklisted:
        return jsonify({'error': 'aapka account blacklist ho chuka hai, admin se baat karo'}), 403

    # company blacklist ya abhi approve nahi hui to bhi mat ghusne do
    if user.role == 'company' and user.company:
        if user.company.is_blacklisted:
            return jsonify({'error': 'aapki company blacklist hai, admin se baat karo'}), 403
        if user.company.approval != 'Approved':
            return jsonify({'error': 'aapki company abhi approved nahi hui'}), 403

    # jwt token banake bhej do, role bhi claim me daal diya taki har route pe check ho sake
    token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role, 'username': user.username},
    )
    return jsonify({'access_token': token, 'role': user.role, 'username': user.username})

from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin / company / student

    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    backlogs = db.Column(db.Integer, default=0)
    skills = db.Column(db.String(200))
    resume_name = db.Column(db.String(200))
    is_blacklisted = db.Column(db.Integer, default=0)

    applications = db.relationship('Application', backref='student', lazy=True, cascade='all, delete-orphan')
    placements = db.relationship('Placement', backref='student', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'name': self.name, 'email': self.email, 'phone': self.phone,
            'department': self.department, 'cgpa': self.cgpa, 'backlogs': self.backlogs,
            'skills': self.skills, 'resume_name': self.resume_name,
            'is_blacklisted': bool(self.is_blacklisted),
        }


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cname = db.Column(db.String(100))
    hr = db.Column(db.String(100))
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    approval = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected
    is_blacklisted = db.Column(db.Integer, default=0)

    drives = db.relationship('Drive', backref='company', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id, 'cname': self.cname, 'hr': self.hr, 'website': self.website,
            'industry': self.industry, 'approval': self.approval,
            'is_blacklisted': bool(self.is_blacklisted),
        }


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    drive_name = db.Column(db.String(100))
    jobtitle = db.Column(db.String(100))
    jobdescription = db.Column(db.Text)

    # free-text summary shown to students, kept from MAD-1
    eligible = db.Column(db.String(200))
    # structured eligibility, used for actual server-side validation
    min_cgpa = db.Column(db.Float, default=0)
    max_backlogs = db.Column(db.Integer, default=99)
    eligible_branches = db.Column(db.String(300), default='')  # comma-separated, blank = all branches

    skills_required = db.Column(db.String(200))
    experience = db.Column(db.String(100))
    deadline = db.Column(db.String(50))
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Pending')  # Pending / Approved / Rejected / Closed

    applications = db.relationship('Application', backref='drive', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_company=True):
        d = {
            'id': self.id, 'drive_name': self.drive_name, 'jobtitle': self.jobtitle,
            'jobdescription': self.jobdescription, 'eligible': self.eligible,
            'min_cgpa': self.min_cgpa, 'max_backlogs': self.max_backlogs,
            'eligible_branches': self.eligible_branches,
            'skills_required': self.skills_required, 'experience': self.experience,
            'deadline': self.deadline, 'salary': self.salary, 'location': self.location,
            'status': self.status, 'applicant_count': len(self.applications),
        }
        if include_company:
            d['company_id'] = self.company_id
            d['company_name'] = self.company.cname if self.company else None
        return d

    def is_eligible(self, student: Student):
        if (student.cgpa or 0) < (self.min_cgpa or 0):
            return False, f'Requires CGPA >= {self.min_cgpa}'
        if (student.backlogs or 0) > (self.max_backlogs or 99):
            return False, f'Max {self.max_backlogs} backlogs allowed'
        if self.eligible_branches:
            branches = [b.strip().lower() for b in self.eligible_branches.split(',') if b.strip()]
            if branches and (student.department or '').strip().lower() not in branches:
                return False, f'Open to: {self.eligible_branches}'
        return True, 'Eligible'


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    applied_date = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Applied')  # Applied/Shortlisted/Interview/Selected/Rejected
    interview_date = db.Column(db.String(50))
    feedback = db.Column(db.String(300))

    def to_dict(self):
        return {
            'id': self.id, 'student_id': self.student_id, 'drive_id': self.drive_id,
            'applied_date': self.applied_date, 'status': self.status,
            'interview_date': self.interview_date, 'feedback': self.feedback,
            'drive_name': self.drive.drive_name if self.drive else None,
            'company_name': self.drive.company.cname if self.drive and self.drive.company else None,
            'jobtitle': self.drive.jobtitle if self.drive else None,
            'student_name': self.student.name if self.student else None,
        }


class Placement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=True)
    position = db.Column(db.String(100))
    salary = db.Column(db.String(100))
    joining_date = db.Column(db.String(50))
    created_at = db.Column(db.String(50))

    company = db.relationship('Company')

    def to_dict(self):
        return {
            'id': self.id, 'student_id': self.student_id, 'company_id': self.company_id,
            'company_name': self.company.cname if self.company else None,
            'position': self.position, 'salary': self.salary,
            'joining_date': self.joining_date, 'created_at': self.created_at,
        }

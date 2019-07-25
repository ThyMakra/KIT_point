from sqlalchemy import Column, Integer, String, Float
from app import db


class Stakeholder(db.Model):
    __tablename__ = 'stakeholder'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    gender = Column(String)
    domain = Column(String)
    charge_rate = Column(Float(2, True, 2), default=0.00)
    user_id = db.Column(Integer, db.ForeignKey('user.id'))
    department_id = db.Column(Integer, db.ForeignKey('department.id'))
    specialty_id = db.Column(Integer, db.ForeignKey('specialty.id'))
    tasks = db.relationship('StakeholderTask', backref='stakeholder', lazy=True)
    summaries = db.relationship('StakeholderSummary', backref='stakeholder', lazy=True)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)

    def __init__(self, name, gender, domain, user_id, department_id, specialty_id, charge_rate):
        self.name = name
        self.gender = gender
        self.domain = domain
        self.user_id = user_id
        self.department_id = department_id
        self.specialty_id = specialty_id
        self.charge_rate = charge_rate

    def __repr__(self):
        return str(self.name)


class Specialty(db.Model):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    code = Column(String(5), unique=True)
    stakeholders = db.relationship('Stakeholder', backref='specialty', lazy=True)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return str(self.name)


class StakeholderTask(db.Model):
    __tablename__ = 'stakeholder_task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    status_id = Column(Integer, db.ForeignKey('task_status.id'))
    assign_to = Column(Integer, db.ForeignKey('stakeholder.id'))
    project_id = Column(Integer, db.ForeignKey('project.id'))
    planning_hour = Column(Float(2, True, 2), default=0.00)
    actual_hour = Column(Float(2, True, 2), default=0.00)
    start_date = Column(db.Date)
    deadline = Column(db.Date)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)

    def __init__(self, name, status_id, assign_to, project_id, planning_hour,
                 actual_hour, start_date, deadline):
        self.name = name
        self.assign_to = assign_to
        self.project_id = project_id
        self.planning_hour = planning_hour
        self.actual_hour = actual_hour
        self.start_date = start_date
        self.deadline = deadline
        self.status_id = status_id

    def __repr__(self):
        return str(self.name)


class StakeholderSummary(db.Model):
    __tablename__ = 'stakeholder_summary'
    id = Column(Integer, primary_key=True, autoincrement=True)
    stakeholder_id = Column(Integer, db.ForeignKey('stakeholder.id'))
    project_id = Column(Integer, db.ForeignKey('project.id'))
    estimate_point = Column(Float(2, True, 2), default=0.00)
    actual_point = Column(Float(2, True, 2), default=0.00)
    propose_point = Column(Float(2, True, 2), default=0.00)
    acquire_point = Column(Float(2, True, 2), default=0.00)
    created_at = Column(db.DateTime)
    updated_at = Column(db.DateTime)

    def __init__(self, stakeholder_id, project_id, estimate_point, actual_point, propose_point, acquire_point):
        self.stakeholder_id = stakeholder_id
        self.project_id = project_id
        self.estimate_point = estimate_point
        self.actual_point = actual_point
        self.propose_point = propose_point
        self.acquire_point = acquire_point

    def __repr__(self):
        return str(self.actual_point)

from sqlalchemy import Column, Integer, String, Float, Boolean
from app import db


class Task(db.Model):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    assign_to = Column(Integer, db.ForeignKey('student.id'))
    project_id = Column(Integer, db.ForeignKey('project.id'))
    batch_id = Column(Integer, db.ForeignKey('batch.id'))
    status_id = Column(Integer, db.ForeignKey('task_status.id'))
    planning_hour = Column(Float(2, True, 2), default=0.00)
    actual_hour = Column(Float(2, True, 2), default=0.00)
    start_date = Column(db.Date)
    deadline = Column(db.Date)
    end_date = Column(db.Date, nullable=True)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)
    reports = db.relationship('Report', backref='task', lazy=True)

    def __init__(self, name, assign_to, project, batch, status, planning_hour, actual_hour, start_date, deadline):
        self.name = name
        self.assign_to = assign_to
        self.project_id = project
        self.batch_id = batch
        self.status_id = status
        self.planning_hour = planning_hour
        self.actual_hour = actual_hour
        self.start_date = start_date
        self.deadline = deadline

    def __repr__(self):
        return str(self.name)


class Report(db.Model):
    __tablename__ = 'report'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session = Column(Integer)
    description = Column(String)
    date = Column(db.Date)
    task_id = Column(Integer, db.ForeignKey('task.id'))
    project_id = Column(Integer, db.ForeignKey('project.id'))
    student_id = Column(Integer, db.ForeignKey('student.id'))
    semester_id = Column(Integer, db.ForeignKey('semester.id'))
    batch_id = Column(Integer, db.ForeignKey('batch.id'))
    is_approved = Column(Boolean, default=False)
    approved_by = Column(String, default='', nullable=True)
    approved_date = Column(db.DateTime, nullable=True)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)

    def __init__(self, session, description, date, task, project, student, batch, semester):
        self.session = session
        self.date = date
        self.task_id = task
        self.project_id = project
        self.description = description
        self.batch_id = batch
        self.semester_id = semester
        self.student_id = student

    def __repr__(self):
        return str(self.description)


class TaskStatus(db.Model):
    __tablename__ = 'task_status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    tasks = db.relationship('Task', backref='task_status', lazy=True)
    adviser_tasks = db.relationship('StakeholderTask', backref='task_status', lazy=True)
    created_at = Column(db.DateTime)
    updated_at = Column(db.DateTime)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)


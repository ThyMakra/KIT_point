from sqlalchemy import Column, Integer, String, Float, Boolean
from app import db


# Define the ProjectSkills association table
ProjectSkills = db.Table('project_skill',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                     db.Column('skill_id', db.Integer, db.ForeignKey('skill.id', ondelete='CASCADE'))
                     )


# Define the ProjectMembers association table
ProjectMembers = db.Table('project_member',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                     db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
                     )

# Define the ProjectCategories association table
ProjectCategories = db.Table('project_category',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                     db.Column('category_id', db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'))
                     )

# Define the ProjectSubCategories association table
ProjectSubCategories = db.Table('project_sub_category',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                     db.Column('sub_category_id', db.Integer, db.ForeignKey('sub_category.id', ondelete='CASCADE'))
                     )


# Define the ProjectSubCategories association table
ProjectAdvisers = db.Table('project_adviser',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('project_id', db.Integer, db.ForeignKey('project.id', ondelete='CASCADE')),
                     db.Column('stakeholder_id', db.Integer, db.ForeignKey('stakeholder.id', ondelete='CASCADE'))
                     )


class Project(db.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True)
    code = Column(String(20), unique=True)
    status_id = Column(Integer, db.ForeignKey('status.id'))
    company_id = Column(Integer, db.ForeignKey('company.id'))
    description = Column(String)
    chairman_remark = Column(String)
    president_remark = Column(String)
    budget = Column(Integer)
    contingency = Column(Integer)
    planning_hour = Column(Float(2, True, 2), default=0.00)
    estimate_point = Column(Float(2, True, 2), default=0.00)
    actual_point = Column(Float(2, True, 2), default=0.00)
    propose_point = Column(Float(2, True, 2), default=0.00)
    acquire_point = Column(Float(2, True, 2), default=0.00)
    leader = Column(Integer, db.ForeignKey('student.id'))
    coordinator = Column(Integer, db.ForeignKey('stakeholder.id'))
    is_old = Column(Boolean)
    skills = db.relationship('Skill',
                             secondary=ProjectSkills,
                             lazy='subquery',
                             backref=db.backref('projects', lazy=True))
    members = db.relationship('Student',
                             secondary=ProjectMembers,
                             lazy='dynamic',
                             backref=db.backref('projects', lazy='dynamic'))

    advisers = db.relationship('Stakeholder',
                              secondary=ProjectAdvisers,
                              lazy='subquery',
                              backref=db.backref('projects', lazy=True))
    categories = db.relationship('Category', secondary=ProjectCategories, backref=db.backref('projects', lazy=True))
    sub_categories = db.relationship('SubCategory', secondary=ProjectSubCategories, backref=db.backref('projects',
                                                                                                       lazy=True))
    start_date = Column(db.Date)
    end_date = Column(db.Date)
    deadline = Column(db.Date)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)
    tasks = db.relationship('Task', backref='project', lazy=True)
    stakeholder_tasks = db.relationship('StakeholderTask', backref='project', lazy=True)
    stakeholder_summaries = db.relationship('StakeholderSummary', backref='project', lazy=True)
    reports = db.relationship('Report', backref='project', lazy=True)
    summaries = db.relationship('StudentSummary', backref='project', lazy=True)

    def __init__(self, name, code, company, description, budget,
                 contingency, leader, coordinator, is_old,
                 start_date, deadline, status):
        self.name = name
        self.code = code
        self.company_id = company
        self.description = description
        self.budget = budget
        self.contingency = contingency
        self.leader = leader
        self.coordinator = coordinator
        self.is_old = is_old
        self.start_date = start_date
        self.deadline = deadline
        self.status_id = status

    def __repr__(self):
        return str(self.name)


class Skill(db.Model):
    __tablename__ = 'skill'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True)
    code = Column(String(5), unique=True)
    created_at = Column(db.DateTime, nullable=True)
    updated_at = Column(db.DateTime, nullable=True)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return str(self.name)


class Category(db.Model):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    code = db.Column(String(10))
    created_at = Column(db.DateTime)
    updated_at = Column(db.DateTime)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return self.name


class SubCategory(db.Model):
    __tablename__ = 'sub_category'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    code = db.Column(String(20))
    created_at = Column(db.DateTime)
    updated_at = Column(db.DateTime)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return self.name


class Status(db.Model):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))
    projects = db.relationship('Project', backref='status', lazy=True)
    created_at = Column(db.DateTime)
    updated_at = Column(db.DateTime)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return str(self.name)

from sqlalchemy import Column, Integer, String, Float, Boolean
from app.student.models import Student
from app import db


CompanyAdviser = db.Table('company_advisers',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('company_id', db.Integer, db.ForeignKey('company.id', ondelete='CASCADE')),
                     db.Column('stakeholder_id', db.Integer, db.ForeignKey('stakeholder.id', ondelete='CASCADE'))
                     )


CompanyStaff = db.Table('company_staffs',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('company_id', db.Integer, db.ForeignKey('company.id', ondelete='CASCADE')),
                     db.Column('stakeholder_id', db.Integer, db.ForeignKey('stakeholder.id', ondelete='CASCADE'))
                     )

CompanyVicepresident = db.Table('company_vicepresidents',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('company_id', db.Integer, db.ForeignKey('company.id', ondelete='CASCADE')),
                     db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
                     ) 
# CompanyActiveMembers = db.Table('company_active_members',
#                      db.Column('id', db.Integer, primary_key=True),
#                      db.Column('company_id', db.Integer, db.ForeignKey('company.id', ondelete='CASCADE')),
#                      db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
#                      )

class CompanyActiveMembers(db.Model):
    __tablename__ = 'company_active_members'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship('Company', backref='active')
    student_id = Column(Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    student = db.relationship('Student', backref='active')


class CompanyInactiveMembers(db.Model):
    __tablename__ = 'company_inactive_members'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship('Company', backref='inactive')
    student_id = Column(Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    student = db.relationship('Student', backref='inactive')
    role = db.Column(String(20), default='Member')


class Company(db.Model):
    # __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    code = Column(String(20), unique=True)
    # using many_to_one relationship for chairman and president    
    chairman_id = Column(Integer, db.ForeignKey('stakeholder.id'))
    # chairman represents the 'Stakeholder' object with PK=chairman_id
    chairman = db.relationship('Stakeholder', backref='chairman_of', lazy=True)
    president_id = Column(Integer, db.ForeignKey('student.id'), nullable=True)
    president = db.relationship('Student', backref='president_of', lazy=True)    
    advisers = db.relationship('Stakeholder',
                              secondary=CompanyAdviser,
                              lazy='subquery',
                              backref=db.backref('adviser_of', lazy=True))
    established_date = Column(String(50), nullable=False)                                                     
    description = Column(String)
    vice_president = db.relationship('Student',
                              secondary=CompanyVicepresident,
                              lazy='subquery',
                              backref=db.backref('vice_president_of', lazy=True))
    a2a_staff = db.relationship('Stakeholder',
                              secondary=CompanyStaff,
                              lazy='subquery',
                              backref=db.backref('staff_of', lazy=True))

    members = db.relationship('Student',
                              secondary='company_active_members',
                              lazy='subquery',
                              backref=db.backref('company', lazy=True))
    inactive_members = db.relationship('Student',
                              secondary='company_inactive_members',
                              lazy='subquery',
                              backref=db.backref('former_company', lazy=True))

    projects = db.relationship('Project', backref='company', lazy=True)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
    

    def __init__(self, name, code, chairman, established_date, description, president):
        self.name = name
        self.code = code
        self.chairman_id = chairman                       
        self.established_date = established_date
        self.description = description                
        self.president_id = president


    def __repr__(self):
        return str(self.name)





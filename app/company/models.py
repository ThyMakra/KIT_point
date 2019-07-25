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
# CompanyMembers = db.Table('company_members',
#                      db.Column('id', db.Integer, primary_key=True),
#                      db.Column('company_id', db.Integer, db.ForeignKey('company.id', ondelete='CASCADE')),
#                      db.Column('student_id', db.Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
#                      )
class CompanyMembers(db.Model):
    __tablename__ = 'company_members'
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, db.ForeignKey('company.id', ondelete='CASCADE'))
    company = db.relationship('Company', backref='association')
    student_id = Column(Integer, db.ForeignKey('student.id', ondelete='CASCADE'))
    student = db.relationship('Student', backref='association')
    status = db.Column(String(10), default='Active')


class Company(db.Model):
    # __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    code = Column(String(20), unique=True)
    # using many_to_one relationship for chairman and president    
    chairman_id = Column(Integer, db.ForeignKey('stakeholder.id'))
    # chairman_re represents the 'Stakeholder' object with PK=chairman_id
    chairman = db.relationship('Stakeholder', backref='chairmanOf', lazy=True)
    president_id = Column(Integer, db.ForeignKey('student.id'))
    president = db.relationship('Student', backref='presidentOf', lazy=True)    
    advisers = db.relationship('Stakeholder',
                              secondary=CompanyAdviser,
                              lazy='subquery',
                              backref=db.backref('adviserOf', lazy=True))
    established_date = Column(String(50), nullable=False)                                                     
    description = Column(String)
    vice_president = db.relationship('Student',
                              secondary=CompanyVicepresident,
                              lazy='subquery',
                              backref=db.backref('vice_presidentOf', lazy=True))    
    a2a_staff = db.relationship('Stakeholder',
                              secondary=CompanyStaff,
                              lazy='subquery',
                              backref=db.backref('staffOf', lazy=True))        
    # members = db.relationship('Student',
    #                           secondary=CompanyMembers,
    #                           lazy='subquery',
    #                           backref=db.backref('company_member', lazy=True))
    
    members = db.relationship('Student', secondary='company_members', lazy='subquery', backref=db.backref('company', lazy=True))

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





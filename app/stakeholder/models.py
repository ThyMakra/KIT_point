from sqlalchemy import Column, Integer, String
from app import db


class Stakeholder(db.Model):
    __tablename__ = 'stakeholder'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    gender = Column(String)
    domain = Column(String(10))
    user_id = db.Column(Integer, db.ForeignKey('user.id'))
    department_id = db.Column(Integer, db.ForeignKey('department.id'))
    specialty_id = db.Column(Integer, db.ForeignKey('specialty.id'))
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)

    def __init__(self, name, gender, domain, user_id, department_id, specialty_id):
        self.name = name
        self.gender = gender
        self.domain = domain
        self.user_id = user_id
        self.department_id = department_id
        self.specialty_id = specialty_id

    def __repr__(self):
        return str(self.name)


class Specialty(db.Model):
    __tablename__ = 'specialty'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    code = Column(String(5), unique=True)
    stakeholders = db.relationship('Stakeholder', backref='specialty', lazy=True)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return str(self.name)


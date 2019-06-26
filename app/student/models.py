from sqlalchemy import Column, Integer, String, Float
from app import db
#hello world

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    roll_number = Column(String, unique=True)
    gender = Column(String)
    user_id = db.Column(Integer, db.ForeignKey('user.id'))
    batch_id = db.Column(Integer, db.ForeignKey('batch.id'))
    department_id = db.Column(Integer, db.ForeignKey('department.id'))
    rank_id = db.Column(Integer, db.ForeignKey('rank.id'))
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
  
    def __init__(self, name, roll_number, gender, user_id, batch_id, department_id, rank_id):
        self.name = name
        self.roll_number = roll_number
        self.gender = gender
        self.user_id = user_id
        self.batch_id = batch_id
        self.department_id = department_id
        self.rank_id = rank_id
  
    def __repr__(self):
        return str(self.name)
    

class Rank(db.Model):
    __tablename__ = 'rank'
    id = Column(Integer, primary_key=True)
    name = Column(String(15), unique=True)
    code = Column(String(5), unique=True)
    description = Column(String(100))
    students = db.relationship('Student', backref='rank', lazy=True)
    chargeTables = db.relationship('ChargeTable', backref='rank', lazy=True)
    created_at = Column(String(50), nullable=True)
    updated_at = Column(String(50), nullable=True)
    
    def __init__(self, name, code, description):
        self.name = name
        self.code = code
        self.description = description
        
    def __repr__(self):
        return str(self.name)
    
    
class ChargeTable(db.Model):
    __tablename__ = 'charge_table'
    id = Column(Integer, primary_key=True)
    price = Column(Float(3, True, 3))
    department_id = db.Column(Integer, db.ForeignKey('department.id'))
    batch_id = db.Column(Integer, db.ForeignKey('batch.id'))
    semester_id = db.Column(Integer, db.ForeignKey('semester.id'))
    rank_id = db.Column(Integer, db.ForeignKey('rank.id'))
    created_at = Column(String(50))
    updated_at = Column(String(50))
    
    def __init__(self, price, department_id, batch_id, semester_id, rank_id):
        self.price = price
        self.department_id = department_id
        self.batch_id = batch_id
        self.semester_id = semester_id
        self.rank_id = rank_id
        
    def __repr__(self):
        return self.price

from bcrypt import gensalt, hashpw
from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String
from app import db, login_manager

# Define the UserRoles association table
UserRoles = db.Table('user_roles',
                     db.Column('id', db.Integer, primary_key=True),
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')),
                     db.Column('role_id', db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))
                     )


class User(db.Model, UserMixin):
    # __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary=UserRoles, lazy='subquery', backref=db.backref('users', lazy=True))
    students = db.relationship('Student', backref='user', lazy=True)
    stakeholders = db.relationship('Stakeholder', backref='user', lazy=True)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)

            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
            if property == 'password':
                value = hashpw(value.encode('utf8'), gensalt())
            setattr(self, property, value)

    def __repr__(self):
      return str(self.username)


# Define the Role data-model
class Role(db.Model):
    # __tablename__ = 'roles'
    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class Department(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    code = Column(String(10))
    created_at = Column(String)
    updated_at = Column(String)
    batches = db.relationship('Batch', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)
    semesters = db.relationship('Semester', backref='department', lazy=True)
    chargeTables = db.relationship('ChargeTable', backref='department', lazy=True)
    stakeholders = db.relationship('Stakeholder', backref='department', lazy=True)

    def __init__(self, name, code):
        self.name = name
        self.code = code

    def __repr__(self):
        return str(self.name)


class Batch(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False)
    code = Column(String(10), unique=True)
    start_date = Column(String(50))
    end_date = Column(String(50))
    created_at = Column(String)
    updated_at = Column(String)
    department_id = Column(Integer, db.ForeignKey('department.id'))
    students = db.relationship('Student', backref='batch', lazy=True)
    semesters = db.relationship('Semester', backref='batch', lazy=True)
    chargeTables = db.relationship('ChargeTable', backref='batch', lazy=True)

    def __init__(self, name, code, start_date, end_date, department_id):
        self.name = name
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.department_id = department_id

    def __repr__(self):
        return str(self.name)


class Semester(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=False)
    code = Column(String(10), unique=True)
    start_date = Column(String(50))
    end_date = Column(String(50))
    created_at = Column(String)
    updated_at = Column(String)
    batch_id = Column(Integer, db.ForeignKey('batch.id'))
    department_id = Column(Integer, db.ForeignKey('department.id'))
    chargeTables = db.relationship('ChargeTable', backref='semester', lazy=True)

    def __init__(self, name, code, start_date, end_date, batch_id, department_id):
        self.name = name
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.batch_id = batch_id
        self.department_id = department_id

    def __repr__(self):
        return str(self.name)

from flask_wtf import FlaskForm
from wtforms import TextField, SelectField, StringField, FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.base.models import User, Department, Batch
from app.student.models import Rank


def get_all_users():
    return User.query.all()


def get_all_departments():
    return Department.query.all()


def get_batches():
    return Batch.query.all()


def get_ranks():
    return Rank.query.all()


class CreateStudentForm(FlaskForm):
    name = StringField('Name', id='name', _name="name")
    roll_number = StringField('Roll Number', _name="roll_number")
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')], _name="gender", id='gender')
    user = QuerySelectField('User', query_factory=get_all_users, allow_blank=True, _name="user", id='user')
    department = QuerySelectField('Department',
                                  query_factory=get_all_departments,
                                  allow_blank=True,
                                  id='department')
    batch = SelectField('Batch', choices=[], id='batch')
    rank = QuerySelectField('Rank', query_factory=get_ranks, allow_blank=True, id='rank')


class CreateRankForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')
    description = StringField('Description', id='description')


class CreateChargeTableForm(FlaskForm):
    price = FloatField('Price', id='price')
    department = QuerySelectField('Department',
                                  query_factory=get_all_departments,
                                  allow_blank=True,
                                  id='department')
    batch = SelectField('Batch', choices=[], id='batch')
    semester = SelectField('Semester', choices=[], id='semester')
    rank = QuerySelectField('Rank', query_factory=get_ranks, id='rank')

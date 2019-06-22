from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.base.models import Department, Batch


## login and registration


class LoginForm(FlaskForm):
    username = StringField('Username', id='username_login')
    password = PasswordField('Password', id='pwd_login')


class CreateAccountForm(FlaskForm):
    username = StringField('Username', id='username_create')
    email = StringField('Email')
    password = PasswordField('Password', id='pwd_create')


class CreateDepartmentForm(FlaskForm):
    name = StringField('Department', _name='name')
    code = StringField('Code', _name='code')


def get_departments():
    return Department.query.all()


def get_batches():
    return Batch.query.all()


class CreateBatchForm(FlaskForm):
    name = StringField('Batch', _name='name')
    code = StringField('Code', _name='code')
    start_date = StringField('Start Date', _name='start_date', id='single_cal1')
    end_date = StringField('End Date', _name='end_date', id='single_cal2')
    department = QuerySelectField('Department',
                                   validators=None,
                                   query_factory=get_departments,
                                   allow_blank=True, _name='department')


# def get_batches(id):
#     return Batch.query.filter_by(deparment_id=id).all()


class CreateSemesterForm(FlaskForm):
    name = StringField('Semester', _name='name')
    code = StringField('Code', _name='code')
    start_date = DateTimeField('Start Date', _name='start_date', id='single_cal1')
    end_date = DateTimeField('End Date', _name='end_date', id='single_cal2')
    department = QuerySelectField('Department',
                                   validators=None,
                                   query_factory=get_departments,
                                   allow_blank=True, id='select_department', _name='department')
    batch = SelectField('Batch', choices=[], id='select_batch', _name='batch')

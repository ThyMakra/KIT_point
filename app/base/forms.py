from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField, DateTimeField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.base.models import Department, Batch, Role


## login and registration

def get_departments():
    return Department.query.all()


def get_batches():
    return Batch.query.all()


def get_roles():
    return Role.query.all()


class LoginForm(FlaskForm):
    username = StringField('Username', id='username_login')
    password = PasswordField('Password', id='pwd_login')


class CreateRoleForm(FlaskForm):
    name = StringField('Role name', id='role')


class CreateAccountForm(FlaskForm):
    username = StringField('Username', id='username_create')
    email = StringField('Email', id='email')
    password = PasswordField('Password', id='pwd_create')
    role = QuerySelectField('Roles', query_factory=get_roles, id='role', allow_blank=True)


class CreateDepartmentForm(FlaskForm):
    name = StringField('Department', _name='name')
    code = StringField('Code', _name='code')


class CreateBatchForm(FlaskForm):
    name = StringField('Name', _name='name')
    code = StringField('Code', _name='code')
    start_date = DateTimeField('Start Date', _name='start_date', id='start_date')
    end_date = DateTimeField('End Date', _name='end_date', id='end_date')
    department = QuerySelectField('Department',
                                   validators=None,
                                   query_factory=get_departments,
                                   allow_blank=True, _name='department')


class CreateSemesterForm(FlaskForm):
    name = StringField('Semester', _name='name')
    code = StringField('Code', _name='code')
    start_date = DateTimeField('Start Date', _name='start_date', id='start_date')
    end_date = DateTimeField('End Date', _name='end_date', id='end_date')
    department = QuerySelectField('Department',
                                   validators=None,
                                   query_factory=get_departments,
                                   allow_blank=True, id='department', _name='department')
    batch = SelectField('Batch', choices=[], id='batch', _name='batch')

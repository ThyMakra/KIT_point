from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, FloatField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.base.models import User, Department
from app.stakeholder.models import Specialty
from app.task.models import TaskStatus
from app.project.models import Project


def get_all_users():
    return User.query.all()


def get_all_departments():
    return Department.query.all()


def get_all_specialties():
    return Specialty.query.all()


def get_statuses():
  return TaskStatus.query.all()


def get_projects():
  return Project.query.all()


class CreateStakeholderForm(FlaskForm):
    name = StringField('Name', id='name', _name="name")
    gender = SelectField('Gender', choices=[('M', 'Male'), ('F', 'Female')], _name="gender", id='gender')
    domain = SelectField('Domain',
                         choices=[('', '-- select --'), ('A2A', 'A2A Staff'), ('KIT', 'KIT Staff')],
                         id='domain')
    department = QuerySelectField('Department',
                                  query_factory=get_all_departments,
                                  allow_blank=True,
                                  id='department')
    specialty = QuerySelectField('Specialty', query_factory=get_all_specialties, allow_blank=True, id='specialty')
    charge_rate = FloatField('Charge Rate', id='charge_rate')
    user = QuerySelectField('User', query_factory=get_all_users, allow_blank=True, _name="user", id='user')


class CreateSpecialtyForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')


class CreateAdviserTaskForm(FlaskForm):
  name = StringField('Name', id='name', _name="name")
  project = QuerySelectField('Project', query_factory=get_projects, id='adviser_project', allow_blank=True)
  actual_hour = FloatField('Actual Hour', id='adviser_actual_hour')
  start_date = DateField('Start Date', id='start_date')
  deadline = DateField('Deadline', id='deadline')
  status = QuerySelectField('Status', query_factory=get_statuses, id='adviser_status', allow_blank=True)


class UpdateAdviserTaskForm(FlaskForm):
  name = StringField('Name', id='name', _name="name")
  project = QuerySelectField('Project', query_factory=get_projects, id='project', allow_blank=True)
  status = QuerySelectField('Status', query_factory=get_statuses, id='status', allow_blank=True)
  start_date = DateField('Start Date', id='start_date')
  deadline = DateField('Deadline', id='deadline')
  planning_hour = FloatField('Planning hour', id='planning_hour')
  actual_hour = FloatField('Actual hour', id='actual_hour')



from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, DateField, IntegerField, FloatField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.base.models import Semester
from app.project.models import Project
from app.task.models import TaskStatus


def get_statuses():
    return TaskStatus.query.all()


def get_projects():
    return Project.query.all()


def get_semesters():
    return Semester.query.all()


class CreateTaskForm(FlaskForm):
    name = StringField('Name', id='name', _name="name")
    project = QuerySelectField('Project', query_factory=get_projects, id='project', allow_blank=True)
    # assign_to = SelectField('Assign to', choices=[], id='assign_to')
    start_date = DateField('Start Date', id='start_date')
    deadline = DateField('Deadline', id='deadline')
    status = QuerySelectField('Status', query_factory=get_statuses, id='project', allow_blank=True)


class CreateTaskFormOld(FlaskForm):
    name = StringField('Name', id='name', _name="name")
    project = QuerySelectField('Project', query_factory=get_projects, id='project', allow_blank=True)
    actual_hour = FloatField('Actual hour', id='actual_hour')
    start_date = DateField('Start Date', id='start_date')
    deadline = DateField('Deadline', id='deadline')
    status = QuerySelectField('Status', query_factory=get_statuses, id='project', allow_blank=True)


class UpdateTaskForm(FlaskForm):
    name = StringField('Name', id='name', _name="name")
    project = QuerySelectField('Project', query_factory=get_projects, id='project', allow_blank=True)
    # assign_to = SelectField('Assign to', choices=[], id='assign_to')
    status = QuerySelectField('Status', query_factory=get_statuses, id='status', allow_blank=True)
    start_date = DateField('Start Date', id='start_date')
    deadline = DateField('Deadline', id='deadline')
    end_date = DateField('End Date', id='end_date')
    planning_hour = FloatField('Planning hour', id='planning_hour')
    actual_hour = FloatField('Actual hour', id='actual_hour')


class CreateReportForm(FlaskForm):
    date = DateField('Date', id='date')
    session = IntegerField('Session', id='session')
    # semester = SelectField('Semester', choices=[], id='semester')
    description = StringField('Description', id='description')


class UpdateReportForm(FlaskForm):
    date = DateField('Date', id='update-date')
    session = IntegerField('Session', id='update-session')
    # semester = SelectField('Semester', choices=[], id='update-semester')
    description = StringField('Description', id='update-description')


class CreateTaskStatusForm(FlaskForm):
    name = StringField('name', id='name')

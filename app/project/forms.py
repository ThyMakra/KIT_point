from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, TextAreaField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.stakeholder.models import Stakeholder
from app.student.models import Student
from app.project.models import Status, Category, SubCategory, Skill
from app.company.models import Company

def get_students():
    return Student.query.all()


def get_stakeholders():
    return Stakeholder.query.all()


def get_statuses():
    return Status.query.all()


def get_categories():
    return Category.query.all()


def get_sub_categories():
    return SubCategory.query.all()


def get_skills():
    return Skill.query.all()

def get_companies():
    return Company.query.all()


class CreateProjectForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')
    company = QuerySelectField('Company', query_factory=get_companies, allow_blank=False, id='company')
    category = QuerySelectField('Category', query_factory=get_categories, allow_blank=True, id='category')
    sub_category = QuerySelectField('Sub category', query_factory=get_sub_categories, allow_blank=True,
                                    id='sub_category')
    description = StringField('Description', id='description')
    budget = IntegerField('Budget', id='budget')
    contingency = IntegerField('Contingency', id='contingency')
    leader = QuerySelectField('Leader', query_factory=get_students, allow_blank=True, id='leader')
    coordinator = QuerySelectField('Coordinator', query_factory=get_stakeholders, allow_blank=True,
                                   id='coordinator')
    start_date = DateField('Start Date', id='start_date')
    deadline = DateField('Deadline', id='deadline')
    is_old = BooleanField('Is old', id='is_old')

    adviser = QuerySelectField('Advisers', query_factory=get_stakeholders, allow_blank=False, id='adviser')
    member = QuerySelectField('Members', query_factory=get_students, allow_blank=False, id='member')
    skill = QuerySelectField('Skills', query_factory=get_skills, allow_blank=False, id='skill')


class UpdateProjectForm(FlaskForm):
  name = StringField('Name', id='name')
  description = StringField('Description', id='description')
  code = StringField('Code', id='code')
  company = QuerySelectField('Company', query_factory=get_companies, allow_blank=False, id='company')
  status = QuerySelectField('Status', query_factory=get_statuses, allow_blank=True, id='status')
  category = QuerySelectField('Category', query_factory=get_categories, allow_blank=True, id='category')
  sub_category = QuerySelectField('Sub category', query_factory=get_sub_categories, allow_blank=True,
                                  id='sub_category')
  budget = IntegerField('Budget', id='budget')
  contingency = IntegerField('Contingency', id='contingency')
  estimate_point = FloatField('Estimate Point', id='estimate_point')
  actual_point = FloatField('Actual Point', id='actual_point')
  propose_point = FloatField('Propose Point', id='propose_point')
  acquire_point = FloatField('Acquire Point', id='acquire_point')
  leader = QuerySelectField('Leader', query_factory=get_students, allow_blank=True, id='leader')
  coordinator = QuerySelectField('Coordinator', query_factory=get_stakeholders, allow_blank=True,
                                 id='coordinator')
  start_date = DateField('Start Date', id='start_date')
  end_date = DateField('End Date', id='end_date')
  deadline = DateField('Deadline', id='deadline')
  is_old = BooleanField('Is old', id='is_old')

  chairman_remark = TextAreaField('Chairman Remark', id='chairman_remark')
  president_remark = TextAreaField('President Remark', id='president_remark')
  adviser = QuerySelectField('Advisers', query_factory=get_stakeholders, allow_blank=False, id='adviser')

  skill = QuerySelectField('Skills', query_factory=get_skills, allow_blank=False, id='skill')
  member = QuerySelectField('Members', query_factory=get_students, allow_blank=False, id='member')


class CreateSkillForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')


class CreateCategoryForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')


class CreateSubCategoryForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')


class CreateStatusForm(FlaskForm):
    name = StringField('Name', id='name')




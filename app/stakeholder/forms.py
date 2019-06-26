from flask_wtf import FlaskForm
from wtforms import SelectField, StringField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from app.base.models import User, Department
from app.stakeholder.models import Specialty


def get_all_users():
    return User.query.all()


def get_all_departments():
    return Department.query.all()


def get_all_specialties():
    return Specialty.query.all()


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
    user = QuerySelectField('User', query_factory=get_all_users, allow_blank=True, _name="user", id='user')


class CreateSpecialtyForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')



from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, BooleanField, TextAreaField, DateField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from app.stakeholder.models import Stakeholder
from app.student.models import Student


def get_students():    
    return Student.query.all()


def get_stakeholders():
    return Stakeholder.query.all()


class CreateCompanyForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')
    chairman = QuerySelectField('Chairman', query_factory=get_stakeholders, allow_blank=False, id='chairman')
    adviser = QuerySelectField('Technical Adviser', query_factory=get_stakeholders, allow_blank=False, id='adviser')
    established_date = DateField('Established Date', id='established_date')
    description = StringField('Description', id='description')
    president = QuerySelectField('President', query_factory=get_students, allow_blank=True, id='president')
    vice_president = QuerySelectField('Vice President', query_factory=get_students, allow_blank=False, id='vice_president')    
    a2a_staff = QuerySelectField('A2A Staff', query_factory=get_stakeholders, allow_blank=False, id='a2a_staff')
    member = QuerySelectField('Members', query_factory=get_students, allow_blank=False, id='member')
    

class UpdateCompanyForm(FlaskForm):
    name = StringField('Name', id='name')
    code = StringField('Code', id='code')
    chairman = QuerySelectField('Chairman', query_factory=get_stakeholders, allow_blank=False, id='chairman')
    adviser = QuerySelectField('Technical Adviser', query_factory=get_stakeholders, allow_blank=False, id='adviser')
    established_date = DateField('Established Date', id='established_date')
    description = StringField('Description', id='description')
    president = QuerySelectField('President', query_factory=get_students, allow_blank=False, id='president')    
    a2a_staff = QuerySelectField('A2A Staff', query_factory=get_stakeholders, allow_blank=False, id='a2a_staff')    


class UpdateMember(FlaskForm):
    member = QuerySelectField('Members', query_factory=get_students, allow_blank=False, id='member')


class UpdateVicePresident(FlaskForm):
    vice_president = QuerySelectField('Vice President', query_factory=get_students, allow_blank=False, id='vice_president')



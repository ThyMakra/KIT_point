from flask import jsonify, render_template, request, flash, redirect, url_for
from flask_login import (
  login_required,
)

from app import db
from app.company import blueprint
from app.company.forms import CreateCompanyForm, UpdateCompanyForm
from app.company.models import Company, CompanyMembers
from app.student.models import Student
from app.stakeholder.models import Stakeholder
from datetime import datetime


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


@blueprint.route('/')
@login_required
def get_company():
    company = db.session.query(Company).all()
    form = CreateCompanyForm(request.form)
    return render_template('company.html', companies=company, form=form)


@blueprint.route('/delete<int:company_id>')
@login_required
def delete_company(company_id):
    try:
        Company.query.filter_by(id=company_id).delete()
        db.session.commit()
        flash('Company deleted!')
        return redirect('/company')
    except Exception as e:
        print(e)
        flash('Delete error! some entities are referring to this')
        return redirect('/company')


@blueprint.route('/<int:company_id>', methods=['GET', 'POST'])
@login_required
def update_company(company_id):    
    form = UpdateCompanyForm(request.form)
    company = Company.query.filter_by(id=company_id).first()    
    active_members = CompanyMembers.query.filter_by(status='Active').all()
    # print("________-----",members[0].company_id)
    if request.method == 'GET':
        return render_template('/update_company.html', form=form, company=company, active_members=active_members)
    else:
        members_list = request.form.getlist('member')
        adviser_list = request.form.getlist('adviser')
        vice_president_list = request.form.getlist('vice_president')
        a2astaff_list = request.form.getlist('a2a_staff')
        
        # To remove members
        for i in company.members:
            if str(i.id) not in members_list:
                company.members.remove(db.session.query(Student).get(i.id))
        # To remove adviser
        for i in company.advisers:
            if str(i.id) not in adviser_list:
                company.advisers.remove(db.session.query(Stakeholder).get(i.id))                
        # To remove vice president
        for i in company.vice_president:
            if str(i.id) not in vice_president_list:
                company.vice_president.remove(db.session.query(Student).get(i.id))
        # To remove a2astaff
        for i in company.a2a_staff:
            if str(i.id) not in a2astaff_list:
                company.a2a_staff.remove(db.session.query(Stakeholder).get(i.id))
        # To add new members
        for i in members_list:
            members = db.session.query(Student).get(i)
            company.members.append(members)
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
            company.advisers.append(adviser)
        # To add new vice president
        for i in vice_president_list:
            vice_president = db.session.query(Student).get(i)
            company.vice_president.append(vice_president)
        #To add new staff
        for i in a2astaff_list:
            a2a_staff = db.session.query(Stakeholder).get(i)
            company.a2a_staff.append(a2a_staff)        
        company.name = request.form['name']
        company.code = request.form['code']
        company.chairman_id = request.form['chairman']
        company.president_id = request.form['president']
        company.established_date = request.form['established_date']
        company.description = request.form['description']                                
        company.updated_at = datetime.now()
        db.session.merge(company)
        db.session.commit()
        flash('Company updated')
        return redirect('/company')        

@blueprint.route('/company<int:company_id>/change_status<int:member_id>', methods=['GET', 'POST'])
@login_required
def change_member_status(company_id, member_id):    
    member = CompanyMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
    if member.status == 'Active':
        member.status = 'Not active'
    else:
        member.status = 'Active'
    db.session.commit()
    return redirect(url_for('company_blueprint.update_company', company_id=company_id))


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_company():    
    if request.method == 'GET':
        form = CreateCompanyForm(request.form)
        active_members = CompanyMembers.query.filter_by(status='Active').all()
        return render_template('create_company.html', form=form, active_members=active_members)
    name = request.form['name']
    code = request.form['code']    
    chairman = request.form['chairman']    
    adviser_list = request.form.getlist('adviser')    
    established_date = request.form['established_date']
    description = request.form['description']
    president = request.form['president']            
    vice_president_list = request.form.getlist('vice_president')
    a2astaff_list = request.form.getlist('a2a_staff')
    member_list = request.form.getlist('member')    
    is_duplicate = Company.query.filter_by(code=code, name=name).first()
    
    if is_duplicate is None:
        company = Company(name, code, chairman, established_date,
                          description, president)        
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
    # why not adviser = Stakeholder.query.all()
            company.advisers.append(adviser)
        # To add new member
        for i in vice_president_list:
            vice_president = db.session.query(Student).get(i)
            company.vice_president.append(vice_president)
            company.members.append(vice_president)
        for i in a2astaff_list:
            a2a_staff = db.session.query(Stakeholder).get(i)
            company.a2a_staff.append(a2a_staff)
#adding member but we need to remove the existing members in another company
# flash error message
        for i in member_list:            
            members = db.session.query(Student).get(i)
            company.members.append(members)
        company.created_at = datetime.now()
        db.session.add(company)
        db.session.commit()
        flash('Company created')            
    else:
        form = CreateCompanyForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_company.html', error=error, form=form)


## Errors
@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/page_500.html'), 500

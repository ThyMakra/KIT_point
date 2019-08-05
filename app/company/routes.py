from flask import jsonify, render_template, request, flash, redirect, url_for
from flask_login import (
  login_required,
)

from app import db
from app.company import blueprint
from app.company.forms import CreateCompanyForm, UpdateCompanyForm, UpdateMember, UpdateVicePresident
from app.company.models import Company, CompanyInactiveMembers, CompanyVicepresident, CompanyActiveMembers
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

    # vp = CompanyVicepresident.session.query.all()
    # advisers = Stakeholder.query.join(Company.advisers).filter_by(id=2).all()
    # # vp = Student.query.join(Company.members).filter(Student.id==)
    # print('----------------',advisers)
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


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_company():    
    if request.method == 'GET':
        form = CreateCompanyForm(request.form)
        active_members = CompanyActiveMembers.query.all()
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
        #adding member but we need to remove the existing members in another company
        # flash error message
        for i in member_list:            
            members = db.session.query(Student).get(i)
            company.members.append(members)
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
    # why not adviser = Stakeholder.query.all()
            company.advisers.append(adviser)
        # To add new member
        for i in vice_president_list:
            vice_president = db.session.query(Student).get(i)
            company.vice_president.append(vice_president)
            # add vice president to members table
            company.members.append(vice_president)
        for i in a2astaff_list:
            a2a_staff = db.session.query(Stakeholder).get(i)
            company.a2a_staff.append(a2a_staff)
        # adding president to members        
        president = Student.query.filter_by(id=company.president_id).first()
        company.members.append(president)
        # 
        company.created_at = datetime.now()
        db.session.add(company)
        db.session.commit()
        flash('Company created')
        return redirect('/company')
    else:
        form = CreateCompanyForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_company.html', error=error, form=form)        


@blueprint.route('/update_<int:company_id>', methods=['GET', 'POST'])
@login_required
def update_company(company_id):    
    form = UpdateCompanyForm(request.form)
    update_member_form = UpdateMember(request.form)
    update_vice_president_form = UpdateVicePresident(request.form)
    company = Company.query.filter_by(id=company_id).first()    
    active_members = CompanyActiveMembers.query.all()
    if request.method == 'GET':
        return render_template('/update_company.html', form=form, update_member_form=update_member_form, update_vice_president_form=update_vice_president_form, company=company, active_members=active_members)
    else:        
        adviser_list = request.form.getlist('adviser')
        # vice_president_list = request.form.getlist('vice_president')
        a2astaff_list = request.form.getlist('a2a_staff')                        
        # To remove adviser
        for i in company.advisers:
            if str(i.id) not in adviser_list:
                company.advisers.remove(db.session.query(Stakeholder).get(i.id))                
        # To remove vice president
        # for i in company.vice_president:
        #     if str(i.id) not in vice_president_list:
        #         company.vice_president.remove(db.session.query(Student).get(i.id))
        # To remove a2astaff
        for i in company.a2a_staff:
            if str(i.id) not in a2astaff_list:
                company.a2a_staff.remove(db.session.query(Stakeholder).get(i.id))        
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
            company.advisers.append(adviser)
        # To add new vice president
        # for i in vice_president_list:
        #     vice_president = db.session.query(Student).get(i)
        #     company.vice_president.append(vice_president)
        #     #adding vice president in to members
        #     company.members.append(vice_president)
        #To add new staff
        for i in a2astaff_list:
            a2a_staff = db.session.query(Stakeholder).get(i)
            company.a2a_staff.append(a2a_staff)        
        company.name = request.form['name']
        company.code = request.form['code']
        company.chairman_id = request.form['chairman']
        company.established_date = request.form['established_date']
        company.description = request.form['description']                                
        company.president_id = request.form['president']
        
        #adding president to member
        president = Student.query.filter_by(id=company.president_id).first()
        company.members.append(president)
        
        company.updated_at = datetime.now()
        db.session.merge(company)
        db.session.commit()
        flash('Company updated', 'success')
        return redirect('/company')        


@blueprint.route('/company<int:company_id>/change_to_inactive<int:member_id>', methods=['GET', 'POST'])
@login_required
def member_status_to_inactive(company_id, member_id):
    # change the status of a company member to inactive
    
    member = CompanyActiveMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
    student = Student.query.filter_by(id=member_id).first()        
    company = Company.query.filter_by(id=company_id).first()            
    company.members.remove(student)
    company.inactive_members.append(student)
    #check if member is president or vicepresident
    if student.id == company.president_id :
        company.president_id = None
        # company.vice_president.remove(db.session.query(Student).get(i.id))
        member = CompanyInactiveMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
        member.role = 'President'

    elif student in company.vice_president :
        company.vice_president.remove(student)
        member = CompanyInactiveMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
        member.role = 'Vice President'
    
    # member = CompanyMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
    # if member.status == 'Active':
    #     member.status = 'Not active'
    # else:
    #     # query association table with student id
    #     already_active = CompanyMembers.query.filter_by(student_id=member_id, status='Active').first()
    #     if already_active is None:            
    #         member.status = 'Active'
    #     else :          
    #         flash("error! Already active in "+already_active.company.name, 'error')
    db.session.commit()
    return redirect(url_for('company_blueprint.update_company', company_id=company_id))


@blueprint.route('/company<int:company_id>/change_to_active<int:member_id>', methods=['GET', 'POST'])
@login_required
def member_status_to_active(company_id, member_id):
    # change the status of a company member to inactive
    
    member = CompanyInactiveMembers.query.filter_by(company_id=company_id, student_id=member_id).first()
    student = Student.query.filter_by(id=member_id).first()    
    company = Company.query.filter_by(id=company_id).first()
    already_active = CompanyActiveMembers.query.filter_by(student_id=member_id).first()
    if already_active is None :        
        company.inactive_members.remove(student)        
        company.members.append(student)
    else :
        flash("error! Already active in "+already_active.company.name, 'error')
    db.session.commit()
    return redirect(url_for('company_blueprint.update_company', company_id=company_id))


@blueprint.route('/updating_adding_members/<int:company_id>', methods=['GET', 'POST'])
@login_required
def update_adding_members(company_id):
    company = Company.query.filter_by(id=company_id).first()
    member_list = request.form.getlist('member')
    for i in member_list:
        members = db.session.query(Student).get(i)
        company.members.append(members)
    db.session.commit()
    return redirect(url_for('company_blueprint.update_company', company_id=company_id))


@blueprint.route('/updating_adding_vice_presidents/<int:company_id>', methods=['GET', 'POST'])
@login_required
def update_adding_vice_presidents(company_id):
    company = Company.query.filter_by(id=company_id).first()
    vice_president_list = request.form.getlist('vice_president')    

    # To remove vice president
    for i in company.vice_president:
        if str(i.id) not in vice_president_list:
            company.vice_president.remove(db.session.query(Student).get(i.id))
    # To add new vice president
    for i in vice_president_list:
        vice_president = db.session.query(Student).get(i)
        company.vice_president.append(vice_president)
        #adding vice president in to members
        company.members.append(vice_president)
    db.session.commit()
    return redirect(url_for('company_blueprint.update_company', company_id=company_id))    


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

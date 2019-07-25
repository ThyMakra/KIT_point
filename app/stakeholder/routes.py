from datetime import datetime

from flask import render_template, request, flash, redirect, jsonify
from flask_login import (
  login_required
)

from app import db
from app.stakeholder.forms import CreateSpecialtyForm, CreateStakeholderForm, CreateAdviserTaskForm
from app.stakeholder.models import Stakeholder, Specialty, StakeholderTask
from app.stakeholder import blueprint


# @blueprint.route('/<template>')
# @login_required
# def route_template(template):
#     return render_template(template + '.html')


@blueprint.route('/stakeholders')
@login_required
def get_all_stakeholders():
    stakeholders = db.session.query(Stakeholder).all()
    return render_template('stakeholder.html', stakeholders=stakeholders)


@blueprint.route('/<stakeholder_id>', methods=['GET', 'POST'])
@login_required
def update_stakeholder(stakeholder_id):
    form = CreateStakeholderForm(request.form)
    stakeholder = Stakeholder.query.filter_by(id=stakeholder_id).first()
    if request.method == 'GET':
        return render_template('/update_stakeholder.html', form=form, stakeholder=stakeholder)
    else:
        name = request.form['name']
        gender = request.form['gender']
        domain = request.form['domain']
        department = request.form['department']
        user = request.form['user']
        specialty = request.form['specialty']
        stakeholder.name = name
        stakeholder.gender = gender
        stakeholder.domain = domain
        stakeholder.department_id = department
        stakeholder.user_id = user
        stakeholder.specialty_id = specialty
        stakeholder.charge_rate = request.form.get('charge_rate')
        stakeholder.updated_at = datetime.now()
        db.session.merge(stakeholder)
    db.session.commit()
    flash('Stakeholder updated')
    return redirect('/stakeholder/stakeholders')


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_stakeholder():
    if request.method == 'GET':
        form = CreateStakeholderForm(request.form)
        return render_template('create_stakeholder.html', form=form)
    name = request.form['name']
    gender = request.form['gender']
    domain = request.form['domain']
    department = request.form['department']
    user = request.form['user']
    specialty = request.form['specialty']
    charge_rate = request.form.get('charge_rate')
    is_duplicate = Stakeholder.query.filter_by(name=name).first()
    if is_duplicate is None:
        stakeholder = Stakeholder(name, gender, domain, user, department, specialty, charge_rate)
        stakeholder.created_at = datetime.now()
        db.session.add(stakeholder)
        db.session.commit()
        flash('Stakeholder created')
        return redirect('/stakeholder/stakeholders')
    else:
        form = CreateStakeholderForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_stakeholder.html', error=error, form=form)


@blueprint.route('/specialties')
@login_required
def get_all_specialties():
    specialties = db.session.query(Specialty).all()
    return render_template('specialty.html', specialties=specialties)


@blueprint.route('specialty/<specialty_id>', methods=['GET', 'POST'])
@login_required
def update_specialty(specialty_id):
    form = CreateSpecialtyForm(request.form)
    specialty = Specialty.query.filter_by(id=specialty_id).first()
    if request.method == 'GET':
        return render_template('/update_specialty.html', form=form, specialty=specialty)
    else:
        specialty.name = request.form['name']
        specialty.code = request.form['code']
        specialty.updated_at = datetime.now()
        db.session.merge(specialty)
    db.session.commit()
    flash('Specialty updated')
    return redirect('/stakeholder/specialties')


@blueprint.route('/specialty/create', methods=['GET', 'POST'])
@login_required
def create_specialty():
    if request.method == 'GET':
        form = CreateSpecialtyForm(request.form)
        return render_template('create_specialty.html', form=form)
    name = request.form['name']
    code = request.form.get('code')
    check_name = db.session.query(Specialty).filter_by(name=name).first()
    print(check_name)
    if check_name is None:
        specialty = Specialty(name, code)
        specialty.created_at = datetime.now()
        db.session.add(specialty)
        db.session.commit()
        flash('Specialty created')
        return redirect('/stakeholder/specialties')
    else:
        form = CreateSpecialtyForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_specialty.html', error=error, form=form)


@blueprint.route('/specialty/delete<specialty_id>')
@login_required
def delete_specialty(specialty_id):
    try:
        Specialty.query.filter_by(id=specialty_id).delete()
        db.session.commit()
        flash('Specialty deleted!')
        return redirect('/stakeholder/specialties')
    except Exception as e:
        print(e)
        flash('Delete error! some entities are referring to this')
        return redirect('/stakeholder/specialties')


@blueprint.route('/delete<stakeholder_id>')
@login_required
def delete_stakeholder(stakeholder_id):
    try:
        Stakeholder.query.filter_by(id=stakeholder_id).delete()
        db.session.commit()
        flash('Stakeholder deleted!')
        return redirect('/stakeholder/stakeholders')
    except Exception as e:
        print(e)
        flash('Delete error!')
        return redirect('/stakeholder/stakeholders')


@blueprint.route('/task/create', methods=['POST', 'GET'])
@login_required
def create_task():
    if request.method == 'GET':
        form = CreateAdviserTaskForm(request.form)
        return render_template('create_stakeholder_task.html', form=form)
    else:
        name = request.form.get('name')
        status = request.form.get('status')
        project = request.form.get('project')
        assign_to = request.form.get('assign_to')
        actual_hour = request.form.get('actual_hour')
        start_date = datetime.strptime(request.form.get('start_date'), '%m/%d/%Y')
        deadline = datetime.strptime(request.form.get('deadline'), '%m/%d/%Y')
        planning_hour = (deadline - start_date).days*8
        task = StakeholderTask(name, status, assign_to, project,
                               planning_hour, actual_hour, start_date, deadline)
        task.created_at = datetime.today()
        db.session.add(task)
        db.session.commit()
        flash('Adviser task created')
        return redirect('/project/'+project)


@blueprint.route('/task/delete<task_id>')
@login_required
def delete_task(task_id):
    project_id = db.session.query(StakeholderTask).filter_by(id=task_id).first().project_id
    try:
        db.session.query(StakeholderTask).filter_by(id=task_id).delete()
        db.session.commit()
        flash('Stakeholder task deleted!')
        return redirect('/project/'+str(project_id))
    except Exception as e:
        print(e)
        flash('Delete error!')
        return redirect('/project/'+str(project_id))


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

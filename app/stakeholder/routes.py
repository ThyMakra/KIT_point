from datetime import datetime

from flask import render_template, request, flash, redirect
from flask_login import (
  login_required
)

from app import db
from app.stakeholder.forms import CreateSpecialtyForm, CreateStakeholderForm
from app.stakeholder.models import Stakeholder, Specialty
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
    is_duplicate = Stakeholder.query.filter_by(name=name).first()
    if is_duplicate is None:
        stakeholder = Stakeholder(name, gender, domain, user, department, specialty)
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
        name = request.form['name']
        code = request.form['code']
        specialty.name = name
        specialty.code = code
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
    code = request.form['code']
    check_name = Specialty.query.filter_by(name=name).first()
    check_code = Specialty.query.filter_by(code=code).first()
    if check_name is None and check_code is None:
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
        flash('Delete error!')
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

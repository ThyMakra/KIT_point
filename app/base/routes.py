from bcrypt import checkpw
from datetime import datetime
from flask import jsonify, render_template, redirect, request, url_for, flash, json, Response
from flask_login import (
  current_user,
  login_required,
  login_user,
  logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm, CreateDepartmentForm, CreateBatchForm, CreateSemesterForm
from app.base.models import User, Role, Department, Batch, Semester


@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/<template>')
@login_required
def route_template(template):
    return render_template(template + '.html')


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


## Login & Registration


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'login' in request.form:
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and checkpw(password.encode('utf8'), user.password):
            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))
        return render_template('errors/page_403.html')
    if not current_user.is_authenticated:
        return render_template(
          'login/login.html',
          login_form=login_form,
          create_account_form=create_account_form
        )
    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET':
        userForm = CreateAccountForm(request.form)
        return render_template('form/create_user.html', userForm=userForm)
    email = request.form['email']
    username = request.form['username']
    print(username)
    check_email = db.session.query(User).filter_by(email=email).first()
    check_username = db.session.query(User).filter_by(username=username).first()
    if '@kit.edu.kh' in email:
        print('yeeeeeeeeeeeeeeee')
    else:
        print('noooooooooooooooooo')
    if check_email is None and check_username is None:
<<<<<<< HEAD
        role = db.session.query(Role).get(2)
=======
        role = db.session.query(Role).get(1)
>>>>>>> created an account
        user = User(**request.form)
        # user.roles.append(Role('ADMIN'))
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
        return jsonify('success')
    else:
        return jsonify('duplicate')


@blueprint.route('/create_department', methods=['GET', 'POST'])
def create_department():
    if request.method == 'GET':
        departmentForm = CreateDepartmentForm(request.form)
        return render_template('form/create_department.html', departmentForm=departmentForm)
    name = request.form['name']
    code = request.form['code']
    check_name = db.session.query(Department).filter_by(name=name).first()
    if check_name is None:
        department = Department(name, code)
        department.created_at = datetime.now()
        db.session.add(department)
        db.session.commit()
        flash('New department created')
        return redirect(url_for('base_blueprint.create_department'))
    else:
        departmentForm = CreateDepartmentForm(request.form)
        error = "Duplicate entry!"
        return render_template('form/create_department.html', error=error, departmentForm=departmentForm)


@blueprint.route('/create_batch', methods=['GET', 'POST'])
def create_batch():
    if request.method == 'GET':
        batchForm = CreateBatchForm(request.form)
        return render_template('form/create_batch.html', batchForm=batchForm)
    name = request.form['name']
    code = request.form['code']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    department_id = request.form['department']
    check_code = db.session.query(Batch).filter_by(code=code).first()
    check_duplicate = db.session.query(Batch).filter_by(name=name, department_id=department_id).first()
    if check_code is None and check_duplicate is None:
        created_at = datetime.now()
        batch = Batch(name, code, start_date, end_date, department_id)
        batch.created_at = created_at
        db.session.add(batch)
        db.session.commit()
        flash('New batch created')
        return redirect(url_for('base_blueprint.create_batch'))
    else:
        batchForm = CreateBatchForm(request.form)
        error = "Duplicate entry!"
        return render_template('form/create_batch.html', error=error, batchForm=batchForm)


@blueprint.route('/create_semester', methods=['GET', 'POST'])
def create_semester():
    if request.method == 'GET':
        semesterForm = CreateSemesterForm(request.form)
        return render_template('form/create_semester.html', semesterForm=semesterForm)
    name = request.form['name']
    code = request.form['code']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    batch_id = request.form['batch']
    department_id = request.form['department']
    check_code = db.session.query(Semester).filter_by(code=code).first()
    check_duplicate = db.session.query(Semester).filter_by(name=name,
                                                           batch_id=batch_id,
                                                           department_id=department_id).first()
    if check_code is None and check_duplicate is None:
        created_at = datetime.now()
        semester = Semester(name, code, start_date, end_date, batch_id, department_id)
        semester.created_at = created_at
        db.session.add(semester)
        db.session.commit()
        flash('New semester created')
        return redirect(url_for('base_blueprint.create_semester'))
    else:
        semesterForm = CreateSemesterForm(request.form)
        error = "Duplicate entry!"
        return render_template('form/create_semester.html', error=error, semesterForm=semesterForm)


@blueprint.route('/departments')
def get_departments():
    departments = db.session.query(Department).all()
    return render_template('list/department.html', departments=departments)


@blueprint.route('/users')
def get_users():
    users = db.session.query(User).all()
    return render_template('list/user.html', users=users)


@blueprint.route('/batches')
def get_batches():
    batches = db.session.query(Batch).all()
    return render_template('list/batch.html', batches=batches)


@blueprint.route('/semesters')
def get_semesters():
    semesters = db.session.query(Semester).all()
    return render_template('list/semester.html', semesters=semesters)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))


@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
      raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


## Errors
@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/page_403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/page_404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/page_500.html'), 500

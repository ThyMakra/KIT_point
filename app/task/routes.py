from datetime import datetime

from flask import render_template, request, flash, redirect, jsonify
from flask_login import (
  login_required, current_user
)

from app import db
from app.base.models import Semester
from app.student.models import Student
from app.task import blueprint
from app.task.forms import CreateTaskForm, UpdateTaskForm, CreateReportForm, \
  CreateTaskStatusForm, UpdateReportForm
from app.task.models import Task, Report, TaskStatus
from app.project.models import Project


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


@blueprint.route('/tasks')
@login_required
def get_tasks():
    if current_user.roles[0].name == 'ADMIN':
        tasks = db.session.query(Task).all()
        return render_template('task.html', tasks=tasks)
    elif current_user.roles[0].name == 'USER':
        tasks = current_user.student.tasks
        return render_template('task.html', tasks=tasks)


@blueprint.route('/<task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    form = UpdateTaskForm(request.form)
    create_report_form = CreateReportForm(request.form)
    update_report_form = UpdateReportForm(request.form)
    task = Task.query.filter_by(id=task_id).first()
    if request.method == 'GET':
        return render_template('/update_task.html',
                               create_report_form=create_report_form,
                               update_report_form=update_report_form,
                               form=form,
                               task=task)
    else:
        actual_hour = 0
        for i in task.reports:
            actual_hour += i.session*5/6
        student = db.session.query(Student).get(request.form.get('assign_to'))
        task.name = request.form.get('name')
        task.project_id = request.form.get('project')
        task.deadline = request.form.get('deadline')
        task.start_date = request.form.get('start_date')
        task.assign_to = request.form.get('assign_to')
        task.status_id = request.form.get('status')
        task.end_date = request.form.get('end_date')
        task.planning_hour = request.form.get('planning_hour')
        if task.project.is_old:
            task.actual_hour = request.form.get('actual_hour')
        else:
            task.actual_hour = actual_hour
        task.batch_id = student.batch_id
        task.updated_at = datetime.now()
        db.session.merge(task)
        db.session.commit()
        flash('Task updated')
        return redirect('/project/'+request.form.get('project'))


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_task():
    if current_user.roles[0].name != 'ADMIN':
        return render_template('errors/page_403.html'), 403
    if request.method == 'GET':
        form = CreateTaskForm(request.form)
        return render_template('create_task.html', form=form)
    name = request.form['name']
    project_id = request.form['project']
    project = Project.query.filter_by(id=project_id).first()
    if project.is_old:
        actual_hour = request.form.get('actual_hour')
    else:
        actual_hour = 0.00
    assign_to = request.form['assign_to']
    student = db.session.query(Student).get(assign_to)
    batch = student.batch_id
    status = request.form['status']
    deadline = datetime.strptime(request.form['deadline'], "%m/%d/%Y").date()
    start_date = datetime.strptime(request.form['start_date'], "%m/%d/%Y").date()
    semester = db.session.query(Semester)\
      .filter(Semester.batch_id == batch)\
      .filter(start_date >= Semester.start_date, deadline <= Semester.end_date).first()
    check_start_date = db.session.query(Project)\
      .filter(Project.id == project_id)\
      .filter(Project.start_date <= start_date)\
      .first()
    # check_deadline = db.session.query(Project) \
    #   .filter(Project.id == project_id) \
    #   .filter(Project.deadline >= deadline) \
    #   .first()

    if semester is None:
        flash('Create error! start date and end date need to be within a semester!')
        return redirect('/project/' + project_id)
    if check_start_date is None:
        flash('Create error! Earlier than project start date!')
        return redirect('/project/' + project_id)
    # if check_deadline is None:
    #     flash('Create error! Exceed project deadline!')
    #     return redirect('/project/' + project_id)
    planning_hour = (deadline - start_date).days*float(semester.average_intern_hour.intern_hour)/7

    task = Task(name, assign_to, project_id, batch, status, planning_hour, actual_hour, start_date, deadline)
    task.created_at = datetime.now()
    db.session.add(task)
    db.session.commit()
    flash('Task created')
    return redirect('/project/'+project_id)


@blueprint.route('/delete<task_id>')
@login_required
def delete_task(task_id):
    if current_user.roles[0].name != 'ADMIN':
        return render_template('errors/page_403.html'), 403
    project_id = Task.query.filter_by(id=task_id).first().project_id
    try:
        Task.query.filter_by(id=task_id).delete()
        db.session.commit()
        flash('Task deleted!')
        return redirect('/project/'+str(project_id))
    except Exception as e:
        print(e)
        flash('Delete error! Some entities are referring to it.')
        return redirect('/project/'+str(project_id))


@blueprint.route('/get_current_semester')
@login_required
def get_current_semester():
    today = request.args.get('today', None)
    batch = request.args.get('batch', None)
    date_format = "%m/%d/%Y"
    print(today, batch)
    a = datetime.strptime(today, date_format).date()
    print(a)
    semesters = db.session.query(Semester).filter_by(batch_id=batch).all()
    for i in semesters:
        print(i.start_date)
        if i.end_date >= a >= i.start_date:
            return jsonify(i.id)
    return jsonify(0)


@blueprint.route('/reports')
@login_required
def get_reports():
    if current_user.roles[0].name == 'ADMIN':
        reports = db.session.query(Report).all()
        return render_template('report.html', reports=reports)
    elif current_user.roles[0].name == 'USER':
        reports = current_user.student.reports
        return render_template('report.html', reports=reports)


@blueprint.route('/report/delete<report_id>')
@login_required
def delete_report(report_id):
    try:
        Report.query.filter_by(id=report_id).delete()
        db.session.commit()
        flash('Report deleted!')
        return redirect('/task/reports')
    except Exception as e:
        print(e)
        error = 'Delete error! some entities are referring to it.'
        flash(error, 'error')
        return redirect('/task/reports')


@blueprint.route('get_report/<report_id>')
@login_required
def get_report(report_id):
    report = Report.query.get(report_id)
    dic = {
      'id': report.id,
      'description': report.description,
      'session': report.session,
      'date': report.date,
      'semester': report.semester_id,
      'assign_to': report.student_id,
      'batch': report.batch_id,
      'task': report.task_id,
      'project': report.project_id,
      'is_approved': report.is_approved,
      'approved_by': report.approved_by,
      'approved_date': report.approved_date
    }
    report = jsonify(dic)
    return report


@blueprint.route('approve_report/<report_id>')
@login_required
def approve_report(report_id):
    if current_user.roles[0].name != 'ADMIN':
        return jsonify('forbidden')
    report = Report.query.filter_by(id=report_id).first()
    report.approved_date = datetime.now()
    if current_user.roles[0].name == 'ADMIN':
        report.approved_by = current_user.stakeholder.name
    elif current_user.roles[0].name == 'USER':
        report.approved_by = current_user.student.name
    report.is_approved = True
    db.session.merge(report)
    db.session.commit()
    return jsonify('success')


@blueprint.route('get_report_by_date')
@login_required
def get_report_by_date():
    date = request.args.get('date')
    is_approved = request.args.get('is_approved')
    date = datetime.strptime(date, "%Y-%m-%d").date()
    print(date)
    global reports
    if current_user.roles[0].name == 'ADMIN':
        reports = db.session.query(Report)\
          .filter(Report.date == date)\
          .filter_by(is_approved=is_approved.capitalize()).all()
    elif current_user.roles[0].name == 'USER':
        student_id = current_user.student.id
        reports = db.session.query(Report) \
          .filter(Report.date == date) \
          .filter_by(is_approved=is_approved.capitalize())\
          .filter_by(student_id=student_id)\
          .all()
    report_dict = {}
    report_list = []
    for report in reports:
        global edit
        if not report.is_approved and current_user.roles[0].name == 'ADMIN':
            edit = '<a id="report' + str(report.id) + '" href="#" onclick="approve_report(' + str(report.id) +\
                   ')" class="btn btn-primary btn-xs"><i class="fa fa-check-circle"></i> Approve </a>\n' +\
                  '<a href="/task/report/' + str(report.id) + '" class="btn btn-info btn-xs"><i class="fa fa-pencil">'\
                   + '</i> Edit </a>\n' + '<a href="report/delete' + str(report.id) + \
                   '"class="btn btn-danger btn-xs"><i class="fa fa-trash-o">' + '</i>\n' + 'Delete </a>\n'
        else:
            edit = '<a href="/task/report/' + str(report.id) + '" class="btn btn-info btn-xs"><i class="fa fa-pencil">' \
                   + '</i> Edit </a>\n' + '<a href="report/delete' + str(report.id) + \
                   '"class="btn btn-danger btn-xs"><i class="fa fa-trash-o">' + '</i>\n' + 'Delete </a>\n'
        dic = {
          'student': report.student.name,
          'session': report.session,
          'description': report.description,
          'semester': report.semester.name,
          'date': report.date,
          'edit': edit,
          'id': report.id,
          'batch': report.batch.name,
          'task': report.task.name,
          'project': report.project.name,
          'is_approved': report.is_approved,
          'approved_by': report.approved_by,
          'approved_date': report.approved_date
        }
        report_list.append(dic)
    report_dict['data'] = report_list

    return jsonify(report_dict)


@blueprint.route('report/<report_id>', methods=['GET', 'POST'])
@login_required
def update_report(report_id):
    if current_user.roles[0].name != 'ADMIN':
        return render_template('errors/page_403.html'), 403
    form = CreateReportForm(request.form)
    report = Report.query.filter_by(id=report_id).first()
    if request.method == 'GET':
        return render_template('/update_report.html', form=form, report=report)
    else:
        report.batch_id = request.form.get('batch')
        report.project_id = request.form.get('project')
        report.student_id = request.form.get('assign_to')
        report.description = request.form['description']
        report.session = request.form.get('session')
        report.date = request.form.get('date')
        report.semester_id = request.form.get('semester')
        report.task_id = request.form.get('task')
        report.updated_at = datetime.now()
        db.session.merge(report)
        db.session.commit()
        return jsonify('success')


@blueprint.route('/report/create', methods=['GET', 'POST'])
@login_required
def create_report():
    if request.method == 'GET':
        form = CreateReportForm(request.form)
        return render_template('create_report.html', form=form)
    date = request.form.get('date')
    myDate = datetime.strptime(date, '%m/%d/%Y').weekday()
    print(myDate)
    task = request.form.get('task')
    project = request.form.get('project')
    assign_to = request.form.get('assign_to')
    description = request.form.get('description')
    session = request.form.get('session')
    if int(session) > 9:
        flash("Submit error! it exceeds 9 sessions")
        return redirect('/task/' + task)
    semester = request.form.get('semester')
    batch = request.form.get('batch')
    is_duplicate = Report.query.filter_by(date=date, task_id=task).first()
    if is_duplicate is None:
        report = Report(session, description, date, task, project, assign_to, batch, semester)
        report.created_at = datetime.now()
        date = datetime.strptime(request.form['date'], "%m/%d/%Y").date()
        is_before_start_date = db.session.query(Task).filter(Task.id == task) \
          .filter(Task.start_date > date).first()
        is_exceed_dateline = db.session.query(Task).filter(Task.id == task) \
          .filter(Task.deadline < date).first()
        if is_before_start_date is not None:
            flash("Submit error! it's before start date")
            return redirect('/task/' + task)
        if is_exceed_dateline is not None:
            flash("Submit error! it exceeds deadline")
            return redirect('/task/' + task)
        db.session.add(report)
        db.session.commit()
        flash('Report created')
        return redirect('/task/'+task)
    else:
        error = 'Submit error! ' + date + ' report already submitted!'
        flash(error)
        return redirect('/task/'+task)


@blueprint.route('/statuses')
@login_required
def get_statuses():
    statuses = db.session.query(TaskStatus).all()
    return render_template('task_status.html', statuses=statuses)


@blueprint.route('/status/create', methods=['GET', 'POST'])
@login_required
def create_status():
    form = CreateTaskStatusForm(request.form)
    if request.method == 'GET':
        return render_template('/create_task_status.html', form=form)
    name = request.form['name']
    check_name = db.session.query(Student).filter_by(name=name).first()
    if check_name is None:
        status = TaskStatus(name)
        status.created_at = datetime.now()
        db.session.add(status)
        db.session.commit()
        flash('New status created')
        return redirect('/task/statuses')
    else:

        error = "Duplicate entry!"
        return render_template('/create_task_status.html', error=error, form=form)


@blueprint.route('/status/<status_id>', methods=['GET', 'POST'])
@login_required
def update_status(status_id):
    form = CreateTaskStatusForm(request.form)
    status = TaskStatus.query.filter_by(id=status_id).first()
    if request.method == 'GET':
        return render_template('/update_task_status.html', form=form, status=status)
    else:
        status.name = request.form.get('name')
        status.updated_at = datetime.now()
        db.session.merge(status)
        db.session.commit()
        flash('Status updated')
        return redirect('/task/statuses')


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

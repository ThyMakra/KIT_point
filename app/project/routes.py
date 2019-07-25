from datetime import datetime

from flask import jsonify, render_template, request, flash, redirect, url_for
from flask_login import (
  login_required, current_user
)

from app import db
from app.project import blueprint
from app.project.forms import CreateProjectForm, CreateSkillForm, \
  CreateCategoryForm, CreateSubCategoryForm, CreateStatusForm, UpdateProjectForm
from app.project.logics import calculate_point, generate_planning_hour, calculate_point_old
from app.project.models import Project, Skill, Category, SubCategory, Status
from app.stakeholder.models import Stakeholder
from app.student.models import Student
from app.task.forms import CreateTaskForm, CreateTaskFormOld
from app.stakeholder.forms import CreateAdviserTaskForm


@blueprint.route('/fixed_<template>')
@login_required
def route_fixed_template(template):
    return render_template('fixed/fixed_{}.html'.format(template))


@blueprint.route('/page_<error>')
def route_errors(error):
    return render_template('errors/page_{}.html'.format(error))


@blueprint.route('/projects')
@login_required
def get_projects():
    if current_user.roles[0].name == 'ADMIN':
        projects = db.session.query(Project).all()
        form = CreateProjectForm(request.form)
        return render_template('project.html', projects=projects, form=form)
    elif current_user.roles[0].name == 'USER':
        projects = current_user.student.projects
        form = CreateProjectForm(request.form)
        return render_template('project.html', projects=projects, form=form)


@blueprint.route('/delete<project_id>')
@login_required
def delete_project(project_id):
    try:
        Project.query.filter_by(id=project_id).delete()
        db.session.commit()
        flash('Project deleted!')
        return redirect('/project/projects')
    except Exception as e:
        print(e)
        flash('Delete error! some entities are referring to this')
        return redirect('/project/projects')


@blueprint.route('/update_project', methods=['GET'])
@login_required
def update_project_from_list():
    project_id = int(request.args.get('id'))
    status = int(request.args.get('status'))
    point = request.args.get('point')
    project = Project.query.filter_by(id=project_id).first()
    generate_planning_hour(project)
    if status == 4:
        project.propose_point = float(point)
        project.status_id = 4
        if project.is_old:
            calculate_point_old(project, project.propose_point, 0)
        else:
            calculate_point(project, project.propose_point, 0)
    elif status == 2:
        project.status_id = 2
    elif status == 5:
        project.acquire_point = float(point)
        project.status_id = 5
        if project.is_old:
            calculate_point_old(project, project.propose_point, project.acquire_point)
        else:
            calculate_point(project, project.propose_point, project.acquire_point)
    db.session.merge(project)
    db.session.commit()
    return jsonify('success')


@blueprint.route('/<project_id>', methods=['GET', 'POST'])
@login_required
def update_project(project_id):
    form = UpdateProjectForm(request.form)
    adviserTaskForm = CreateAdviserTaskForm(request.form)
    project = Project.query.filter_by(id=project_id).first()
    if project.is_old:
        taskForm = CreateTaskFormOld(request.form)
    else:
        taskForm = CreateTaskForm(request.form)
    if request.method == 'GET':
        return render_template('/update_project.html', form=form,
                               taskForm=taskForm, project=project,
                               adviserTaskForm=adviserTaskForm)
    else:
        acquire_point = request.form.get('acquire_point')
        propose_point = request.form.get('propose_point')
        generate_planning_hour(project)
        member_list = request.form.getlist('member')
        member_list.append(request.form.get('leader'))
        adviser_list = request.form.getlist('adviser')
        skill_list = request.form.getlist('skill')
        # To remove skill
        for i in project.skills:
            if str(i.id) not in skill_list:
                project.skills.remove(db.session.query(Skill).get(i.id))
        # To remove member
        for i in project.members:
            if str(i.id) not in member_list:
                project.members.remove(db.session.query(Student).get(i.id))
        # To remove adviser
        for i in project.advisers:
            if str(i.id) not in adviser_list:
                project.advisers.remove(db.session.query(Stakeholder).get(i.id))
        # To add new skill
        for i in skill_list:
            skill = db.session.query(Skill).get(i)
            project.skills.append(skill)
        # To add new member
        for i in member_list:
            member = db.session.query(Student).get(i)
            project.members.append(member)
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
            project.advisers.append(adviser)
        category = db.session.query(Category).get(request.form.get('category'))
        sub_category = db.session.query(SubCategory).get(request.form.get('sub_category'))
        project.name = request.form.get('name')
        project.code = request.form.get('code')
        project.company_id = request.form['company']
        project.status_id = request.form.get('status')
        project.categories.append(category)
        project.sub_categories.append(sub_category)
        project.description = request.form.get('description')
        project.chairman_remark = request.form.get('chairman_remark')
        project.president_remark = request.form.get('president_remark')
        project.budget = request.form.get('budget')
        project.contingency = request.form.get('contingency')
        # project.estimate_point = request.form.get('estimate_point')
        # project.actual_point = actual_point
        project.acquire_point = acquire_point
        project.propose_point = request.form.get('propose_point')
        project.leader = request.form.get('leader')
        project.coordinator = request.form.get('coordinator')
        if request.form.get('is_old') is None:
            project.is_old = False
            calculate_point(project, propose_point, acquire_point)
        else:
            project.is_old = True
            calculate_point_old(project, propose_point, acquire_point)
        project.start_date = request.form.get('start_date')
        project.end_date = request.form.get('end_date')
        project.deadline = request.form.get('deadline')
        project.updated_at = datetime.now()
        db.session.merge(project)
        db.session.commit()
        flash('Project updated')
        return redirect('/project/'+str(project_id))


@blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'GET':
        form = CreateProjectForm(request.form)
        return render_template('create_project.html', form=form)
    name = request.form['name']
    code = request.form['code']
    company = request.form['company']
    description = request.form['description']
    budget = request.form['budget']
    contingency = request.form['contingency']
    leader = request.form['leader']
    coordinator = request.form['coordinator']
    status = 3
    cat_id = request.form['category']
    sub_cat_id = request.form['sub_category']
    category = db.session.query(Category).get(cat_id)
    sub_category = db.session.query(SubCategory).get(sub_cat_id)
    if request.form.get('is_old') is not None:
        is_old = True
    else:
        is_old = False
    member_list = request.form.getlist('member')
    adviser_list = request.form.getlist('adviser')
    member_list.append(int(leader))
    skill_list = request.form.getlist('skill')
    deadline = datetime.strptime(request.form['deadline'], "%m/%d/%Y").date()
    start_date = datetime.strptime(request.form['start_date'], "%m/%d/%Y").date()
    is_duplicate = Project.query.filter_by(code=code, name=name).first()
    if is_duplicate is None:
        project = Project(name, code, company, description, budget, contingency,
                          leader, coordinator, is_old,
                          start_date, deadline, status)
        # To add new skill
        for i in skill_list:
            skill = db.session.query(Skill).get(i)
            project.skills.append(skill)
        # To add new member
        for i in member_list:
            member = db.session.query(Student).get(i)
            project.members.append(member)
        # To add new adviser
        for i in adviser_list:
            adviser = db.session.query(Stakeholder).get(i)
            project.advisers.append(adviser)
        project.categories.append(category)
        project.sub_categories.append(sub_category)
        project.created_at = datetime.now()
        generate_planning_hour(project)
        db.session.add(project)
        db.session.commit()
        flash('Project created')
        return redirect('/project/projects')
    else:
        form = CreateProjectForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_project.html', error=error, form=form)


@blueprint.route('/members/<project_id>')
@login_required
def get_project_members(project_id):
    project = db.session.query(Project).get(project_id)
    members = {}
    for i in project.members:
        members[str(i.id)] = {
          'name': i.name
        }
    members['code'] = 200
    return jsonify(members)


@blueprint.route('/skills')
@login_required
def get_skills():
    skills = db.session.query(Skill).all()
    return render_template('skill.html', skills=skills)


@blueprint.route('/skill/delete<skill_id>')
@login_required
def delete_skill(skill_id):
    try:
        Skill.query.filter_by(id=skill_id).delete()
        db.session.commit()
        flash('Skill deleted!')
        return redirect('/project/skills')
    except Exception as e:
        print(e)
        error = 'Delete error! some entities are referring to it.'
        flash(error, 'error')
        return redirect('/project/skills')


@blueprint.route('skill/<skill_id>', methods=['GET', 'POST'])
@login_required
def update_skill(skill_id):
    form = CreateSkillForm(request.form)
    skill = Skill.query.filter_by(id=skill_id).first()
    if request.method == 'GET':
        return render_template('/update_skill.html', form=form, skill=skill)
    else:
        skill.name = request.form['name']
        skill.code = request.form['code']
        skill.updated_at = datetime.now()
        db.session.merge(skill)
    db.session.commit()
    flash('Skill updated')
    return redirect('/project/skills')


@blueprint.route('/skill/create', methods=['GET', 'POST'])
@login_required
def create_skill():
    if request.method == 'GET':
        form = CreateSkillForm(request.form)
        return render_template('create_skill.html', form=form)
    name = request.form['name']
    code = request.form['code']
    is_duplicate = db.session.query(Skill).filter_by(name=name, code=code).first()
    if is_duplicate is None:
        skill = Skill(name, code)
        skill.created_at = datetime.now()
        db.session.add(skill)
        db.session.commit()
        flash('Skill created')
        return redirect('/project/skills')
    else:
        form = CreateSkillForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_skill.html', error=error, form=form)


@blueprint.route('/categories')
@login_required
def get_categories():
    categories = db.session.query(Category).all()
    return render_template('category.html', categories=categories)


@blueprint.route('category/delete<category_id>')
@login_required
def delete_category(category_id):
    try:
        Category.query.filter_by(id=category_id).delete()
        db.session.commit()
        flash('Category deleted!')
        return redirect('/project/categories')
    except Exception as e:
        print(e)
        flash('Delete error! some entities are referring to this')
        return redirect('/project/categories')


@blueprint.route('/category/create', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CreateCategoryForm(request.form)
    if request.method == 'GET':
        return render_template('/create_category.html', form=form)
    name = request.form['name']
    code = request.form['code']
    is_duplicate = db.session.query(Category).filter_by(name=name, code=code).first()
    if is_duplicate is None:
        category = Category(name, code)
        category.created_at = datetime.now()
        db.session.add(category)
        db.session.commit()
        flash('New category created')
        return redirect(url_for('project_blueprint.create_category'))
    else:
        error = "Duplicate entry!"
        return render_template('/create_category.html', error=error, form=form)
    # return jsonify('success')


@blueprint.route('category/<category_id>', methods=['GET', 'POST'])
@login_required
def update_category(category_id):
    form = CreateCategoryForm(request.form)
    category = Category.query.filter_by(id=category_id).first()
    if request.method == 'GET':
        return render_template('/update_category.html', form=form, category=category)
    else:
        name = request.form['name']
        code = request.form['code']
        category.name = name
        category.code = code
        db.session.merge(category)
    db.session.commit()
    flash('Category updated')
    return redirect('/project/categories')


@blueprint.route('/sub_categories')
@login_required
def get_sub_categories():
    sub_categories = db.session.query(SubCategory).all()
    return render_template('sub_category.html', sub_categories=sub_categories)


@blueprint.route('sub_category/delete<sub_category_id>')
@login_required
def delete_sub_category(sub_category_id):
    try:
        SubCategory.query.filter_by(id=sub_category_id).delete()
        db.session.commit()
        flash('Sub Category deleted!')
        return redirect('/project/sub_categories')
    except Exception as e:
        print(e)
        flash('Delete error! some entities are referring to this')
        return redirect('/project/sub_categories')


@blueprint.route('/sub_category/create', methods=['GET', 'POST'])
@login_required
def create_sub_category():
    form = CreateSubCategoryForm(request.form)
    if request.method == 'GET':
        return render_template('/create_sub_category.html', form=form)
    name = request.form['name']
    code = request.form['code']
    is_duplicate = db.session.query(SubCategory).filter_by(name=name, code=code).first()
    if is_duplicate is None:
        sub_category = SubCategory(name, code)
        sub_category.created_at = datetime.now()
        db.session.add(sub_category)
        db.session.commit()
        flash('New sub category created')
        return redirect(url_for('project_blueprint.create_sub_category'))
    else:

        error = "Duplicate entry!"
        return render_template('/create_sub_category.html', error=error, form=form)
    # return jsonify('success')


@blueprint.route('sub_category/<sub_category_id>', methods=['GET', 'POST'])
@login_required
def update_sub_category(sub_category_id):
    form = CreateCategoryForm(request.form)
    sub_category = SubCategory.query.filter_by(id=sub_category_id).first()
    if request.method == 'GET':
        return render_template('/update_sub_category.html', form=form, sub_category=sub_category)
    else:
        name = request.form['name']
        code = request.form['code']
        sub_category.name = name
        sub_category.code = code
        db.session.merge(sub_category)
    db.session.commit()
    flash('Sub Category updated')
    return redirect('/project/sub_categories')


@blueprint.route('/statuses')
@login_required
def get_statuses():
    statuses = db.session.query(Status).all()
    return render_template('status.html', statuses=statuses)


@blueprint.route('/status/delete<status_id>')
@login_required
def delete_status(status_id):
    try:
        Status.query.filter_by(id=status_id).delete()
        db.session.commit()
        flash('Status deleted!')
        return redirect('/project/statuses')
    except Exception as e:
        print(e)
        error = 'Delete error! some entities are referring to it.'
        flash(error, 'error')
        return redirect('/project/statuses')


@blueprint.route('status/<status_id>', methods=['GET', 'POST'])
@login_required
def update_status(status_id):
    form = CreateStatusForm(request.form)
    status = Status.query.filter_by(id=status_id).first()
    if request.method == 'GET':
        return render_template('/update_status.html', form=form, status=status)
    else:
        status.name = request.form['name']
        status.updated_at = datetime.now()
        db.session.merge(status)
    db.session.commit()
    flash('Status updated')
    return redirect('/project/statuses')


@blueprint.route('/status/create', methods=['GET', 'POST'])
@login_required
def create_status():
    if request.method == 'GET':
        form = CreateStatusForm(request.form)
        return render_template('create_status.html', form=form)
    name = request.form['name']
    is_duplicate = db.session.query(Skill).filter_by(name=name).first()
    if is_duplicate is None:
        status = Status(name)
        status.created_at = datetime.now()
        db.session.add(status)
        db.session.commit()
        flash('Status created')
        return redirect('/project/statuses')
    else:
        form = CreateSkillForm(request.form)
        error = 'Duplicate entry'
        return render_template('create_status.html', error=error, form=form)




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

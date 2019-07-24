from app import db
from app.base.models import KitPointValue, AverageInternHour, Semester, Batch
from app.student.models import StudentSummary, Student
from app.task.models import Report, Task
from app.stakeholder.models import StakeholderTask, StakeholderSummary, Stakeholder
from datetime import datetime


def generate_planning_hour(project):
    total_hour = 0
    student_point = 0
    adviser_point = 0
    for i in project.summaries:
        StudentSummary.query.filter_by(id=i.id).delete()
        db.session.commit()
    # Estimate student cost of the project #
    for m in project.members:
        res = db.session.query(Semester).join(AverageInternHour) \
          .filter(Semester.start_date <= project.deadline, Semester.end_date >= project.start_date) \
          .filter(m.batch_id == Semester.batch_id)\
          .order_by(Semester.name)\
          .all()
        if len(res) == 0:
            return False
        count = 1
        for i in res:
            if len(res) == 1:
                diff = (project.deadline - project.start_date).days/7
            else:
                if count == 1:
                    diff = (i.end_date - project.start_date).days/7
                elif count < len(res):
                    diff = (i.end_date - i.start_date).days/7
                else:
                    diff = (project.deadline - i.start_date).days/7

                count += 1

            if diff == 26:
                diff -= 4
            elif diff == 25:
                diff -= 3
            elif diff == 24:
                diff -= 2

            s_hour = diff*i.average_intern_hour.intern_hour
            s_point = s_hour*float(m.rank.chargeTable.price)/100
            total_hour += s_hour
            student_point += s_point
            summary = StudentSummary(m.department_id, m.batch_id, i.id, m.id,
                                     project.id, s_hour, 0, 0, s_point, 0, 0)
            summary.created_at = datetime.now()
            db.session.add(summary)

    # Estimate advisers cost of the project #
    for i in project.stakeholder_summaries:
        StakeholderSummary.query.filter_by(id=i.id).delete()
        db.session.commit()
    coordinator = Stakeholder.query.filter_by(id=project.coordinator).first()
    project.advisers.append(coordinator)
    for adviser in project.advisers:
        weeks = (project.deadline - project.start_date).days / 7
        days = (project.deadline - project.start_date).days - weeks*2
        hours = days*8
        total_hour += hours
        point = hours*float(adviser.charge_rate)/100
        adviser_point += point
        stakeholder_summary = StakeholderSummary(
          adviser.id, project.id, point, 0, 0, 0
        )
        stakeholder_summary.created_at = datetime.now()
        db.session.add(stakeholder_summary)

    contingency = student_point*float(project.contingency)/100
    budget = float(project.budget)/100
    total_point = student_point + contingency + budget + adviser_point
    project.estimate_point = total_point
    project.planning_hour = total_hour


def calculate_point(project, propose_point, acquire_point):
    total_actual = 0
    point_value = KitPointValue.query.all()
    point_value = float(point_value[0].value)
    actual_point = float(project.actual_point)
    acquire_point = float(acquire_point)
    propose_point = float(propose_point)
    summaries = db.session.query(Report.project_id,
                                 Report.student_id,
                                 Report.batch_id,
                                 Report.semester_id,
                                 db.func.sum(Report.session).label('session') * 5 / 6)\
      .group_by(Report.project_id,
                Report.student_id,
                Report.batch_id,
                Report.semester_id)\
      .filter(Report.project_id == project.id)\
      .filter(Report.is_approved is True)\
      .all()
    stakeholder_summaries = db.session.query(StakeholderTask.assign_to, db.func.sum(StakeholderTask.actual_hour)) \
      .filter(StakeholderTask.project_id == project.id) \
      .group_by(StakeholderTask.assign_to) \
      .all()
    if acquire_point == 0 and propose_point == 0:
        for i in project.members:
            student = db.session.query(Student).get(i.id)
            price = float(student.rank.chargeTable.price)
            hours = db.session.query(Report.semester_id, db.func.sum(Report.session).label('session') * 5 / 6)\
              .group_by(Report.semester_id)\
              .filter(Report.project_id == project.id, i.id == Report.student_id)\
              .order_by(Report.semester_id).all()
            summaries = StudentSummary.query.filter_by(project_id=project.id, student_id=i.id).all()

            sem_ids = []
            for l in summaries:
                sem_ids.append(l.semester_id)
            for j in hours:
                for k in summaries:
                    if k.semester_id == j[0]:
                        k.actual_point = price*float(j[1])/point_value
                        total_actual += k.actual_point
                if j[0] not in sem_ids:
                    summary = StudentSummary(
                      i.department_id, i.batch_id, int(j[0]), i.id, project.id, float(j[1]),
                      float(j[1]), float(j[1] * price / point_value), float(j[1] * price / point_value), 0, 0)
                    db.session.add(summary)
                    total_actual += float(j[1] * price / point_value)

        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
        project.actual_point = total_actual
    if propose_point > 0:
        generate_propose_point(project, summaries, stakeholder_summaries, propose_point, actual_point, point_value)
    if acquire_point > 0:
        generate_acquire_point(project, summaries, stakeholder_summaries, acquire_point, actual_point, point_value)


def generate_propose_point(project, summaries, stakeholder_summaries, propose_point, actual_point, point_value):
    total_actual = 0
    total_propose = 0
    if propose_point == actual_point:
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.propose_point = price * float(j[4]) / point_value
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.propose_point = price*float(j[1]) / point_value
                    i.actual_point = price*float(j[1]) / point_value
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point

    elif propose_point > actual_point:
        percentage = actual_point/propose_point
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.propose_point = i.actual_point/percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.propose_point = i.actual_point / percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point
    else:
        percentage = propose_point / actual_point
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.propose_point = i.actual_point * percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.propose_point = i.actual_point * percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_propose += i.propose_point

    project.actual_point = total_actual
    project.propose_point = total_propose


def generate_acquire_point(project, summaries, stakeholder_summaries, acquire_point, actual_point, point_value):
    total_actual = 0
    total_acquire = 0
    if acquire_point == actual_point:
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.acquire_point = price * float(j[4]) / point_value
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.acquire_point = i.actual_point
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point
    elif acquire_point > actual_point:
        percentage = actual_point / acquire_point
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.acquire_point = i.actual_point / percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.acquire_point = i.actual_point / percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point
    else:
        percentage = acquire_point / actual_point
        for i in project.summaries:
            price = float(i.student.rank.chargeTable.price)
            for j in summaries:
                if i.semester_id == j[3] and i.student_id == j[1]:
                    i.actual_point = price * float(j[4]) / point_value
                    i.acquire_point = i.actual_point * percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.acquire_point = i.actual_point * percentage
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
                    total_acquire += i.acquire_point

    project.actual_point = total_actual
    project.acquire_point = total_acquire


def calculate_point_old(project, propose_point, acquire_point):
    point_value = KitPointValue.query.all()
    point_value = float(point_value[0].value)
    actual_point = float(project.actual_point)
    acquire_point = float(acquire_point)
    propose_point = float(propose_point)
    total_actual = 0
    summaries = db.session\
      .query(Task.batch_id, Task.assign_to, Task.project_id,
             Semester.id, db.func.sum(Task.actual_hour))\
      .group_by(Semester.id, Task.batch_id, Task.assign_to,
                Task.project_id)\
      .filter(Task.project_id == project.id)\
      .filter(Task.start_date >= Semester.start_date, Task.deadline <= Semester.end_date)\
      .filter(Semester.batch_id == Task.batch_id)\
      .all()

    stakeholder_summaries = db.session.query(StakeholderTask.assign_to, db.func.sum(StakeholderTask.actual_hour)) \
      .filter(StakeholderTask.project_id == project.id) \
      .group_by(StakeholderTask.assign_to) \
      .all()

    if acquire_point == 0 and propose_point == 0:
        for i in project.members:
            price = float(i.rank.chargeTable.price)
            hours = db.session.query(Semester.id, db.func.sum(Task.actual_hour).label('session'))\
              .group_by(Semester.id)\
              .filter(Task.start_date <= Semester.end_date, Task.deadline >= Semester.start_date)\
              .filter(Task.batch_id == Semester.batch_id)\
              .filter(Task.assign_to == i.id)\
              .filter(project.id == Task.project_id)\
              .order_by(Semester.name).all()
            print(hours, i)
            summaries = StudentSummary.query.filter_by(project_id=project.id, student_id=i.id).all()

            sem_ids = []
            for l in summaries:
                sem_ids.append(l.semester_id)
            for j in hours:
                for k in summaries:
                    if k.semester_id == j[0]:
                        k.actual_point = price*float(j[1]/len(hours))/point_value
                        total_actual += k.actual_point
                if j[0] not in sem_ids:
                    summary = StudentSummary(
                      i.department_id, i.batch_id, int(j[0]), i.id, project.id, float(j[1]),
                      float(j[1]), float(j[1]/len(hours)) * price / point_value,
                      float(j[1]/len(hours)) * price / point_value, 0, 0)
                    db.session.add(summary)
                    total_actual += float(j[1]/len(hours)) * price / point_value
        for i in project.stakeholder_summaries:
            price = float(i.stakeholder.charge_rate)
            for j in stakeholder_summaries:
                if i.stakeholder_id == j[0]:
                    i.actual_point = price*float(j[1]) / point_value
                    i.updated_at = datetime.now()
                    db.session.merge(i)
                    total_actual += i.actual_point
        project.actual_point = total_actual

    if propose_point > 0:
        generate_propose_point(project, summaries, stakeholder_summaries, propose_point, actual_point, point_value)
    if acquire_point > 0:
        generate_acquire_point(project, summaries, stakeholder_summaries, acquire_point, actual_point, point_value)


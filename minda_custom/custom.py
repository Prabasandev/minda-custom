# -*- coding: utf-8 -*-
# Copyright (c) 2017, VHRS and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.data import today
from frappe import _
from frappe.utils import formatdate, getdate, cint, add_months, date_diff, add_days, flt
from frappe.utils.xlsxutils import make_xlsx
import requests
from datetime import datetime


@frappe.whitelist()
def send_wage_report():
    custom_filter = {'date': add_days(today(), -1)}
    report = frappe.get_doc('Report', "Wage Monitor Report")
    columns, data = report.get_data(
        limit=100, filters=custom_filter, as_dict=True)
    spreadsheet_data = get_spreadsheet_data(columns, data)
    xlsx_file = make_xlsx(spreadsheet_data, "Minda Custom")
    data = xlsx_file.getvalue()
    attachments = [{
        'fname': add_days(today(), -1) + '.xlsx',
        'fcontent': data
    }]
    frappe.sendmail(
        recipients=['loganathan.k@mindasai.com', 'jayapradha@mindasai.com',
                    'ajay.agrawal@mindasai.com', 'kennedy.j@mindasai.com', 'sqlmurugan@mindasai.com', 'abdulla.pi@voltechgroup.com'],
        subject='Wage Monitor Report - ' +
        formatdate(add_days(today(), -1)),
        message='Kindly find the attached Excel Sheet of Daily Attendance Report of' + formatdate(
            add_days(today(), -1)),
        attachments=attachments
    )


def send_daily_att_report():
    custom_filter = {'date': add_days(today(), -1)}
    report = frappe.get_doc('Report', "Daily Attendance Report")
    columns, data = report.get_data(
        limit=100, filters=custom_filter, as_dict=True)
    spreadsheet_data = get_spreadsheet_data(columns, data)
    xlsx_file = make_xlsx(spreadsheet_data, "Attendance")
    data = xlsx_file.getvalue()
    attachments = [{
        'fname': add_days(today(), -1) + '.xlsx',
        'fcontent': data
    }]
    frappe.sendmail(
        recipients=['loganathan.k@mindasai.com', 'jayapradha@mindasai.com',
                    'ajay.agrawal@mindasai.com', 'kennedy.j@mindasai.com', 'sqlmurugan@mindasai.com', 'abdulla.pi@voltechgroup.com'],
        subject='Employee Attendance Report - ' +
        formatdate(add_days(today(), -1)),
        message='Kindly find the attached Excel Sheet of Daily Attendance Report of' + formatdate(
            add_days(today(), -1)),
        attachments=attachments
    )


def send_daily_linewise_report():
    custom_filter = {'date': add_days(today(), -1)}
    report = frappe.get_doc('Report', "Linewise Count")
    columns, data = report.get_data(
        limit=100, filters=custom_filter, as_dict=True)
    spreadsheet_data = get_spreadsheet_data(columns, data)
    xlsx_file = make_xlsx(spreadsheet_data, "Attendance")
    data = xlsx_file.getvalue()
    attachments = [{
        'fname': add_days(today(), -1) + '.xlsx',
        'fcontent': data
    }]
    frappe.sendmail(
        recipients=['loganathan.k@mindasai.com', 'jayapradha@mindasai.com',
                    'ajay.agrawal@mindasai.com', 'kennedy.j@mindasai.com', 'sqlmurugan@mindasai.com', 'abdulla.pi@voltechgroup.com'],
        subject='Employee Attendance Report - ' +
        formatdate(add_days(today(), -1)),
        message='Kindly find the attached Excel Sheet of Linewise Count Report of' + formatdate(
            add_days(today(), -1)),
        attachments=attachments
    )


def get_spreadsheet_data(columns, data):
    out = [[_(df.label) for df in columns], ]
    for row in data:
        new_row = []
        out.append(new_row)
        for df in columns:
            new_row.append(frappe.format(row[df.fieldname], df, row))

    return out


# @frappe.whitelist()
# def send_count_report():
#     custom_filter = {'date': add_days(today(), -1)}
#     report = frappe.get_doc('Report', "Linewise Count")
#     columns, data = report.get_data(
#         limit=500 or 500, filters=custom_filter, as_dict=True)
# # html = _("Kindly Find the attached Linewise Count Report for your reference")
#     html = frappe.render_template(
#         'frappe/templates/includes/print_table.html', {'columns': columns, 'data': data})
#     frappe.sendmail(
#         recipients=['abdulla.pi@voltechgroup.com'],
#         subject='Employee Linewise Present COunt Report - ' +
#         formatdate(add_days(today(), -1)),
#         message=html
#     )


@frappe.whitelist()
def update_in_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/update?uid=%s&uname=%s&stgid=%s" % (
            uid, uname, stgid.name)
        r = requests.post(url)
    return r.content


@frappe.whitelist()
def delete_bulk():
    left_employees = frappe.get_list(
        "Employee", fields=["biometric_id"], filters={"status": "Left"})
    for l in left_employees:
        stgids = frappe.db.get_all("Service Tag")
        for stgid in stgids:
            uid = l.biometric_id
            url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
                uid, stgid.name)
            frappe.errprint(url)
            r = requests.post(url)
            print r.content


@frappe.whitelist()
def delete_from_biometric_machine(uid, uname):
    stgids = frappe.db.get_all("Service Tag")
    for stgid in stgids:
        url = "http://robot.camsunit.com/external/1.0/user/delete?uid=%s&stgid=%s" % (
            uid, stgid.name)
        r = requests.post(url)
    return r.content


@frappe.whitelist()
def emp_absent_today():
    day = add_days(today(), -1)
    holiday = frappe.get_list("Holiday List", filters={
                              'holiday_date': day})
    if holiday:
        pass
    else:
        query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
		WHERE att.employee = emp.name AND att.attendance_date = '%s'""" % (day)
        present_emp = frappe.db.sql(query, as_dict=True)
        for emp in frappe.get_list('Employee', filters={'status': 'Active'}):
            if emp in present_emp:
                pass
            else:
                doc = frappe.get_doc('Employee', emp)
                leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date and status = 'Approved'
				and docstatus = 1""", (doc.name, day))
                if leave:
                    status = 'On Leave'
                else:
                    status = 'Absent'
                attendance = frappe.new_doc("Attendance")
                attendance.update({
                    "employee": doc.name,
                    "employee_name": doc.employee_name,
                    "attendance_date": day,
                    "in_time": '00:00',
                    "out_time": '00:00',
                    "status": status,
                    "company": doc.company
                })
                attendance.save(ignore_permissions=True)
                attendance.submit()
                frappe.db.commit()


@frappe.whitelist()
def calculate_wages():
    day = add_days(today(), -1)
    # day = '2018-03-04'
    for line in frappe.get_list("Line"):
        att = frappe.db.sql(
            """select count(*) as count from `tabAttendance` where
                        docstatus=1 and status='Present' and line=%s and attendance_date= %s""", (line["name"], day), as_dict=1)
        for present in att:
            present_days = present.count

        att = frappe.db.sql(
            """select count(*) as count from `tabAttendance` where
                        docstatus=1 and status='Absent' and line=%s and attendance_date= %s""", (line["name"], day), as_dict=1)
        for absent in att:
            absent_days = absent.count

        wm = frappe.new_doc("Wage Monitor")
        wm.date = day
        wm.line = line["name"]
        wm.present = present_days
        wm.absent = absent_days
        wm.wage = '452'
        wm.calculated_wages = flt(wm.wage) * flt(wm.present)
        wm.save(ignore_permissions=True)

        # print absent_days


@frappe.whitelist()
def update_leave_application():
    day = add_days(today(), -1)
    employees = frappe.get_all('Employee', filters={"status": "Active"})
    for employee in employees:
        lwp = get_leave(employee.name, day)
        if lwp:
            pass
        else:
            query = """SELECT emp.name FROM `tabAttendance` att, `tabEmployee` emp
		               WHERE att.employee = emp.name AND att.status = 'Absent' AND att.attendance_date = '%s'""" % (day)
            absent_emp = frappe.db.sql(query, as_dict=True)
            if employee in absent_emp:
                leave_approvers = [l.leave_approver for l in frappe.db.sql("""select leave_approver from `tabEmployee Leave Approver` where parent = %s""",
                                                                           (employee.name), as_dict=True)]
                lap = frappe.new_doc("Leave Application")
                lap.leave_type = "Leave Without Pay"
                lap.status = "Approved"
                lap.follow_via_email = 0
                lap.description = "Absent Auto Marked"
                lap.from_date = day
                lap.to_date = day
                lap.employee = employee.name
                if leave_approvers:
                    lap.leave_approver = leave_approvers[0]
                else:
                    lap.leave_approver = "Administrator"
                lap.posting_date = day
                lap.company = frappe.db.get_value(
                    "Employee", employee.name, "company")
                lap.save(ignore_permissions=True)
                lap.submit()
                frappe.db.commit()


def get_leave(emp, day):
    leave = frappe.db.sql("""select name from `tabLeave Application`
				where employee = %s and %s between from_date and to_date
				""", (emp, day))
    return leave


def daily_punch_record():
    from zk import ZK, const
    conn = None
    zk = ZK('192.168.1.65', port=4370, timeout=5)
    try:
        conn = zk.connect()
        attendance = conn.get_attendance()
        curdate = datetime.now().date()
        for att in attendance:
            # if att.user_id == '170':
            date = att.timestamp.date()
            if date == curdate:
                mtime = att.timestamp.time()
                userid = att.user_id
                employee = frappe.db.get_value("Employee", {
                    "employee_no": userid, "status": "Active"})
                if employee:
                    doc = frappe.get_doc("Employee", employee)
                    pr_id = frappe.db.get_value("Punch Record", {
                        "employee": employee, "attendance_date": date})
                    if pr_id:
                        pr = frappe.get_doc("Punch Record", pr_id)
                        pr.append("timetable", {
                            "punch_time": str(mtime)
                        })
                        pr.save(ignore_permissions=True)
                    else:
                        pr = frappe.new_doc("Punch Record")
                        pr.employee = employee
                        pr.employee_name = doc.employee_name
                        pr.attendance_date = date
                        pr.append("timetable", {
                            "punch_time": mtime
                        })
                        pr.insert()
                        pr.save(ignore_permissions=True)
    except Exception, e:
        print "Process terminate : {}".format(e)
    finally:
        if conn:
            conn.disconnect()

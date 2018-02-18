# Copyright (c) 2013, Minda Sai Pvt LTd and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}
    data, row = [], []

    columns = [_("Contractor") + ":Link/Contractor:120"]
    columns += get_columns(filters)
    contractors = frappe.db.sql(
        """select name from `tabContractor` order by name""", as_dict=1)
    line_list = ["HONDA - A1", "HONDA - A2", "HONDA - A3", "EXPORT - A"]

    for contractor in contractors:
        row = [contractor.name]
        for line in frappe.get_list("Line"):
            att = frappe.db.sql(
                """select count(*) as count from `tabAttendance` where
                    docstatus=1 and status='Present' and contractor=%s and line=%s and attendance_date= %s""", (contractor.name, line["name"], filters.get("date")), as_dict=1)
            for present in att:
                present_days = present.count

            row += [present_days]
        data.append(row)

    return columns, data


def get_columns(filters):
    columns, data = [], []
    # for contractor in frappe.get_list("Contractor"):
    for line in frappe.get_list("Line"):
            # att = frappe.db.sql(
            #     """select count(*) as count from `tabAttendance` where
            #         docstatus=1 and status='Present' and contractor=%s and line=%s and attendance_date= %s""", (contractor.name, line["name"], filters.get("date")), as_dict=1)
            # for present in att:
            #     present_days = present.count
            # if present_days > 0:
        columns.append(_(line["name"]) + "::90")

    return columns

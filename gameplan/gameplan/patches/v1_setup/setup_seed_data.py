import frappe

def execute():
    # Insert System Roles/Teams if not exists
    setup_sample_project()
    setup_sample_sla_rules()

def setup_sample_project():
    if not frappe.db.exists("GP Project", "Demo Alpha"):
        proj = frappe.get_doc({
            "doctype": "GP Project",
            "title": "Demo Alpha",
            "description": "Project for UAT purposes.",
            "is_private": 0
        })
        proj.insert(ignore_permissions=True)

    if not frappe.db.exists("GP Task", {"title": "Sample Task UAT"}):
        task = frappe.get_doc({
            "doctype": "GP Task",
            "title": "Sample Task UAT",
            "project": frappe.db.get_value("GP Project", {"title": "Demo Alpha"}, "name"),
            "status": "Todo",
            "priority": "High"
        })
        task.insert(ignore_permissions=True)

def setup_sample_sla_rules():
    if not frappe.db.exists("GP SLA Rule", "มาตรฐาน 1 วัน (ด่วน)"):
        sla = frappe.get_doc({
            "doctype": "GP SLA Rule",
            "title": "มาตรฐาน 1 วัน (ด่วน)",
            "priority": "Urgent",
            "resolve_within_hours": 24,
            "is_active": 1
        })
        sla.insert(ignore_permissions=True)
        frappe.db.commit()

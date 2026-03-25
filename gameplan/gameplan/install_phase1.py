import frappe

def create_doctype(name, module, fields, is_submittable=0, is_child=0, title_field=""):
    if not frappe.db.exists("DocType", name):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": name,
            "module": module,
            "custom": 0,
            "istable": is_child,
            "is_submittable": is_submittable,
            "title_field": title_field,
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1}] if not is_child else [],
            "fields": fields
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"Created DocType: {name}")
    else:
        print(f"DocType already exists: {name}")

def execute():
    module = "Gameplan"
    
    # GP Task Dependency (Child Table)
    create_doctype("GP Task Dependency", module, [
        {"fieldname": "task", "fieldtype": "Link", "label": "Task", "options": "GP Task", "in_list_view": 1, "reqd": 1},
        {"fieldname": "dependency_type", "fieldtype": "Select", "label": "Type", "options": "Blocks\nIs Blocked By\nRelates To", "reqd": 1}
    ], is_child=1)

    # GP SLA Rule
    create_doctype("GP SLA Rule", module, [
        {"fieldname": "title", "fieldtype": "Data", "label": "Rule Name", "reqd": 1},
        {"fieldname": "priority", "fieldtype": "Select", "label": "Priority", "options": "Urgent\nHigh\nMedium\nLow", "reqd": 1},
        {"fieldname": "resolve_within_hours", "fieldtype": "Int", "label": "Resolve Within (Hours)", "reqd": 1},
        {"fieldname": "is_active", "fieldtype": "Check", "label": "Is Active", "default": "1"}
    ], title_field="title")

    # GP Escalation Rule
    create_doctype("GP Escalation Rule", module, [
        {"fieldname": "title", "fieldtype": "Data", "label": "Escalation Title", "reqd": 1},
        {"fieldname": "sla_rule", "fieldtype": "Link", "label": "SLA Rule", "options": "GP SLA Rule"},
        {"fieldname": "escalate_to", "fieldtype": "Link", "label": "Escalate To", "options": "User", "reqd": 1},
        {"fieldname": "notify_after_hours", "fieldtype": "Int", "label": "Notify After (Hours from Breach)", "default": "0"}
    ], title_field="title")

    # GP Task Template
    create_doctype("GP Task Template", module, [
        {"fieldname": "title", "fieldtype": "Data", "label": "Template Name", "reqd": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Description"},
        {"fieldname": "project", "fieldtype": "Link", "label": "Project", "options": "GP Project"},
        {"fieldname": "points", "fieldtype": "Int", "label": "Points"}
    ], title_field="title")

    # GP Workload Snapshot
    create_doctype("GP Workload Snapshot", module, [
        {"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1},
        {"fieldname": "snapshot_date", "fieldtype": "Date", "label": "Date", "reqd": 1},
        {"fieldname": "total_points", "fieldtype": "Int", "label": "Total Points Assigned"},
        {"fieldname": "overdue_tasks", "fieldtype": "Int", "label": "Overdue Tasks Count"}
    ])

    # GP Capacity Profile
    create_doctype("GP Capacity Profile", module, [
        {"fieldname": "user", "fieldtype": "Link", "label": "User", "options": "User", "reqd": 1},
        {"fieldname": "max_points_per_week", "fieldtype": "Int", "label": "Max Points Weekly", "default": "40"}
    ])

    print("Phase 1 DocTypes generation complete.")

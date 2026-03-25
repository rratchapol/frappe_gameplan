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
    
    # GP Sprint
    create_doctype("GP Sprint", module, [
        {"fieldname": "title", "fieldtype": "Data", "label": "Sprint Name", "reqd": 1},
        {"fieldname": "project", "fieldtype": "Link", "label": "Project", "options": "GP Project", "reqd": 1, "in_list_view": 1},
        {"fieldname": "start_date", "fieldtype": "Date", "label": "Start Date", "reqd": 1, "in_list_view": 1},
        {"fieldname": "end_date", "fieldtype": "Date", "label": "End Date", "reqd": 1, "in_list_view": 1},
        {"fieldname": "status", "fieldtype": "Select", "label": "Status", "options": "Planning\nActive\nCompleted", "default": "Planning", "in_list_view": 1},
        {"fieldname": "description", "fieldtype": "Text Editor", "label": "Sprint Goal"}
    ], title_field="title")

    print("Phase 4 Sprint DocType generation complete.")

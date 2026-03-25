import frappe

def execute():
    # 1. Create GP Checklist Item (Child Table)
    if not frappe.db.exists("DocType", "GP Checklist Item"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "GP Checklist Item",
            "module": "Gameplan",
            "custom": 0,
            "istable": 1,
            "fields": [
                {"fieldname": "is_completed", "fieldtype": "Check", "label": "Completed", "default": "0", "in_list_view": 1, "columns": 1},
                {"fieldname": "title", "fieldtype": "Data", "label": "Title", "reqd": 1, "in_list_view": 1, "columns": 9}
            ]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        print("Created GP Checklist Item")
    
    # 2. Update GP Task schema to include parent_task and checklists if missing
    task_dt = frappe.get_doc("DocType", "GP Task")
    
    has_parent_task = any(f.fieldname == "parent_task" for f in task_dt.fields)
    has_checklists = any(f.fieldname == "checklists" for f in task_dt.fields)
    
    changed = False
    if not has_parent_task:
        task_dt.append("fields", {
            "fieldname": "parent_task",
            "fieldtype": "Link",
            "options": "GP Task",
            "label": "Parent Task",
            "insert_after": "project"
        })
        changed = True
        
    if not has_checklists:
        task_dt.append("fields", {
            "fieldname": "checklists",
            "fieldtype": "Table",
            "options": "GP Checklist Item",
            "label": "Checklist Items",
            "insert_after": "description"
        })
        changed = True

    if changed:
        task_dt.save(ignore_permissions=True)
        frappe.db.commit()
        print("Updated GP Task with parent_task and checklists")
    else:
        print("GP Task already has required fields")

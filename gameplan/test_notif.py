import frappe

def execute():
    frappe.set_user("Administrator")
    # Get a project
    project = frappe.db.get_value("GP Project", {}, "name")
    if not project:
        print("No project found!")
        return
        
    # Create task assigned to Administrator
    task = frappe.get_doc({
        "doctype": "GP Task",
        "title": "Assignment Test Task " + frappe.generate_hash(length=4),
        "project": project,
        "assigned_to": "Administrator"
    })
    task.insert()
    frappe.db.commit()
    print(f"Task created: {task.name}. Assigned to Administrator.")
    
    # Check if notification exists
    notif = frappe.db.get_value("GP Notification", {"task": task.name, "to_user": "Administrator"}, "name")
    if notif:
        data = frappe.db.get_value("GP Notification", notif, ["name", "type", "message", "to_user", "team"], as_dict=True)
        print(f"Notification found: {data}")
    else:
        print("No notification found for this task.")

import frappe

def execute():
    frappe.set_user("Administrator")
    # Get a task
    task_name = frappe.db.get_value("GP Task", {}, "name")
    if not task_name:
        print("No task found!")
        return
        
    task = frappe.get_doc("GP Task", task_name)
    print(f"Assigning task {task.name} to alex@example.com")
    task.assigned_to = "alex@example.com"
    task.save()
    frappe.db.commit()
    
    # Check
    notif = frappe.db.get_value("GP Notification", {"task": task.name, "to_user": "alex@example.com", "type": "Assignment"}, "name")
    if notif:
        print(f"SUCCESS: Notification created: {notif}")
    else:
        print("FAILED: No notification created.")

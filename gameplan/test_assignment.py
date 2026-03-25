import frappe
def execute():
    # Make a dummy task and assignment to test Inbox notification
    proj = frappe.get_all("GP Project", limit=1)
    if not proj: return False
    
    # Try finding an existing task or make one
    task = frappe.get_doc({
        "doctype": "GP Task",
        "title": "Debug Inbox Task " + frappe.generate_hash(length=4),
        "project": proj[0].name,
        "status": "Todo",
        "assigned_to": "Administrator" 
    })
    frappe.set_user("Administrator")
    task.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # Check if notification got created
    notifs = frappe.get_all("GP Notification", filters={"task": task.name}, limit=1)
    print("Notification Output:", notifs)

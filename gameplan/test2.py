import frappe
def execute():
    proj = frappe.get_all("GP Project", limit=1)
    if not proj: return
    
    # Create empty task
    task = frappe.get_doc({
        "doctype": "GP Task",
        "title": "Inbox Debug 2 " + frappe.generate_hash(length=4),
        "project": proj[0].name,
        "status": "Todo"
    })
    frappe.set_user("Administrator")
    task.insert(ignore_permissions=True)
    frappe.db.commit()
    
    # Reload, modify assignment mathematically triggering prev_doc != current
    task.reload()
    task.assigned_to = "test_user_alpha@example.com"
    if not frappe.db.exists("User", task.assigned_to):
        frappe.get_doc({"doctype":"User", "email":task.assigned_to, "first_name":"Alpha"}).insert(ignore_permissions=True)
    
    task.save(ignore_permissions=True)
    frappe.db.commit()
    
    notifs = frappe.get_all("GP Notification", filters={"task": task.name}, limit=10)
    print("Notification Output Update:", notifs)

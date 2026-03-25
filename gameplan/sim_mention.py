import frappe

def execute():
    # Simulate a mention for Administrator
    task = frappe.get_doc("GP Task", frappe.db.get_value("GP Task", {}, "name"))
    task.description = "Hey @Administrator check this out"
    task.save()
    frappe.db.commit()
    print("Mention saved. Check Inbox.")

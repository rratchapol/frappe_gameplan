import frappe

def execute():
    try:
        data = frappe.db.get_all("GP Notification", 
                                 fields=["name", "to_user", "from_user", "type", "read", "message", "task", "project", "team"],
                                 limit=20,
                                 order_by="creation desc")
        
        output = "GP Notifications:\n"
        for d in data:
            output += f"Name: {d.name}, To: {d.to_user}, Type: {d.type}, Read: {d.read}, Task: {d.task}, Project: {d.project}, Team: {d.team}\n"
        
        with open("/workspace/notif_debug.txt", "w") as f:
            f.write(output)
        print("Debug file written to /workspace/notif_debug.txt")
    except Exception as e:
        with open("/workspace/notif_debug.txt", "w") as f:
            f.write(f"Error: {str(e)}")
        print("Error during debug script execution")

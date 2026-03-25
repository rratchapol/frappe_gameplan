import frappe

def execute():
    try:
        # Check all unread notifications
        data = frappe.get_all("GP Notification", filters={"read": 0}, fields=["*"], limit=20)
        with open("/workspace/notifs_all.txt", "w") as f:
            f.write(f"Total unread: {len(data)}\n")
            for d in data:
                f.write(str(d) + "\n")
        print("Done")
    except Exception as e:
        with open("/workspace/notifs_all.txt", "w") as f:
            f.write(f"Error: {str(e)}")

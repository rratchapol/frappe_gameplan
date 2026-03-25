import frappe

def execute():
    try:
        count = frappe.db.count("GP Notification", filters={"to_user": "Administrator", "read": 0})
        with open("/workspace/notif_count.txt", "w") as f:
            f.write(str(count))
        print(f"Debug file written to /workspace/notif_count.txt: {count}")
    except Exception as e:
        with open("/workspace/notif_count.txt", "w") as f:
            f.write(f"Error: {str(e)}")
        print("Error during debug script execution")

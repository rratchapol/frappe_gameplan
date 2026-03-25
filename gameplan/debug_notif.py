import frappe

def execute():
    frappe.set_user("Administrator")
    
    # Test 1: สร้าง GP Notification โดยตรง ตรวจสอบว่า type 'Assignment' รับได้ไหม
    try:
        n = frappe.get_doc({
            "doctype": "GP Notification",
            "to_user": "Administrator",
            "from_user": "Administrator",
            "type": "Assignment",
            "message": "debug test assignment notification",
        })
        n.insert(ignore_permissions=True)
        frappe.db.commit()
        print(f"[OK] Notification created: {n.name}")
    except Exception as e:
        print(f"[ERR] Failed to create notification: {e}")
        return
    
    # Test 2: ตรวจสอบว่า record มีอยู่จริง
    all_notifs = frappe.get_all(
        "GP Notification",
        fields=["name", "to_user", "type", "message"],
        limit=10
    )
    print(f"[INFO] All notifications in DB ({len(all_notifs)} records):")
    for x in all_notifs:
        print(f"  - {x}")

import frappe

def execute():
    # Check all notifications for Administrator
    notifs = frappe.get_all(
        "GP Notification",
        filters={"to_user": "Administrator"},
        fields=["name", "to_user", "from_user", "type", "read", "message", "task"],
        limit=20
    )
    print(f"Total notifications for Administrator: {len(notifs)}")
    for n in notifs:
        print(f"  [{n.type}] read={n.read} task={n.task} - {n.message[:50] if n.message else ''}")

    # Check ALL notifications
    all_notifs = frappe.get_all(
        "GP Notification",
        fields=["name", "to_user", "type", "read"],
        limit=20
    )
    print(f"\nAll notifications in DB: {len(all_notifs)}")
    for n in all_notifs:
        print(f"  to={n.to_user} type={n.type} read={n.read}")

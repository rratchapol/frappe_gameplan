import frappe
from frappe.utils import now_datetime, datetime, time_diff_in_hours

def check_sla_breaches():
    """ตรวจสอบว่างานแต่ละชิ้นหลุด SLA ตามกฎที่ตั้งไว้หรือไม่ แล้วยิงแจ้งเตือน/Escalate"""
    active_tasks = frappe.get_all(
        "GP Task",
        filters={
            "status": ["not in", ["Done", "Canceled"]],
            "sla_rule": ["is", "set"]
        },
        fields=["name", "creation", "title", "assigned_to", "sla_rule", "priority"]
    )
    
    now = now_datetime()
    
    for task in active_tasks:
        rule = frappe.get_doc("GP SLA Rule", task.sla_rule)
        if not rule.is_active or not rule.resolve_within_hours:
            continue
            
        elapsed_hours = time_diff_in_hours(now, task.creation)
        
        if elapsed_hours > rule.resolve_within_hours:
            # หลุด SLA
            escalation_rules = frappe.get_all(
                "GP Escalation Rule",
                filters={"sla_rule": rule.name},
                fields=["title", "escalate_to", "notify_after_hours"]
            )
            
            # ยิงแจ้งเตือน
            for esc in escalation_rules:
                if elapsed_hours >= (rule.resolve_within_hours + esc.notify_after_hours):
                    create_sla_notification(task, esc.escalate_to)

def create_sla_notification(task, notify_user):
    """ฟังก์ชันหลีกเลี่ยง Loop: เช็คว่าวันนี้ยิงแจ้งเตือนเรื่องนี้หรือยัง"""
    today_date = str(now_datetime().date())
    alert_name = f"SLA_BREACH_{task.name}_{notify_user}_{today_date}"
    
    # เช็คว่าเคยคอมเมนต์วันนี้ไหมเพื่อป้องกัน Spam
    existing_alert = frappe.get_all(
        "GP Comment",
        filters={
            "reference_doctype": "GP Task",
            "reference_name": task.name,
            "content": ["like", f"%{alert_name}%"]
        },
        limit=1
    )
    
    if existing_alert:
        return # วันนี้แจ้งไปแล้ว ป้องกัน Loop
        
    task_doc = frappe.get_doc("GP Task", task.name)
    comment_text = f"⚠️ **SLA BREACH ALERT** \nงานใบนี้เกินกำหนดระยะเวลาแก้ไขตามเงื่อนไข `{task.sla_rule}` แล้วครับ\n\nโปรดตรวจสอบด่วน @{notify_user}!\n<!-- {alert_name} -->"
    
    task_doc.add_comment("Comment", comment_text)
    task_doc.db_set("priority", "Urgent")

    # Create inbox notification
    project = task_doc.project
    team = frappe.db.get_value("GP Project", project, "team") if project else None
    notif_values = frappe._dict(
        to_user=notify_user,
        type="SLA Breach",
        task=task.name,
        project=project,
        team=team,
    )
    # Deduplicate by day using the alert_name marker in message
    existing_notif = frappe.db.exists(
        "GP Notification",
        {"to_user": notify_user, "type": "SLA Breach", "task": task.name, "message": ["like", f"%{today_date}%"]},
    )
    if not existing_notif:
        notif = frappe.get_doc(doctype="GP Notification")
        notif.message = f'Task "{task.title}" has breached its SLA ({task.sla_rule}) — {today_date}'
        notif.update(notif_values)
        notif.insert(ignore_permissions=True)

    frappe.db.commit()

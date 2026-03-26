import frappe
from datetime import timedelta
from frappe.utils import today, getdate


def get_week_start():
    """คืนค่า Monday ของ week ปัจจุบัน เพื่อใช้เป็น key ของ snapshot รายสัปดาห์"""
    d = getdate(today())
    return d - timedelta(days=d.weekday())  # weekday() 0=Mon


class WorkloadEngine:
    @staticmethod
    def capture_team_snapshots():
        week_start = get_week_start()
        week_start_str = str(week_start)
        week_end_str = str(week_start + timedelta(days=6))

        users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
        for user in users:
            # ข้ามถ้าเก็บ snapshot ของ week นี้ไปแล้ว
            if frappe.db.exists("GP Workload Snapshot", {"user": user, "snapshot_date": week_start_str}):
                continue

            active_tasks = frappe.get_all("GP Task", filters={
                "assigned_to": user,
                "status": ["not in", ["Done", "Canceled"]],
            }, fields=["name", "points", "status", "due_date"])

            # นับเฉพาะ task ที่อยู่ใน scope ของ week นี้ (logic เดียวกับ frontend)
            week_tasks = [
                t for t in active_tasks
                if (t.due_date and str(t.due_date) <= week_end_str)
                or (not t.due_date and t.status == "In Progress")
            ]

            total_points = sum(t.points or 0 for t in week_tasks)
            overdue_count = sum(1 for t in week_tasks if t.due_date and str(t.due_date) < week_start_str)

            if total_points == 0 and overdue_count == 0:
                continue

            snapshot = frappe.get_doc({
                "doctype": "GP Workload Snapshot",
                "user": user,
                "snapshot_date": week_start_str,
                "total_points": total_points,
                "overdue_tasks": overdue_count,
            })
            snapshot.insert(ignore_permissions=True)

        frappe.db.commit()

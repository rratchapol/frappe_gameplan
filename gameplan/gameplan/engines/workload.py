import frappe
from frappe.utils import today

class WorkloadEngine:
    @staticmethod
    def capture_team_snapshots():
        users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
        for user in users:
            # คำนวณ Point งานทั้งหมดที่กำลังทำ
            active_tasks = frappe.get_all("GP Task", filters={
                "assigned_to": user,
                "status": ["in", ["Backlog", "Todo", "In Progress"]]
            }, fields=["name", "points", "status", "due_date"])
            
            total_points = sum(t.points or 0 for t in active_tasks)
            current_date = str(today())
            overdue_count = sum(1 for t in active_tasks if t.due_date and str(t.due_date) < current_date)
            
            if total_points == 0 and overdue_count == 0:
                continue

            snapshot = frappe.get_doc({
                "doctype": "GP Workload Snapshot",
                "user": user,
                "snapshot_date": current_date,
                "total_points": total_points,
                "overdue_tasks": overdue_count
            })
            snapshot.insert(ignore_permissions=True)
            
        frappe.db.commit()

import frappe
from datetime import timedelta
from frappe.utils import today as today_fn, getdate


class WorkloadEngine:
    @staticmethod
    def capture_team_snapshots():
        """Run on Monday morning — records the PREVIOUS week (Mon–Sun) for reporting."""
        today = getdate(today_fn())
        # previous week: today - 7 days is last Monday, today - 1 is last Sunday
        prev_week_start = today - timedelta(days=7)
        prev_week_end = today - timedelta(days=1)
        week_start_str = str(prev_week_start)
        week_end_str = str(prev_week_end)

        users = frappe.get_all("User", filters={"enabled": 1}, pluck="name")
        for user in users:
            if frappe.db.exists("GP Workload Snapshot", {"user": user, "snapshot_date": week_start_str}):
                continue

            all_tasks = frappe.get_all("GP Task", filters={
                "assigned_to": user,
                "due_date": ["between", [week_start_str, week_end_str]],
            }, fields=["points", "status"])

            if not all_tasks:
                continue

            assigned_points = sum(t.points or 0 for t in all_tasks)
            completed_points = sum(t.points or 0 for t in all_tasks if t.status in ["Done", "Canceled"])
            incomplete_count = sum(1 for t in all_tasks if t.status not in ["Done", "Canceled"])

            snapshot = frappe.get_doc({
                "doctype": "GP Workload Snapshot",
                "user": user,
                "snapshot_date": week_start_str,
                "assigned_points": assigned_points,
                "completed_points": completed_points,
                "total_points": assigned_points - completed_points,
                "overdue_tasks": incomplete_count,
            })
            snapshot.insert(ignore_permissions=True)

        frappe.db.commit()


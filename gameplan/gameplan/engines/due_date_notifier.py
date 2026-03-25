import frappe
from frappe.utils import today, add_days, getdate


def check_due_dates():
	"""Run daily: notify assignees of tasks due tomorrow (Due Soon) or already past due (Overdue)."""
	today_date = getdate(today())
	tomorrow = add_days(today_date, 1)

	Task = frappe.qb.DocType("GP Task")

	active_filters = (
		Task.assigned_to.isnotnull()
		& (Task.assigned_to != "")
		& (Task.status.notin(["Done", "Canceled"]))
	)

	# Due Soon: tasks due exactly tomorrow
	due_soon_tasks = (
		frappe.qb.from_(Task)
		.select(Task.name, Task.title, Task.assigned_to, Task.project, Task.team, Task.due_date)
		.where(active_filters & (Task.due_date == tomorrow))
	).run(as_dict=True)

	for task in due_soon_tasks:
		_create_notification(
			task=task,
			notif_type="Due Soon",
			message=f'Task "{task.title}" is due tomorrow',
		)

	# Overdue: tasks past their due date (only notify once — dedup prevents repeats)
	overdue_tasks = (
		frappe.qb.from_(Task)
		.select(Task.name, Task.title, Task.assigned_to, Task.project, Task.team, Task.due_date)
		.where(active_filters & (Task.due_date < today_date) & Task.due_date.isnotnull())
	).run(as_dict=True)

	for task in overdue_tasks:
		_create_notification(
			task=task,
			notif_type="Overdue",
			message=f'Task "{task.title}" is overdue (due {task.due_date})',
		)

	frappe.db.commit()


def _create_notification(task, notif_type, message):
	values = frappe._dict(
		to_user=task.assigned_to,
		type=notif_type,
		task=task.name,
		project=task.project,
		team=task.team,
	)
	if frappe.db.exists("GP Notification", values):
		return

	notif = frappe.get_doc(doctype="GP Notification")
	notif.message = message
	notif.update(values)
	notif.insert(ignore_permissions=True)

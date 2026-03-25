# Copyright (c) 2022, Frappe Technologies Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import gameplan
from gameplan.extends.client import check_permissions
from gameplan.gameplan.doctype.gp_notification.gp_notification import GPNotification
from gameplan.mixins.activity import HasActivity
from gameplan.mixins.mentions import HasMentions


class GPTask(HasMentions, HasActivity, Document):
	on_delete_cascade = ["GP Comment", "GP Activity"]
	on_delete_set_null = ["GP Notification"]
	activities = ["Task Value Changed"]
	mentions_field = "description"

	def before_insert(self):
		if not self.status:
			self.status = "Backlog"

	def validate(self):
		self.validate_status_workflow()
		self.validate_dependencies()

	def validate_status_workflow(self):
		# Sync 'Done' status with 'is_completed'
		if self.status == "Done" and not self.is_completed:
			self.is_completed = 1
			self.completed_at = frappe.utils.now_datetime()
			self.completed_by = frappe.session.user
		elif self.status != "Done" and self.is_completed:
			self.is_completed = 0
			self.completed_at = None
			self.completed_by = None

	def validate_dependencies(self):
		if self.status == "Done":
			# Ensure no active blockers remain
			if getattr(self, "dependencies", None):
				for dep in self.dependencies:
					if dep.dependency_type == "Is Blocked By":
						blocking_task_status = frappe.db.get_value("GP Task", dep.task, "status")
						if blocking_task_status not in ["Done", "Canceled"]:
							frappe.throw(f"ไม่สามารถปิดงานได้ (Blocked): งานนี้ถูกบล็อคโดย Task <b>{dep.task}</b> ซึ่งยังไม่เสร็จ")

	def after_insert(self):
		self.update_tasks_count()
		if self.assigned_to:
			self.notify_assignment()

	def on_update(self):
		self.notify_mentions()
		self.log_value_updates()
		self.run_engines()

	def run_engines(self):
		prev_doc = self.get_doc_before_save()
		
		# 1. Dependency Check (ถ้างานตัวเองเพิ่งเปลี่ยนสถานะเป็น Done => วิ่งไปปลดล็อคให้ชาวบ้าน)
		if self.status == "Done" and (not prev_doc or prev_doc.status != "Done"):
			from gameplan.gameplan.engines.dependency import DependencyEngine
			frappe.enqueue(DependencyEngine.check_unblocked_tasks, completed_task_name=self.name, enqueue_after_commit=True)
			
		# 2. Auto-Assign (ถ้ายูสเซอร์ไม่ได้ Assign ใครมา ระบบจะจัดการคำนวณจาก Workload Engine หาคนที่ว่างที่สุดมาทำแทน)
		if not self.assigned_to and self.status not in ["Done", "Canceled"] and self.project:
			from gameplan.gameplan.engines.assignment import AssignmentEngine
			frappe.enqueue(AssignmentEngine.auto_assign, task_name=self.name, enqueue_after_commit=True)

	def log_value_updates(self):
		fields = ["title", "description", "status", "priority", "assigned_to", "due_date", "project"]
		for field in fields:
			prev_doc = self.get_doc_before_save()
			if prev_doc and str(self.get(field)) != str(prev_doc.get(field)):
				self.log_activity(
					"Task Value Changed",
					data={
						"field": field,
						"field_label": self.meta.get_label(field),
						"old_value": prev_doc.get(field),
						"new_value": self.get(field),
					},
				)
				if field == "assigned_to" and self.assigned_to:
					if prev_doc.assigned_to:
						self.notify_reassignment(prev_doc.assigned_to)
					else:
						self.notify_assignment()
				elif field == "status" and self.status == "Blocked":
					self.notify_blocked()

	def notify_assignment(self):
		if not self.assigned_to:
			return

		from frappe.utils import get_fullname
		author = get_fullname(frappe.session.user)

		values = frappe._dict(
			from_user=frappe.session.user,
			to_user=self.assigned_to,
			type="Assignment",
			task=self.name,
			project=self.project,
		)
		if self.project:
			values.team = frappe.db.get_value("GP Project", self.project, "team")

		if frappe.db.exists("GP Notification", values):
			return

		notification = frappe.get_doc(doctype="GP Notification")
		notification.message = f"{author} assigned you to task \"{self.title}\""
		notification.update(values)
		notification.insert(ignore_permissions=True)

	def notify_reassignment(self, old_assignee):
		if not self.assigned_to or not old_assignee:
			return

		from frappe.utils import get_fullname
		author = get_fullname(frappe.session.user)
		new_assignee_name = get_fullname(self.assigned_to)
		team = frappe.db.get_value("GP Project", self.project, "team") if self.project else None

		# Notify the new assignee
		new_values = frappe._dict(
			from_user=frappe.session.user,
			to_user=self.assigned_to,
			type="Assignment",
			task=self.name,
			project=self.project,
			team=team,
		)
		if not frappe.db.exists("GP Notification", new_values):
			notif = frappe.get_doc(doctype="GP Notification")
			notif.message = f"{author} assigned you to task \"{self.title}\""
			notif.update(new_values)
			notif.insert(ignore_permissions=True)

		# Notify the old assignee that the task was reassigned away
		old_values = frappe._dict(
			from_user=frappe.session.user,
			to_user=old_assignee,
			type="Reassignment",
			task=self.name,
			project=self.project,
			team=team,
		)
		if not frappe.db.exists("GP Notification", old_values):
			notif = frappe.get_doc(doctype="GP Notification")
			notif.message = f'Task "{self.title}" has been reassigned to {new_assignee_name}'
			notif.update(old_values)
			notif.insert(ignore_permissions=True)

	def notify_blocked(self):
		user_to_notify = self.assigned_to or self.owner
		if not user_to_notify:
			return

		values = frappe._dict(
			from_user=frappe.session.user,
			to_user=user_to_notify,
			type="Blocked",
			task=self.name,
			project=self.project,
		)
		if self.project:
			values.team = frappe.db.get_value("GP Project", self.project, "team")

		if frappe.db.exists("GP Notification", values):
			return

		notif = frappe.get_doc(doctype="GP Notification")
		notif.message = f'Task "{self.title}" has been marked as Blocked'
		notif.update(values)
		notif.insert(ignore_permissions=True)

	def update_comments_count(self):
		comments_count = frappe.db.count(
			"GP Comment", {"reference_doctype": "GP Task", "reference_name": self.name}
		)
		self.db_set("comments_count", comments_count)

	def on_trash(self):
		self.update_tasks_count()

	def update_tasks_count(self):
		if not self.project:
			return
		frappe.get_doc("GP Project", self.project).update_tasks_count()

	@frappe.whitelist()
	def track_visit(self):
		GPNotification.clear_notifications(task=self.name)


@frappe.whitelist()
def get_list(
	fields: str = None,
	filters: str = None,
	order_by: str = None,
	start: int = 0,
	limit: int = 20,
	group_by: str = None,
	parent: str = None,
	debug=False,
):
	doctype = "GP Task"
	check_permissions(doctype, parent)
	fields = frappe.parse_json(fields) if fields else None
	filters = frappe.parse_json(filters) if filters else None
	assigned_or_owner = filters.pop("assigned_or_owner", None) if filters else None
	limit = int(limit)

	query = frappe.qb.get_query(
		doctype,
		fields=fields,
		filters=filters,
		order_by=order_by,
		offset=start,
		limit=limit + 1,
		group_by=group_by,
	)
	if assigned_or_owner:
		Task = frappe.qb.DocType(doctype)
		query = query.where((Task.assigned_to == assigned_or_owner) | (Task.owner == assigned_or_owner))

	data = query.run(as_dict=True, debug=debug)
	frappe.response["has_next_page"] = len(data) > limit
	return data[:limit]


def get_permission_query_conditions(user):
	if not user:
		user = frappe.session.user

	if not gameplan.is_guest(user):
		return None

	escaped_user = frappe.db.escape(user)
	return f"""`tabGP Task`.project in (
		select `tabGP Guest Access`.project
		from `tabGP Guest Access`
		where `tabGP Guest Access`.user = {escaped_user}
	)"""


def has_permission(doc, ptype="read", user=None):
	user = user or frappe.session.user

	if not gameplan.is_guest(user):
		return True

	if not doc.project:
		return False

	return bool(frappe.db.exists("GP Guest Access", {"user": user, "project": doc.project}))

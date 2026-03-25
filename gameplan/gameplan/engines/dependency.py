import frappe

class DependencyEngine:
    @staticmethod
    def check_unblocked_tasks(completed_task_name):
        """ปลดล็อค Task อื่นๆ ที่กำลังถูกบล็อคโดย Task นี้ หากเสร็จสิ้นแล้ว"""
        # หางานอื่นที่ลงสถานะว่าตัวเองถูกบล็อคโดยงานที่เพิ่งเสร็จนี้
        blocked_links = frappe.get_all("GP Task Dependency", filters={
            "task": completed_task_name,
            "dependency_type": "Is Blocked By"
        }, pluck="parent")

        # ตรวจสอบแต่ละงานว่าพ้นสถานะ Blocker หมดหรือยัง
        for parent_task_name in set(blocked_links):
            parent_task = frappe.get_doc("GP Task", parent_task_name)
            
            # เช็คว่า Blocker ทุกตัวของของ parent_task สถานะเป็น Done ครบยัง
            all_blockers_done = True
            for dep in parent_task.dependencies:
                if dep.dependency_type == "Is Blocked By":
                    status = frappe.db.get_value("GP Task", dep.task, "status")
                    if status not in ["Done", "Canceled"]:
                        all_blockers_done = False
                        break
            
            # ถ้าครบแล้ว และตัวเองอยู่ในสถานะคลุมเครือ (ยังไม่เสร็จ) => ปรับให้พร้อมทำ
            if all_blockers_done and parent_task.status not in ["Done", "Canceled", "In Progress", "Todo"]:
                parent_task.db_set("status", "Todo")
                parent_task.add_comment("Comment", "🔄 **Dependency Engine:** งานทั้งหมดที่ขวางงานนี้อยู่เสร็จสิ้นเรียบร้อยแล้ว ระบบปรับสถานะเป็น **Todo** อัตโนมัติพร้อมเริ่มงาน!")

import frappe
import unittest

from gameplan.gameplan.engines.workload import WorkloadEngine
from gameplan.gameplan.engines.dependency import DependencyEngine
from gameplan.gameplan.engines.assignment import AssignmentEngine

class TestGameplanEngines(unittest.TestCase):
    def setUp(self):
        # Create Mock User if doesn't exist
        if not frappe.db.exists("User", "test_user_alpha@example.com"):
            user = frappe.get_doc({"doctype": "User", "email": "test_user_alpha@example.com", "first_name": "Alpha"})
            user.insert(ignore_permissions=True)
            
        # Create Mock Project
        if not frappe.db.exists("GP Project", "Test Project Alpha"):
            project = frappe.get_doc({"doctype": "GP Project", "title": "Test Project Alpha", "is_private": 0})
            project.insert(ignore_permissions=True)
            self.project_name = project.name
        else:
            self.project_name = frappe.db.get_value("GP Project", {"title": "Test Project Alpha"}, "name")

    def test_dependency_engine_blocks_task_completion(self):
        # สร้างงานต้นน้ำ
        blocker = frappe.get_doc({
            "doctype": "GP Task",
            "title": "Blocker Task",
            "project": self.project_name,
            "status": "Todo"
        }).insert(ignore_permissions=True)
        
        # สร้างงานปลายน้ำที่ถูกบล็อค
        dependent = frappe.get_doc({
            "doctype": "GP Task",
            "title": "Dependent Task",
            "project": self.project_name,
            "status": "Blocked"
        })
        dependent.append("dependencies", {
            "task": blocker.name,
            "dependency_type": "Is Blocked By"
        })
        dependent.insert(ignore_permissions=True)
        
        # ถ้ายูสเซอร์ทะลึ่งพยายามปรับ status เป็น Done ควรจะ throw error!
        dependent.status = "Done"
        self.assertRaises(frappe.ValidationError, dependent.save)
        
        # ลบข้อมูลทิ้งหลังเทสต์เสร็จ
        frappe.delete_doc("GP Task", dependent.name)
        frappe.delete_doc("GP Task", blocker.name)

    def test_assignment_engine_capacity(self):
        # ลองรันจำลอง ไม่ต้องเจาะจง Project ก็ได้ ให้ Method ไม่ error โค้ด
        user = AssignmentEngine.recommend_assignee(self.project_name, 5)
        # อาจจะคืนค่า None ถ้าไม่มี Team Member ก็ถือว่าปกติ
        self.assertIn(user, [None, "test_user_alpha@example.com"])
        
    def test_workload_engine(self):
        # โค้ดควรจะรันผ่านได้โดยไม่บอมบ์
        try:
            WorkloadEngine.capture_team_snapshots()
            ran_successfully = True
        except Exception:
            ran_successfully = False
        
        self.assertTrue(ran_successfully)

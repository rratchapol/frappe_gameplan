import frappe

class AssignmentEngine:
    @staticmethod
    @frappe.whitelist()
    def recommend_assignee(project, required_points=0):
        # ดึงสมาชิกทั้งหมดในทีมของโปรเจกต์นี้
        project_doc = frappe.get_doc("GP Project", project)
        if not project_doc.team:
            return None
            
        team_members = frappe.get_all("GP Team Member", filters={"parent": project_doc.team}, pluck="user")
        if not team_members:
            return None

        candidates = []
        for user in team_members:
            # ตรวจสอบ Capacity สูงสุดต่อสัปดาห์
            capacity_profile = frappe.get_all("GP Capacity Profile", filters={"user": user}, fields=["max_points_per_week"])
            max_points = capacity_profile[0].max_points_per_week if capacity_profile else 40
            
            # ตรวจสอบภาระงานที่ถืออยู่ปัจจุบัน
            active_tasks = frappe.get_all("GP Task", filters={
                "assigned_to": user,
                "status": ["in", ["Backlog", "Todo", "In Progress"]]
            }, pluck="points")
            
            current_points = sum(filter(None, active_tasks))
            
            available_capacity = max_points - current_points
            
            # ถ้ารับไหว คัดลอนเข้าลิตส์
            if available_capacity >= required_points:
                candidates.append({
                    "user": user,
                    "available_capacity": available_capacity,
                    "current_points": current_points
                })

        if not candidates:
            return None

        # เรียงลำดับคนที่ว่างที่สุดขึ้นมาก่อน
        candidates.sort(key=lambda x: x["available_capacity"], reverse=True)
        return candidates[0]["user"]

    @staticmethod
    def auto_assign(task_name):
        task = frappe.get_doc("GP Task", task_name)
        if task.assigned_to:
            return # มีคนทำแล้ว
        
        if not task.project:
            return
            
        best_user = AssignmentEngine.recommend_assignee(task.project, task.points or 0)
        if best_user:
            task.db_set("assigned_to", best_user)
            task.add_comment("Comment", f"🤖 Auto-Assignment Engine: มอบหมายงานให้ **{best_user}** เนื่องจากเป็นผู้ที่มีเวลาว่างมากที่สุดในทีม")
            return best_user
        
        return None

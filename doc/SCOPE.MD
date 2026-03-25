🎯 Scope หลักของ Project Manager (ใน Frappe Gameplan)
เอกสารทั้งสองพูดถึงระบบที่ต้องดีกว่า ClickUp ในบริบทองค์กร โดยต้องการมองเห็นภาพรวมและควบคุมโครงการได้จริง

📦 ฟีเจอร์ที่ต้องการ (แบ่งตามกลุ่ม)
1. Task & Project Visibility

สร้าง Task จาก Project พร้อม field บังคับ (owner, due date, status, priority, type)
แตก Subtask และ Checklist จากงานหลักได้
มองเห็น Task lifecycle ครบ: backlog → in progress → blocked → done → closed

2. Assignment & Workload Control

Smart assignment ตาม role, ทีม, skill, capacity และ priority
Reassign งานพร้อม audit trail (เห็นว่าใครโอนให้ใคร เมื่อไหร่)
Workload View — ดูภาระงานรายคน/รายทีม และ capacity ที่เหลือ
Queue balancing และ rebalancing recommendation

3. Dependency & Blocker Management

กำหนด dependency ระหว่าง task (blocked-by / blocking)
ระบบแสดง blocked status ชัดเจน, ป้องกันปิดงาน downstream ก่อนงาน upstream เสร็จ
เห็น risk ได้ทันที

4. Sprint & Release Planning

Sprint planning — เพิ่มงานเข้า sprint และมองเห็น capacity
Backlog grooming และ carry-forward rule (งานค้างข้าม sprint)
Milestone tracking และ release bucket

5. Cockpit / Dashboard

Dashboard สำหรับ ดู: overdue, blocked, at-risk, unassigned, overloaded, sprint health
Workload/capacity view รายคนและรายทีม
Dashboard ตัวเลขหลักต้องตรงกับข้อมูลจริง (UAT-TA-011 Critical)

6. Notification & Escalation

แจ้งเตือนตามเหตุการณ์: assigned, due soon, overdue, blocked, reassigned, SLA breach
Escalation chain → Team Lead → PM → Operations
ไม่ spam / มี throttle และ digest

7. Reporting

รายงานเชิงบริหาร: งานเสี่ยง, overdue summary, owner performance, sprint status
Filter และ export สำหรับ operational และ management view

8. Permission & Audit Trail

สิทธิ์แยกชัด: Developer, Team Lead, PM, Operations, Executive Viewer
ทุก action บันทึก audit (assign, reassign, delay, close, AI suggestion)


🔲 ขอบเขต UAT ที่ต้องยืนยัน (Scenario หลัก)
Testสิ่งที่ต้อง  Pass
UAT-TA-001  สร้าง Task จาก Project task ถูกสร้าง, ID ถูก generate, owner/due date/status ถูกต้อง
UAT-TA-002  แตก Subtask และ Checklist subtask เชื่อม parent ถูก, checklist แสดงครบ
UAT-TA-003  Assignment + รับแจ้งเตือนถูกต้อง
UAT-TA-004  Reassign + audit trail
UAT-TA-005  Dependency blocking ทำงานถูก
UAT-TA-006  Overdue + escalation ถึง PM
UAT-TA-007  Sprint planning + dashboard อัปเดต
UAT-TA-008  Workload view ตรงจริง
UAT-TA-009  Permission Restriction ยืนยันว่า user ไม่เห็น/แก้ไขงานนอกสิทธิ์
UAT-TA-010  Close/Reopen Task ยืนยันว่าวงจรปิดงานและเปิดใหม่ตรง policy close criteria ถูกบังคับ, reopen เก็บประวัติ
UAT-TA-011  Dashboard ตัวเลขถูกต้อง (Critical)


สรุปคือ Frappe Gameplan ที่ใช้ ในโปรเจกต์นี้ต้องครอบคลุมตั้งแต่ Task Lifecycle → Assignment → Dependency → Sprint → Dashboard → Escalation แบบ end-to-end ไม่ใช่แค่ดู task รายตัว
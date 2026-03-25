1. หลักการดำเนินงาน
ทีม Programmer ต้องพัฒนาระบบโดยหลีกเลี่ยงการแก้ไข ERPNext core โดยตรงให้มากที่สุด ใช้ Custom App, Custom DocType, Custom Field, Hooks, Fixtures, Services, Reports, Dashboard 

2. ผลลัพธ์ที่คาดหวัง
ได้ระบบ Task & Assignment บน ERPNext ที่รองรับ task lifecycle, smart assignment, dependency control, workload balancing, sprint planning, notifications, PM cockpit และรายงานเชิงบริหาร
ได้โครงสร้างทางเทคนิคที่รองรับการขยายต่อไปยัง HR, CRM, ERP operations, Helpdesk, Approval flow และ analytics เชิงผู้บริหาร

3. หลักการออกแบบเชิงเทคนิค
Extension-first architecture: พัฒนาโดยใช้ custom app และกลไกมาตรฐานของ Frappe/ERPNext ก่อนการแตะ core เสมอ
Service-layer business logic: นำ logic เรื่อง assignment, workload, scoring, dependency และ SLA ไปไว้ใน Python services เพื่อให้ทดสอบและบำรุงรักษาได้ง่าย
Configuration before hard-code: matrix ของ status, priority, queue, SLA, escalation และ assignment policy ต้องตั้งค่าได้
Auditability: การมอบหมาย การเปลี่ยน owner การเลื่อนกำหนด การปิดงานอัตโนมัติ และข้อเสนอจาก AI ต้องตรวจสอบย้อนหลังได้
Role-safe UX: สิทธิ์ของ Developer, Team Lead, Project Manager, Operations และ Executive Viewer ต้องแยกชัดเจน
Upgrade-safe and testable: ทุกพฤติกรรมสำคัญต้องมี tests, fixtures หรือ migration patches รองรับ

4. โครงสร้างแอปและการแบ่งโมดูล
รายละเอียดงาน
สร้าง package structure สำหรับ task intelligence, assignment, dependency, workload, automation, dashboard, report, API, permissions, fixtures, patches และ tests
กำหนดหน้าที่ของแต่ละโมดูลให้ชัดเจน ลดการอ้างอิงไขว้ และทำให้ import path อ่านง่าย
เตรียม hooks.py, public assets, doctype_js และ service package layout ให้พร้อมต่อยอด
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
approved module map
เกณฑ์สำเร็จของงาน
โครงสร้างตรงกับ technical design
ไม่เกิด circular imports ในรอบแรก

5. การสร้าง Domain Model จริง
รายละเอียดงาน
สร้าง Custom DocType ตามแบบที่อนุมัติ เช่น Task Template, Task Dependency, Assignment Queue, Workload Snapshot, Capacity Profile, SLA Rule, Escalation Rule และ AI Task Draft
กำหนด field type, child table, naming series, link relationship, permissions และ policy เรื่อง amend/cancel ตามความจำเป็น
เชื่อมข้อมูลเข้ากับ Project, Task, ToDo, Timesheet, Employee และ User ของ ERPNext/Frappe ให้เรียบร้อย
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
approved domain model
เกณฑ์สำเร็จของงาน
DocType ทำงานได้จริง
link และ permission ถูกต้อง

6. การเพิ่ม Custom Field ให้ Standard Objects
รายละเอียดงาน
นำ custom field matrix มาปรับใช้กับ Project, Task, ToDo, Employee และวัตถุอื่นที่เกี่ยวข้อง
กำหนด field grouping, default value, visibility, depends_on และ required conditions ให้เหมาะกับการใช้งานจริง
export fixtures และจัดทำรายการ property setter ที่จำเป็นอย่างเป็นระบบ
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
approved custom field matrix
เกณฑ์สำเร็จของงาน
form ใช้งานได้ไม่รก
fixtures sync ได้สม่ำเสมอ

7. การพัฒนา Task Lifecycle และ Status Model
รายละเอียดงาน
สร้างโมเดลสถานะงานแบบตั้งค่าได้ เช่น backlog, ready, in progress, blocked, in review, waiting external, done, closed, archived
กำหนด transition rule, required field, approval gate, reopen logic และ guard condition ก่อนปิดงาน
รองรับ task type หลายประเภท เช่น bug, story, implementation, issue, request, approval และ operational task
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
PM-approved status model
เกณฑ์สำเร็จของงาน
สถานะงานเปลี่ยนตาม matrix ที่อนุมัติ

8. การพัฒนา Assignment Engine
รายละเอียดงาน
สร้าง rule-based assignment logic โดยใช้บทบาท ทีม queue skill tag capacity score priority SLA และ project context
รองรับทั้งโหมด auto-assign และ recommendation mode พร้อมเหตุผลประกอบ
บันทึกคะแนน เหตุผล และประวัติการ reassign เพื่อการ audit
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
assignment policy approved
เกณฑ์สำเร็จของงาน
assignment scenarios ทำงานคงที่และตรวจสอบได้

9. การจัดการ Dependency และ Blocker
รายละเอียดงาน
สร้าง predecessor-successor relationship สำหรับ task/subtask
คำนวณ blocked state, unblocking event, warning indicator, critical dependency flag และ overdue predecessor escalation
ป้องกันการปิดงาน downstream ก่อนงานต้นน้ำที่จำเป็นเสร็จ
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
approved dependency model
เกณฑ์สำเร็จของงาน
blocked logic ทำงานถูกต้อง
PM มองเห็น risk ได้

10. การคำนวณ Workload และ Capacity
รายละเอียดงาน
พัฒนา service สำหรับคำนวณภาระงานปัจจุบัน ความจุที่เหลือ งานค้างเกินกำหนด และความพร้อมในช่วงเวลาถัดไปทั้งระดับบุคคลและทีม
สร้าง snapshot และ summary view สำหรับ PM, Team Lead และ Operations
เตรียม data structure สำหรับคำแนะนำการ rebalancing และ fairness analysis
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
capacity planning design approved
เกณฑ์สำเร็จของงาน
workload summary และ rebalancing data ใช้งานได้

11. การทำ Sprint / Queue / Recurring Task Support
รายละเอียดงาน
เพิ่มการรองรับ sprint, release bucket, operational queue, recurring task template และ carry-forward rule
กำหนดความสัมพันธ์ระหว่าง recurring tasks กับ assignment policy และ due date calculation
รองรับการ roll-over ของงานค้างจาก sprint ก่อนหน้าอย่างควบคุมได้
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
planning policy approved
เกณฑ์สำเร็จของงาน
planner ใช้งานได้ใน scenario จริง

12. การพัฒนา UI, Dashboard และ PM Cockpit
รายละเอียดงาน
ปรับฟอร์ม task และ project ให้แสดงข้อมูล assignment, dependency, workload, SLA, blocker อย่างอ่านง่าย
สร้าง dashboard สำหรับ Team Lead และ PM เพื่อดู overdue, blocked, at-risk, unassigned, overloaded และ sprint health
พัฒนารายงานและ filter ให้พร้อมใช้จริงทั้งในมุม operational และ management
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
dashboard/report specification
เกณฑ์สำเร็จของงาน
key users ใช้งานได้จริง
ข้อมูลตรงกับ source documents

13. Notification, Escalation และ Workflow Automation
รายละเอียดงาน
พัฒนากลไกแจ้งเตือนตามเหตุการณ์ เช่น assigned, due soon, overdue, blocked, waiting approval, reassigned และ SLA breach
สร้าง escalation chain ไปยัง Team Lead / PM / Operations ตามเงื่อนไขที่กำหนด
ออกแบบ automation ให้โปร่งใส ปรับค่าได้ และไม่สร้าง loop การแจ้งเตือน
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
notification matrix approved
เกณฑ์สำเร็จของงาน
notification ตรงเวลาและไม่ spam

14.  การเขียน Migration, Patch และ Seed Data
รายละเอียดงาน
จัดทำ patches สำหรับสร้างค่าเริ่มต้น ย้ายข้อมูลเดิม และ backfill custom fields / statuses / queues / rules
จัดทำ seed data สำหรับ SIT และ UAT เช่น project template, task template, users, team structures และ sample tasks
ทดสอบ install ใหม่และ migrate จาก site ตัวอย่างให้ครบ
ข้อมูลนำเข้า / เงื่อนไขก่อนเริ่ม
installation and migration design
เกณฑ์สำเร็จของงาน
site ใหม่ install ได้
site เดิม update ได้


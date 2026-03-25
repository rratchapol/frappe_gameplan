# 📋 Gameplan Custom App - Implementation Plan & TODO

เอกสารนี้รวบรวมแผนการทำงานตามข้อกำหนดใน `SPEC.MD` และ `PROGRAMMER.MD` 
เพื่อป้องกันการเกิด Error และรักษาโครงสร้าง Clean Architecture เราจะแบ่งการพัฒนาออกเป็นเฟส (Phases) เพื่อให้ง่ายต่อการทดสอบและตรวจสอบความถูกต้อง

---

## 🏗️ Phase 1: Core Foundation & Domain Model (SPEC #4, #5, #6)
เป้าหมาย: สร้างโครงสร้างตารางและฐานข้อมูลพื้นฐานที่ไม่กระทบระบบหลัก
- [x] จัดโครงสร้างโฟลเดอร์สำหรับ Service Layer (เช่น `gameplan/services/`, `gameplan/engines/`)
- [x] สร้าง Custom DocTypes หลัก:
  - [x] `GP Task Dependency` (เก็บความสัมพันธ์งานอ้างอิง)
  - [x] `GP Capacity Profile` / `GP Workload Snapshot` (คำนวณภาระงาน)
  - [x] `GP SLA Rule` & `GP Escalation Rule` (กฎการแจ้งเตือน)
  - [x] `GP Task Template` & `GP AI Task Draft`
- [x] ผูก Fixtures / Custom Fields เข้ากับ `GP Task` และ `GP Project` ให้ทำงานร่วมกันได้ตามโครงสร้างที่ออกแบบมา

## 🚦 Phase 2: Workflow & Task Lifecycle (SPEC #7)
เป้าหมาย: คุมสถานะงานและการเปลี่ยนสถานะ (State Machine)
- [x] วางระบบ Transition Logic ให้ Status (เช่น จาก Backlog -> In Progress -> Done)
- [x] ฝัง Python Hooks ป้องกันการเปลี่ยนสถานะข้ามขั้น หรือการปิดงานที่ข้อมูลไม่ครบ

## ⚙️ Phase 3: Core Business Engines (SPEC #8, #9, #10)
เป้าหมาย: สร้างสมองกลในการคำนวณต่างๆ (ทดสอบด้วย Unit Test ได้)
- [x] **Dependency Engine**: Logic คำนวณสถานะ Blocked / Unblocked อัตโนมัติเมื่ออัปเดตงานต้นน้ำ
- [x] **Workload Engine**: Service สรุป Capacity ของคนในทีม และสถานะคำนวณ Overload
- [x] **Assignment Engine**: ระบบแนะนำหรือ Auto-assign ผู้รับผิดชอบงานตาม Skill/Priority

## 📊 Phase 4: Sprints & Front-end UI / Dashboards (SPEC #11, #12)
เป้าหมาย: อัปเดตหน้าจอ Gameplan Vue.js ให้ผู้จัดการและลูกทีมใช้งานง่าย
- [x] เพิ่มโครงสร้างระบบ Sprint / Release Bucket
- [x] ปรับปรุงหน้าจอรายละเอียก Task ให้แสดง SLA, Blocker, และข้อมูลจาก Engine
- [x] สร้าง **PM Cockpit Dashboard** ในหน้าจอ Vue.js แสดงงาน Overdue/Blocked

## 🔔 Phase 5: Notification & Automation (SPEC #13)
- [x] สร้าง Event-driven triggers แจ้งเตือนเมื่อ SLA breach หรือเมื่อมี Blocker เพิ่ม
- [x] ทำระบบจำกัด Loop ของ Notification

## 🧪 Phase 6: Test Package & Deployment (SPEC #14, PROGRAMMER.MD)
- [x] เขียน Unit Tests สำหรับทุก Engines หลัก
- [x] สร้าง Seed Data & Patch สำหรับหน้างาน UAT
- [x] รวบรวม Deployment scripts ให้พร้อม Deploy จริง

---

**Next Action (ที่กำลังจะทำ):**
- 🌟 PROJECT COMPLETED! 🎉 ฉลองความสำเร็จ! ขอแสดงความยินดีด้วยครับ ทีมสามารถนำแพ็กเกจนี้ขึ้น Production ได้เลย

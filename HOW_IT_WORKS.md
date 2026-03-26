# วิธีการทำงานของ Gameplan

คู่มือสำหรับศึกษาโครงสร้างและ flow ของ project นี้

---

## 1. ภาพรวม

**Gameplan** คือ **async-first discussions tool** สำหรับทีมที่ทำงาน remote สร้างด้วย Frappe Framework (Python) และ Vue 3 SPA (TypeScript) โดยเปิดให้คนเข้ามาคุยในเวลาของตัวเองโดยไม่ต้องออนไลน์พร้อมกัน

ฟีเจอร์หลัก:
- **Spaces** (GP Project) — พื้นที่สำหรับจัดกลุ่ม Discussion / Task / Page ตาม topic
- **Projects** (GP Team) — Category ที่ใช้รวม Space หลายๆ อันไว้ด้วยกัน
- **Discussions** — กระทู้หลักสำหรับถกเถียงแบบ async ไม่ต้องอยู่พร้อมกัน
- **Tasks** — การจัดการงานพร้อม SLA, Dependency, Auto-assignment, Sprint
- **Pages** — Collaborative documents คล้ายกับ Notion
- **Notifications** — แจ้งเตือน mention, reaction, assignment, role changed, project added, task status changed
- **Full-text Search** — ค้นหา Discussion / Task / Page / Comment ด้วย SQLite FTS5
- **Roles** — GP Role ผูกกับ Frappe Role (Admin / Member / Guest) ต่อ user
- **Invitations** — เชิญ user ใหม่ผ่าน email พร้อมกำหนด GP Role
- **Workload** — วัด capacity และบันทึก workload snapshot รายวัน
- **SLA** — กำหนดระยะเวลาตอบสนองต่อ task พร้อม escalation

---

## 2. โครงสร้างของ Repository

```
gameplan/
│
├── frontend/                    ← Vue 3 SPA (TypeScript + Vite)
│   ├── src/
│   │   ├── main.js              ← Entry point: ลงทะเบียน plugins, global components
│   │   ├── router.js            ← Vue Router: ทุก route ของ SPA
│   │   ├── socket.js            ← Socket.IO: รับ real-time events
│   │   ├── App.vue              ← Root component
│   │   ├── pages/               ← Page components (1 ไฟล์ต่อ route)
│   │   ├── components/          ← Shared UI components
│   │   ├── data/                ← Composables สำหรับ fetch ข้อมูล (useList, useDoc)
│   │   ├── composables/         ← Reusable Vue logic
│   │   └── utils/               ← Helper functions
│
├── gameplan/                    ← Frappe app (Python backend)
│   ├── hooks.py                 ← จุดเริ่มต้น: ลงทะเบียน hooks ทั้งหมด
│   ├── api.py                   ← Whitelisted API endpoints
│   ├── search_sqlite.py         ← Full-text search (SQLite FTS5)
│   ├── www/g.py                 ← Serve Vue SPA + boot data
│   ├── mixins/                  ← Reusable Python mixins สำหรับ DocType
│   │   ├── mentions.py          ← HasMentions: notify เมื่อมี @mention
│   │   ├── reactions.py         ← HasReactions: emoji reactions
│   │   ├── activity.py          ← HasActivity: บันทึก activity log
│   │   ├── tags.py              ← HasTags: tagging system
│   │   ├── archivable.py        ← Archivable: archive/unarchive document
│   │   └── manage_members.py    ← ManageMembersMixin: จัดการ member ใน project/team
│   └── gameplan/
│       ├── doctype/             ← DocType definitions (schema + controller)
│       └── engines/             ← Background logic engines
│           ├── assignment.py    ← Auto-assign งานให้คนที่ว่างที่สุด
│           ├── dependency.py    ← ปลดล็อค task เมื่อ blocker เสร็จ
│           ├── sla.py           ← ตรวจสอบงานที่หลุด SLA และ escalate
│           ├── workload.py      ← บันทึก workload snapshot รายวัน
│           └── due_date_notifier.py ← แจ้งเตือนงานที่ใกล้ครบกำหนด
│
├── frappe-ui/                   ← Local copy ของ frappe-ui library
└── docker/                      ← Docker infrastructure
```

---

## 3. จุดเริ่มต้น: `hooks.py`

`hooks.py` คือไฟล์ที่ Frappe อ่านเพื่อรู้ว่า app นี้ทำอะไรบ้าง

### 3.1 ลงทะเบียน Permission Hooks

```python
permission_query_conditions = {
    "GP Discussion": "...gp_discussion.get_permission_query_conditions",
    "GP Task":       "...gp_task.get_permission_query_conditions",
    "GP Comment":    "...gp_comment.get_permission_query_conditions",
    "GP Page":       "...gp_page.get_permission_query_conditions",
}

has_permission = {
    "GP Discussion": "...gp_discussion.has_permission",
    "GP Task":       "...gp_task.has_permission",
    "GP Comment":    "...gp_comment.has_permission",
    "GP Page":       "...gp_page.has_permission",
}
```

Frappe เรียก function เหล่านี้ทุกครั้งก่อน query หรือก่อน load document เพื่อตรวจสอบสิทธิ์

### 3.2 ลงทะเบียน Document Event Hooks

```python
doc_events = {
    "*": {
        "on_trash": "gameplan.mixins.on_delete.on_trash",  # cascade delete ทุก doctype
    },
    "User": {
        "after_insert": "...gp_user_profile.create_user_profile",  # สร้าง profile อัตโนมัติ
        "on_trash":     ["...delete_user_profile", "...on_user_delete"],
        "on_update":    "...gp_user_profile.on_user_update",
    },
}
```

### 3.3 Scheduled Tasks

```python
scheduler_events = {
    "hourly": [
        "...gp_invitation.expire_invitations",          # ลบ invitation ที่หมดอายุ
        "...engines.sla.check_sla_breaches"             # ตรวจงานที่หลุด SLA
    ],
    "daily": [
        "...demo.generate_data_daily",
        "...engines.workload.WorkloadEngine.capture_team_snapshots",  # บันทึก workload
        "...engines.due_date_notifier.check_due_dates", # แจ้งเตือนงานใกล้ครบกำหนด
    ],
}
```

---

## 4. Entry Point ของ Frontend: `www/g.py`

เมื่อ user เปิด `/g` ใน browser:

```
GET /g/anything
    └→ www/g.py :: get_context()
        ├── login_as_demo_user_if_enabled()
        ├── get_boot()  → ส่งข้อมูลเริ่มต้นไปให้ Vue SPA
        │      ├── frappe_version, app_version
        │      ├── site_name, system_timezone
        │      └── default_route (home page ที่จะ redirect ไป)
        └── csrf_token → ส่งไปใน context สำหรับ security

Vue SPA รับ boot data แล้ว mount app ผ่าน main.js
    → router.js ตัดสินใจว่าจะ redirect ไป route ไหน
```

---

## 5. Document Lifecycle ใน Frappe

```
User กด Save
    → validate(doc)       ← ตรวจสอบข้อมูล sanitize content
    → before_insert(doc)  ← set default fields ก่อน insert ครั้งแรก
    → [บันทึกลง DB]
    → after_insert(doc)   ← trigger side effects (notifications, unread records)
    → on_update(doc)      ← trigger เมื่อ save ทุกครั้ง (mentions, reactions)

User กด Delete
    → on_trash(doc)       ← cleanup related records
    → after_delete(doc)   ← update counters ใน parent documents

docstatus: ใน Gameplan ไม่ใช้ Submit/Cancel workflow
```

---

## 6. Flow: Discussion (กระทู้)

### เมื่อ User **สร้าง Discussion**

```
POST /api/resource/GP Discussion
    └→ GPDiscussion.before_insert()
        ├── check_if_project_is_archived()  → โยน error ถ้า project ถูก archive
        ├── last_post_at = now()
        └── update_participants_count()      → นับจำนวนคนที่มีส่วนร่วม

    └→ GPDiscussion.after_insert()
        ├── update_discussions_count()       → บวก counter ใน GP Project
        └── GPUnreadRecord.create_unread_records_for_discussion()
               → สร้าง unread record ให้ทุกคนใน project (ยกเว้น owner)
```

### เมื่อ User **เปิดอ่าน Discussion**

```
GET /api/resource/GP Discussion/<name>
    └→ GPDiscussion.as_dict()
        ├── ดึง last_visit ของ user คนนี้จาก GP Discussion Visit
        ├── หา last_unread_comment (comment แรกหลัง last_visit)
        ├── หา last_unread_poll
        ├── is_bookmarked (เช็ค GP Bookmark)
        └── views = count ของ GP Discussion Visit

frontend track_visit() → อัปเดต GP Discussion Visit.last_visit = now()
```

### เมื่อ User **comment ใน Discussion**

```
POST /api/resource/GP Comment
    └→ GPComment.before_insert()
        └── เช็คว่า discussion ไม่ได้ closed อยู่ (ถ้า closed → throw error)

    └→ GPComment.after_insert()
        ├── update_discussion_meta()
        │      ├── discussion.update_last_post()      → อัปเดต last_post_at
        │      ├── discussion.update_post_count()      → นับจำนวน comment
        │      ├── discussion.update_participants_count()
        │      └── discussion.track_visit()            → mark ว่า owner อ่านแล้ว
        └── GPUnreadRecord.create_unread_records_for_comment()
               → สร้าง unread record ให้คนอื่นๆ ใน project

    └→ GPComment.on_update()
        ├── notify_mentions()           → แจ้งเตือน @mention (ผ่าน HasMentions mixin)
        └── notify_reactions()          → แจ้งเตือน reaction (ผ่าน HasReactions mixin)
```

---

## 7. Flow: Notifications (การแจ้งเตือน)

### ประเภททั้งหมดของ GP Notification

| type | เกิดจาก |
|---|---|
| `Mention` | ถูก @mention ใน discussion/comment/task |
| `Rich Quote` | มีคน quote content ของเรา |
| `Reaction` | มีคน react emoji กับ post ของเรา |
| `Assignment` | ถูก assign task |
| `Reassignment` | task ถูก reassign มาหาเรา |
| `Due Soon` | task ใกล้ถึง due date (engine รายวัน) |
| `Overdue` | task เลย due date แล้ว (engine รายวัน) |
| `Blocked` | task ถูก mark เป็น Blocked |
| `SLA Breach` | discussion/task เกิน SLA (engine รายชั่วโมง) |
| `Role Changed` | GP Role ของเราถูกเปลี่ยน |
| `Project Added` | ถูกเพิ่มเข้า Space |
| `Task Status Changed` | status ของ task ที่เรา own/assigned ถูกเปลี่ยน |

### เมื่อมี **@mention**

```
GPComment.on_update()
    └→ HasMentions.notify_mentions()
        ├── extract_mentions(self.content)   → parse HTML หา @username
        ├── ถ้า mention == "@everyone"
        │      └→ _notify_everyone_mention() → แจ้งเตือนทุกคนใน Gameplan
        └── ต่อ user ทุกคนที่ถูก mention
               └→ _notify_user(email, type="Mention")
                      ├── สร้าง GP Notification document
                      │      (from_user, to_user, discussion/task/comment)
                      └→ GPNotification.after_insert()
                             └── gameplan.refetch_resource("Unread Notifications Count")
                                    → ยิง Socket.IO event ให้ browser reload counter
```

### เมื่อมี **Rich Quote** (อ้างอิงข้อความคนอื่น)

```
HasMentions.notify_mentions()
    └→ _notify_rich_quote_authors()
        └── extract_rich_quote_authors(content) → หาคนที่ถูก quote
            └→ _notify_user(author, type="Rich Quote")
```

### เมื่อมี **Reaction (Emoji)**

```
HasReactions.notify_reactions()
    └── เปรียบเทียบ reactions ก่อน/หลัง save
        └→ _notify_user(reactor, type="Reaction")
               → สร้าง GP Notification
```

---

## 8. Flow: Unread Records (ติดตามการอ่าน)

Gameplan ใช้ `GP Unread Record` แทนระบบ read/unread แบบ flag ทั่วไป

```
Discussion สร้างใหม่
    └→ GPUnreadRecord.create_unread_records_for_discussion()
        └── ดึงสมาชิกทุกคนใน project
            → bulk insert GP Unread Record ให้ทุกคน (ยกเว้น owner)
               { user, discussion, project, is_unread: 1 }

Comment สร้างใหม่
    └→ GPUnreadRecord.create_unread_records_for_comment()
        └── ดึงสมาชิกทุกคนใน project
            → bulk insert GP Unread Record ให้ทุกคน (ยกเว้น commenter)
               { user, discussion, project, comment, is_unread: 1 }

User เปิดอ่าน Discussion
    → track_visit() → อัปเดต GP Discussion Visit.last_visit
    → frontend mark unread records เป็น is_unread: 0

Discussion/Comment ถูกลบ
    └→ GPUnreadRecord.delete_unread_records_for_discussion/comment()
        → DELETE ทุก unread record ที่เกี่ยวข้อง
```

---

## 9. Flow: Task (การจัดการงาน)

### เมื่อ User **สร้าง Task**

```
POST /api/resource/GP Task
    └→ GPTask.before_insert()
        └── ถ้าไม่มี status → set เป็น "Backlog"

    └→ GPTask.after_insert()
        ├── update_tasks_count()     → บวก counter ใน GP Project
        └── ถ้ามี assigned_to → notify_assignment() → สร้าง Notification

    └→ GPTask.on_update()
        ├── notify_mentions()        → แจ้ง @mention ใน description
        ├── log_value_updates()      → บันทึก activity log ทุกครั้งที่ field เปลี่ยน
        └── run_engines()
```

### `run_engines()` — ตัดสินใจเรียก Engine ตาม context

```
GPTask.run_engines()
    ├── ถ้า status เพิ่งเปลี่ยนเป็น "Done"
    │      └→ enqueue DependencyEngine.check_unblocked_tasks()
    │             → ปลดล็อค Task อื่นที่ถูกตัวนี้ block อยู่
    │
    └── ถ้าไม่มี assigned_to และ status ไม่ใช่ Done/Canceled และมี project
           └→ enqueue AssignmentEngine.auto_assign()
                  → หาคนที่ว่างที่สุดใน team มา assign อัตโนมัติ
```

### Status Workflow ของ Task

```
validate_status_workflow()
    ├── ถ้า status == "Done"     → ตั้ง is_completed=1, completed_at, completed_by
    └── ถ้า status != "Done"     → clear is_completed, completed_at, completed_by

validate_dependencies()
    └── ถ้าพยายาม Done แต่ยังมี blocker ที่ยัง active → throw error
```

---

## 10. Engines (Background Logic)

### AssignmentEngine (`engines/assignment.py`)

```
recommend_assignee(project, required_points)
    ├── ดึง team members ทั้งหมดใน project
    ├── ต่อ user แต่ละคน:
    │      ├── ดึง max_points_per_week จาก GP Capacity Profile
    │      ├── Sum points ของ active tasks ที่ถืออยู่
    │      └── available_capacity = max_points - current_points
    └── เรียงตาม available_capacity มากสุด → คืนค่า user ที่ว่างที่สุด

auto_assign(task_name)
    └── recommend_assignee() → ถ้าได้ user → db_set assigned_to + add comment
```

### DependencyEngine (`engines/dependency.py`)

```
check_unblocked_tasks(completed_task_name)
    ├── หา GP Task Dependency ที่มี task = completed_task_name
    └── ต่อ task ที่ถูกบล็อคโดยตัวนี้:
           ├── เช็คว่า blocker ทุกตัวสถานะ Done/Canceled ครบหรือยัง
           └── ถ้าครบ → db_set status = "Todo" + add comment อัตโนมัติ
```

### WorkloadEngine (`engines/workload.py`)

```
capture_team_snapshots()  (รัน daily)
    └── ต่อ user ทุกคน:
        ├── Sum points ของ active tasks
        ├── นับงานที่ overdue
        └── insert GP Workload Snapshot { user, date, total_points, overdue_tasks }
```

### SLA Engine (`engines/sla.py`)

```
check_sla_breaches()  (รัน hourly)
    └── ดึง active tasks ที่มี sla_rule ตั้งไว้
        └── ต่อ task แต่ละอัน:
            ├── ดึง rule: resolve_within_hours
            ├── คำนวณ elapsed_hours ตั้งแต่ task ถูกสร้าง
            └── ถ้า elapsed > resolve_within_hours → ดึง GP Escalation Rule
                   → create_sla_notification() ยิงแจ้งเตือนไปหา escalate_to_user
```

---

## 11. DocType ที่สำคัญ

| DocType | ชื่อใน UI | หน้าที่ |
|---|---|---|
| `GP Team` | Project | Category หลัก รวม Space หลายๆ อันไว้ด้วยกัน |
| `GP Project` | Space | พื้นที่ที่ Discussion / Task / Page อยู่ในนั้น |
| `GP Discussion` | Discussion | กระทู้หลัก พร้อม content แบบ rich text |
| `GP Comment` | Comment | ความคิดเห็นใต้ Discussion หรือ Task |
| `GP Task` | Task | งานที่ต้องทำ มี status, priority, assignee, due_date |
| `GP Page` | Page | Collaborative document คล้าย Notion |
| `GP Notification` | — | record แจ้งเตือน (mention, reaction, assignment) |
| `GP Unread Record` | — | ติดตาม discussion/comment ที่ยังไม่ได้อ่าน |
| `GP User Profile` | — | ข้อมูล profile เพิ่มเติมของ user |
| `GP Member` | — | Child doctype สำหรับเก็บ members ใน Team/Project |
| `GP Guest Access` | — | อนุญาต guest user เข้า project เฉพาะ |
| `GP SLA Rule` | — | กำหนดระยะเวลาตอบสนองของ task |
| `GP Escalation Rule` | — | กำหนดว่าใครต้องถูก escalate เมื่อ SLA หลุด |
| `GP Capacity Profile` | — | กำหนด max_points_per_week ของ user แต่ละคน |
| `GP Workload Snapshot` | — | บันทึก workload รายวันสำหรับ analytics |
| `GP Sprint` | Sprint | Sprint planning สำหรับจัด task ลงใน sprint |
| `GP Poll` | Poll | การโหวต embed ใน Discussion |
| `GP Draft` | Draft | Discussion ที่ยังไม่ publish |
| `GP Invitation` | — | Invitation link สำหรับเชิญ user เข้าระบบ พร้อม gp_role |
| `GP Role` | Role | กำหนดชื่อ role + Frappe role mapping |

---

## 12. Mixins (Reusable Python Logic)

### `HasMentions` (`mixins/mentions.py`)
- ใช้กับ: `GP Discussion`, `GP Comment`, `GP Task`
- call `notify_mentions()` ใน `on_update` hook
- parse `@username` จาก rich text content → สร้าง `GP Notification`

### `HasReactions` (`mixins/reactions.py`)
- ใช้กับ: `GP Discussion`, `GP Comment`
- call `notify_reactions()` ใน `on_update` hook
- เปรียบเทียบ emoji reactions ก่อน/หลัง save → แจ้งเตือน user ที่เพิ่ม reaction

### `HasActivity` (`mixins/activity.py`)
- ใช้กับ: `GP Discussion`, `GP Task`
- call `log_activity()` เมื่อ field สำคัญเปลี่ยนแปลง
- บันทึกลงใน `GP Activity` สำหรับแสดง activity timeline

### `HasTags` (`mixins/tags.py`)
- ใช้กับ: `GP Discussion`, `GP Comment`, `GP Task`
- parse `#tag` จาก content → บันทึกลง `GP Tag` + `GP Tag Link`

### `Archivable` (`mixins/archivable.py`)
- ใช้กับ: `GP Team`, `GP Project`
- จัดการ archive/unarchive: set `is_archived` flag

### `ManageMembersMixin` (`mixins/manage_members.py`)
- ใช้กับ: `GP Project`
- จัดการ invite, remove member จาก project

---

## 13. Roles & Permissions

### GP Role vs Frappe Role

Gameplan มีสองชั้นของ role:

| ชั้น | DocType | หน้าที่ |
|---|---|---|
| **GP Role** | `GP Role` | ชื่อ role ที่แสดงใน UI เช่น "Developer", "Designer" |
| **Frappe Role** | field `frappe_role` ใน GP Role | role จริงที่ตัดสินสิทธิ์ใน Frappe |

เมื่อ Admin เปลี่ยน `gp_role` ของ user ใน `GP User Profile`:

```
GPUserProfile.on_update()
    └── has_value_changed("gp_role")
        ├── _sync_frappe_role_from_gp_role()
        │      ├── ดึง frappe_role จาก GP Role
        │      ├── ลบ Gameplan role เก่าทั้งหมดออกจาก User
        │      └── append_roles(frappe_role) → save user
        └── _notify_role_changed()
               → สร้าง GP Notification ประเภท "Role Changed" ส่งให้ user
```

### Frappe Permission Roles

| Role | สิทธิ์ |
|---|---|
| `Gameplan Admin` | สร้าง/แก้ไข/ลบได้ทุกอย่าง |
| `Gameplan Member` | สร้าง discussion/task/page ใน public space ได้ |
| `Gameplan Guest` | เข้าถึงได้เฉพาะ project ที่ถูก grant ผ่าน `GP Guest Access` |

Logic หลักอยู่ใน:
- `get_permission_query_conditions()` — SQL filter ระดับ list (ก่อน query)
- `has_permission()` — เช็ครายละเอียดระดับ document (ก่อน open)
- `GPProject.get_list_query()` — filter private project ให้แสดงเฉพาะ member

---

## 14. Flow: Invitation (การเชิญ user)

### เมื่อ Admin **เชิญ user ใหม่**

```
API: invite_by_email(emails, gp_role)
    ├── ดึง frappe_role จาก GP Role
    ├── กรอง email ที่มี user หรือ invitation อยู่แล้ว
    └── ต่อ email ที่เหลือ:
           └→ frappe.get_doc(doctype="GP Invitation", ...).insert()

GPInvitation.before_insert()
    ├── validate email format
    ├── ถ้า role == Guest และไม่มี project → throw error
    ├── generate key (12-char hash)
    ├── invited_by = session.user
    └── status = "Pending"

GPInvitation.after_insert()
    └── invite_via_email()
           → sendmail ส่ง link: /api/method/gameplan.api.accept_invitation?key=<hash>
```

### เมื่อ user **คลิก Accept**

```
GET /api/method/gameplan.api.accept_invitation?key=<hash>
    └→ GPInvitation.accept()
        ├── เช็ค status ≠ Expired
        ├── create_user_if_not_exists()    → สร้าง Frappe User ถ้ายังไม่มี
        ├── user.append_roles(role)        → ให้ Frappe Role
        ├── create_guest_access(user)      → ถ้าเป็น Guest: สร้าง GP Guest Access ต่อ project
        ├── ถ้ามี gp_role → db_set gp_role ใน GP User Profile
        ├── status = "Accepted"
        └── redirect ไปหน้า /g/
```

---

## 15. Flow: Sprint

Sprint คือช่วงเวลาสำหรับจัด task ลงไปทำ เชื่อมกับ GP Project (Space)

```
GP Sprint fields:
    name, title, project, status (Open/Closed), starts_on, ends_on

Task ใน Sprint:
    GP Task.sprint → Link → GP Sprint

API: carry_forward_sprint_tasks(source_sprint, target_sprint)
    ├── ตรวจว่าทั้งสอง sprint อยู่ใน project เดียวกัน
    └── bulk db_set sprint = target_sprint สำหรับ task ที่ยังไม่ Done/Canceled
```

---

## 16. Full-text Search (`search_sqlite.py`)

```
GameplanSearch (extends SQLiteSearch)
    ├── INDEX_NAME: "gameplan_search.db"  (SQLite FTS5)
    └── INDEXABLE_DOCTYPES:
           ├── GP Discussion  → index: title, content
           ├── GP Task        → index: title, description
           ├── GP Page        → index: title, content
           └── GP Comment     → index: content (with project/team metadata)

User พิมพ์ใน Search bar
    └→ API call → GameplanSearch.search(query)
        ├── ตรวจ permission → filter result ตาม project ที่ user เข้าถึงได้
        └── คืน results พร้อม highlight snippet
```

---

## 17. Frontend Architecture (Vue 3 SPA)

### Entry Flow

```
Browser เปิด /g/
    → www/g.py serve HTML + boot data (JSON)
    → main.js:
          ├── createApp(App)
          ├── setConfig('resourceFetcher', frappeRequest)  ← ใช้ Frappe CSRF
          ├── setConfig('defaultListUrl', 'gameplan.extends.client.get_list')
          ├── app.use(router)  ← Vue Router
          ├── app.use(resourcesPlugin)  ← frappe-ui data fetching
          └── initSocket()  ← เชื่อมต่อ Socket.IO
```

### Data Fetching Pattern

```ts
// ดึง list ของ documents
const discussions = useList<GPDiscussion>({
  doctype: 'GP Discussion',
  filters: () => ({ project: currentProject.value }),
  fields: ['name', 'title', 'last_post_at'],
})

// ดึง single document
const discussion = useDoc<GPDiscussion>({
  doctype: 'GP Discussion',
  name: props.discussionId,
})
discussion.setValue.submit({ title: 'New Title' })  // update
```

### Real-time Updates (Socket.IO)

```
socket.js:
    socket.on('refetch_resource', (data) => {
        ├── data.cache_key → หา resource ใน frappe-ui cache
        └── resource.reload()  ← re-fetch จาก API อัตโนมัติ
    })

Backend trigger (gameplan/__init__.py):
    gameplan.refetch_resource("Unread Notifications Count", user=user)
        └→ frappe.publish_realtime('refetch_resource', { cache_key }, user=user)
               → ส่ง Socket.IO event ไปหา browser ของ user คนนั้น
```

### Route Structure

```
/g/
├── /dashboard                  ← Dashboard
├── /dashboard/personal         ← Personal Dashboard
├── /discussions/:feedType      ← Discussions (recent/my/all-teams)
├── /drafts                     ← Drafts
├── /inbox                      ← Inbox (notifications + unread)
├── /projects                   ← Teams/Projects list
├── /projects/:teamId           ← Team Overview (list of spaces)
├── /spaces                     ← All Spaces
├── /:teamId/:projectId/        ← Space Overview
├── /:teamId/:projectId/discussions/:discussionId  ← Discussion thread
├── /:teamId/:projectId/tasks   ← Task board
├── /:teamId/:projectId/pages   ← Pages list
├── /tasks                      ← All Tasks
├── /people                     ← People directory
├── /roles                      ← Role management (admin)
└── /search                     ← Search
```

---

## 18. ถ้าอยากแก้อะไร ไปที่ไหน

| ต้องการ | ไปแก้ที่ |
|---|---|
| แก้ logic เมื่อสร้าง/แก้ Discussion | `gameplan/doctype/gp_discussion/gp_discussion.py` |
| แก้ logic เมื่อ comment | `gameplan/doctype/gp_comment/gp_comment.py` |
| แก้ logic เมื่อสร้าง/อัปเดต Task | `gameplan/doctype/gp_task/gp_task.py` |
| แก้วิธี auto-assign task | `gameplan/engines/assignment.py` |
| แก้วิธีปลดล็อค task dependency | `gameplan/engines/dependency.py` |
| แก้กฎ SLA / escalation | `gameplan/engines/sla.py` |
| แก้วิธีแจ้งเตือน mention | `gameplan/mixins/mentions.py` |
| แก้วิธีแจ้งเตือน reaction | `gameplan/mixins/reactions.py` |
| แก้ search indexing | `gameplan/search_sqlite.py` |
| แก้ boot data ที่ส่งให้ frontend | `gameplan/www/g.py` |
| แก้สิทธิ์การเข้าถึง | `gp_<doctype>.py` → `has_permission()` / `get_permission_query_conditions()` |
| แก้ field บน DocType | `doctype/<ชื่อ>/<ชื่อ>.json` แล้ว `bench migrate` |
| แก้ scheduled task | `hooks.py` → `scheduler_events` + function ใน `engines/` |
| แก้ API endpoint | `gameplan/api.py` (@frappe.whitelist) |
| แก้ UI page | `frontend/src/pages/<PageName>.vue` |
| แก้ shared component | `frontend/src/components/<ComponentName>.vue` |
| แก้ data fetching composable | `frontend/src/data/<name>.ts` |
| แก้ routing | `frontend/src/router.js` |
| แก้ real-time event | `frontend/src/socket.js` + backend `gameplan.refetch_resource()` |
| แก้ GP Role / permission mapping | `gameplan/doctype/gp_role/gp_role.json` + `gp_user_profile.py` |
| แก้ invitation flow | `gameplan/doctype/gp_invitation/gp_invitation.py` + `api.py invite_by_email()` |
| แก้ Sprint carry-forward logic | `gameplan/api.py carry_forward_sprint_tasks()` |
| แก้ workload calculation | `gameplan/engines/workload.py` |

---

## 19. การไหลของข้อมูล (Data Flow Summary)

```
User สร้าง Discussion ใหม่
    ↓ before_insert  → ตรวจ project ไม่ archived, set last_post_at
    ↓ [save to DB]
    ↓ after_insert   → update discussions_count ใน GP Project
                        สร้าง GP Unread Record ให้ทุกคนใน space
    ↓ Socket.IO      → browser ของ user อื่นโหลด discussion list ใหม่

User comment ใน Discussion
    ↓ before_insert  → เช็ค discussion ไม่ได้ closed
    ↓ [save to DB]
    ↓ after_insert   → update last_post_at, post_count, participants_count
                        สร้าง GP Unread Record ให้คนอื่น
    ↓ on_update      → notify @mentions → สร้าง GP Notification → Socket.IO

User สร้าง Task
    ↓ before_insert  → set status = "Backlog"
    ↓ [save to DB]
    ↓ after_insert   → update tasks_count, notify assignee
    ↓ on_update      → log_value_updates (activity log)
                        run_engines:
                          ถ้า Done → DependencyEngine (ปลดล็อค blocked tasks)
                          ถ้าไม่มี assignee → AssignmentEngine (auto-assign)

Hourly (background)
    → SLA Engine     → ตรวจงานที่หลุด SLA → สร้าง GP Notification (SLA Breach)
                       → ตรวจ GP Invitation ที่หมดอายุ → ลบออก

Daily (background)
    → WorkloadEngine  → บันทึก GP Workload Snapshot รายวัน
    → DueDateNotifier → แจ้งเตือน task ที่ใกล้ครบกำหนด (Due Soon) หรือเกินแล้ว (Overdue)

Admin เปลี่ยน GP Role ของ user
    ↓ GPUserProfile.on_update()
    ↓ _sync_frappe_role_from_gp_role() → อัปเดต Frappe User role
    ↓ _notify_role_changed() → สร้าง GP Notification (Role Changed)

Admin เพิ่ม user เข้า Space
    ↓ GPProject.add_member(user)
    ↓ append + save
    ↓ _notify_member_added() → สร้าง GP Notification (Project Added)

Task status เปลี่ยน (non-Blocked)
    ↓ log_value_updates() ตรวจ field "status"
    ↓ notify_status_changed() → สร้าง GP Notification (Task Status Changed)
           ส่งให้ assigned_to หรือ owner (ถ้าไม่ใช่คนที่เปลี่ยนเอง)
```

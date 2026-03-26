# Gameplan

Async-first discussions and project management tool for remote teams, built on Frappe Framework.

---

## Features

| Feature | รายละเอียด |
|---|---|
| **Spaces** | จัดกลุ่ม discussions, tasks และ pages ไว้ที่เดียว แบ่งตาม project หรือ team |
| **Discussions** | เขียน thread พร้อม rich text, รูปภาพ, reactions, mentions, polls, quotes |
| **Tasks** | จัดการงานพร้อม assignee, due date, sprint, parent task, checklist, dependencies |
| **Pages** | Collaborative documents สำหรับ docs ภายในทีม |
| **Notifications** | แจ้งเตือน assigned, mentioned, due soon, overdue, blocked, SLA breach, role changed, project added, task status changed |
| **Sprints** | วางแผนงานเป็น sprint ภายใน space |
| **Roles** | กำหนด GP Role (Admin / Member / Guest) ต่อ user พร้อม Frappe permission |
| **Workload** | ดู capacity และ workload snapshot ของแต่ละ user |
| **SLA** | กำหนด SLA rule ต่อ space และแจ้งเตือนเมื่อ breach |
| **Full-text Search** | ค้นหา discussions, tasks, pages ด้วย SQLite FTS5 |
| **Real-time** | Live updates ผ่าน Socket.IO |

---

## Requirements

- Docker + Docker Compose
- (สำหรับพัฒนา) Python 3.10+, Node 18+, Yarn

---

## Quick Start (Docker)

### 1. Clone

```bash
git clone https://github.com/your-org/gameplan.git
cd gameplan
```

### 2. Start services

```bash
cd docker
docker compose up -d
```

> **หมายเหตุ:** ครั้งแรกจะใช้เวลา ~5–10 นาที เพราะ `init.sh` จะ:
> - สร้าง Frappe bench ใหม่
> - ติดตั้ง Python/Node dependencies
> - สร้าง site `gameplan.localhost`
> - ติดตั้งและ migrate app
>
> ครั้งถัดไปจะ start ทันทีเพราะ bench ถูก init แล้ว

ตรวจสอบว่า init เสร็จแล้วด้วย:

```bash
docker logs -f gameplan-frappe-1
# รอจนเห็น "bench start" output
```

### 3. เพิ่ม hosts entry

**Windows** — เปิด `C:\Windows\System32\drivers\etc\hosts` แล้วเพิ่ม:
```
127.0.0.1 gameplan.localhost
```

**macOS / Linux:**
```bash
echo "127.0.0.1 gameplan.localhost" | sudo tee -a /etc/hosts
```

### 4. เปิดในเบราว์เซอร์

```
http://gameplan.localhost:8000
Username: Administrator
Password: admin
```

---

## Development

### Frontend (Vue 3 + Vite)

```bash
cd frontend
yarn install
yarn dev
# เข้าใช้งานที่ http://gameplan.frappe.test:8080/g
```

> Vite dev server proxy ไปที่ backend port 8000 อัตโนมัติ  
> ต้องเพิ่ม `127.0.0.1 gameplan.frappe.test` ใน hosts file ด้วย

### Deploy backend changes to Docker

```bash
# Copy ไฟล์ที่แก้ไปยัง container
docker cp "<local_file>" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/<relative_path>

# ตัวอย่าง: แก้ไข gp_task.py
docker cp "gameplan/gameplan/doctype/gp_task/gp_task.py" \
  gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/gameplan/gameplan/doctype/gp_task/gp_task.py
```

### Deploy frontend changes to Docker

```bash
# Build inside container (แนะนำ)
docker exec gameplan-frappe-1 bash -c "
  cd /home/frappe/frappe-bench/apps/gameplan/frontend && yarn build &&
  cd /home/frappe/frappe-bench && bench build --app gameplan
"
```

### Database migration

ทำทุกครั้งที่แก้ไข DocType JSON (เพิ่ม field, เพิ่ม option ฯลฯ):

```bash
docker exec gameplan-frappe-1 bash -c \
  "cd /home/frappe/frappe-bench && bench --site gameplan.localhost migrate"
```

### Debug backend

สร้างไฟล์ `gameplan/debug.py` พร้อม function `execute()`:

```python
def execute():
    import frappe
    print(frappe.db.get_all("GP Task", limit=5))
```

รันด้วย:

```bash
docker exec gameplan-frappe-1 bash -c \
  "cd /home/frappe/frappe-bench && bench --site gameplan.localhost execute gameplan.debug.execute"
```

### Restart workers / services

```bash
# Restart ทุก process (gunicorn, worker, scheduler)
docker restart gameplan-frappe-1

# ดู log แบบ real-time
docker logs -f gameplan-frappe-1
```

---

## Project Structure

```
gameplan/
├── docker/
│   ├── docker-compose.yml          ← Services: frappe, mariadb, redis
│   └── init.sh                     ← Init script (รันอัตโนมัติครั้งแรก)
├── frontend/
│   ├── src/
│   │   ├── pages/                  ← Page components
│   │   │   ├── Spaces/             ← Space listing & layout
│   │   │   ├── SpaceTasks.vue      ← Task list ภายใน space
│   │   │   ├── SpaceDiscussions.vue
│   │   │   ├── Notifications.vue   ← Inbox / notification feed
│   │   │   ├── People.vue          ← Member directory
│   │   │   ├── RolesPage.vue       ← GP Role management
│   │   │   ├── WorkloadView.vue    ← Team workload dashboard
│   │   │   └── ...
│   │   ├── components/             ← Shared UI components
│   │   │   ├── NewTaskDialog/      ← Create task with role-based assignment
│   │   │   ├── AddMemberDialog.vue ← Add member to space
│   │   │   └── Settings/
│   │   │       └── InvitePeople.vue ← Invite user พร้อมกำหนด GP Role
│   │   ├── data/                   ← Data composables (useList / useDoc wrappers)
│   │   │   └── roles.ts            ← GP Role + user profile composables
│   │   ├── composables/            ← Shared Vue composables
│   │   ├── utils/                  ← Utility helpers
│   │   └── router.js               ← Vue Router config
│   └── vite.config.ts
├── gameplan/
│   ├── api.py                      ← Whitelisted API endpoints
│   ├── hooks.py                    ← Frappe hooks & scheduled jobs
│   ├── gameplan/
│   │   ├── doctype/
│   │   │   ├── gp_project/         ← Space
│   │   │   ├── gp_team/            ← Category / Project group
│   │   │   ├── gp_discussion/      ← Discussion threads
│   │   │   ├── gp_comment/         ← Comments + reactions
│   │   │   ├── gp_task/            ← Tasks
│   │   │   ├── gp_task_checklist/  ← Checklist items
│   │   │   ├── gp_task_dependency/ ← Task dependencies
│   │   │   ├── gp_task_template/   ← Reusable task templates
│   │   │   ├── gp_page/            ← Collaborative pages
│   │   │   ├── gp_sprint/          ← Sprints
│   │   │   ├── gp_role/            ← GP Role definitions
│   │   │   ├── gp_user_profile/    ← Extended user info + gp_role
│   │   │   ├── gp_invitation/      ← User invitations
│   │   │   ├── gp_notification/    ← Notification records
│   │   │   ├── gp_poll/            ← Polls inside discussions
│   │   │   ├── gp_sla_rule/        ← SLA rules per space
│   │   │   ├── gp_escalation_rule/ ← SLA escalation rules
│   │   │   └── gp_workload_snapshot/ ← Daily workload snapshots
│   │   └── engines/
│   │       ├── sla.py              ← SLA breach checker (scheduled)
│   │       ├── due_date_notifier.py ← Due date notifications (scheduled)
│   │       ├── assignment.py       ← Assignment engine
│   │       ├── dependency.py       ← Task dependency resolver
│   │       └── workload.py         ← Workload calculation
│   └── mixins/
│       ├── activity.py             ← Activity log mixin
│       ├── archivable.py           ← Archive/unarchive mixin
│       ├── manage_members.py       ← Member management mixin
│       ├── mentions.py             ← @mention parsing mixin
│       ├── reactions.py            ← Emoji reactions mixin
│       └── tags.py                 ← Tagging mixin
└── frappe-ui/                      ← Local copy of frappe-ui component library
```

---

## Notification Types

| Type | เมื่อไหร่ |
|---|---|
| Mention | ถูก @mention ใน discussion หรือ comment |
| Reaction | มีคน react กับ post ของเรา |
| Rich Quote | มีคน quote content ของเรา |
| Assignment | ถูก assign task |
| Reassignment | task ถูก reassign มาให้ |
| Due Soon | task ใกล้ถึง due date |
| Overdue | task เลย due date แล้ว |
| Blocked | task ถูก mark เป็น Blocked |
| SLA Breach | discussion เกิน SLA ที่กำหนด |
| Role Changed | GP Role ของเราถูกเปลี่ยน |
| Project Added | ถูกเพิ่มเข้า space |
| Task Status Changed | status ของ task ที่เรา own ถูกเปลี่ยน |

---

## Naming Conventions (UI vs Backend)

| UI แสดงผล | DocType จริงใน backend |
|---|---|
| Space | GP Project |
| Project / Category | GP Team |
| Inbox | GP Notification |
| Role | GP Role |
| Person | GP User Profile |

---

## Scheduled Jobs

กำหนดใน `hooks.py` → `scheduler_events`:

| Job | ความถี่ | ทำอะไร |
|---|---|---|
| `due_date_notifier` | ทุกวัน | ส่ง notification Due Soon / Overdue |
| `sla` | ทุกชั่วโมง | ตรวจสอบ SLA breach |
| `workload` | ทุกวัน | บันทึก workload snapshot |

---

## License

AGPLv3

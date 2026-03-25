# Gameplan

Async-first discussions and project management tool for remote teams, built on Frappe Framework.

- **Spaces** — จัดกลุ่ม discussions, tasks และ pages ไว้ที่เดียว แบ่งตาม project หรือ team
- **Discussions** — เขียน thread พร้อม rich text, รูปภาพ, reactions, แท็กคน
- **Tasks** — จัดการงานพร้อม assignee, due date, sprint, parent task, checklist
- **Pages** — collaborative documents คล้าย Notion สำหรับ docs ภายในทีม
- **Notifications** — แจ้งเตือน assigned, mentioned, due soon, overdue, blocked, SLA breach
- **Sprints** — วางแผนงานเป็น sprint ภายใน space
- **Roles** — กำหนด role (Gameplan Admin / Member / Guest) ต่อ user

---

## Requirements

- Docker + Docker Compose
- (สำหรับ dev) Python 3.10+, Node 18+, Yarn

---

## Quick Start (Docker)

### 1. Clone

```bash
git clone https://github.com/your-org/gameplan.git
cd gameplan
```

---

### 2. Start services

```bash
cd docker
docker compose up -d
```

> **หมายเหตุ:** ครั้งแรกจะใช้เวลานาน (~5–10 นาที) เพราะ `init.sh` จะ:
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

---

### 3. Open in browser

```
http://gameplan.localhost:8000
Username: Administrator
Password: admin
```

> ถ้าหน้าไม่โหลด ให้เพิ่ม `127.0.0.1 gameplan.localhost` ใน hosts file

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

### Deploy changes to Docker

ทุกครั้งที่แก้ไขไฟล์ local ต้อง copy ขึ้น Docker ก่อน build:

```bash
# 1. Copy ไฟล์ที่แก้ไปยัง container
docker cp "<local_file>" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/<path>

# 2. Build frontend
docker exec gameplan-frappe-1 bash -c "cd /home/frappe/frappe-bench/apps/gameplan/frontend && yarn build && cd /home/frappe/frappe-bench && bench build --app gameplan"
```

### Database migration (เมื่อแก้ DocType JSON)

```bash
docker exec gameplan-frappe-1 bash -c "cd /home/frappe/frappe-bench && bench --site gameplan.localhost migrate"
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
docker exec gameplan-frappe-1 bash -c "cd /home/frappe/frappe-bench && bench --site gameplan.localhost execute gameplan.debug.execute"
```

---

## Project Structure

```
gameplan/
├── docker/
│   ├── docker-compose.yml     ← Services: frappe, mariadb, redis
│   └── init.sh                ← Init script (รันอัตโนมัติครั้งแรก)
├── frontend/
│   ├── src/
│   │   ├── pages/             ← Page components (Space, Tasks, People ฯลฯ)
│   │   ├── components/        ← Shared UI components
│   │   ├── data/              ← Data fetching composables (useList, useDoc)
│   │   └── router.js          ← Vue Router config
│   └── vite.config.ts
├── gameplan/
│   ├── api.py                 ← Whitelisted API endpoints
│   ├── hooks.py               ← Frappe app hooks & schedulers
│   ├── gameplan/doctype/      ← DocType definitions
│   │   ├── gp_project/        ← Space (GP Project)
│   │   ├── gp_team/           ← Project/Category (GP Team)
│   │   ├── gp_discussion/     ← Discussion threads
│   │   ├── gp_task/           ← Tasks
│   │   ├── gp_page/           ← Collaborative pages
│   │   ├── gp_sprint/         ← Sprints
│   │   └── gp_notification/   ← Notifications
│   └── engines/
│       ├── sla.py             ← SLA breach checker
│       └── due_date_notifier.py ← Daily due date notifications
└── frappe-ui/                 ← Local copy of frappe-ui component library
```

---

## Naming Conventions (UI vs Backend)

| UI แสดงผล | DocType จริงใน backend |
|---|---|
| Space | GP Project |
| Project (หมวดหมู่) | GP Team |
| Inbox | GP Notification |

---

## License

AGPLv3

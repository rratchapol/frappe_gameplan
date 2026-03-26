แก้ไฟล์ Frontend (.vue, .ts, .js)

# 1. Copy ไฟล์ขึ้น Docker
docker cp "C:\Users\user\Desktop\TEST\gameplan\frontend\src\...\File.vue" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/frontend/src/.../File.vue

# 1.5 ทางเลือกกรณีเเก้เยอะ copy ทั้ง folder src ครั้งเดียวแทนการ copy ทีละไฟล์
docker cp "C:\Users\user\Desktop\TEST\gameplan\frontend\src" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/frontend/
---
docker cp "C:\Users\taora\Desktop\Witsawa\Red Queen\frappe_gameplan\frontend\src" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/frontend/

# 2. Build
docker exec gameplan-frappe-1 bash -c "cd /home/frappe/frappe-bench/apps/gameplan/frontend && yarn build 2>&1 | tail -4 && cd /home/frappe/frappe-bench && bench build --app gameplan 2>&1 | tail -2"


------------------------------------------------------------------------------------------------------------------

แก้ไฟล์ Backend Python (.py)

# Copy ไฟล์ขึ้น Docker เท่านั้น (ไม่ต้อง build)
docker cp "C:\Users\user\Desktop\TEST\gameplan\gameplan\...\file.py" gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/gameplan/.../file.py


------------------------------------------------------------------------------------------------------------------

แก้ DocType JSON (.json ใน doctype/)

# 1. Copy ไฟล์
docker cp "..." gameplan-frappe-1:/home/frappe/frappe-bench/apps/gameplan/...

# 2. Migrate
docker exec gameplan-frappe-1 bash -c "cd /home/frappe/frappe-bench && bench --site gameplan.localhost migrate"
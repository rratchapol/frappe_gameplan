<template>
  <div class="flex h-full flex-col bg-surface-gray-2">
    <!-- Header -->
    <header class="sticky top-0 z-20 border-b bg-white/80 backdrop-blur-md px-6 py-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="rounded-lg bg-surface-gray-2 p-2">
            <LucideBarChart2 class="h-6 w-6 text-ink-gray-7" />
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-ink-gray-9">Workload View</h1>
            <p class="text-xs text-ink-gray-5">{{ weekLabel }} · tasks due this week</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <Badge variant="outline" class="text-xs">
            {{ activeMembers.length }} members
          </Badge>
          <Badge variant="outline" class="text-xs text-red-600 border-red-200">
            {{ overloadedCount }} overloaded
          </Badge>
        </div>
      </div>
    </header>

    <div class="flex-1 overflow-auto p-6">
      <!-- Loading state -->
      <div v-if="!weekTasks.isFinished || !noDueTasks.isFinished || !capacityProfiles.isFinished" class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div v-for="i in 6" :key="i" class="h-48 animate-pulse rounded-2xl bg-surface-gray-3" />
      </div>

      <div v-else-if="activeMembers.length === 0" class="py-20 text-center text-ink-gray-5">
        <LucideUsers class="mx-auto mb-3 h-10 w-10 text-ink-gray-3" />
        <p>No active team members found.</p>
      </div>

      <!-- Member cards -->
      <div v-else class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div
          v-for="member in workloadData"
          :key="member.user"
          class="flex flex-col rounded-2xl border bg-surface-white shadow-sm transition-all hover:shadow-md"
          :class="member.isOverloaded ? 'border-red-200' : 'border-outline-gray-2'"
        >
          <!-- Card header -->
          <div class="flex items-center gap-3 border-b border-outline-gray-1 px-5 py-4">
            <div class="relative">
              <img
                v-if="member.userImage"
                :src="member.userImage"
                class="h-10 w-10 rounded-full object-cover"
              />
              <div
                v-else
                class="flex h-10 w-10 items-center justify-center rounded-full bg-surface-gray-3 text-sm font-bold text-ink-gray-6"
              >
                {{ member.fullName?.charAt(0)?.toUpperCase() }}
              </div>
              <span
                v-if="member.isOverloaded"
                class="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500"
                title="Overloaded"
              >
                <LucideAlertTriangle class="h-2.5 w-2.5 text-white" />
              </span>
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate font-semibold text-ink-gray-9">{{ member.fullName }}</p>
              <p class="truncate text-xs text-ink-gray-5">{{ member.user }}</p>
            </div>
            <div class="text-right">
              <p class="text-lg font-extrabold" :class="member.isOverloaded ? 'text-red-600' : 'text-ink-gray-8'">
                {{ member.utilization }}%
              </p>
              <p class="text-xs text-ink-gray-5">of capacity</p>
            </div>
          </div>

          <!-- Capacity / Utilization bar -->
          <div class="px-5 pt-3 pb-2">
            <div class="mb-1.5 flex items-center justify-between text-xs text-ink-gray-5">
              <span>{{ member.assignedPoints }} pts assigned</span>
              <div class="flex items-center gap-1">
                <template v-if="editingUser === member.user">
                  <input
                    v-model.number="editingValue"
                    type="number"
                    min="1"
                    class="w-14 rounded border border-outline-gray-3 bg-surface-white px-1.5 py-0.5 text-xs text-ink-gray-8 focus:outline-none focus:ring-1 focus:ring-outline-gray-4"
                    @keyup.enter="saveCapacity(member.user, member.profileName)"
                    @keyup.escape="editingUser = null"
                  />
                  <span class="text-ink-gray-5">pts/week</span>
                  <button @click="saveCapacity(member.user, member.profileName)" class="text-ink-gray-6 hover:text-ink-gray-9">
                    <LucideCheck class="h-3 w-3" />
                  </button>
                  <button @click="editingUser = null" class="text-ink-gray-4 hover:text-ink-gray-7">
                    <LucideX class="h-3 w-3" />
                  </button>
                </template>
                <template v-else>
                  <span>Max: {{ member.maxPoints }} pts/week</span>
                  <button @click="startEdit(member.user, member.maxPoints)" class="text-ink-gray-3 hover:text-ink-gray-6">
                    <LucidePencil class="h-3 w-3" />
                  </button>
                </template>
              </div>
            </div>
            <!-- Utilization bar -->
            <div class="h-2 w-full overflow-hidden rounded-full bg-surface-gray-3">
              <div
                class="h-full rounded-full transition-all duration-500"
                :class="[
                  member.utilization >= 100 ? 'bg-red-500' :
                  member.utilization >= 75 ? 'bg-orange-400' :
                  member.utilization >= 50 ? 'bg-blue-400' : 'bg-green-400'
                ]"
                :style="{ width: Math.min(member.utilization, 100) + '%' }"
              />
            </div>
          </div>

          <!-- Completion bar -->
          <div class="px-5 pb-3">
            <div class="mb-1.5 flex items-center justify-between text-xs text-ink-gray-5">
              <span>{{ member.completedPoints }} / {{ member.assignedPoints }} pts done</span>
              <div class="flex items-center gap-1.5">
                <span
                  class="rounded px-1.5 py-0.5 text-xs font-semibold"
                  :class="member.assignedPoints === 0 ? 'text-ink-gray-4' : member.isOnTrack ? 'text-green-600 bg-green-50' : 'text-orange-600 bg-orange-50'"
                >
                  {{ member.completionRate }}% done
                </span>
                <LucideTrendingUp v-if="member.isOnTrack && member.assignedPoints > 0" class="h-3 w-3 text-green-500" />
                <LucideTrendingDown v-else-if="member.assignedPoints > 0" class="h-3 w-3 text-orange-400" />
              </div>
            </div>
            <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-3">
              <div
                class="h-full rounded-full bg-green-400 transition-all duration-500"
                :style="{ width: member.completionRate + '%' }"
              />
            </div>
          </div>

          <!-- Tasks list -->
          <div class="flex-1 px-5 pb-4">
            <div class="mb-2 flex items-center gap-2">
              <p class="text-xs font-semibold text-ink-gray-5">
                REMAINING ({{ member.remainingTasks.length }})
              </p>
              <span v-if="member.doneTasks.length > 0" class="text-xs text-green-600 font-medium">
                · {{ member.doneTasks.length }} done ✓
              </span>
            </div>
            <div v-if="member.remainingTasks.length === 0 && member.assignedPoints === 0" class="py-3 text-center text-xs text-ink-gray-4">
              No tasks this week
            </div>
            <div v-else-if="member.remainingTasks.length === 0" class="py-3 text-center text-xs text-green-600 font-medium">
              All tasks done!
            </div>
            <ul v-else class="space-y-1.5 max-h-40 overflow-y-auto">
              <li
                v-for="task in member.remainingTasks.slice(0, 8)"
                :key="task.name"
                class="flex items-center justify-between rounded-lg bg-surface-gray-1 px-2.5 py-1.5 text-xs"
              >
                <div class="flex min-w-0 items-center gap-2">
                  <span
                    class="inline-block h-2 w-2 shrink-0 rounded-full"
                    :class="statusColor(task.status)"
                  />
                  <span class="truncate text-ink-gray-7">{{ task.title }}</span>
                </div>
                <div class="ml-2 flex shrink-0 items-center gap-1.5">
                  <span
                    v-if="task.due_date && isOverdue(task.due_date)"
                    class="rounded px-1 py-0.5 text-xs font-medium bg-red-50 text-red-600"
                  >overdue</span>
                  <span class="rounded bg-surface-gray-3 px-1.5 py-0.5 font-medium text-ink-gray-6">
                    {{ task.points || 0 }}pt
                  </span>
                </div>
              </li>
              <li v-if="member.remainingTasks.length > 8" class="text-center text-xs text-ink-gray-4 pt-1">
                +{{ member.remainingTasks.length - 8 }} more
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useList, Badge } from 'frappe-ui'
import { users } from '@/data/users'

// --- Current week boundaries (Monday–Sunday) ---
function getWeekBounds() {
  const d = new Date()
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  const diffToMonday = day === 0 ? -6 : 1 - day
  const monday = new Date(d)
  monday.setDate(d.getDate() + diffToMonday)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  sunday.setHours(23, 59, 59, 999)
  return { monday, sunday }
}

const { monday: weekStart, sunday: weekEnd } = getWeekBounds()
const weekStartStr = weekStart.toISOString().split('T')[0]
const weekEndStr = weekEnd.toISOString().split('T')[0]

const weekLabel = computed(() => {
  const fmt = (d: Date) => d.toLocaleDateString('th-TH', { day: 'numeric', month: 'short' })
  return `${fmt(weekStart)} – ${fmt(weekEnd)}`
})

// ความคืบหน้าที่ควรทำได้ตามวันในสัปดาห์ (จ=0%, อ=20%, พ=40%, พฤ=60%, ศ=80%, เสาร์/อา=100%)
function getExpectedProgress(): number {
  const day = new Date().getDay()
  if (day === 0 || day === 6) return 100
  return Math.round(((day - 1) / 5) * 100)
}
const expectedProgress = getExpectedProgress()

const capacityProfiles = useList({
  doctype: 'GP Capacity Profile',
  fields: ['name', 'user', 'max_points_per_week'],
  limit: 999,
  auto: true,
})

// Tasks ที่ due ใน week นี้ (รวม Done เพื่อวัด completion)
const weekTasks = useList({
  doctype: 'GP Task',
  fields: ['name', 'title', 'assigned_to', 'points', 'status', 'priority', 'due_date'],
  filters: {
    due_date: ['between', [weekStartStr, weekEndStr]],
    assigned_to: ['is', 'set'],
  },
  limit: 9999,
  auto: true,
})

// In Progress ที่ไม่มี due_date (กำลังทำอยู่จริง นับเข้า week นี้)
const noDueTasks = useList({
  doctype: 'GP Task',
  fields: ['name', 'title', 'assigned_to', 'points', 'status', 'priority', 'due_date'],
  filters: {
    status: 'In Progress',
    due_date: ['is', 'not set'],
    assigned_to: ['is', 'set'],
  },
  limit: 999,
  auto: true,
})

const activeMembers = computed(() => {
  return (users.data || []).filter((u: any) => u.enabled && !u.isGuest)
})

const workloadData = computed(() => {
  if (!weekTasks.isFinished || !noDueTasks.isFinished || !capacityProfiles.isFinished) return []

  const capacityMap: Record<string, { maxPoints: number; profileName: string | null }> = {}
  for (const cp of (capacityProfiles.data || []) as any[]) {
    capacityMap[cp.user] = { maxPoints: cp.max_points_per_week ?? 40, profileName: cp.name }
  }

  // รวม 2 list, dedup ด้วย name
  const allByUser: Record<string, any[]> = {}
  for (const task of [...(weekTasks.data || []), ...(noDueTasks.data || [])] as any[]) {
    if (!task.assigned_to) continue
    if (!allByUser[task.assigned_to]) allByUser[task.assigned_to] = []
    if (!allByUser[task.assigned_to].find((t: any) => t.name === task.name)) {
      allByUser[task.assigned_to].push(task)
    }
  }

  return activeMembers.value
    .map((user: any) => {
      const tasks = allByUser[user.name] || []
      const doneTasks = tasks.filter((t: any) => ['Done', 'Canceled'].includes(t.status))
      const remainingTasks = tasks.filter((t: any) => !['Done', 'Canceled'].includes(t.status))
      const assignedPoints = tasks.reduce((s: number, t: any) => s + (t.points || 0), 0)
      const completedPoints = doneTasks.reduce((s: number, t: any) => s + (t.points || 0), 0)
      const maxPoints = capacityMap[user.name]?.maxPoints ?? 40
      const profileName = capacityMap[user.name]?.profileName ?? null
      const utilization = maxPoints > 0 ? Math.round((assignedPoints / maxPoints) * 100) : 0
      const completionRate = assignedPoints > 0 ? Math.round((completedPoints / assignedPoints) * 100) : 0
      const isOnTrack = assignedPoints > 0 && completionRate >= expectedProgress
      return {
        user: user.name,
        fullName: user.full_name,
        userImage: user.user_image,
        assignedPoints,
        completedPoints,
        maxPoints,
        profileName,
        utilization,
        completionRate,
        isOnTrack,
        tasks,
        doneTasks,
        remainingTasks,
        isOverloaded: assignedPoints > maxPoints,
      }
    })
    .sort((a, b) => b.utilization - a.utilization)
})

const overloadedCount = computed(() => workloadData.value.filter(m => m.isOverloaded).length)

const editingUser = ref<string | null>(null)
const editingValue = ref(40)

function startEdit(user: string, currentMax: number) {
  editingUser.value = user
  editingValue.value = currentMax
}

async function saveCapacity(user: string, profileName: string | null) {
  if (!editingValue.value || editingValue.value < 1) return
  if (profileName) {
    await capacityProfiles.setValue.submit({ name: profileName, max_points_per_week: editingValue.value })
  } else {
    await capacityProfiles.insert.submit({ user, max_points_per_week: editingValue.value })
  }
  editingUser.value = null
  capacityProfiles.reload()
}

function isOverdue(dateStr: string) {
  return dateStr < new Date().toISOString().split('T')[0]
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    'Backlog': 'bg-ink-gray-4',
    'Todo': 'bg-blue-400',
    'In Progress': 'bg-orange-400',
    'Blocked': 'bg-red-500',
    'In Review': 'bg-purple-400',
    'Done': 'bg-green-400',
  }
  return map[status] || 'bg-ink-gray-3'
}
</script>

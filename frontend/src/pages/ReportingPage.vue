<template>
  <div class="flex h-full flex-col bg-surface-gray-2">
    <!-- Header -->
    <header class="sticky top-0 z-20 border-b bg-white/80 backdrop-blur-md px-6 py-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="rounded-lg bg-surface-gray-2 p-2">
            <LucideClipboardList class="h-6 w-6 text-ink-gray-7" />
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight text-ink-gray-9">Reports</h1>
            <p class="text-xs text-ink-gray-5">Task analytics and export for PM</p>
          </div>
        </div>
        <Button variant="solid" @click="exportCsv">
          <template #prefix><LucideDownload class="h-4 w-4" /></template>
          Export CSV
        </Button>
      </div>
    </header>

    <div class="flex-1 overflow-auto p-6 space-y-6">
      <!-- Filters -->
      <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
        <h2 class="mb-3 text-sm font-semibold text-ink-gray-7">Filters</h2>
        <div class="flex flex-wrap gap-3">
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Status</label>
            <select
              v-model="filters.status"
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:border-outline-gray-5"
            >
              <option value="">All</option>
              <option>Backlog</option>
              <option>Todo</option>
              <option>In Progress</option>
              <option>Blocked</option>
              <option>In Review</option>
              <option>Done</option>
              <option>Canceled</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Task Type</label>
            <select
              v-model="filters.task_type"
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:border-outline-gray-5"
            >
              <option value="">All</option>
              <option>Bug</option>
              <option>Story</option>
              <option>Implementation</option>
              <option>Issue</option>
              <option>Request</option>
              <option>Approval</option>
              <option>Operational</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Priority</label>
            <select
              v-model="filters.priority"
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:border-outline-gray-5"
            >
              <option value="">All</option>
              <option>Urgent</option>
              <option>High</option>
              <option>Medium</option>
              <option>Low</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Assigned To</label>
            <select
              v-model="filters.assigned_to"
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:border-outline-gray-5"
            >
              <option value="">All users</option>
              <option v-for="u in userOptions" :key="u.name" :value="u.name">{{ u.full_name }}</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Space (Project)</label>
            <select
              v-model="filters.project"
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-8 focus:outline-none focus:border-outline-gray-5"
            >
              <option value="">All spaces</option>
              <option v-for="s in spaces.data" :key="s.name" :value="s.name">{{ s.title }}</option>
            </select>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-xs text-ink-gray-5">Overdue only</label>
            <div class="flex items-center h-[34px]">
              <input type="checkbox" v-model="filters.overdueOnly" class="h-4 w-4 rounded border-outline-gray-3 text-ink-gray-8 focus:ring-0" />
            </div>
          </div>
          <div class="flex items-end">
            <button
              class="rounded-md border border-outline-gray-3 bg-surface-white px-3 py-1.5 text-sm text-ink-gray-6 hover:bg-surface-gray-1 transition-colors"
              @click="resetFilters"
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      <!-- Summary cards -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div class="rounded-xl border border-outline-gray-2 bg-surface-white px-5 py-4">
          <p class="text-xs text-ink-gray-5">Total Tasks</p>
          <p class="mt-1 text-2xl font-bold text-ink-gray-9">{{ filteredTasks.length }}</p>
        </div>
        <div class="rounded-xl border border-outline-gray-2 bg-surface-white px-5 py-4">
          <p class="text-xs text-ink-gray-5">Done</p>
          <p class="mt-1 text-2xl font-bold text-green-600">{{ countByStatus('Done') }}</p>
        </div>
        <div class="rounded-xl border border-red-200 bg-surface-white px-5 py-4">
          <p class="text-xs text-ink-gray-5">Blocked</p>
          <p class="mt-1 text-2xl font-bold text-red-600">{{ countByStatus('Blocked') }}</p>
        </div>
        <div class="rounded-xl border border-orange-200 bg-surface-white px-5 py-4">
          <p class="text-xs text-ink-gray-5">Overdue</p>
          <p class="mt-1 text-2xl font-bold text-orange-600">{{ overdueCount }}</p>
        </div>
      </div>

      <!-- Breakdown by type and status -->
      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <!-- By status -->
        <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
          <h3 class="mb-3 text-sm font-semibold text-ink-gray-7">Tasks by Status</h3>
          <div class="space-y-2">
            <div
              v-for="(count, status) in byStatus"
              :key="status"
              class="flex items-center gap-3"
            >
              <span class="w-28 shrink-0 text-sm text-ink-gray-7">{{ status }}</span>
              <div class="flex-1 h-2 rounded-full bg-surface-gray-3 overflow-hidden">
                <div
                  class="h-full rounded-full bg-ink-gray-5 transition-all"
                  :style="{ width: filteredTasks.length ? (count / filteredTasks.length * 100) + '%' : '0%' }"
                />
              </div>
              <span class="w-8 shrink-0 text-right text-sm font-medium text-ink-gray-8">{{ count }}</span>
            </div>
          </div>
        </div>
        <!-- By type -->
        <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
          <h3 class="mb-3 text-sm font-semibold text-ink-gray-7">Tasks by Type</h3>
          <div class="space-y-2">
            <div
              v-for="(count, type) in byType"
              :key="type"
              class="flex items-center gap-3"
            >
              <span class="w-28 shrink-0 text-sm text-ink-gray-7">{{ type || '— None —' }}</span>
              <div class="flex-1 h-2 rounded-full bg-surface-gray-3 overflow-hidden">
                <div
                  class="h-full rounded-full bg-ink-gray-5 transition-all"
                  :style="{ width: filteredTasks.length ? (count / filteredTasks.length * 100) + '%' : '0%' }"
                />
              </div>
              <span class="w-8 shrink-0 text-right text-sm font-medium text-ink-gray-8">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Assignee performance table -->
      <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
        <h3 class="mb-3 text-sm font-semibold text-ink-gray-7">Assignee Summary</h3>
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-outline-gray-1 text-left text-xs text-ink-gray-5">
                <th class="pb-2 font-medium">Assignee</th>
                <th class="pb-2 font-medium text-right">Total</th>
                <th class="pb-2 font-medium text-right">Done</th>
                <th class="pb-2 font-medium text-right">In Progress</th>
                <th class="pb-2 font-medium text-right">Blocked</th>
                <th class="pb-2 font-medium text-right">Overdue</th>
                <th class="pb-2 font-medium text-right">Points</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr
                v-for="row in assigneeSummary"
                :key="row.user"
                class="hover:bg-surface-gray-1 transition-colors"
              >
                <td class="py-2 text-ink-gray-8 font-medium">{{ row.fullName }}</td>
                <td class="py-2 text-right text-ink-gray-7">{{ row.total }}</td>
                <td class="py-2 text-right text-green-600">{{ row.done }}</td>
                <td class="py-2 text-right text-blue-600">{{ row.inProgress }}</td>
                <td class="py-2 text-right text-red-600">{{ row.blocked }}</td>
                <td class="py-2 text-right text-orange-600">{{ row.overdue }}</td>
                <td class="py-2 text-right text-ink-gray-6">{{ row.points }}</td>
              </tr>
              <tr v-if="!assigneeSummary.length">
                <td colspan="7" class="py-4 text-center text-ink-gray-4">No data</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Task table -->
      <div class="rounded-xl border border-outline-gray-2 bg-surface-white p-4">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-ink-gray-7">Task List ({{ filteredTasks.length }})</h3>
        </div>
        <div v-if="!tasks.isFinished" class="py-8 text-center text-sm text-ink-gray-4">Loading...</div>
        <div v-else-if="!filteredTasks.length" class="py-8 text-center text-sm text-ink-gray-4">No tasks match the current filters.</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-outline-gray-1 text-left text-xs text-ink-gray-5">
                <th class="pb-2 font-medium">Title</th>
                <th class="pb-2 font-medium">Type</th>
                <th class="pb-2 font-medium">Status</th>
                <th class="pb-2 font-medium">Priority</th>
                <th class="pb-2 font-medium">Assignee</th>
                <th class="pb-2 font-medium">Space</th>
                <th class="pb-2 font-medium">Sprint</th>
                <th class="pb-2 font-medium text-right">pts</th>
                <th class="pb-2 font-medium">Due</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-outline-gray-1">
              <tr
                v-for="task in filteredTasks"
                :key="task.name"
                class="cursor-pointer hover:bg-surface-gray-1 transition-colors"
                @click="$router.push({ name: 'Task', params: { taskId: task.name } })"
              >
                <td class="py-2 pr-4 font-medium text-ink-gray-8 max-w-[200px] truncate">{{ task.title }}</td>
                <td class="py-2 pr-3">
                  <span v-if="task.task_type" class="rounded-full bg-surface-gray-2 px-2 py-0.5 text-xs text-ink-gray-6">{{ task.task_type }}</span>
                  <span v-else class="text-xs text-ink-gray-3">—</span>
                </td>
                <td class="py-2 pr-3">
                  <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="statusClass(task.status)">{{ task.status }}</span>
                </td>
                <td class="py-2 pr-3">
                  <span v-if="task.priority" class="text-xs" :class="priorityClass(task.priority)">{{ task.priority }}</span>
                  <span v-else class="text-xs text-ink-gray-3">—</span>
                </td>
                <td class="py-2 pr-3 text-ink-gray-6">{{ task.assigned_to || '—' }}</td>
                <td class="py-2 pr-3 text-ink-gray-5 text-xs">{{ spaceTitle(task.project) }}</td>
                <td class="py-2 pr-3 text-ink-gray-5 text-xs">{{ task.sprint || '—' }}</td>
                <td class="py-2 text-right text-ink-gray-6">{{ task.points || '—' }}</td>
                <td class="py-2 text-xs" :class="isOverdue(task.due_date) && !['Done','Canceled'].includes(task.status) ? 'text-red-500 font-medium' : 'text-ink-gray-5'">
                  {{ task.due_date || '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useList, Button } from 'frappe-ui'
import { users } from '@/data/users'

const router = useRouter()
const today = new Date().toISOString().split('T')[0]

const filters = reactive({
  status: '',
  task_type: '',
  priority: '',
  assigned_to: '',
  project: '',
  overdueOnly: false,
})

function resetFilters() {
  filters.status = ''
  filters.task_type = ''
  filters.priority = ''
  filters.assigned_to = ''
  filters.project = ''
  filters.overdueOnly = false
}

const tasks = useList({
  doctype: 'GP Task',
  fields: ['name', 'title', 'task_type', 'status', 'priority', 'assigned_to', 'project', 'sprint', 'points', 'due_date'],
  orderBy: 'creation desc',
  limit: 9999,
  auto: true,
})

const spaces = useList({
  doctype: 'GP Project',
  fields: ['name', 'title'],
  limit: 999,
  auto: true,
})

const userOptions = computed(() => (users.data || []).filter((u: any) => u.enabled))

const filteredTasks = computed(() => {
  let list = (tasks.data || []) as any[]
  if (filters.status) list = list.filter(t => t.status === filters.status)
  if (filters.task_type) list = list.filter(t => t.task_type === filters.task_type)
  if (filters.priority) list = list.filter(t => t.priority === filters.priority)
  if (filters.assigned_to) list = list.filter(t => t.assigned_to === filters.assigned_to)
  if (filters.project) list = list.filter(t => t.project === filters.project)
  if (filters.overdueOnly) list = list.filter(t => isOverdue(t.due_date) && !['Done', 'Canceled'].includes(t.status))
  return list
})

function isOverdue(d: string) {
  return !!d && d < today
}

const overdueCount = computed(() =>
  filteredTasks.value.filter(t => isOverdue(t.due_date) && !['Done', 'Canceled'].includes(t.status)).length
)

function countByStatus(status: string) {
  return filteredTasks.value.filter(t => t.status === status).length
}

const byStatus = computed(() => {
  const statuses = ['Backlog', 'Todo', 'In Progress', 'Blocked', 'In Review', 'Done', 'Canceled']
  const result: Record<string, number> = {}
  for (const s of statuses) {
    const c = filteredTasks.value.filter(t => t.status === s).length
    if (c > 0) result[s] = c
  }
  return result
})

const byType = computed(() => {
  const result: Record<string, number> = {}
  for (const t of filteredTasks.value) {
    const key = t.task_type || ''
    result[key] = (result[key] || 0) + 1
  }
  return Object.fromEntries(Object.entries(result).sort((a, b) => b[1] - a[1]))
})

const assigneeSummary = computed(() => {
  const map: Record<string, any> = {}
  const userMap: Record<string, string> = {}
  for (const u of (users.data || []) as any[]) userMap[u.name] = u.full_name

  for (const t of filteredTasks.value) {
    const key = t.assigned_to || '__unassigned__'
    if (!map[key]) map[key] = { user: key, fullName: t.assigned_to ? (userMap[t.assigned_to] || t.assigned_to) : '— Unassigned —', total: 0, done: 0, inProgress: 0, blocked: 0, overdue: 0, points: 0 }
    map[key].total++
    if (t.status === 'Done') map[key].done++
    if (t.status === 'In Progress') map[key].inProgress++
    if (t.status === 'Blocked') map[key].blocked++
    if (isOverdue(t.due_date) && !['Done', 'Canceled'].includes(t.status)) map[key].overdue++
    map[key].points += t.points || 0
  }
  return Object.values(map).sort((a, b) => b.total - a.total)
})

const spaceMap = computed(() => {
  const m: Record<string, string> = {}
  for (const s of (spaces.data || []) as any[]) m[s.name] = s.title
  return m
})

function spaceTitle(name: string) {
  return spaceMap.value[name] || name || '—'
}

function statusClass(status: string) {
  const map: Record<string, string> = {
    'Backlog': 'bg-surface-gray-2 text-ink-gray-6',
    'Todo': 'bg-blue-50 text-blue-700',
    'In Progress': 'bg-orange-50 text-orange-700',
    'Blocked': 'bg-red-50 text-red-700',
    'In Review': 'bg-purple-50 text-purple-700',
    'Done': 'bg-green-50 text-green-700',
    'Canceled': 'bg-surface-gray-2 text-ink-gray-4',
  }
  return map[status] || 'bg-surface-gray-2 text-ink-gray-6'
}

function priorityClass(priority: string) {
  const map: Record<string, string> = {
    'Urgent': 'text-red-600 font-semibold',
    'High': 'text-orange-600',
    'Medium': 'text-ink-gray-7',
    'Low': 'text-ink-gray-4',
  }
  return map[priority] || 'text-ink-gray-6'
}

function exportCsv() {
  const headers = ['ID', 'Title', 'Type', 'Status', 'Priority', 'Assigned To', 'Space', 'Sprint', 'Points', 'Due Date']
  const rows = filteredTasks.value.map(t => [
    t.name,
    `"${(t.title || '').replace(/"/g, '""')}"`,
    t.task_type || '',
    t.status || '',
    t.priority || '',
    t.assigned_to || '',
    spaceTitle(t.project),
    t.sprint || '',
    t.points || '',
    t.due_date || '',
  ])
  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `tasks-report-${today}.csv`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="flex h-full flex-col bg-surface-gray-2 text-ink-gray-9">
    <!-- Premium Header -->
    <header class="sticky top-0 z-20 border-b bg-white/80 backdrop-blur-md px-6 py-4 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <div class="rounded-lg bg-blue-100 p-2 text-blue-600">
            <LucideLayoutGrid class="h-6 w-6" />
          </div>
          <div>
            <h1 class="text-2xl font-bold tracking-tight">
              {{ props.personal ? 'Personal Dashboard' : 'Overview Dashboard' }}
            </h1>
            <p class="text-xs text-ink-gray-5 font-medium opacity-60">
              {{ greeting }}, {{ sessionUser.full_name }}
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2">
           <Badge variant="ghost" class="hidden sm:inline-flex">
             {{ tasks.data?.length || 0 }} Total Tasks
           </Badge>
        </div>
      </div>
    </header>

    <div class="flex-1 overflow-auto p-6 space-y-8">
      <!-- High-Level Stats Cards -->
      <section>
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          <!-- Stat Cards with better styling -->
          <div class="relative overflow-hidden group rounded-2xl border border-red-100 bg-white p-6 shadow-sm transition-all hover:scale-[1.02] hover:shadow-lg">
            <div class="flex items-center justify-between mb-4">
              <div class="rounded-lg bg-red-100 p-2 text-red-600">
                <LucideAlertOctagon class="h-5 w-5" />
              </div>
              <span class="text-xs font-bold text-red-500 bg-red-50 px-2 py-0.5 rounded-full">Alert</span>
            </div>
            <p class="text-sm font-semibold text-ink-gray-5">Blocked / At-Risk</p>
            <h3 class="mt-1 text-3xl font-extrabold text-red-700">{{ blockedCount }}</h3>
            <div class="absolute bottom-0 left-0 h-1 bg-red-400 transition-all duration-500 group-hover:w-full" :style="{ width: (blockedCount / (tasks.data?.length || 1) * 100) + '%' }"></div>
          </div>

          <div class="relative overflow-hidden group rounded-2xl border border-orange-100 bg-white p-6 shadow-sm transition-all hover:scale-[1.02] hover:shadow-lg">
            <div class="flex items-center justify-between mb-4">
              <div class="rounded-lg bg-orange-100 p-2 text-orange-600">
                <LucideClock class="h-5 w-5" />
              </div>
              <span class="text-xs font-bold text-orange-500 bg-orange-50 px-2 py-0.5 rounded-full">Urgent</span>
            </div>
            <p class="text-sm font-semibold text-ink-gray-5">Overdue Tasks</p>
            <h3 class="mt-1 text-3xl font-extrabold text-orange-700">{{ overdueCount }}</h3>
            <div class="absolute bottom-0 left-0 h-1 bg-orange-400 transition-all duration-500 group-hover:w-full" :style="{ width: (overdueCount / (tasks.data?.length || 1) * 100) + '%' }"></div>
          </div>

          <div class="relative overflow-hidden group rounded-2xl border border-blue-100 bg-white p-6 shadow-sm transition-all hover:scale-[1.02] hover:shadow-lg">
            <div class="flex items-center justify-between mb-4">
              <div class="rounded-lg bg-blue-100 p-2 text-blue-600">
                <LucideListTodo class="h-5 w-5" />
              </div>
              <span class="text-xs font-bold text-blue-500 bg-blue-50 px-2 py-0.5 rounded-full">In Progress</span>
            </div>
            <p class="text-sm font-semibold text-ink-gray-5">Active Processing</p>
            <h3 class="mt-1 text-3xl font-extrabold text-blue-700">{{ activeCount }}</h3>
            <div class="absolute bottom-0 left-0 h-1 bg-blue-400 transition-all duration-500 group-hover:w-full" :style="{ width: (activeCount / (tasks.data?.length || 1) * 100) + '%' }"></div>
          </div>

          <div class="relative overflow-hidden group rounded-2xl border border-green-100 bg-white p-6 shadow-sm transition-all hover:scale-[1.02] hover:shadow-lg">
            <div class="flex items-center justify-between mb-4">
              <div class="rounded-lg bg-green-100 p-2 text-green-600">
                <LucideCheckCircle class="h-5 w-5" />
              </div>
              <span class="text-xs font-bold text-green-500 bg-green-50 px-2 py-0.5 rounded-full">Achieved</span>
            </div>
            <p class="text-sm font-semibold text-ink-gray-5">Tasks Completed</p>
            <h3 class="mt-1 text-3xl font-extrabold text-green-700">{{ completedCount }}</h3>
            <div class="absolute bottom-0 left-0 h-1 bg-green-400 transition-all duration-500 group-hover:w-full" :style="{ width: (completedCount / (tasks.data?.length || 1) * 100) + '%' }"></div>
          </div>
        </div>
      </section>

      <!-- Advanced Data Visuals -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-12">
        <!-- Main Content Area -->
        <div class="lg:col-span-8 space-y-8">
          <!-- Upcoming Deadlines -->
          <div class="rounded-2xl border bg-white shadow-sm overflow-hidden">
            <div class="flex items-center justify-between border-b bg-white px-6 py-4">
              <div class="flex items-center space-x-2">
                <LucideTimer class="h-5 w-5 text-ink-gray-5" />
                <h2 class="font-bold text-lg">Upcoming Critical Deadlines</h2>
              </div>
              <button class="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors">View All</button>
            </div>
            <div class="p-6">
              <ul v-if="upcomingTasks.length > 0" class="divide-y divide-ink-gray-1">
                <li v-for="task in upcomingTasks" :key="task.name" class="py-4 first:pt-0 last:pb-0 group transition-all hover:bg-surface-gray-1 rounded-lg px-2 -mx-2">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                      <div :class="['w-2 h-2 rounded-full', getPriorityColor(task.priority)]"></div>
                      <div>
                        <p class="font-bold text-sm text-ink-gray-9">{{ task.title || task.name }}</p>
                        <p class="text-xs text-ink-gray-5 mt-0.5">Assigned to: {{ task.assigned_to_full_name || task.assigned_to }}</p>
                      </div>
                    </div>
                    <div class="flex items-center space-x-4">
                      <div class="text-right">
                        <p class="text-sm font-semibold" :class="isOverdue(task.due_date) ? 'text-red-500' : 'text-ink-gray-7'">
                          {{ formatDate(task.due_date) }}
                        </p>
                        <p class="text-xs text-ink-gray-4 uppercase tracking-tighter">{{ task.status }}</p>
                      </div>
                      <LucideArrowRight class="h-4 w-4 text-ink-gray-3 opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
                    </div>
                  </div>
                </li>
              </ul>
              <div v-else class="flex h-48 flex-col items-center justify-center text-ink-gray-4">
                <LucideSmile class="mb-3 h-12 w-12 opacity-10" />
                <p class="text-sm">No upcoming deadlines. Good job!</p>
              </div>
            </div>
          </div>

          <!-- Section for Overview: Workload Distribution / Space Activity -->
          <div v-if="!props.personal" class="rounded-2xl border bg-white shadow-sm overflow-hidden">
            <div class="flex items-center justify-between border-b px-6 py-4">
              <div class="flex items-center space-x-2">
                <LucideUsers class="h-5 w-5 text-ink-gray-5" />
                <h2 class="font-bold text-lg">Team Workload Distribution</h2>
              </div>
            </div>
            <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div v-for="(count, user) in workloadDistribution" :key="user" class="flex flex-col space-y-1.5 p-4 rounded-xl border border-ink-gray-1 hover:border-blue-200 transition-colors">
                 <div class="flex items-center justify-between">
                   <div class="flex items-center space-x-2">
                      <div class="h-8 w-8 rounded-full bg-surface-gray-7 text-white flex items-center justify-center text-xs font-bold">
                        {{ user.charAt(0).toUpperCase() }}
                      </div>
                      <span class="text-sm font-bold text-ink-gray-8">{{ user }}</span>
                   </div>
                   <span class="text-xs font-bold bg-blue-50 text-blue-600 px-2 py-0.5 rounded-md">Tasks: {{ count }}</span>
                 </div>
                 <div class="w-full h-1.5 bg-ink-gray-1 rounded-full mt-2 overflow-hidden">
                   <div class="h-full bg-blue-500 rounded-full" :style="{ width: (count / activeCount * 100) + '%' }"></div>
                 </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Components -->
        <div class="lg:col-span-4 space-y-8">
           <!-- Productivity Pulse -->
          <div class="rounded-2xl border bg-white shadow-sm p-6">
             <div class="flex items-center space-x-2 mb-6">
                <LucideActivity class="h-5 w-5 text-blue-500" />
                <h3 class="font-bold text-lg">Productivity Pulse</h3>
             </div>
             <div class="space-y-6">
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-bold text-ink-gray-5 uppercase">Overall Completion Rate</span>
                    <span class="text-xs font-bold text-blue-600">{{ completionRate }}%</span>
                  </div>
                  <div class="w-full h-3 bg-surface-gray-2 rounded-full overflow-hidden shadow-inner p-0.5">
                    <div class="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full transition-all duration-1000 shadow-sm" :style="{ width: completionRate + '%' }"></div>
                  </div>
                </div>

                <div class="flex items-center justify-between pointer-events-none opacity-40">
                  <div class="text-ink-gray-5 text-xs">
                    <p class="font-bold text-ink-gray-8">Velocity</p>
                    <p>+12% this week</p>
                  </div>
                  <LucideLineChart class="h-10 w-20 text-blue-300" />
                </div>
             </div>
          </div>

          <!-- Quick Tip or Motivation -->
          <div class="rounded-2xl bg-gradient-to-br from-indigo-600 to-purple-700 p-6 text-black shadow-lg overflow-hidden relative">
             <div class="relative z-10">
                <h4 class="text-lg font-bold mb-2">Did you know?</h4>
                <p class="text-sm text-indigo-50 opacity-90 leading-relaxed">
                  Breaking large tasks into smaller sub-tasks increases completion probability by 40%. Try it out today!
                </p>
             </div>
             <LucideLayers class="absolute -right-4 -bottom-4 h-32 w-32 text-black/10 rotate-12" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useList, Badge } from 'frappe-ui'
import { spaces } from '@/data/spaces'
import { activeUsers, useSessionUser } from '@/data/users'
import LucideListTodo from '~icons/lucide/list-todo'
import LucideLayoutGrid from '~icons/lucide/layout-grid'
import LucideUsers from '~icons/lucide/users'
import LucideCheckCircle from '~icons/lucide/check-circle'
import LucideActivity from '~icons/lucide/activity'
import LucideLineChart from '~icons/lucide/line-chart'
import LucideAlertOctagon from '~icons/lucide/alert-octagon'
import LucideClock from '~icons/lucide/clock'
import LucidePieChart from '~icons/lucide/pie-chart'
import LucideTimer from '~icons/lucide/timer'
import LucideArrowRight from '~icons/lucide/arrow-right'
import LucideSmile from '~icons/lucide/smile'
import LucideLayers from '~icons/lucide/layers'

const props = defineProps({
  personal: {
    type: Boolean,
    default: false
  }
})

const sessionUser = useSessionUser()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 18) return 'Good Afternoon'
  return 'Good Evening'
})

const tasks = useList({
  doctype: 'GP Task',
  fields: ['name', 'title', 'status', 'is_completed', 'assigned_to', 'assigned_to_full_name', 'due_date', 'priority', 'project'],
  filters: computed(() => props.personal ? { assigned_to: sessionUser.name } : {}),
  limit: 9999,
  auto: true
})

const blockedCount = computed(() => {
  return tasks.data?.filter(t => t.status === 'Blocked' || t.priority === 'Critical').length || 0
})

const completedCount = computed(() => {
  return tasks.data?.filter(t => t.status === 'Done' || t.is_completed).length || 0
})

const activeCount = computed(() => {
  return tasks.data?.filter(t => t.status !== 'Done' && !t.is_completed).length || 0
})

const overdueCount = computed(() => {
  if (!tasks.data) return 0
  const today = new Date().toISOString().split('T')[0]
  return tasks.data.filter(t => t.due_date && t.due_date < today && t.status !== 'Done' && !t.is_completed).length
})

const upcomingTasks = computed(() => {
  if (!tasks.data) return []
  const today = new Date().toISOString().split('T')[0]
  return tasks.data
    .filter(t => t.due_date && t.due_date >= today && t.status !== 'Done' && !t.is_completed)
    .sort((a, b) => a.due_date.localeCompare(b.due_date))
    .slice(0, 5)
})

const workloadDistribution = computed(() => {
  if (!tasks.data) return {}
  return tasks.data
    .filter(t => t.status !== 'Done' && !t.is_completed)
    .reduce((acc, t) => {
      const user = t.assigned_to || 'Unassigned'
      acc[user] = (acc[user] || 0) + 1
      return acc
    }, {})
})

const completionRate = computed(() => {
  const total = tasks.data?.length || 0
  if (total === 0) return 0
  return Math.round((completedCount.value / total) * 100)
})

const formatDate = (dateStr) => {
  if (!dateStr) return 'No Date'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { day: 'numeric', month: 'short' })
}

const isOverdue = (dateStr) => {
  if (!dateStr) return false
  const today = new Date().toISOString().split('T')[0]
  return dateStr < today
}

const getPriorityColor = (priority) => {
  switch (priority) {
    case 'Critical': return 'bg-red-500'
    case 'High': return 'bg-orange-500'
    case 'Medium': return 'bg-blue-500'
    case 'Low': return 'bg-green-500'
    default: return 'bg-ink-gray-2'
  }
}
</script>

<style scoped>
.bg-surface-gray-2 {
  background-color: #F9FAFB;
}
.bg-gradient-to-br {
  background-image: linear-gradient(to bottom right, var(--tw-gradient-stops));
}
</style>

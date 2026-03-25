<template>
  <div v-if="tasks.data?.length" class="overflow-x-auto pb-4">
    <div class="flex gap-3 min-w-max">
      <div
        v-for="column in columns"
        :key="column.status"
        class="w-60 flex-shrink-0"
        @dragover.prevent="dragOverColumn = column.status"
        @dragleave="onColumnDragLeave(column.status, $event)"
        @drop.prevent="onDrop(column.status)"
      >
        <div
          class="mb-2 flex items-center gap-2 rounded-md px-2.5 py-2 transition-colors"
          :class="dragOverColumn === column.status ? 'bg-surface-gray-3' : 'bg-surface-gray-1'"
        >
          <TaskStatusIcon :status="column.status" />
          <span class="text-sm font-medium text-ink-gray-7">{{ column.status }}</span>
          <span class="ml-auto text-sm text-ink-gray-4">{{ column.tasks.length }}</span>
        </div>
        <div
          class="min-h-12 space-y-2 rounded-lg transition-colors"
          :class="dragOverColumn === column.status ? 'bg-surface-gray-2' : ''"
        >
          <div
            v-for="task in column.tasks"
            :key="task.name"
            draggable="true"
            @dragstart="onDragStart(task)"
            @dragend="onDragEnd"
            :class="[
              'block rounded-lg border bg-surface-white p-3 transition cursor-grab active:cursor-grabbing active:opacity-50',
              draggingTask?.name === task.name
                ? 'border-outline-gray-3 opacity-40'
                : 'border-outline-gray-2 hover:bg-surface-gray-1',
            ]"
          >
            <router-link
              :to="{
                name: task.project ? 'SpaceTask' : 'Task',
                params: { spaceId: task.project, taskId: task.name },
              }"
              class="block focus:outline-none"
              @click.prevent="!isDragging && $router.push({ name: task.project ? 'SpaceTask' : 'Task', params: { spaceId: task.project, taskId: task.name } })"
            >
              <p class="text-sm font-medium text-ink-gray-8 line-clamp-2 leading-snug">
                {{ task.title }}
              </p>
              <div class="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-ink-gray-5">
                <span>#{{ task.name }}</span>
                <template v-if="task.project_title">
                  <span>&middot;</span>
                  <span class="max-w-28 truncate">{{ task.project_title }}</span>
                </template>
                <template v-if="task.due_date">
                  <span>&middot;</span>
                  <span class="flex items-center gap-1">
                    <LucideCalendar class="size-3" />
                    {{ dayjsLocal(task.due_date).format('D MMM') }}
                  </span>
                </template>
                <template v-if="task.priority">
                  <span>&middot;</span>
                  <span class="flex items-center gap-1.5">
                    <span
                      class="h-2 w-2 rounded-full"
                      :class="{
                        'bg-red-500': task.priority === 'High',
                        'bg-amber-400': task.priority === 'Medium',
                        'bg-surface-gray-5': task.priority === 'Low',
                      }"
                    />
                    {{ task.priority }}
                  </span>
                </template>
              </div>
              <div v-if="task.assigned_to" class="mt-2 text-xs text-ink-gray-5">
                {{ $user(task.assigned_to).full_name }}
              </div>
            </router-link>
          </div>
        </div>
        <div
          v-if="!column.tasks.length"
          class="mt-2 rounded-lg border border-dashed px-3 py-5 text-center text-sm transition-colors"
          :class="dragOverColumn === column.status ? 'border-outline-gray-4 bg-surface-gray-2 text-ink-gray-5' : 'border-outline-gray-2 text-ink-gray-3'"
        >
          No tasks
        </div>
      </div>
    </div>
  </div>
  <EmptyStateBox v-else>
    <LucideCoffee class="h-7 w-7 text-ink-gray-4" />
    No tasks
  </EmptyStateBox>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useList, dayjsLocal } from 'frappe-ui'
import type { UseListOptions } from 'frappe-ui'
import { GPTask } from '@/types/doctypes'
import TaskStatusIcon from './NewTaskDialog/TaskStatusIcon.vue'
import EmptyStateBox from './EmptyStateBox.vue'

type TaskWithProject = GPTask & { project_title?: string }

interface Props {
  listOptions?: {
    filters?: UseListOptions<GPTask>['filters']
    orderBy?: UseListOptions<GPTask>['orderBy']
    pageLength?: UseListOptions<GPTask>['limit']
  }
}

const props = withDefaults(defineProps<Props>(), {
  listOptions: () => ({ orderBy: 'creation desc', pageLength: 200 }),
})

type TaskStatus = 'Backlog' | 'Todo' | 'In Progress' | 'Done' | 'Canceled'
const statusOrder: TaskStatus[] = ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled']

interface KanbanColumn {
  status: TaskStatus
  tasks: TaskWithProject[]
}

const tasks = useList<TaskWithProject>({
  url: '/api/v2/method/gameplan.gameplan.doctype.gp_task.gp_task.get_list',
  doctype: 'GP Task',
  fields: ['*', 'project.title as project_title'],
  filters: props.listOptions.filters,
  orderBy: props.listOptions.orderBy,
  limit: props.listOptions.pageLength ?? 200,
  cacheKey: ['Tasks', props.listOptions],
})

const tasksByStatus = computed<Record<TaskStatus, TaskWithProject[]>>(() => {
  const grouped: Record<TaskStatus, TaskWithProject[]> = {
    Backlog: [], Todo: [], 'In Progress': [], Done: [], Canceled: [],
  }
  for (const task of tasks.data || []) {
    const key = ((task as TaskWithProject).status as TaskStatus) || 'Backlog'
    grouped[key].push(task as TaskWithProject)
  }
  return grouped
})

const columns = computed<KanbanColumn[]>(() =>
  statusOrder.map((status) => ({
    status,
    tasks: tasksByStatus.value[status] || [],
  })),
)

// Drag & drop
const draggingTask = ref<TaskWithProject | null>(null)
const dragOverColumn = ref<TaskStatus | null>(null)
const isDragging = ref(false)

function onDragStart(task: TaskWithProject) {
  draggingTask.value = task
  isDragging.value = true
}

function onDragEnd() {
  draggingTask.value = null
  dragOverColumn.value = null
  // small delay so click handler can check isDragging before reset
  setTimeout(() => { isDragging.value = false }, 100)
}

function onColumnDragLeave(status: TaskStatus, event: DragEvent) {
  const related = event.relatedTarget as HTMLElement | null
  const col = (event.currentTarget as HTMLElement)
  if (related && col.contains(related)) return
  if (dragOverColumn.value === status) dragOverColumn.value = null
}

function onDrop(targetStatus: TaskStatus) {
  dragOverColumn.value = null
  if (!draggingTask.value || draggingTask.value.status === targetStatus) return
  tasks.setValue.submit({ name: draggingTask.value.name, status: targetStatus })
  draggingTask.value = null
}
</script>

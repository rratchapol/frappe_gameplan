<template>
  <div class="mt-5 body-container">
    <SpaceHeaderActions>
      <Button variant="solid" @click="openCreateDialog">
        <template #prefix><LucidePlus class="h-4 w-4" /></template>
        New Sprint
      </Button>
    </SpaceHeaderActions>
    <div class="mb-4 flex items-center">
      <SpaceTabs :spaceId="spaceId" />
    </div>

    <!-- Empty state -->
    <div v-if="sprints.isFinished && !sprints.data?.length" class="py-16 text-center text-base text-ink-gray-5">
      No sprints yet. Create one to get started.
    </div>

    <!-- Sprint list -->
    <div class="space-y-3 pb-16">
      <div
        v-for="sprint in sprints.data"
        :key="sprint.name"
        class="rounded-lg border bg-surface-white p-4 transition-colors"
        :class="isOverCapacity(sprint) ? 'border-red-200' : 'border-outline-gray-2 hover:border-outline-gray-3'"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="font-semibold text-ink-gray-8">{{ sprint.title }}</span>
              <span
                class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium"
                :class="{
                  'bg-surface-gray-2 text-ink-gray-6': sprint.status === 'Planning',
                  'bg-surface-gray-3 text-ink-gray-8': sprint.status === 'Active',
                  'bg-surface-gray-1 text-ink-gray-4': sprint.status === 'Completed',
                }"
              >
                {{ sprint.status }}
              </span>
              <span
                v-if="isOverCapacity(sprint)"
                class="inline-flex items-center gap-1 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600"
              >
                <LucideAlertTriangle class="h-3 w-3" /> Over capacity
              </span>
            </div>

            <div class="mt-1 flex items-center gap-4 text-sm text-ink-gray-5">
              <span v-if="sprint.start_date">
                <LucideCalendar class="inline h-3.5 w-3.5 mr-1" />{{ formatDate(sprint.start_date) }} → {{ formatDate(sprint.end_date) }}
              </span>
              <span>{{ getTaskCount(sprint.name) }} tasks</span>
              <span>{{ getPointsUsed(sprint.name) }} pts used</span>
            </div>

            <!-- Capacity bar -->
            <div v-if="sprint.capacity_points > 0" class="mt-2.5">
              <div class="mb-1 flex items-center justify-between text-xs text-ink-gray-4">
                <span>{{ getPointsUsed(sprint.name) }} / {{ sprint.capacity_points }} pts</span>
                <span>{{ Math.round((getPointsUsed(sprint.name) / sprint.capacity_points) * 100) }}% full</span>
              </div>
              <div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-gray-3">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="isOverCapacity(sprint) ? 'bg-red-500' : getCapacityPct(sprint) >= 75 ? 'bg-orange-400' : 'bg-blue-400'"
                  :style="{ width: Math.min(getCapacityPct(sprint), 100) + '%' }"
                />
              </div>
            </div>

            <!-- Expand/collapse toggle -->
            <button
              class="mt-2.5 flex items-center gap-1 text-xs text-ink-gray-5 hover:text-ink-gray-8 transition-colors"
              @click.stop="toggleExpand(sprint.name)"
            >
              <LucideChevronDown v-if="!expandedSprints.has(sprint.name)" class="h-3.5 w-3.5" />
              <LucideChevronUp v-else class="h-3.5 w-3.5" />
              {{ expandedSprints.has(sprint.name) ? 'Hide tasks' : 'Show tasks' }}
            </button>

            <!-- Task list -->
            <div v-if="expandedSprints.has(sprint.name)" class="mt-3 divide-y divide-outline-gray-1 border-t border-outline-gray-1">
              <div
                v-if="!getSprintTasks(sprint.name).length"
                class="py-3 text-sm text-ink-gray-4"
              >
                No tasks in this sprint.
              </div>
              <div
                v-for="task in getSprintTasks(sprint.name)"
                :key="task.name"
                class="flex items-center gap-3 py-2 cursor-pointer hover:bg-surface-gray-1 rounded px-1 transition-colors"
                @click="router.push({ name: 'Task', params: { taskId: task.name } })"
              >
                <TaskStatusIcon :status="task.status" class="shrink-0" />
                <span class="flex-1 truncate text-sm text-ink-gray-8">{{ task.title }}</span>
                <span v-if="task.points" class="shrink-0 text-xs text-ink-gray-4">{{ task.points }}pt</span>
                <span v-if="task.assigned_to" class="shrink-0 text-xs text-ink-gray-5">{{ task.assigned_to }}</span>
              </div>
            </div>
          </div>

          <div class="flex shrink-0 items-center gap-1">
            <!-- Carry-forward button: only when sprint has incomplete tasks -->
            <Button
              v-if="getIncompleteCount(sprint.name) > 0"
              variant="ghost"
              :tooltip="`Carry forward ${getIncompleteCount(sprint.name)} incomplete task(s)`"
              @click="openCarryForwardDialog(sprint)"
            >
              <template #icon><LucideForward class="h-4 w-4 text-ink-gray-5" /></template>
            </Button>
            <Button variant="ghost" @click="openEditDialog(sprint)">
              <template #icon><LucidePencil class="h-4 w-4" /></template>
            </Button>
            <Button variant="ghost" @click="confirmDelete(sprint)">
              <template #icon><LucideTrash2 class="h-4 w-4 text-ink-gray-5" /></template>
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Create / Edit Dialog -->
    <Dialog v-model="dialog.show" :options="{ title: dialog.editing ? 'Edit Sprint' : 'New Sprint' }">
      <template #body-content>
        <div class="space-y-3">
          <FormControl label="Sprint Name" v-model="form.title" autofocus />
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-1 block text-sm text-ink-gray-6">Start Date</label>
              <DatePicker v-model="form.start_date" variant="outline" placeholder="Start date" />
            </div>
            <div>
              <label class="mb-1 block text-sm text-ink-gray-6">End Date</label>
              <DatePicker v-model="form.end_date" variant="outline" placeholder="End date" />
            </div>
          </div>
          <FormControl
            label="Status"
            type="select"
            :options="[
              { label: 'Planning', value: 'Planning' },
              { label: 'Active', value: 'Active' },
              { label: 'Completed', value: 'Completed' },
            ]"
            v-model="form.status"
          />
          <FormControl
            label="Capacity Points"
            type="number"
            v-model="form.capacity_points"
            placeholder="0 = unlimited"
          />
        </div>
      </template>
      <template #actions>
        <Button
          variant="solid"
          class="w-full"
          :loading="sprints.insert.loading || sprints.setValue.loading"
          @click="saveSprint"
        >
          {{ dialog.editing ? 'Save' : 'Create Sprint' }}
        </Button>
      </template>
    </Dialog>

    <!-- Carry-forward Dialog -->
    <Dialog
      v-model="cfDialog.show"
      :options="{ title: 'Carry Forward Tasks' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <p class="text-sm text-ink-gray-6">
            Move <strong>{{ getIncompleteCount(cfDialog.sourceSprint) }}</strong> incomplete task(s) from
            <strong>{{ cfDialog.sourceTitle }}</strong> to:
          </p>
          <div>
            <label class="mb-1 block text-sm text-ink-gray-6">Target Sprint</label>
            <select
              v-model="cfDialog.targetSprint"
              class="w-full rounded-md border border-outline-gray-3 bg-surface-white px-3 py-2 text-sm text-ink-gray-8 focus:border-outline-gray-5 focus:outline-none"
            >
              <option value="" disabled>Select a sprint...</option>
              <option
                v-for="s in otherSprints"
                :key="s.name"
                :value="s.name"
              >
                {{ s.title }} ({{ s.status }})
              </option>
            </select>
          </div>
          <p class="text-xs text-ink-gray-4">
            Only tasks with status Backlog, Todo, In Progress, Blocked, or In Review will be moved.
          </p>
        </div>
      </template>
      <template #actions>
        <Button
          variant="solid"
          class="w-full"
          :disabled="!cfDialog.targetSprint"
          :loading="carryForwardCall.loading"
          @click="doCarryForward"
        >
          Move Tasks
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Dialog, FormControl, DatePicker, Button, useList, useCall } from 'frappe-ui'
import SpaceHeaderActions from '@/components/SpaceHeaderActions.vue'
import SpaceTabs from '@/components/SpaceTabs.vue'
import TaskStatusIcon from '@/components/NewTaskDialog/TaskStatusIcon.vue'
import { dayjsLocal } from 'frappe-ui'

const props = defineProps<{ spaceId: string }>()
const router = useRouter()
const expandedSprints = reactive(new Set<string>())

function toggleExpand(sprintName: string) {
  if (expandedSprints.has(sprintName)) {
    expandedSprints.delete(sprintName)
  } else {
    expandedSprints.add(sprintName)
  }
}

const sprints = useList({
  doctype: 'GP Sprint',
  fields: ['name', 'title', 'status', 'start_date', 'end_date', 'capacity_points'],
  filters: () => ({ project: props.spaceId }),
  orderBy: 'creation desc',
  limit: 100,
  auto: true,
})

// All tasks in this space with sprint + points for capacity calculations
const sprintTasks = useList({
  doctype: 'GP Task',
  fields: ['name', 'title', 'sprint', 'points', 'status', 'assigned_to', 'priority'],
  filters: () => ({ project: props.spaceId, sprint: ['is', 'set'] }),
  orderBy: 'creation asc',
  limit: 9999,
  auto: true,
})

function getSprintTasks(sprintName: string) {
  return (sprintTasks.data || []).filter((t: any) => t.sprint === sprintName)
}

// Per-sprint computed helpers
function getTaskCount(sprintName: string) {
  return (sprintTasks.data || []).filter((t: any) => t.sprint === sprintName).length
}

function getPointsUsed(sprintName: string) {
  return (sprintTasks.data || [])
    .filter((t: any) => t.sprint === sprintName)
    .reduce((sum: number, t: any) => sum + (t.points || 0), 0)
}

function getIncompleteCount(sprintName: string) {
  return (sprintTasks.data || []).filter(
    (t: any) => t.sprint === sprintName && !['Done', 'Canceled'].includes(t.status)
  ).length
}

function getCapacityPct(sprint: any) {
  if (!sprint.capacity_points) return 0
  return Math.round((getPointsUsed(sprint.name) / sprint.capacity_points) * 100)
}

function isOverCapacity(sprint: any) {
  if (!sprint.capacity_points) return false
  return getPointsUsed(sprint.name) > sprint.capacity_points
}

function formatDate(d: string) {
  return dayjsLocal(d).format('D MMM YYYY')
}

// Create / Edit dialog
const dialog = reactive({ show: false, editing: false, editingName: '' })
const emptyForm = () => ({ title: '', start_date: '', end_date: '', status: 'Planning', capacity_points: 0 })
const form = reactive(emptyForm())

function openCreateDialog() {
  Object.assign(form, emptyForm())
  dialog.editing = false
  dialog.editingName = ''
  dialog.show = true
}

function openEditDialog(sprint: any) {
  Object.assign(form, {
    title: sprint.title,
    start_date: sprint.start_date || '',
    end_date: sprint.end_date || '',
    status: sprint.status,
    capacity_points: sprint.capacity_points || 0,
  })
  dialog.editing = true
  dialog.editingName = sprint.name
  dialog.show = true
}

async function saveSprint() {
  if (!form.title.trim()) return
  if (dialog.editing) {
    await sprints.setValue.submit({ name: dialog.editingName, ...form })
  } else {
    await sprints.insert.submit({ ...form, project: props.spaceId })
  }
  dialog.show = false
  sprints.reload()
}

function confirmDelete(sprint: any) {
  if (confirm(`Delete sprint "${sprint.title}"?`)) {
    sprints.delete.submit(sprint.name).then(() => sprints.reload())
  }
}

// Carry-forward dialog
const cfDialog = reactive({
  show: false,
  sourceSprint: '',
  sourceTitle: '',
  targetSprint: '',
})

const otherSprints = computed(() => {
  return (sprints.data || []).filter((s: any) => s.name !== cfDialog.sourceSprint)
})

function openCarryForwardDialog(sprint: any) {
  cfDialog.sourceSprint = sprint.name
  cfDialog.sourceTitle = sprint.title
  cfDialog.targetSprint = ''
  cfDialog.show = true
}

const carryForwardCall = useCall({
  url: '/api/v2/method/gameplan.api.carry_forward_sprint_tasks',
  immediate: false,
})

async function doCarryForward() {
  if (!cfDialog.targetSprint) return
  await carryForwardCall.submit({
    source_sprint: cfDialog.sourceSprint,
    target_sprint: cfDialog.targetSprint,
  })
  cfDialog.show = false
  sprints.reload()
  sprintTasks.reload()
}
</script>

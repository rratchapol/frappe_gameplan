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
        class="rounded-lg border border-outline-gray-2 bg-surface-white p-4 hover:border-outline-gray-3 transition-colors"
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
            </div>
            <div class="mt-1 flex items-center gap-4 text-sm text-ink-gray-5">
              <span v-if="sprint.start_date">
                <LucideCalendar class="inline h-3.5 w-3.5 mr-1" />{{ formatDate(sprint.start_date) }} → {{ formatDate(sprint.end_date) }}
              </span>
              <span>{{ getTaskCount(sprint.name) }} tasks</span>
            </div>
          </div>
          <div class="flex shrink-0 items-center gap-1">
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { Dialog, FormControl, DatePicker, Button, useList } from 'frappe-ui'
import SpaceHeaderActions from '@/components/SpaceHeaderActions.vue'
import SpaceTabs from '@/components/SpaceTabs.vue'
import { dayjsLocal } from 'frappe-ui'

const props = defineProps<{ spaceId: string }>()

const sprints = useList({
  doctype: 'GP Sprint',
  fields: ['name', 'title', 'status', 'start_date', 'end_date'],
  filters: () => ({ project: props.spaceId }),
  orderBy: 'creation desc',
  limit: 100,
  auto: true,
})

const sprintTaskCounts = useList({
  doctype: 'GP Task',
  fields: ['sprint', 'count(name) as task_count'],
  filters: () => ({ project: props.spaceId, sprint: ['is', 'set'] }),
  groupBy: 'sprint',
  limit: 100,
  auto: true,
})

function getTaskCount(sprintName: string) {
  const row = (sprintTaskCounts.data || []).find((r: any) => r.sprint === sprintName)
  return row?.task_count ?? 0
}

function formatDate(d: string) {
  return dayjsLocal(d).format('D MMM YYYY')
}

const dialog = reactive({ show: false, editing: false, editingName: '' })
const emptyForm = () => ({ title: '', start_date: '', end_date: '', status: 'Planning' })
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
</script>

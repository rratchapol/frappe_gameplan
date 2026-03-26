<template>
  <Dialog
    :options="{ title: 'New Task' }"
    :disableOutsideClickToClose="disableOutsideClickToClose"
    v-model="showDialog"
  >
    <template #body-content>
      <div class="space-y-4" v-if="newTask">
        <FormControl
          label="Title"
          v-model="newTask.doc.title"
          autocomplete="off"
          required
          ref="titleInput"
          @keydown.enter="onCreateClick"
        />
        <FormControl
          label="Description"
          type="textarea"
          v-model="newTask.doc.description"
          @keydown.enter="onCreateClick"
        />
        <div class="grid grid-cols-2 gap-2">
          <Combobox
            placeholder="Assign a user or role"
            :options="assignableOptions"
            v-model="newTask.doc.assigned_to"
          />
          <DatePicker
            v-model="newTask.doc.due_date"
            placeholder="Set due date"
            format="D MMM, YYYY"
          />
          <FormControl
            type="select"
            v-model="newTask.doc.task_type"
            placeholder="Task Type"
            :options="[
              { label: '— None —', value: '' },
              { label: 'Bug', value: 'Bug' },
              { label: 'Story', value: 'Story' },
              { label: 'Implementation', value: 'Implementation' },
              { label: 'Issue', value: 'Issue' },
              { label: 'Request', value: 'Request' },
              { label: 'Approval', value: 'Approval' },
              { label: 'Operational', value: 'Operational' },
            ]"
          />
          <FormControl
            type="number"
            v-model="newTask.doc.points"
            placeholder="Point Score"
            min="0"
            @keydown.enter="onCreateClick"
          />
          <Combobox
            placeholder="Select space"
            :options="spaceOptions"
            v-model="newTask.doc.project"
          />
          <Dropdown class="w-full" :options="statusOptions()">
            <Button>
              <template #prefix v-if="newTask.doc.status">
                <TaskStatusIcon :status="newTask.doc.status" />
              </template>
              {{ newTask.doc.status }}
            </Button>
          </Dropdown>
        </div>
        <ErrorMessage class="mt-2" :message="newTask.error" />
      </div>
    </template>
    <template #actions>
      <Button class="w-full relative" variant="solid" @click="onCreateClick">
        Create
        <div class="absolute right-0 top-0 h-7 pr-2 flex items-center justify-center">
          <KeyboardShortcut ctrl> Enter </KeyboardShortcut>
        </div>
      </Button>
    </template>
  </Dialog>
</template>
<script setup lang="ts">
import { computed, h, useTemplateRef, watch } from 'vue'
import { Dialog, FormControl, Dropdown, Combobox, DatePicker, useNewDoc } from 'frappe-ui'
import TaskStatusIcon from './TaskStatusIcon.vue'
import { activeUsers } from '@/data/users'
import { GPTask } from '@/types/doctypes'
import { showDialog, newTask, _onSuccess } from './state'
import { useGroupedSpaceOptions } from '@/data/groupedSpaces'
import KeyboardShortcut from '../KeyboardShortcut.vue'
import { roles, roleUsersMap } from '@/data/roles'

const titleInput = useTemplateRef('titleInput')
let spaceOptions = useGroupedSpaceOptions({ filterFn: (space) => !space.archived_at })

function statusOptions() {
  return (['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled'] as GPTask['status'][]).map(
    (status) => {
      return {
        icon: () => h(TaskStatusIcon, { status }),
        label: status,
        onClick: () => {
          if (newTask.value) {
            newTask.value.doc.status = status
          }
        },
      }
    },
  )
}

const assignableOptions = computed(() => {
  const result = []

  if (roles.data?.length) {
    result.push({
      group: 'Roles',
      options: roles.data.map((role) => ({
        label: role.title,
        value: `role:${role.name}`,
        description: `${(roleUsersMap.value[role.name] || []).length} members`,
      })),
    })
  }

  result.push({
    group: 'Users',
    options: activeUsers.value.map((user: any) => ({
      label: user.full_name,
      value: user.name,
      description: user.email,
    })),
  })

  return result
})

async function onCreateClick(e: KeyboardEvent) {
  if (e instanceof KeyboardEvent && !(e.ctrlKey || e.metaKey)) {
    return
  }

  if (!newTask.value) return
  if (!newTask.value.doc.title) {
    newTask.value.error = new Error('Task title is required')
    return
  }

  const assignedTo = newTask.value.doc.assigned_to
  if (assignedTo?.startsWith('role:')) {
    const roleName = assignedTo.slice(5)
    const members = roleUsersMap.value[roleName] || []
    const baseDoc = { ...newTask.value.doc }
    const tasks = members.length > 0 ? members : [null]
    for (const user of tasks) {
      const draft = useNewDoc<GPTask>('GP Task', { ...baseDoc, assigned_to: user || '' })
      await draft.submit()
    }
    showDialog.value = false
    _onSuccess.value(null as any)
    return
  }

  return newTask.value.submit().then((doc : any) => {
    showDialog.value = false
    _onSuccess.value(doc)
  })
}

let disableOutsideClickToClose = computed(() => {
  return newTask.value?.loading || newTask.value?.doc?.title != ''
})

watch(showDialog, (val) => {
  if (val) {
    setTimeout(() => {
      titleInput?.value?.$el?.querySelector('input')?.focus()
    }, 100)
  }
})
</script>

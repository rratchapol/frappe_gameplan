<template>
  <div class="flex h-full flex-col">
    <PageHeader>
      <Breadcrumbs :items="[{ label: 'Roles', route: { name: 'Roles' } }]" />
      <div class="h-7" />
    </PageHeader>
    <div class="flex min-h-0 flex-1 overflow-hidden">
      <!-- Left panel: role list -->
      <div class="w-64 shrink-0 overflow-y-auto border-r p-3">
        <div class="mb-2 flex items-center justify-between px-2 py-1">
          <span class="text-sm font-medium text-ink-gray-6">All Roles</span>
          <Button variant="ghost" @click="openCreateDialog">
            <LucidePlus class="size-4 text-ink-gray-6" />
          </Button>
        </div>
        <button
          v-for="role in roles.data"
          :key="role.name"
          @click="selectedRoleName = role.name"
          class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left transition"
          :class="
            selectedRoleName === role.name
              ? 'bg-surface-gray-3 text-ink-gray-9'
              : 'hover:bg-surface-gray-2 text-ink-gray-7'
          "
        >
          <span
            class="size-3 shrink-0 rounded-full border border-outline-gray-2"
            :style="{ background: role.color || '#94a3b8' }"
          />
          <span class="min-w-0 flex-1 truncate text-sm font-medium">{{ role.title }}</span>
          <span class="text-xs text-ink-gray-4">{{ countMembersInRole(role.name) }}</span>
        </button>
        <p v-if="roles.data?.length === 0" class="px-3 py-2 text-sm text-ink-gray-4">
          No roles yet. Create one.
        </p>
      </div>

      <!-- Right panel: role detail -->
      <div class="flex-1 overflow-y-auto p-6">
        <template v-if="selectedRole">
          <div class="mb-6 flex items-center justify-between">
            <div class="flex items-center gap-3">
              <span
                class="size-4 rounded-full border border-outline-gray-2"
                :style="{ background: selectedRole.color || '#94a3b8' }"
              />
              <h2 class="text-xl font-semibold text-ink-gray-8">{{ selectedRole.title }}</h2>
            </div>
            <div class="flex gap-2">
              <Button @click="openEditDialog">Edit</Button>
              <Button variant="subtle" @click="showDeleteDialog = true">
                <LucideTrash2 class="size-4 text-ink-gray-5" />
              </Button>
            </div>
          </div>

          <div class="mb-4 flex items-center justify-between">
            <h3 class="text-sm font-medium text-ink-gray-6">
              {{ selectedMembers.length }} member{{ selectedMembers.length !== 1 ? 's' : '' }}
            </h3>
            <Button @click="showAssignDialog = true">
              <template #prefix><LucidePlus class="size-3.5" /></template>
              Add Member
            </Button>
          </div>

          <ul class="divide-y divide-outline-gray-1">
            <li
              v-for="profile in selectedMembers"
              :key="profile.name"
              class="flex items-center justify-between py-3"
            >
              <router-link
                :to="{ name: 'PersonProfile', params: { personId: profile.name } }"
                class="flex items-center gap-3 hover:opacity-80"
              >
                <UserAvatar :user="profile.user" size="xl" />
                <div>
                  <div class="text-sm font-medium text-ink-gray-8">
                    {{ $user(profile.user).full_name }}
                  </div>
                  <div class="text-xs text-ink-gray-5">{{ $user(profile.user).email }}</div>
                </div>
              </router-link>
              <Button
                variant="ghost"
                @click="removeMemberRole(profile)"
                :loading="profiles.setValue.loading"
              >
                Remove
              </Button>
            </li>
            <li v-if="selectedMembers.length === 0" class="py-8 text-center text-sm text-ink-gray-4">
              No members with this role yet
            </li>
          </ul>
        </template>
        <div v-else class="flex h-full items-center justify-center text-sm text-ink-gray-4">
          Select a role to view its members
        </div>
      </div>
    </div>

    <!-- Create Role Dialog -->
    <Dialog :options="{ title: 'New Role' }" v-model="showCreateDialog">
      <template #body-content>
        <div class="space-y-4">
          <FormControl
            label="Title"
            placeholder="e.g. Developer, Designer, Manager"
            v-model="roleForm.title"
            @keydown.enter="createRole"
          />
          <div>
            <label class="mb-1.5 block text-xs text-ink-gray-6">Color</label>
            <input
              type="color"
              v-model="roleForm.color"
              class="h-8 w-20 cursor-pointer rounded border border-outline-gray-2"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2">
          <Button
            class="flex-1"
            variant="solid"
            @click="createRole"
            :loading="roles.insert.loading"
          >
            Create
          </Button>
          <Button class="flex-1" @click="showCreateDialog = false">Cancel</Button>
        </div>
      </template>
    </Dialog>

    <!-- Edit Role Dialog -->
    <Dialog :options="{ title: 'Edit Role' }" v-model="showEditDialog">
      <template #body-content>
        <div class="space-y-4">
          <FormControl label="Title" v-model="roleForm.title" @keydown.enter="saveEdit" />
          <div>
            <label class="mb-1.5 block text-xs text-ink-gray-6">Color</label>
            <input
              type="color"
              v-model="roleForm.color"
              class="h-8 w-20 cursor-pointer rounded border border-outline-gray-2"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <div class="flex gap-2">
          <Button
            class="flex-1"
            variant="solid"
            @click="saveEdit"
            :loading="roles.setValue.loading"
          >
            Save
          </Button>
          <Button class="flex-1" @click="showEditDialog = false">Cancel</Button>
        </div>
      </template>
    </Dialog>

    <!-- Delete Confirmation Dialog -->
    <Dialog
      :options="deleteDialogOptions"
      v-model="showDeleteDialog"
    >
      <template #actions>
        <div class="flex gap-2">
          <Button
            class="flex-1"
            variant="solid"
            theme="red"
            @click="executeDelete"
            :loading="roles.delete.loading"
          >
            Delete
          </Button>
          <Button class="flex-1" @click="showDeleteDialog = false">Cancel</Button>
        </div>
      </template>
    </Dialog>

    <!-- Add Member Dialog -->
    <Dialog :options="{ title: 'Add Member' }" v-model="showAssignDialog">
      <template #body-content>
        <div class="mb-3">
          <FormControl
            placeholder="Search members..."
            v-model="memberSearch"
            type="text"
          >
            <template #prefix>
              <LucideSearch class="size-4 text-ink-gray-4" />
            </template>
          </FormControl>
        </div>
        <div class="max-h-80 overflow-y-auto space-y-0.5">
          <button
            v-for="profile in filteredUnassigned"
            :key="profile.name"
            @click="assignRole(profile)"
            class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left hover:bg-surface-gray-2"
            :disabled="profiles.setValue.loading"
          >
            <UserAvatar :user="profile.user" size="xl" />
            <div>
              <div class="text-sm font-medium text-ink-gray-8">
                {{ $user(profile.user).full_name }}
              </div>
              <div class="text-xs text-ink-gray-5">{{ $user(profile.user).email }}</div>
            </div>
          </button>
          <p
            v-if="filteredUnassigned.length === 0"
            class="py-4 text-center text-sm text-ink-gray-4"
          >
            No available members
          </p>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useList, Dialog, FormControl, Breadcrumbs } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import UserAvatar from '@/components/UserAvatar.vue'
import { useUser } from '@/data/users'

interface GPRole {
  name: string
  title: string
  color?: string
}

interface GPUserProfileSlim {
  name: string
  user: string
  gp_role?: string
}

const roles = useList<GPRole>({
  doctype: 'GP Role',
  fields: ['name', 'title', 'color'],
  limit: 999,
  cacheKey: 'gp-roles-list',
  immediate: true,
})

const profiles = useList<GPUserProfileSlim>({
  doctype: 'GP User Profile',
  fields: ['name', 'user', 'gp_role'],
  filters: { enabled: 1 },
  limit: 999,
  immediate: true,
})

const selectedRoleName = ref<string | null>(null)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const showAssignDialog = ref(false)
const memberSearch = ref('')
const roleForm = ref({ title: '', color: '#6366f1' })

const selectedRole = computed(
  () => roles.data?.find((r : any) => r.name === selectedRoleName.value) ?? null,
)

const deleteDialogOptions = computed(() => ({
  title: 'Delete Role',
  message: selectedRole.value
    ? `Are you sure you want to delete the role "${selectedRole.value.title}"? Members will lose this role.`
    : '',
}))

const selectedMembers = computed(
  () => (profiles.data || []).filter((p  : any) => p.gp_role === selectedRoleName.value),
)

const unassignedProfiles = computed(
  () => (profiles.data || []).filter((p : any) => p.gp_role !== selectedRoleName.value),
)

const filteredUnassigned = computed(() => {
  const term = memberSearch.value.toLowerCase()
  if (!term) return unassignedProfiles.value
  return unassignedProfiles.value.filter((p : any) => {
    const user = useUser(p.user)
    return (
      (user.full_name || '').toLowerCase().includes(term) ||
      (user.email || '').toLowerCase().includes(term)
    )
  })
})

function countMembersInRole(roleName: string): number | '' {
  const count = (profiles.data || []).filter((p : any) => p.gp_role === roleName).length
  return count || ''
}

function openCreateDialog() {
  roleForm.value = { title: '', color: '#6366f1' }
  showCreateDialog.value = true
}

function createRole() {
  if (!roleForm.value.title.trim()) return
  roles.insert.submit(
    { title: roleForm.value.title.trim(), color: roleForm.value.color },
    {
      onSuccess(doc: GPRole) {
        showCreateDialog.value = false
        roleForm.value = { title: '', color: '#6366f1' }
        selectedRoleName.value = doc.name
      },
    },
  )
}

function openEditDialog() {
  if (!selectedRole.value) return
  roleForm.value = {
    title: selectedRole.value.title,
    color: selectedRole.value.color || '#6366f1',
  }
  showEditDialog.value = true
}

function saveEdit() {
  if (!selectedRole.value || !roleForm.value.title.trim()) return
  roles.setValue.submit(
    { name: selectedRole.value.name, title: roleForm.value.title.trim(), color: roleForm.value.color },
    { onSuccess: () => { showEditDialog.value = false } },
  )
}

function executeDelete() {
  if (!selectedRole.value) return
  // Clear gp_role from all members first
  const membersToUpdate = selectedMembers.value.slice()
  membersToUpdate.forEach((p : any) => {
    profiles.setValue.submit({ name: p.name, gp_role: '' })
  })
  roles.delete.submit(selectedRole.value.name, {
    onSuccess: () => {
      selectedRoleName.value = null
      showDeleteDialog.value = false
    },
  })
}

function assignRole(profile: GPUserProfileSlim) {
  profiles.setValue.submit(
    { name: profile.name, gp_role: selectedRoleName.value },
    { onSuccess: () => { showAssignDialog.value = false; memberSearch.value = '' } },
  )
}

function removeMemberRole(profile: GPUserProfileSlim) {
  profiles.setValue.submit({ name: profile.name, gp_role: '' })
}
</script>

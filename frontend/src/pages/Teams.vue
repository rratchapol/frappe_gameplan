<template>
  <div class="pb-10">
    <header class="sticky top-0 z-10 border-b bg-surface-white px-4 py-2.5 sm:px-5">
      <div class="flex items-center justify-between">
        <Breadcrumbs :items="[{ label: 'Teams', route: { name: 'Teams' } }]" />
        <Button variant="solid" @click="showNewTeamDialog = true">
          <template #prefix><LucidePlus class="h-4 w-4" /></template>
          New Team
        </Button>
      </div>
    </header>

    <!-- No teams state -->
    <div v-if="activeTeams.length === 0" class="flex flex-col items-center justify-center py-24 text-ink-gray-4">
      <LucideUsers2 class="mb-4 h-12 w-12" />
      <p class="text-lg font-medium">No Teams yet</p>
      <p class="mt-1 text-sm">Create a team to group your Spaces together</p>
      <Button class="mt-4" variant="solid" @click="showNewTeamDialog = true">
        Create your first Team
      </Button>
    </div>

    <!-- Team list -->
    <div v-else class="divide-y px-4">
      <router-link
        v-for="team in activeTeams"
        :key="team.name"
        :to="{ name: 'TeamOverview', params: { teamId: team.name } }"
        class="flex w-full items-center py-3 hover:bg-surface-gray-1 rounded px-2"
      >
        <span class="mr-2 flex h-6 w-6 items-center justify-center text-xl">
          {{ team.icon || '🏢' }}
        </span>
        <span class="text-base font-medium text-ink-gray-8">{{ team.title }}</span>
        <LucideLock v-if="team.is_private" class="ml-2 h-3 w-3 text-ink-gray-4" />
        <LucideChevronRight class="ml-auto h-5 w-5 text-ink-gray-4" />
      </router-link>
    </div>

    <!-- New Team Dialog -->
    <Dialog v-model="showNewTeamDialog" :options="{ title: 'New Team' }">
      <template #body-content>
        <div class="space-y-3">
          <FormControl
            v-model="newTeamTitle"
            type="text"
            label="Team Name"
            placeholder="e.g. Engineering, Marketing"
            autofocus
            @keydown.enter="createTeam"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="solid" :loading="isCreating" @click="createTeam">
          Create Team
        </Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Breadcrumbs, Button, Dialog, FormControl, createResource } from 'frappe-ui'
import { activeTeams, teams } from '@/data/teams'
import LucideChevronRight from '~icons/lucide/chevron-right'
import LucideUsers2 from '~icons/lucide/users-2'
import LucideLock from '~icons/lucide/lock'
import LucidePlus from '~icons/lucide/plus'

const showNewTeamDialog = ref(false)
const newTeamTitle = ref('')
const isCreating = ref(false)

const newTeamResource = createResource({
  url: 'frappe.client.insert',
  makeParams() {
    return {
      doc: {
        doctype: 'GP Team',
        title: newTeamTitle.value,
      },
    }
  },
  onSuccess() {
    teams.reload()
    showNewTeamDialog.value = false
    newTeamTitle.value = ''
    isCreating.value = false
  },
  onError() {
    isCreating.value = false
  },
})

function createTeam() {
  if (!newTeamTitle.value.trim()) return
  isCreating.value = true
  newTeamResource.submit()
}
</script>

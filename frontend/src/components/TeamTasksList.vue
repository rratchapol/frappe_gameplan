<template>
  <div v-if="spaceIds.length > 0" class="mt-8">
    <div class="mb-5 flex items-center justify-between">
      <h2 class="text-2xl font-semibold text-ink-gray-8">Tasks</h2>
      <div class="flex items-center rounded-md border border-outline-gray-2 p-0.5">
        <button
          class="rounded px-2 py-1 transition"
          :class="view === 'list' ? 'bg-surface-gray-3 text-ink-gray-8' : 'text-ink-gray-5 hover:text-ink-gray-7'"
          @click="view = 'list'"
        >
          <LucideList class="size-4" />
        </button>
        <button
          class="rounded px-2 py-1 transition"
          :class="view === 'kanban' ? 'bg-surface-gray-3 text-ink-gray-8' : 'text-ink-gray-5 hover:text-ink-gray-7'"
          @click="view = 'kanban'"
        >
          <LucideKanban class="size-4" />
        </button>
      </div>
    </div>
    <TaskList v-if="view === 'list'" :listOptions="listOptions" :groupByStatus="true" />
    <TaskKanbanBoard v-else :listOptions="listOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLocalStorage } from '@vueuse/core'
import TaskList from '@/components/TaskList.vue'
import TaskKanbanBoard from '@/components/TaskKanbanBoard.vue'
import { spaces } from '@/data/spaces'

const props = defineProps<{
  teamId: string
}>()

const view = useLocalStorage<'list' | 'kanban'>('teamTasksView', 'list')

const spaceIds = computed(() =>
  (spaces.data || [])
    .filter((space) => !space.archived_at && space.team?.toString() === props.teamId.toString())
    .map((space) => space.name),
)

const listOptions = computed(() => ({
  filters: () => ({ project: ['in', spaceIds.value] }),
  pageLength: 200,
}))
</script>

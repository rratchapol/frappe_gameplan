<template>
  <Dialog :options="{ title: 'Add members' }" @close="resetValues" v-model="open">
    <template #body-content>
      <ul v-if="membersToAdd.length" class="flex flex-wrap gap-2 py-2">
        <li
          class="flex items-center space-x-2 rounded bg-surface-gray-2 px-2 py-1.5"
          v-for="user in membersToAdd"
          :key="user.email"
          :title="user.email"
        >
          <UserAvatar :user="user.name" size="sm" />
          <span class="text-base" :class="{ 'ml-2': !user.user_image }">
            {{ user.full_name || user.email }}
          </span>
          <button
            @click="membersToAdd = membersToAdd.filter((a) => a != user)"
            class="grid h-4 w-4 place-items-center rounded text-ink-gray-7"
          >
            <LucideX class="h-4 w-4" />
          </button>
        </li>
      </ul>
      <div>
        <Combobox
          :options="invitableUsers"
          v-model="selectedUser"
          placeholder="Add member by name"
        />
        <ErrorMessage class="mt-2" :message="resource.addMembers.error" />
      </div>
      <div class="mt-4" v-show="!addMembersIntent">
        <h4 class="text-base font-medium">Members</h4>
        <ul role="list" class="mt-2 divide-y">
          <li class="flex w-full items-center py-2" v-for="member in members" :key="member.name">
            <UserAvatar :user="member.user" />
            <div class="ml-3">
              <div class="text-base font-medium text-ink-gray-7">
                {{ $user(member.user).full_name }}
              </div>
              <div class="text-sm text-ink-gray-5">
                {{ $user(member.user).email }}
              </div>
            </div>
            <Button
              class="ml-auto"
              @click="resource.removeMember.submit({ user: member.user })"
              :disabled="resource.removeMember.loading"
            >
              <template #icon>
                <LucideX class="h-4 w-4" />
              </template>
            </Button>
          </li>
        </ul>
      </div>
    </template>
    <template #actions v-if="membersToAdd.length">
      <Button
        class="w-full"
        variant="solid"
        @click="sendInvites"
        :loading="resource.addMembers.loading"
      >
        Add
      </Button>
    </template>
  </Dialog>
</template>
<script>
import { Combobox, ErrorMessage } from 'frappe-ui'
import { activeUsers } from '@/data/users'

export default {
  name: 'AddMemberDialog',
  props: ['resource', 'modelValue'],
  components: {
    ErrorMessage,
    Combobox,
  },
  data() {
    return {
      membersToAdd: [],
      selectedUser: null,
      addMembersIntent: false,
    }
  },
  watch: {
    selectedUser(userEmail) {
      if (!userEmail) return
      let user = activeUsers.value.find((u) => u.email === userEmail)
      if (user && !this.membersToAdd.find((m) => m.email === userEmail)) {
        this.membersToAdd.push(user)
        this.selectedUser = null
      }
    },
  },
  computed: {
    open: {
      get() {
        return this.modelValue
      },
      set(val) {
        this.$emit('update:modelValue', val)
        if (!val) {
          this.$emit('close')
        }
      },
    },
    members() {
      return this.resource.doc.members.map((member) => {
        let { full_name, user_image } = this.$user(member.user)
        return {
          ...member,
          full_name,
          user_image,
        }
      })
    },
    invitableUsers() {
      let memberEmails = this.members.map((m) => m.user)
      memberEmails = memberEmails.concat(this.membersToAdd.map((user) => user.email))

      return activeUsers.value
        .filter((user) => !memberEmails.includes(user.email))
        .sort((a, b) => a.full_name.localeCompare(b.full_name))
        .map((user) => ({
          label: user.full_name,
          value: user.email,
          description: user.email,
        }))
    },
  },
  methods: {
    sendInvites() {
      let users = this.membersToAdd.map((user) => user.email)
      this.resource.addMembers.submit({ users }).then(() => {
        this.membersToAdd = []
        this.addMembersIntent = false
      })
    },
    resetValues() {
      this.open = false
      this.membersToAdd = []
      this.selectedUser = null
      this.addMembersIntent = false
    },
  },
}
</script>

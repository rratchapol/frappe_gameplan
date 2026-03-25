<template>
  <div class="flex h-full flex-col">
    <div class="flex flex-1">
      <div class="w-full">
        <PageHeader>
          <Breadcrumbs :items="[{ label: 'People', route: { name: 'People' } }]" />
          <div class="h-7"></div>
        </PageHeader>
        <div class="mx-auto w-full body-container pt-6">
          <div class="flex items-center justify-between">
            <h2 class="text-xl font-semibold text-ink-gray-7">{{ people.length }} members</h2>
            <div class="flex items-center gap-2">
              <TextInput
                class="hidden sm:block"
                type="text"
                placeholder="Search"
                v-model="search"
                :debounce="500"
              >
                <template #prefix>
                  <LucideSearch class="w-4 text-ink-gray-5" />
                </template>
              </TextInput>
              <Select
                class="!w-fit"
                :options="[
                  { label: 'Name', value: 'full_name asc' },
                  { label: 'Last updated', value: 'modified desc' },
                  { label: 'Points', value: 'points' },
                  { label: 'System Role', value: 'role' },
                  { label: 'Custom Role', value: 'gp_role' },
                  { label: 'Posts', value: 'posts' },
                  { label: 'Replies', value: 'replies' },
                ]"
                v-model="orderBy"
              >
                <template #prefix>
                  <LucideArrowDownUp class="w-4 text-ink-gray-5" />
                </template>
              </Select>
              <Button variant="solid" @click="showSettingsDialog('Invites')">
                <template #prefix><LucideUserPlus2 class="w-4" /></template>
                Invite
              </Button>
            </div>
          </div>
          <div class="sm:hidden mt-4">
            <TextInput
              class="w-full"
              type="text"
              placeholder="Search"
              v-model="search"
              :debounce="500"
            >
              <template #prefix>
                <LucideSearch class="w-4 text-ink-gray-5" />
              </template>
            </TextInput>
          </div>
          <div class="mt-4 pb-16 -mx-3">
            <template v-for="user in people" :key="user.name">
              <router-link
                :to="{
                  name: 'PersonProfile',
                  params: {
                    personId: user.name,
                  },
                }"
                class="flex sm:rounded px-3 py-2 sm:h-15 sm:hover:bg-surface-gray-2 duration-150 active:bg-surface-gray-2 transition-colors"
                exact-active-class="!bg-surface-gray-2"
              >
                <div class="flex w-full sm:w-1/2 items-center">
                  <UserAvatarWithHover :user="user.user" size="2xl" />
                  <div class="ml-3 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <div class="text-base font-medium text-ink-gray-8">
                        {{ $user(user.user).full_name }}
                      </div>
                      <!-- <Badge v-if="user.role === 'Gameplan Admin'" theme="orange">Admin</Badge>
                      <Badge v-else-if="user.role !== 'Gameplan Admin'">Member</Badge> -->
                      <span
                        v-if="user.gp_role_title"
                        class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium text-ink-gray-7 border border-outline-gray-2"
                      >
                        {{ user.gp_role_title }}
                      </span>
                    </div>
                    <div
                      v-if="user.bio"
                      class="mt-1.5 min-w-0 overflow-hidden text-ellipsis whitespace-nowrap text-base text-ink-gray-5"
                    >
                      {{ user.bio }}
                    </div>
                    <div
                      class="sm:hidden mt-1.5 flex items-center space-x-1 text-base text-ink-gray-5"
                    >
                      <span>{{ user.discussions_count }} posts</span>
                      <span class="text-ink-gray-4">&middot;</span>
                      <span>{{ user.comments_count }} replies</span>
                      <template v-if="user.points">
                        <span class="text-ink-gray-4">&middot;</span>
                        <span>{{ user.points }} pts</span>
                      </template>
                    </div>
                  </div>
                </div>
                <div class="hidden sm:flex ml-auto items-center gap-6 text-base text-ink-gray-5">
                  <span class="w-24 text-right">{{ roleLabel(user.role) }}</span>
                  <router-link
                    class="w-20 text-right hover:text-ink-gray-8"
                    :to="{
                      name: 'PersonProfilePosts',
                      params: { personId: user.name },
                    }"
                    @click.prevent
                  >
                    {{ user.discussions_count }} posts
                  </router-link>
                  <router-link
                    class="w-24 text-right hover:text-ink-gray-8"
                    :to="{
                      name: 'PersonProfileReplies',
                      params: { personId: user.name },
                    }"
                    @click.prevent
                  >
                    {{ user.comments_count }} replies
                  </router-link>
                  <div class="w-16 text-right">
                    <span class="font-medium text-ink-gray-7">{{ user.points || 0 }}</span>
                    <span class="ml-1 text-ink-gray-4">pts</span>
                  </div>
                </div>
              </router-link>
              <div class="mx-2 border-b"></div>
            </template>
            <div class="p-3" v-if="$resources.profiles.hasNextPage">
              <Button
                @click="$resources.profiles.next()"
                :loading="$resources.profiles.list.loading"
              >
                Load more
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { Breadcrumbs, Badge, Input, Select, TextInput } from 'frappe-ui'
import PageHeader from '@/components/PageHeader.vue'
import { showSettingsDialog } from '@/components/Settings'
import UserAvatarWithHover from '@/components/UserAvatarWithHover.vue'

export default {
  name: 'People',
  props: ['person'],
  components: { Badge, Input, TextInput, Select, Breadcrumbs, PageHeader },
  data() {
    return {
      search: '',
      orderBy: 'modified desc',
    }
  },
  setup() {
    return {
      showSettingsDialog,
    }
  },
  resources: {
    profiles() {
      let orderBy = this.orderBy
      if (['posts', 'replies', 'points', 'role', 'gp_role'].includes(orderBy)) {
        orderBy = 'modified desc'
      }
      return {
        type: 'list',
        url: '/api/method/gameplan.gameplan.doctype.gp_user_profile.gp_user_profile.get_list',
        cache: ['People', orderBy],
        doctype: 'GP User Profile',
        filters: { enabled: 1 },
        fields: ['name', 'user', 'bio', 'modified', 'cover_image', 'cover_image_position', 'gp_role'],
        pageLength: 999,
        orderBy: this.orderBy,
        auto: true,
      }
    },
  },
  computed: {
    people() {
      if (!this.profiles.length) return []
      let myProfile = this.profiles.find((p) => p.user == this.$user().name)
      if (this.search) {
        return this.profiles.filter((p) => {
          return (
            p.full_name.toLowerCase().includes(this.search.toLowerCase()) ||
            p.email.toLowerCase().includes(this.search.toLowerCase())
          )
        })
      }

      let list = [myProfile, ...this.profiles.filter((p) => p != myProfile)].filter(Boolean)

      if (this.orderBy == 'posts') {
        list = list.sort((a, b) => b.discussions_count - a.discussions_count)
      } else if (this.orderBy == 'replies') {
        list = list.sort((a, b) => b.comments_count - a.comments_count)
      } else if (this.orderBy == 'points') {
        list = list.sort((a, b) => (b.points || 0) - (a.points || 0))
      } else if (this.orderBy == 'role') {
        const roleOrder = { 'Gameplan Admin': 0, 'Gameplan Member': 1, 'Gameplan Guest': 2 }
        list = list.sort((a, b) => (roleOrder[a.role] ?? 1) - (roleOrder[b.role] ?? 1))
      } else if (this.orderBy == 'gp_role') {
        list = list.sort((a, b) => (a.gp_role_title || 'zzz').localeCompare(b.gp_role_title || 'zzz'))
      }
      return list
    },
    profiles() {
      return (this.$resources.profiles.data || []).map((profile) => {
        return {
          ...profile,
          email: this.$user(profile.user).email,
          full_name: this.$user(profile.user).full_name,
          role: this.$user(profile.user).role,
          gp_role: profile.gp_role || '',
          gp_role_title: profile.gp_role_title || '',
        }
      })
    },
  },
  methods: {
    roleLabel(role) {
      const map = { 'Gameplan Admin': 'Admin', 'Gameplan Member': 'Member', 'Gameplan Guest': 'Guest' }
      return map[role] || role
    },
    coverImageUrl(url) {
      if (!url) return null
      if (url.startsWith('https://images.unsplash.com')) {
        return url + '&w=300&fit=crop&crop=entropy,faces,focalpoint'
      }
      return url
    },
  },
  pageMeta() {
    return {
      title: 'People',
    }
  },
}
</script>

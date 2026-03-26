import { computed } from 'vue'
import { useList } from 'frappe-ui'

interface GPRole {
  name: string
  title: string
  color?: string
  frappe_role?: string
}

interface UserProfileWithRole {
  name: string
  user: string
  gp_role: string
}

export const roles = useList<GPRole>({
  doctype: 'GP Role',
  fields: ['name', 'title', 'color', 'frappe_role'],
  orderBy: 'title asc',
  cacheKey: 'gp-roles',
  immediate: true,
})

export const roleProfiles = useList<UserProfileWithRole>({
  doctype: 'GP User Profile',
  fields: ['user', 'gp_role'],
  limit: 999,
  cacheKey: 'gp-role-profiles',
  immediate: true,
})

/** Returns a map of { roleName -> userEmail[] } */
export const roleUsersMap = computed<Record<string, string[]>>(() => {
  const map: Record<string, string[]> = {}
  for (const profile of roleProfiles.data || []) {
    if (!profile.gp_role || !profile.user) continue
    if (!map[profile.gp_role]) map[profile.gp_role] = []
    map[profile.gp_role].push(profile.user)
  }
  return map
})

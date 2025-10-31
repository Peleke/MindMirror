// Role and Domain constants to match backend enum values
export const ROLES = {
  COACH: 'coach',
  CLIENT: 'client', 
  ADMIN: 'admin',
} as const

export const DOMAINS = {
  PRACTICES: 'practices',
  MEALS: 'meals',
  HABITS: 'habits',
} as const

// Type helpers for TypeScript
export type Role = typeof ROLES[keyof typeof ROLES]
export type Domain = typeof DOMAINS[keyof typeof DOMAINS]

// Utility function to check if user has a specific role in a domain
export const hasRole = (userRoles: any[], role: Role, domain: Domain): boolean => {
  return userRoles?.some((userRole: any) => 
    userRole.role === role && userRole.domain === domain
  ) ?? false
}

// Specific helper for coach role in practices domain (commonly used)
export const isCoachInPractices = (userRoles: any[]): boolean => {
  // Backend returns GraphQL enum names (uppercase), not enum values (lowercase)
  return userRoles?.some((userRole: any) => 
    userRole.role === 'COACH' && userRole.domain === 'PRACTICES'
  ) ?? false
} 
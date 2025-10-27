import AsyncStorage from '@react-native-async-storage/async-storage'

export type RecentFood = {
  id_: string
  name: string
  servingSize?: number | undefined
  servingUnit?: string | undefined
  calories?: number | undefined
  updatedAt: number
}

const foodsKey = (userId: string) => `mm_recents_foods_${userId}`

export async function getRecentFoods(userId: string, max: number = 25): Promise<RecentFood[]> {
  if (!userId) return []
  try {
    const raw = await AsyncStorage.getItem(foodsKey(userId))
    const list: RecentFood[] = raw ? JSON.parse(raw) : []
    return Array.isArray(list) ? list.slice(0, max) : []
  } catch {
    return []
  }
}

export async function addRecentFood(userId: string, item: { id_: string; name: string; servingSize?: number | undefined; servingUnit?: string | undefined; calories?: number | undefined }) {
  if (!userId || !item?.id_) return
  try {
    const now = Date.now()
    const existing = await getRecentFoods(userId, 100)
    const filtered = existing.filter(f => f.id_ !== item.id_)
    const next: RecentFood = { id_: item.id_, name: item.name, servingSize: item.servingSize, servingUnit: item.servingUnit, calories: item.calories, updatedAt: now }
    const merged = [next, ...filtered].slice(0, 50)
    await AsyncStorage.setItem(foodsKey(userId), JSON.stringify(merged))
  } catch {
    // noop
  }
} 
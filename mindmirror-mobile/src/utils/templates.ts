import AsyncStorage from '@react-native-async-storage/async-storage'

export type TemplateFoodSnapshot = {
  id_: string
  name: string
  servingUnit?: string | undefined
  servingSize?: number | undefined
  calories?: number | undefined
  protein?: number | undefined
  carbohydrates?: number | undefined
  fat?: number | undefined
}

export type MealTemplateItem = {
  foodItem: TemplateFoodSnapshot
  quantity: number
  servingUnit: string
}

export type MealTemplate = {
  name: string
  items: MealTemplateItem[]
  uses: number
  updatedAt: number
}

const templatesKey = (userId: string) => `mm_templates_${userId}`

export async function getTemplates(userId: string): Promise<MealTemplate[]> {
  if (!userId) return []
  try {
    const raw = await AsyncStorage.getItem(templatesKey(userId))
    const list: MealTemplate[] = raw ? JSON.parse(raw) : []
    return Array.isArray(list) ? list : []
  } catch {
    return []
  }
}

export async function upsertTemplate(userId: string, tpl: MealTemplate) {
  if (!userId || !tpl?.name) return
  try {
    const existing = await getTemplates(userId)
    const nameKey = tpl.name.trim().toLowerCase()
    const filtered = existing.filter(t => t.name.trim().toLowerCase() !== nameKey)
    const merged = [{ ...tpl, updatedAt: Date.now() }, ...filtered].slice(0, 100)
    await AsyncStorage.setItem(templatesKey(userId), JSON.stringify(merged))
  } catch {
    // noop
  }
}

export async function recordMealAsTemplate(userId: string, name: string, items: MealTemplateItem[]) {
  const existing = await getTemplates(userId)
  const nameKey = (name || '').trim().toLowerCase()
  const current = existing.find(t => t.name.trim().toLowerCase() === nameKey)
  const uses = (current?.uses || 0) + 1
  await upsertTemplate(userId, { name, items, uses, updatedAt: Date.now() })
}

export async function findMatchingTemplates(userId: string, term: string, limit: number = 5): Promise<MealTemplate[]> {
  const list = await getTemplates(userId)
  const q = (term || '').trim().toLowerCase()
  if (!q) return []
  return list
    .filter(t => t.name.toLowerCase().includes(q))
    .sort((a, b) => (b.uses || 0) - (a.uses || 0) || b.updatedAt - a.updatedAt)
    .slice(0, limit)
} 
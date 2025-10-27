import React from 'react'

export type ThemeVariantId = 'autumnHarvest' | 'classic' | 'brightGreens' | 'freshGreens'

export const ThemeVariants: { id: ThemeVariantId; label: string; description?: string }[] = [
  { id: 'autumnHarvest', label: 'Autumn Harvest' },
  { id: 'brightGreens', label: 'Bright Greens' },
  { id: 'freshGreens', label: 'Fresh Greens' },
  { id: 'classic', label: 'Classic (Pre‑polish)' },
]

type ThemeVariantContextType = {
  themeId: ThemeVariantId
  setThemeId: (id: ThemeVariantId) => void
  toggle: () => void
}

const ThemeVariantContext = React.createContext<ThemeVariantContextType>({
  themeId: 'classic',
  setThemeId: () => {},
  toggle: () => {},
})

export function ThemeVariantProvider({ children }: { children: React.ReactNode }) {
  const [themeId, setThemeId] = React.useState<ThemeVariantId>('classic')
  const toggle = React.useCallback(() => {
    setThemeId((prev) => (prev === 'autumnHarvest' ? 'classic' : 'autumnHarvest'))
  }, [])
  const value = React.useMemo(() => ({ themeId, setThemeId, toggle }), [themeId, toggle])
  return <ThemeVariantContext.Provider value={value}>{children}</ThemeVariantContext.Provider>
}

export function useThemeVariant() {
  return React.useContext(ThemeVariantContext)
} 
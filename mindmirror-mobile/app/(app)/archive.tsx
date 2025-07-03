import { useState } from 'react'
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useRouter } from 'expo-router'
import { useNavigation } from '@react-navigation/native'
import { Ionicons } from '@expo/vector-icons'

type JournalType = 'all' | 'gratitude' | 'reflection' | 'freeform'

interface JournalEntry {
  id: string
  type: JournalType
  title: string
  content: string
  date: string
}

// Mock data for now
const mockEntries: JournalEntry[] = [
  {
    id: '1',
    type: 'gratitude',
    title: 'Grateful for today',
    content: 'I am grateful for the beautiful weather and the opportunity to spend time with family...',
    date: '2024-01-15',
  },
  {
    id: '2',
    type: 'reflection',
    title: 'Daily reflection',
    content: 'Today was productive. I accomplished my main goals and learned something new...',
    date: '2024-01-14',
  },
  {
    id: '3',
    type: 'freeform',
    title: 'Random thoughts',
    content: 'Sometimes I wonder about the nature of consciousness and how we perceive reality...',
    date: '2024-01-13',
  },
  {
    id: '4',
    type: 'gratitude',
    title: 'Thankful for health',
    content: 'I am grateful for my health and the ability to move freely...',
    date: '2024-01-12',
  },
]

const typeOptions: { value: JournalType; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'gratitude', label: 'Gratitude' },
  { value: 'reflection', label: 'Reflection' },
  { value: 'freeform', label: 'Freeform' },
]

export default function ArchiveScreen() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedType, setSelectedType] = useState<JournalType>('all')
  const router = useRouter()
  const navigation = useNavigation()

  const handleMenuPress = () => {
    ;(navigation as any).openDrawer()
  }

  const filteredEntries = mockEntries.filter(entry => {
    const matchesSearch = entry.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         entry.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = selectedType === 'all' || entry.type === selectedType
    return matchesSearch && matchesType
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      year: 'numeric' 
    })
  }

  const getTypeIcon = (type: JournalType) => {
    switch (type) {
      case 'gratitude':
        return 'heart'
      case 'reflection':
        return 'bulb'
      case 'freeform':
        return 'create'
      default:
        return 'document'
    }
  }

  const getTypeColor = (type: JournalType) => {
    switch (type) {
      case 'gratitude':
        return colors.primary[100]
      case 'reflection':
        return colors.secondary[100]
      case 'freeform':
        return colors.primary[200]
      default:
        return colors.gray[100]
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity style={styles.menuButton} onPress={handleMenuPress}>
          <Ionicons name="menu" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <Text style={styles.appBarTitle}>Archive</Text>
        
        <TouchableOpacity 
          style={styles.profileButton}
          onPress={() => router.push('/(app)/profile')}
        >
          <Ionicons name="person-circle" size={28} color={colors.text.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView}>
        {/* Search Section */}
        <View style={styles.searchSection}>
          <View style={styles.searchBar}>
            <Ionicons name="search" size={20} color={colors.text.secondary} />
            <TextInput
              style={styles.searchInput}
              placeholder="Search journal entries..."
              value={searchQuery}
              onChangeText={setSearchQuery}
              placeholderTextColor={colors.text.secondary}
            />
          </View>

          {/* Type Filter */}
          <ScrollView 
            horizontal 
            showsHorizontalScrollIndicator={false}
            style={styles.filterContainer}
          >
            {typeOptions.map((option) => (
              <TouchableOpacity
                key={option.value}
                style={[
                  styles.filterChip,
                  selectedType === option.value && styles.filterChipActive
                ]}
                onPress={() => setSelectedType(option.value)}
              >
                <Text style={[
                  styles.filterChipText,
                  selectedType === option.value && styles.filterChipTextActive
                ]}>
                  {option.label}
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>

        {/* Divider */}
        <View style={styles.divider} />

        {/* Journal Entries */}
        <View style={styles.entriesContainer}>
          {filteredEntries.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="document-text" size={48} color={colors.text.tertiary} />
              <Text style={styles.emptyStateTitle}>No entries found</Text>
              <Text style={styles.emptyStateSubtitle}>
                Try adjusting your search or filter criteria
              </Text>
            </View>
          ) : (
            filteredEntries.map((entry) => (
              <Card key={entry.id} style={styles.entryCard}>
                <View style={styles.entryHeader}>
                  <View style={styles.entryTypeContainer}>
                    <View style={[
                      styles.entryTypeIcon,
                      { backgroundColor: getTypeColor(entry.type) }
                    ]}>
                      <Ionicons 
                        name={getTypeIcon(entry.type) as any} 
                        size={16} 
                        color={colors.primary[600]} 
                      />
                    </View>
                    <Text style={styles.entryType}>
                      {entry.type.charAt(0).toUpperCase() + entry.type.slice(1)}
                    </Text>
                  </View>
                  <Text style={styles.entryDate}>{formatDate(entry.date)}</Text>
                </View>
                
                <Text style={styles.entryTitle}>{entry.title}</Text>
                <Text style={styles.entryContent} numberOfLines={3}>
                  {entry.content}
                </Text>
              </Card>
            ))
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background.primary,
  },
  appBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border.light,
    backgroundColor: colors.background.primary,
  },
  menuButton: {
    padding: spacing.sm,
  },
  appBarTitle: {
    fontSize: typography.sizes.xl,
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
  },
  profileButton: {
    padding: spacing.sm,
  },
  scrollView: {
    flex: 1,
  },
  searchSection: {
    padding: spacing.lg,
  },
  searchBar: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: colors.background.secondary,
    borderRadius: 12,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    marginBottom: spacing.md,
  },
  searchInput: {
    flex: 1,
    marginLeft: spacing.sm,
    fontSize: typography.sizes.base,
    color: colors.text.primary,
  },
  filterContainer: {
    marginBottom: spacing.sg,
  },
  filterChip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    borderRadius: 20,
    backgroundColor: colors.background.secondary,
    marginRight: spacing.sm,
    borderWidth: 1,
    borderColor: colors.border.light,
  },
  filterChipActive: {
    backgroundColor: colors.primary[600],
    borderColor: colors.primary[600],
  },
  filterChipText: {
    fontSize: typography.sizes.sm,
    color: colors.text.secondary,
    fontWeight: typography.weights.medium,
  },
  filterChipTextActive: {
    color: colors.text.inverse,
  },
  divider: {
    height: 1,
    backgroundColor: colors.border.light,
    marginHorizontal: spacing.lg,
  },
  entriesContainer: {
    padding: spacing.lg,
  },
  entryCard: {
    marginBottom: spacing.md,
    padding: spacing.lg,
  },
  entryHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  entryTypeContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  entryTypeIcon: {
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing.xs,
  },
  entryType: {
    fontSize: typography.sizes.sm,
    color: colors.text.secondary,
    fontWeight: typography.weights.medium,
  },
  entryDate: {
    fontSize: typography.sizes.sm,
    color: colors.text.tertiary,
  },
  entryTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  entryContent: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    lineHeight: 20,
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: spacing.xl * 2,
  },
  emptyStateTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginTop: spacing.md,
    marginBottom: spacing.xs,
  },
  emptyStateSubtitle: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    textAlign: 'center',
  },
}) 
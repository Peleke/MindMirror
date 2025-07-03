import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { useRouter } from 'expo-router'
import { Ionicons } from '@expo/vector-icons'
import { Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'

const JOURNAL_TYPES = [
  {
    id: 'gratitude',
    title: 'Gratitude Journal',
    description: 'Reflect on what you\'re grateful for today',
    icon: 'heart',
    color: colors.primary[100],
    route: '/journal/gratitude'
  },
  {
    id: 'reflection',
    title: 'Daily Reflection',
    description: 'Look back on your day and insights',
    icon: 'bulb',
    color: colors.secondary[100],
    route: '/journal/reflection'
  },
  {
    id: 'freeform',
    title: 'Freeform Writing',
    description: 'Express your thoughts freely',
    icon: 'create',
    color: colors.primary[200],
    route: '/journal/freeform'
  }
]

export default function JournalScreen() {
  const router = useRouter()

  const handleJournalPress = (route: string) => {
    router.push(route as any)
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* App Bar */}
      <View style={styles.appBar}>
        <TouchableOpacity style={styles.menuButton}>
          <Ionicons name="menu" size={24} color={colors.text.primary} />
        </TouchableOpacity>
        
        <Text style={styles.appBarTitle}>Journal</Text>
        
        <TouchableOpacity 
          style={styles.profileButton}
          onPress={() => router.push('/profile')}
        >
          <Ionicons name="person-circle" size={28} color={colors.text.primary} />
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Start Your Journal</Text>
          <Text style={styles.subtitle}>Choose the type of entry you'd like to create</Text>
        </View>
        
        <View style={styles.content}>
          {JOURNAL_TYPES.map((journalType) => (
            <TouchableOpacity
              key={journalType.id}
              onPress={() => handleJournalPress(journalType.route)}
              style={styles.cardTouchable}
            >
              <Card style={{ ...styles.card, backgroundColor: journalType.color }}>
                <View style={styles.cardHeader}>
                  <Ionicons 
                    name={journalType.icon as any} 
                    size={32} 
                    color={colors.primary[600]} 
                  />
                </View>
                <Text style={styles.cardTitle}>{journalType.title}</Text>
                <Text style={styles.cardDescription}>{journalType.description}</Text>
                <View style={styles.cardFooter}>
                  <Ionicons name="arrow-forward" size={20} color={colors.text.secondary} />
                </View>
              </Card>
            </TouchableOpacity>
          ))}
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
  header: {
    padding: spacing.lg,
    paddingBottom: spacing.md,
  },
  title: {
    fontSize: typography.sizes['2xl'],
    fontWeight: typography.weights.bold,
    color: colors.text.primary,
    marginBottom: spacing.xs,
  },
  subtitle: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
  },
  content: {
    padding: spacing.lg,
    paddingTop: 0,
  },
  cardTouchable: {
    marginBottom: spacing.md,
  },
  card: {
    padding: spacing.lg,
    minHeight: 120,
  },
  cardHeader: {
    marginBottom: spacing.md,
  },
  cardTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginBottom: spacing.sm,
  },
  cardDescription: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    lineHeight: 22,
    flex: 1,
  },
  cardFooter: {
    marginTop: spacing.md,
    alignItems: 'flex-end',
  },
}) 
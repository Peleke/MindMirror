
import { View, Text, StyleSheet, ScrollView, Alert } from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { Button, Card } from '@/components/common'
import { colors, spacing, typography } from '@/theme'
import { useAuth } from '@/features/auth/context/AuthContext'
import { auth } from '@/services/supabase/client'

export default function ProfileScreen() {
  const { user } = useAuth()

  const handleSignOut = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Sign Out', 
          style: 'destructive', 
          onPress: async () => {
            const { error } = await auth.signOut()
            if (error) {
              Alert.alert('Error', 'Failed to sign out')
            }
          }
        },
      ]
    )
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        <View style={styles.header}>
          <Text style={styles.title}>Profile</Text>
          <Text style={styles.subtitle}>Manage your account</Text>
        </View>
        
        <View style={styles.content}>
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Account Info</Text>
            <Text style={styles.userEmail}>{user?.email}</Text>
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Account Settings</Text>
            <Button
              title="Edit Profile"
              onPress={() => console.log('Edit profile')}
              variant="outline"
              style={styles.button}
            />
            <Button
              title="Change Password"
              onPress={() => console.log('Change password')}
              variant="outline"
              style={styles.button}
            />
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Preferences</Text>
            <Button
              title="Notification Settings"
              onPress={() => console.log('Notification settings')}
              variant="outline"
              style={styles.button}
            />
            <Button
              title="Privacy Settings"
              onPress={() => console.log('Privacy settings')}
              variant="outline"
              style={styles.button}
            />
          </Card>
          
          <Card style={styles.card}>
            <Text style={styles.cardTitle}>Support</Text>
            <Button
              title="Help & FAQ"
              onPress={() => console.log('Help & FAQ')}
              variant="outline"
              style={styles.button}
            />
            <Button
              title="Contact Support"
              onPress={() => console.log('Contact support')}
              variant="outline"
              style={styles.button}
            />
          </Card>
          
          <Button
            title="Sign Out"
            onPress={handleSignOut}
            variant="ghost"
            style={styles.signOutButton}
          />
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
  card: {
    marginBottom: spacing.md,
  },
  cardTitle: {
    fontSize: typography.sizes.lg,
    fontWeight: typography.weights.semibold,
    color: colors.text.primary,
    marginBottom: spacing.md,
  },
  button: {
    marginBottom: spacing.sm,
  },
  signOutButton: {
    marginTop: spacing.lg,
  },
  userEmail: {
    fontSize: typography.sizes.base,
    color: colors.text.secondary,
    fontFamily: typography.fonts.regular,
  },
}) 
import React from 'react'
import { View, Text, ActivityIndicator, ViewStyle } from 'react-native'
import { colors, typography, spacing } from '@/theme'
import { styles } from './Loading.styles'

export interface LoadingProps {
  size?: 'small' | 'large'
  color?: string
  text?: string
  style?: ViewStyle
  testID?: string
}

export const Loading: React.FC<LoadingProps> = ({
  size = 'large',
  color = colors.primary[600],
  text,
  style,
  testID,
}) => {
  return (
    <View style={[styles.container, style]} testID={testID}>
      <ActivityIndicator size={size} color={color} />
      {text && <Text style={styles.text}>{text}</Text>}
    </View>
  )
}

export const LoadingScreen: React.FC<LoadingProps> = (props) => {
  return (
    <View style={styles.screen}>
      <Loading {...props} />
    </View>
  )
} 
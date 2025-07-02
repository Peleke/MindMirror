import React from 'react'
import { View, ViewStyle } from 'react-native'
import { colors, spacing, shadows } from '@/theme'
import { styles } from './Card.styles'

export interface CardProps {
  children: React.ReactNode
  variant?: 'default' | 'elevated' | 'outlined'
  padding?: 'none' | 'small' | 'medium' | 'large'
  style?: ViewStyle
  testID?: string
}

export const Card: React.FC<CardProps> = ({
  children,
  variant = 'default',
  padding = 'medium',
  style,
  testID,
}) => {
  const cardStyle = [
    styles.base,
    styles[variant],
    styles[`padding${padding.charAt(0).toUpperCase() + padding.slice(1)}`],
    style,
  ]

  return (
    <View style={cardStyle} testID={testID}>
      {children}
    </View>
  )
} 
import React, { forwardRef } from 'react'
import {
  TextInput,
  View,
  Text,
  TextInputProps,
  ViewStyle,
  TextStyle,
} from 'react-native'
import { colors, typography, spacing, shadows } from '@/theme'
import { styles } from './Input.styles'

export interface InputProps extends Omit<TextInputProps, 'style'> {
  label?: string
  error?: string
  variant?: 'default' | 'outlined' | 'filled'
  size?: 'small' | 'medium' | 'large'
  style?: ViewStyle
  inputStyle?: TextStyle
  testID?: string
}

export const Input = forwardRef<TextInput, InputProps>(
  (
    {
      label,
      error,
      variant = 'default',
      size = 'medium',
      style,
      inputStyle,
      testID,
      ...props
    },
    ref
  ) => {
    const containerStyle = [
      styles.container,
      styles[variant],
      styles[size],
      error && styles.error,
      style,
    ]

    const inputStyleCombined = [
      styles.input,
      styles[`${variant}Input`],
      styles[`${size}Input`],
      error && styles.errorInput,
      inputStyle,
    ]

    return (
      <View style={containerStyle}>
        {label && <Text style={styles.label}>{label}</Text>}
        <TextInput
          ref={ref}
          style={inputStyleCombined}
          placeholderTextColor={colors.text.tertiary}
          testID={testID}
          {...props}
        />
        {error && <Text style={styles.errorText}>{error}</Text>}
      </View>
    )
  }
)

Input.displayName = 'Input' 
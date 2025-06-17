'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Brain, Mail, Lock, Eye, EyeOff, ArrowLeft, Check, AlertCircle } from 'lucide-react'
import { cn } from '../../../lib/utils'
import { auth } from '../../../lib/supabase'
import { signUpSchema, type SignUpFormData } from '../../../lib/validations'

const FormField = ({ 
  label, 
  error, 
  children, 
  required = false 
}: { 
  label: string
  error?: string
  children: React.ReactNode
  required?: boolean
}) => (
  <div className="space-y-2">
    <label className="block text-sm font-semibold text-gray-700">
      {label}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
    {children}
    {error && (
      <div className="flex items-center gap-2 text-red-600 text-sm">
        <AlertCircle className="w-4 h-4" />
        <span>{error}</span>
      </div>
    )}
  </div>
)

const PasswordInput = React.forwardRef<HTMLInputElement, { 
  placeholder: string
  error?: boolean
  disabled?: boolean
  [key: string]: any
}>(({ placeholder, error, disabled = false, ...props }, ref) => {
  const [showPassword, setShowPassword] = useState(false)

  return (
    <div className="relative">
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
        <Lock className="w-5 h-5" />
      </div>
      <input
        ref={ref}
        type={showPassword ? 'text' : 'password'}
        placeholder={placeholder}
        disabled={disabled}
        className={cn(
          "w-full pl-10 pr-12 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-200 text-gray-900 placeholder-gray-500",
          error && "border-red-300 focus:border-red-500 focus:ring-red-500/20",
          disabled && "bg-gray-50 cursor-not-allowed opacity-50"
        )}
        {...props}
      />
      <button
        type="button"
        onClick={() => setShowPassword(!showPassword)}
        disabled={disabled}
        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors disabled:cursor-not-allowed"
      >
        {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
      </button>
    </div>
  )
})

export default function SignUpPage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [submitError, setSubmitError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: 'onBlur'
  })

  const password = watch('password')
  const confirmPassword = watch('confirmPassword')

  const onSubmit = async (data: SignUpFormData) => {
    setIsSubmitting(true)
    setSubmitError('')
    setSuccessMessage('')

    try {
      const { data: authData, error } = await auth.signUp(data.email, data.password)

      if (error) {
        if (error.message.includes('already registered')) {
          setSubmitError('An account with this email already exists. Try signing in instead.')
        } else {
          setSubmitError(error.message)
        }
        return
      }

      if (authData.user && !authData.session) {
        // Email confirmation required
        setSuccessMessage(
          'Success! Please check your email and click the confirmation link to complete your signup.'
        )
      } else {
        // Immediate sign in (if email confirmation is disabled)
        router.push('/dashboard')
      }
    } catch (error) {
      setSubmitError('An unexpected error occurred. Please try again.')
      console.error('Signup error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const getPasswordStrength = (password: string) => {
    if (!password) return { strength: 0, label: '', color: '' }
    
    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z\d]/.test(password)) strength++

    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong']
    const colors = ['', 'bg-red-400', 'bg-orange-400', 'bg-yellow-400', 'bg-green-400', 'bg-green-500']
    
    return {
      strength,
      label: labels[strength],
      color: colors[strength]
    }
  }

  const passwordStrength = getPasswordStrength(password || '')

  if (successMessage) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-3xl shadow-xl p-8 text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <Check className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Check Your Email!</h1>
            <p className="text-gray-600 mb-6 leading-relaxed">{successMessage}</p>
            <Link
              href="/"
              className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-3 mb-6 group">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              MindMirror
            </span>
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
          <p className="text-gray-600">Start your journey to deeper thinking</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-3xl shadow-xl p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Email Field */}
            <FormField label="Email Address" error={errors.email?.message} required>
              <div className="relative">
                <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="email"
                  placeholder="Enter your email"
                  disabled={isSubmitting}
                  className={cn(
                    "w-full pl-10 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-200 text-gray-900 placeholder-gray-500",
                    errors.email && "border-red-300 focus:border-red-500 focus:ring-red-500/20",
                    isSubmitting && "bg-gray-50 cursor-not-allowed opacity-50"
                  )}
                  {...register('email')}
                />
              </div>
            </FormField>

            {/* Password Field */}
            <FormField label="Password" error={errors.password?.message} required>
              <PasswordInput
                placeholder="Create a strong password"
                error={!!errors.password}
                disabled={isSubmitting}
                {...register('password')}
              />
              {password && (
                <div className="mt-2">
                  <div className="flex items-center gap-2 mb-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className={cn("h-2 rounded-full transition-all duration-300", passwordStrength.color)}
                        style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600">{passwordStrength.label}</span>
                  </div>
                </div>
              )}
            </FormField>

            {/* Confirm Password Field */}
            <FormField label="Confirm Password" error={errors.confirmPassword?.message} required>
              <PasswordInput
                placeholder="Confirm your password"
                error={!!errors.confirmPassword}
                disabled={isSubmitting}
                {...register('confirmPassword')}
              />
            </FormField>

            {/* Submit Error */}
            {submitError && (
              <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-xl border border-red-200">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <span className="text-sm font-medium">{submitError}</span>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isSubmitting}
              className={cn(
                "w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300",
                "focus:ring-4 focus:ring-blue-500/20 outline-none",
                "disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:hover:shadow-lg"
              )}
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-6 pt-6 border-t border-gray-100 text-center">
            <p className="text-gray-600">
              Already have an account?{' '}
              <Link 
                href="/login" 
                className="text-blue-600 hover:text-blue-700 font-semibold transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>

        {/* Back to Home */}
        <div className="text-center mt-6">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>
      </div>
    </div>
  )
} 
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowRight, Brain, MessageSquare, BookOpen, Sparkles, Eye, Lightbulb, Target, Shield, Check } from 'lucide-react';
import { cn } from '../../lib/utils';

const EmailCaptureForm = ({ size = 'large', className = '' }: { size?: 'default' | 'large', className?: string }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');

    try {
      // Call the existing landing page API endpoint
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email,
          source: 'homepage_newsletter' 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to subscribe');
      }

      setIsSubmitted(true);
      setEmail('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
  return (
      <div className={cn('text-center', className)}>
        <div className="inline-flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-50 to-emerald-50 text-green-800 rounded-2xl border border-green-200/50 shadow-sm">
          <Check className="w-5 h-5" />
          <span className="font-semibold">Thanks! You're subscribed to our newsletter.</span>
        </div>
      </div>
    );
  }

  const inputClass = size === 'large' 
    ? 'px-6 py-4 text-lg border-2 border-gray-200 rounded-2xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-300 flex-1 bg-white shadow-sm'
    : 'px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all duration-200 flex-1 bg-white';
  
  const buttonClass = size === 'large'
    ? 'px-8 py-4 text-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 focus:ring-4 focus:ring-blue-500/20 outline-none transition-all duration-300 font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none'
    : 'px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all duration-200 font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <div className={className}>
      <form onSubmit={handleSubmit} className="flex gap-4 max-w-lg mx-auto">
              <input
                type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email address"
                required
          disabled={isSubmitting}
          className={inputClass}
              />
              <button
                type="submit"
          disabled={isSubmitting || !email}
          className={buttonClass}
        >
          {isSubmitting ? (
            <div className="flex items-center gap-2">
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Subscribing...
            </div>
          ) : (
            <div className="flex items-center gap-2">
              Subscribe
              <ArrowRight className="w-5 h-5" />
            </div>
          )}
        </button>
      </form>
      {error && (
        <p className="text-red-600 text-sm mt-3 text-center font-medium">{error}</p>
      )}
                </div>
  );
};

const FloatingElements = () => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      <div className="absolute top-20 left-10 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-purple-400/20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute top-40 right-20 w-40 h-40 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
      <div className="absolute bottom-20 left-20 w-36 h-36 bg-gradient-to-br from-cyan-400/20 to-blue-400/20 rounded-full blur-3xl animate-pulse delay-500" />
              </div>
  );
};

const FeatureCard = ({ icon: Icon, title, description, gradient }: {
  icon: React.ElementType;
  title: string;
  description: string;
  gradient: string;
}) => (
  <div className="group relative p-8 bg-white rounded-3xl border border-gray-100 shadow-lg hover:shadow-2xl transition-all duration-500 hover:-translate-y-2">
    <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-5 rounded-3xl transition-opacity duration-500" style={{ background: gradient }} />
    <div className={cn(
      "w-16 h-16 rounded-2xl flex items-center justify-center mb-6 shadow-lg transition-transform duration-500 group-hover:scale-110",
      `bg-gradient-to-br ${gradient}`
    )}>
      <Icon className="w-8 h-8 text-white" />
                </div>
    <h3 className="text-xl font-bold text-gray-900 mb-3">{title}</h3>
    <p className="text-gray-600 leading-relaxed">{description}</p>
              </div>
);

export default function HomePage() {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const testimonials = [
    {
      text: "MindMirror doesn't just store my thoughts—it helps me think better. It's like having a conversation with the wisest version of myself.",
      author: "Sarah Chen",
      role: "Product Designer at Linear"
    },
    {
      text: "Finally, a journal that actually helps me grow. The AI insights have changed how I process my experiences completely.",
      author: "Marcus Rodriguez", 
      role: "Engineering Manager at Stripe"
    },
    {
      text: "I've tried every journaling app. This is different. It's not just recording—it's actively helping me become more self-aware.",
      author: "Dr. Emily Watson",
      role: "Clinical Psychologist"
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    return () => clearInterval(timer);
  }, [testimonials.length]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50/30 overflow-hidden">
      {/* Floating Background Elements */}
      <FloatingElements />

      {/* Header */}
      <header className="relative z-50 px-4 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              MindMirror
            </span>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="px-6 py-3 text-gray-700 hover:text-gray-900 font-semibold transition-colors duration-200"
            >
              Sign In
            </Link>
            <Link
              href="/signup"
              className="px-6 py-3 bg-gray-900 text-white rounded-xl font-semibold hover:bg-gray-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Sign Up
            </Link>
          </div>
            </div>
      </header>

      {/* Hero Section */}
      <section className="relative px-4 pt-20 pb-32">
        <div className="max-w-6xl mx-auto text-center">
          {/* Power User Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-50 to-purple-50 text-blue-800 rounded-full border border-blue-200/50 font-semibold text-sm mb-8 shadow-sm">
            <Sparkles className="w-4 h-4" />
            For people who think deeply
              </div>

          {/* Main Headline */}
          <h1 className="text-6xl sm:text-7xl md:text-8xl font-black tracking-tight text-gray-900 leading-none mb-8">
            Your journal
            <span className="block bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
              thinks back
            </span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl sm:text-2xl text-gray-600 max-w-4xl mx-auto mb-6 leading-relaxed font-medium">
            Most journals just store your thoughts. MindMirror reflects them back, 
            connects patterns you missed, and asks the questions that matter.
          </p>

          <p className="text-lg text-gray-500 max-w-3xl mx-auto mb-12">
            The first self-aware journaling companion for people who refuse to settle for surface-level thinking.
          </p>

          {/* Primary CTA */}
          <div className="mb-6">
            <Link
              href="/signup"
              className="inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl font-bold text-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-300 focus:ring-4 focus:ring-blue-500/20 outline-none"
            >
              Get Started Free
              <ArrowRight className="w-6 h-6" />
            </Link>
          </div>

          <p className="text-sm text-gray-500 mb-16">
            Join 2,847 deep thinkers • No credit card required
          </p>

          {/* Social Proof Preview */}
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 max-w-2xl mx-auto border border-gray-200/50 shadow-xl">
            <div className="flex items-center justify-center gap-1 mb-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="w-6 h-6 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center">
                  <span className="text-white text-xs font-bold">★</span>
                </div>
              ))}
            </div>
            <blockquote className="text-lg text-gray-700 mb-4 leading-relaxed italic">
              "{testimonials[currentTestimonial].text}"
            </blockquote>
            <div className="text-gray-600">
              <div className="font-semibold">{testimonials[currentTestimonial].author}</div>
              <div className="text-sm">{testimonials[currentTestimonial].role}</div>
              </div>
              </div>
          </div>
        </section>

      {/* Features Grid */}
      <section className="relative px-4 pb-32">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl sm:text-5xl font-bold text-gray-900 mb-6">
              Why settle for a passive journal?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              MindMirror uses advanced AI to turn your thoughts into insights, 
              patterns into breakthroughs, and questions into clarity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={MessageSquare}
              title="Conversational Reflection"
              description="Your journal doesn't just listen—it responds. Ask questions, explore ideas, and get insights tailored to your thinking patterns."
              gradient="from-blue-500 to-blue-700"
            />
            <FeatureCard
              icon={Eye}
              title="Pattern Recognition"
              description="See connections between your thoughts across time. MindMirror identifies recurring themes and blind spots you might miss."
              gradient="from-purple-500 to-purple-700"
            />
            <FeatureCard
              icon={Lightbulb}
              title="Intelligent Prompts"
              description="Get personalized questions that dig deeper into your experiences. Not generic prompts—questions designed for you."
              gradient="from-cyan-500 to-cyan-700"
            />
            <FeatureCard
              icon={Target}
              title="Growth Tracking"
              description="Watch your thinking evolve over time. Bi-weekly reviews show your progress and suggest areas for development."
              gradient="from-emerald-500 to-emerald-700"
            />
            <FeatureCard
              icon={Shield}
              title="Private & Secure"
              description="Your thoughts stay yours. Advanced encryption and privacy-first architecture ensure your journal remains confidential."
              gradient="from-red-500 to-red-700"
            />
            <FeatureCard
              icon={BookOpen}
              title="Knowledge Integration"
              description="Upload books, articles, and documents. MindMirror connects your personal insights with external knowledge."
              gradient="from-orange-500 to-orange-700"
            />
          </div>
          </div>
        </section>

      {/* Final CTA Section */}
      <section className="relative px-4 pb-20">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-3xl p-12 text-white shadow-2xl">
            <h2 className="text-4xl sm:text-5xl font-bold mb-6">
              Stay in the loop
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Get insights on deep thinking, journaling techniques, and be the first to know 
              when MindMirror launches new features.
            </p>
            <EmailCaptureForm size="large" className="mb-6" />
            <p className="text-gray-400 text-sm">
              Weekly insights, no spam. Unsubscribe anytime.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative px-4 py-12 border-t border-gray-200">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900">MindMirror</span>
          </div>
          <p className="text-gray-600 mb-6">
            Self-aware software for self-aware people.
          </p>
          <p className="text-sm text-gray-500">
            Built with ❤️ by the <Link href="https://swae.io" className="text-blue-600 hover:text-blue-700 font-semibold">Swae OS</Link> team
          </p>
        </div>
      </footer>
    </div>
  );
}
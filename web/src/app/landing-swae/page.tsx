'use client';

import React from 'react';
import { Brain, HeartHandshake, BarChart3, Activity, Soup, Dumbbell, Moon, Shield, CheckCircle2 } from 'lucide-react';

export default function SwaeLanding() {
  return (
    <div className="min-h-screen bg-white text-gray-900">
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-gradient-to-br from-gray-900 to-gray-700 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="ml-3 text-xl font-semibold tracking-tight">Swae OS</span>
          </div>
          <a href="#join" className="px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors">Join the movement</a>
        </div>
      </header>

      <main className="pt-20">
        <section className="px-4 py-20 bg-gradient-to-b from-gray-50 to-white">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-4">The operating system for your embodied life</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10">Swae is a suite of coordinated services—habits, journaling, meals, movement, sleep—that help you change what matters. Start small. Grow steadily. Own your data.</p>
          </div>
        </section>

        <section id="features" className="px-4 py-16">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">
            <ValueCard icon={<CheckCircle2 className="w-6 h-6 text-emerald-700" />} title="Habits & Lessons" desc="Bite‑sized daily practice with streaks, adherence rings, and timely prompts. Featured: Unf*ck Your Eating—our flagship, user‑favorite program." />
            <ValueCard icon={<HeartHandshake className="w-6 h-6 text-indigo-700" />} title="Journaling" desc="Reflect with structure or free‑form; AI helps surface patterns and next steps." />
            <ValueCard icon={<Soup className="w-6 h-6 text-orange-600" />} title="Meals (soon)" desc="Track meals simply. Add optional computer‑vision estimates for macros/calories." />
            <ValueCard icon={<Dumbbell className="w-6 h-6 text-fuchsia-700" />} title="Movement (soon)" desc="Workout programs powered by a movement graph—progressions, regressions, substitutions." />
            <ValueCard icon={<Moon className="w-6 h-6 text-blue-700" />} title="Sleep (later)" desc="Import Apple Health / Fitbit; adapt your plan based on readiness and rest." />
            <ValueCard icon={<Shield className="w-6 h-6 text-gray-700" />} title="Privacy by design" desc="You own your data. Clear export, granular permissions, and service isolation." />
          </div>
        </section>

        <section className="px-4 py-16 bg-gray-50">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8">Where we’re going vs where we are</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <RoadmapCol title="Now" items={["Habits: daily tasks, lessons, stats", "Journaling: gratitude, reflection, freeform", "UYE program: PDF + tracker + in‑app trial"]} />
              <RoadmapCol title="Next" items={["Meals tracking", "Movement programs with graph explorer", "Sleep readiness integration", "Assistant tools: anticipatory coaching"]} />
            </div>
          </div>
        </section>

        <section id="join" className="px-4 py-24">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-4">Join the movement</h2>
            <p className="text-gray-600 mb-6">Start with Unf*ck Your Eating or Daily Journaling. Your email unlocks early access, and we’ll send you a trial voucher when the time is right.</p>
            <div className="inline-flex items-center gap-3 px-6 py-3 rounded-xl bg-gray-900 text-white cursor-not-allowed opacity-80">
              Mock purchase (Stripe) — Coming Soon
            </div>
            <p className="text-xs text-gray-400 mt-3">After purchase, we’ll email you an access code; log in with the same email for auto‑enrollment.</p>
          </div>
        </section>
      </main>
    </div>
  )
}

function ValueCard({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) {
  return (
    <div className="p-6 rounded-2xl border border-gray-200 bg-white/60">
      <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{desc}</p>
    </div>
  )
}

function RoadmapCol({ title, items }: { title: string, items: string[] }) {
  return (
    <div className="p-6 rounded-2xl border border-gray-200 bg-white">
      <h3 className="text-xl font-semibold mb-3">{title}</h3>
      <ul className="space-y-2 list-disc pl-5 text-gray-700">
        {items.map((i) => <li key={i}>{i}</li>)}
      </ul>
    </div>
  )
}



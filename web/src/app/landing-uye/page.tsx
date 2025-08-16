'use client';

import React, { useState } from 'react';
import { Flame, Salad, Apple, CheckCircle2, Sparkles } from 'lucide-react';

const EmailCapture = () => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    try {
      const res = await fetch('/api/subscribe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, tag: 'uye' }) });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed');
      setIsSubmitted(true);
      setEmail('');
    } catch (err: any) {
      setError(err.message || 'Something went wrong');
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isSubmitted) {
    return (
      <div className="text-center">
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 text-green-700 rounded-xl border border-green-200">
          <CheckCircle2 className="w-5 h-5" />
          <span className="font-medium">Check your email to verify and get your PDF + tracker.</span>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="flex gap-3 max-w-md mx-auto">
      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Your email" required disabled={isSubmitting} className="px-6 py-4 text-lg border-2 border-gray-200 rounded-xl focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all duration-200 flex-1" />
      <button type="submit" disabled={isSubmitting || !email} className="px-8 py-4 text-lg bg-emerald-600 text-white rounded-xl hover:bg-emerald-700 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all duration-200 font-semibold disabled:opacity-50">{isSubmitting ? 'Sending…' : 'Get PDF + Tracker'}</button>
    </form>
  );
}

export default function UYELandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white text-gray-900">
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <Flame className="w-5 h-5 text-white" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight">Unf*ck Your Eating</span>
            </div>
            <a href="#get" className="px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors">Get the PDF</a>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-16">
        <section className="relative pt-20 pb-24 px-4 bg-gradient-to-b from-emerald-50 to-white">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-6">
              Eat better without willpower
              <span className="block bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">in seven simple habits</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10">A practical, bullshit-free guide to transforming your relationship with food. No macros. No shame. Just seven habits that stack wins.</p>
            <div id="get" className="mb-6">
              <EmailCapture />
            </div>
            <p className="text-sm text-gray-500">Includes a limited-time voucher for free trial access to the in-app UYE program</p>
          </div>
        </section>

        <section className="px-4 py-20">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-2xl border border-gray-200 bg-white/60">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4"><Apple className="w-6 h-6 text-emerald-700" /></div>
              <h3 className="text-xl font-semibold mb-2">Seven Habits</h3>
              <p className="text-gray-600">One habit per week with a bonus practice week. Learn, practice, and stack momentum without overwhelm.</p>
            </div>
            <div className="p-6 rounded-2xl border border-gray-200 bg-white/60">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4"><Salad className="w-6 h-6 text-emerald-700" /></div>
              <h3 className="text-xl font-semibold mb-2">PDF + Tracker</h3>
              <p className="text-gray-600">A beautifully formatted PDF and a Google Sheets tracker so you can start immediately—no app required.</p>
            </div>
            <div className="p-6 rounded-2xl border border-gray-200 bg-white/60">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center mb-4"><Sparkles className="w-6 h-6 text-emerald-700" /></div>
              <h3 className="text-xl font-semibold mb-2">App Trial Voucher</h3>
              <p className="text-gray-600">Your email unlocks a trial voucher for the Swae app’s guided UYE program—bite-sized lessons and daily practice.</p>
            </div>
          </div>
        </section>

        <section className="bg-gray-50 px-4 py-20">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8">What you’ll learn</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[
                'Eat Slowly',
                'Screens Off Evenings',
                'Protein First',
                'Plan Simple Meals',
                'Hydrate Enough',
                'Mindful Snacking',
                'Sleep and Satiety'
              ].map((t) => (
                <div key={t} className="p-5 rounded-xl border border-gray-200 bg-white">
                  <div className="flex items-center gap-3 text-emerald-700 font-semibold"><CheckCircle2 className="w-5 h-5" /> {t}</div>
                  <p className="text-gray-600 mt-2">Actionable guidance, short daily practice, and a prompt to reflect. Stack wins weekly.</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="px-4 py-24">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl font-bold mb-4">Get the PDF and tracker now</h2>
            <p className="text-gray-600 mb-8">Then check your email for a special voucher: free trial access to the UYE program in Swae.</p>
            <EmailCapture />
            <p className="text-xs text-gray-400 mt-3">No spam. We’ll send your link and the voucher details.</p>
          </div>
        </section>
      </main>
    </div>
  );
}



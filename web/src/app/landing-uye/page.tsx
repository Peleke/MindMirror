'use client';

import React, { useState } from 'react';
import { Flame, Salad, Apple, CheckCircle2, Sparkles, Leaf, Shield, XCircle, Check, CreditCard, Tag } from 'lucide-react';

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
            <a href="#get" className="px-4 py-2 text-sm font-medium text-white bg-emerald-700 rounded-lg hover:bg-emerald-800 transition-colors">Get the PDF</a>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-16">
        <section className="relative pt-16 pb-10 px-4 bg-gradient-to-b from-emerald-50 to-white">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-6">
              Eat better without willpower
              <span className="block bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">in seven simple habits</span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-6">A practical, bullshit-free guide to transforming your relationship with food. No macros. No shame. Just seven habits that stack wins.</p>
            <div id="get" className="mb-6">
              <EmailCapture />
            </div>
            <p className="text-sm text-gray-500">Includes a limited-time discounted access voucher for the premium in‑app UYE program in <a href="/landing-swae" className="underline decoration-emerald-500/60 hover:decoration-emerald-600">Swae OS</a></p>
          </div>
        </section>


        {/* Conversational Sales Section */}
        <section className="px-4 pt-8 pb-20 -mt-4 sm:-mt-6">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-lg max-w-none">
              <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">We’ve been there too...</h2>
              <p className="text-gray-700 leading-relaxed">
                If you’ve cycled through diets, tracked like it was a second job, and still ended up right back where you started—hey, same. The <strong>problem isn’t you.</strong> It’s the all-or-nothing playbook that burns you out and blames you when it breaks.
              </p>
              <p className="text-gray-700 leading-relaxed mt-4">
                You push hard for a few weeks. You cut more, try harder, feel worse. Social plans get complicated. Energy dips. Mood tanks. And
                eventually, life happens—and the plan collapses. Cue the guilt, the restart, repeat.
              </p>
              <p className="text-gray-700 leading-relaxed mt-4">
                UYE was born from getting off that roller coaster. We replaced restriction with rhythm. We kept the parts that work—structure,
                support, simple rules of thumb—and ditched the shame.
              </p>
              <p className="text-gray-700 leading-relaxed mt-4">
                We’ve used this exact habit‑first approach with countless people—and personally. Our founder lost over 100 lbs combining these
                habits with consistent, sustainable exercise. Not overnight. Not by starving. By stacking small wins until they became a life.
                You don’t need more willpower. You need a plan that works with your life, not against it.
              </p>
            </div>
          </div>
        </section>

        {/* Us vs Them Callout (juxtaposed) */}
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-teal-500/10 to-lime-500/10 rounded-3xl transform rotate-1"></div>
              <div className="relative bg-emerald-900 rounded-2xl shadow-2xl overflow-hidden">
                <div className="p-8">
                  <div className="text-center mb-10">
                    <h2 className="text-3xl sm:text-4xl font-bold text-white">Why diets fail—and what works instead</h2>
                    <p className="text-emerald-100 mt-2">The old playbook vs. the UYE way</p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                    <div className="bg-emerald-800 rounded-xl p-6">
                      <h4 className="text-white font-medium mb-4">Traditional Dieting</h4>
                      <div className="space-y-3">
                        {[
                          'All-or-nothing rules, quick fixes, guilt cycles',
                          'Restriction, fear foods, moralizing meals',
                          'Track everything or fail completely',
                          'Short bursts, burnout, start over Monday',
                          'Yo-yo progress, mood swings, loss of trust',
                        ].map((t) => (
                          <div key={t} className="inline-flex items-start gap-2 rounded-lg border border-rose-300/40 bg-rose-200/20 px-3 py-2 text-rose-100">
                            <XCircle className="w-4 h-4 mt-0.5" />
                            <span className="text-sm">{t}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div className="bg-emerald-800 rounded-xl p-6">
                      <h4 className="text-white font-medium mb-4">With UYE</h4>
                      <div className="space-y-3">
                        {[
                          'One habit a week, practical wins, steady momentum',
                          'Real food you enjoy, flexible options, no shame',
                          'Simple tracker for consistency (not perfection)',
                          'Tiny actions, stacked wins, resilient growth',
                          'Sustainable change, better energy, confidence',
                        ].map((t) => (
                          <div key={t} className="inline-flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50/10 px-3 py-2 text-emerald-100">
                            <Check className="w-4 h-4 mt-0.5" />
                            <span className="text-sm">{t}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Social proof directly below comparison */}
        <section className="py-16 px-4 bg-gray-50">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
              <div>
                <h3 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">It’s already working for people like you.</h3>
                <p className="text-gray-700 mb-6">And it will work for you too—here’s why:</p>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Leaf className="w-6 h-6 text-emerald-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Habit-first beats hype</div>
                      <div className="text-gray-600">You build skills that last. No more chasing hacks or starting from scratch.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Salad className="w-6 h-6 text-teal-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Fits your real life</div>
                      <div className="text-gray-600">Travel? Kids? Deadlines? UYE adapts so consistency becomes easier than quitting.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 bg-lime-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <CheckCircle2 className="w-6 h-6 text-lime-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Progress you can feel</div>
                      <div className="text-gray-600">Better energy, steadier mood, clothes that fit—without obsessing over numbers.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
                      <Shield className="w-6 h-6 text-emerald-600" />
                    </div>
                    <div>
                      <div className="font-semibold text-gray-900">Kind, evidence-aware approach</div>
                      <div className="text-gray-600">Rooted in behavior change and nutrition fundamentals—not fads, not shaming.</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-6">
                {[{
                  name: 'Jordan • Busy Parent', quote: 'Meals stopped being a battle. I actually have energy after work.'
                }, {
                  name: 'Riley • Startup Founder', quote: 'I got out of the all-or-nothing loop. Small wins, big results.'
                }, {
                  name: 'Sam • Returning to Fitness', quote: 'UYE helped me eat like an athlete again—without obsessing.'
                }].map((p, i) => (
                  <div key={p.name} className="p-6 rounded-2xl border border-gray-200 bg-white">
                    <div className="flex items-center gap-3 mb-3">
                      <img
                        src={`https://i.pravatar.cc/80?img=${[12,27,35][i % 3]}`}
                        alt={`${p.name} avatar`}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                      <div className="font-medium text-gray-900">{p.name}</div>
                    </div>
                    <div className="text-gray-700">“{p.quote}”</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Better Way Callout */}
        <section className="py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">There’s a better way</h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">A habit‑first system that fits your life and compounds over time.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Apple className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Learn one habit</h3>
                <p className="text-gray-600">
                  Focus on just one habit each week so change feels doable and sticks.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-teal-500 to-teal-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Salad className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Practice daily</h3>
                <p className="text-gray-600">
                  Tiny actions add up. Use the tracker to build momentum without perfection.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-lime-500 to-lime-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <CheckCircle2 className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Stack wins</h3>
                <p className="text-gray-600">
                  Week over week, the habits compound into confident, sustainable change.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Leaf className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Enjoy real food</h3>
                <p className="text-gray-600">Eat foods you love with simple, flexible guardrails—not strict rules.</p>
              </div>
            </div>
          </div>
        </section>

        {/* (Moved "What you’ll learn" below 'Why UYE is different' and aligned to data) */}

        {/* Why UYE is different (analogous structure) */}
        <section className="bg-gray-50 py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
              <div>
                <h2 className="text-4xl font-bold text-gray-900 mb-6">
                  Why UYE is different
                </h2>
                <p className="text-xl text-gray-600 mb-8">
                  Not another diet. A habit-first system that helps you eat well—confidently, enjoyably, and for good.
                </p>
              </div>

              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Leaf className="w-6 h-6 text-emerald-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Habit-first methodology</h3>
                    <p className="text-gray-600">
                      Build durable skills instead of chasing hacks. One habit at a time—real growth, no burnout.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-teal-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Compassion over shame</h3>
                    <p className="text-gray-600">
                      Progress thrives with psychological safety. UYE keeps it kind, practical, and judgment-free.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-lime-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Apple className="w-6 h-6 text-lime-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Built for real life</h3>
                    <p className="text-gray-600">
                      Eat foods you love and fit habits to your context. No macros, no moralizing.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Part of something bigger</h3>
                    <p className="text-gray-600">
                      A glimpse into Swae OS—tools for growth that feel human. Start with UYE and keep evolving.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-24 px-4 bg-gray-50">
          <div className="max-w-5xl mx-auto">
            <h3 className="text-3xl font-bold text-gray-900 text-center mb-10">Frequently asked questions</h3>
            <div className="rounded-2xl border border-gray-200 bg-white">
              {[{
                q: 'Do I need to count calories or macros?', a: 'No. UYE focuses on simple habits that guide your choices without obsessive tracking.'
              }, {
                q: 'What if I have a busy schedule?', a: 'The system is designed for real life—10–15 minutes a day, flexible meals, and simple prompts.'
              }, {
                q: 'Is this a meal plan?', a: 'No. You’ll learn principles, examples, and patterns that fit your preferences and culture.'
              }, {
                q: 'What happens after the 8 weeks?', a: 'You’ll have a set of skills you can keep using. Many people repeat favorite weeks and keep stacking wins.'
              }].map((item, i) => (
                <details key={i} className="group border-t first:border-t-0 border-gray-200">
                  <summary className="flex items-center justify-between px-6 py-4 cursor-pointer select-none">
                    <span className="font-semibold text-gray-900">{item.q}</span>
                    <span className="ml-4 text-gray-400 group-open:rotate-180 transition-transform">▾</span>
                  </summary>
                  <div className="px-6 pb-4 text-gray-600">{item.a}</div>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* Offer / Mock Stripe */}
        <section className="py-24 px-4">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-3xl border border-gray-200 bg-white shadow-sm overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-2">
                <div className="p-8 md:p-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm">
                    <Tag className="w-4 h-4" /> Limited-time offer
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mt-4">Unf*ck Your Eating — PDF + Tracker</h3>
                  <p className="text-gray-600 mt-2">Start now with the complete guide, weekly habits, examples, and a discounted‑access voucher for Swae’s premium UYE program.</p>
                  <div className="flex items-end gap-3 mt-6">
                    <div className="text-4xl font-extrabold text-gray-900">$0</div>
                    <div className="text-gray-400 line-through">$79</div>
                    <div className="text-emerald-700 font-medium">Limited time</div>
                  </div>
                  <div className="mt-6 space-y-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> Instant access to the PDF + tracker</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> Email prompts for 8 weeks</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> Discount voucher for Swae’s premium UYE app</div>
                  </div>
                </div>
                <div className="p-8 md:p-10 bg-gray-50 border-t md:border-t-0 md:border-l border-gray-200 flex flex-col justify-center">
                  <div className="space-y-3">
                    <button className="w-full px-6 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl transition-colors inline-flex items-center justify-center gap-2">
                      <CreditCard className="w-5 h-5" /> Download the PDF + Tracker (Free)
                    </button>
                    <div className="text-xs text-gray-500 text-center">Mock checkout — button for design only</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Premium Offer / Mock Stripe */}
        <section className="py-6 px-4 -mt-12">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-3xl border border-gray-200 bg-white shadow-sm overflow-hidden">
              <div className="grid grid-cols-1 md:grid-cols-2">
                <div className="p-8 md:p-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-100 text-emerald-800 rounded-full text-sm">
                    <Tag className="w-4 h-4" /> Premium bundle
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mt-4">UYE Premium — PDF + Tracker + Swae Voucher</h3>
                  <p className="text-gray-600 mt-2">Everything in the free bundle, plus a discounted Swae voucher (14‑day trial + 6 weeks discounted access; $19/mo after, cancel anytime).</p>
                  <div className="flex items-end gap-3 mt-6">
                    <div className="text-4xl font-extrabold text-gray-900">$19</div>
                    <div className="text-gray-400 line-through">$99</div>
                    <div className="text-emerald-700 font-medium">Limited time</div>
                  </div>
                  <div className="mt-6 space-y-2 text-sm text-gray-600">
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> PDF + tracker + email prompts</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> Discount voucher for Swae UYE (trial + 6 weeks)</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4 text-emerald-600" /> Priority tips and extras</div>
                  </div>
                </div>
                <div className="p-8 md:p-10 bg-gray-50 border-t md:border-t-0 md:border-l border-gray-200 flex flex-col justify-center">
                  <div className="space-y-3">
                    <button className="w-full px-6 py-4 bg-gray-300 text-gray-700 font-semibold rounded-xl cursor-not-allowed inline-flex items-center justify-center gap-2">
                      <CreditCard className="w-5 h-5" /> Get the Premium Bundle (Coming soon)
                    </button>
                    <div className="text-xs text-gray-500 text-center">Mock layout — checkout coming later</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* What you’ll learn (moved and aligned to data with custom descriptions) */}
        <section className="bg-gray-50 px-4 py-20">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-3xl font-bold text-center mb-8">What you’ll learn</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[{
                title: 'Put the Phone (and TV) Down', desc: 'Undistracted meals reconnect hunger and fullness cues—so you eat enough, not past enough.'
              }, {
                title: 'Eat Slowly and Chew Thoroughly', desc: 'Give your body time to register fullness. Feel satisfied without feeling stuffed.'
              }, {
                title: 'Stop at 80% Full (Leave a Bite or Two)', desc: 'Pause before “too full.” Reduce bloating and learn to trust your appetite again.'
              }, {
                title: 'More Fiber: Fruits, Veggies, and Grains', desc: 'Front‑load fiber to steady energy and tame cravings—no restriction required.'
              }, {
                title: 'Prioritize Protein', desc: 'A palm of protein at meals calms hunger, stabilizes energy, and reduces snack spirals.'
              }, {
                title: 'Rethink Drinks: Choose Water or Unsweetened Options', desc: 'Liquid calories don’t satisfy. Lead with water so sweet drinks become optional.'
              }, {
                title: 'Prefer Whole Foods', desc: 'Gently swap processed items for whole, flavor‑forward choices—satisfaction that lasts.'
              }].map((item) => (
                <div key={item.title} className="p-5 rounded-xl border border-gray-200 bg-white">
                  <div className="flex items-center gap-3 text-emerald-700 font-semibold"><CheckCircle2 className="w-5 h-5" /> {item.title}</div>
                  <p className="text-gray-600 mt-2">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Featured Testimonial (styled like MindMirror) */}
        <section className="py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <blockquote className="text-2xl sm:text-3xl font-medium text-gray-900 mb-8 leading-relaxed">
              “UYE didn’t ask me to become a different person. It helped me become a consistent one.”
            </blockquote>
            <div className="flex items-center justify-center gap-4">
              <img src="https://i.pravatar.cc/96?img=15" alt="Taylor Morgan avatar" className="w-12 h-12 rounded-full object-cover" />
              <div className="text-left">
                <div className="font-semibold text-gray-900">Taylor Morgan</div>
                <div className="text-gray-600">Early Participant</div>
              </div>
            </div>
          </div>
        </section>

        {/* Bottom Email Capture CTA */}
        <section className="bg-emerald-900 py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl sm:text-5xl font-bold text-white mb-6">Get the UYE PDF + Tracker free</h2>
            <p className="text-xl text-emerald-100 mb-10 max-w-2xl mx-auto">Start today. Everyone who signs up will get a discounted Swae voucher when it’s ready—so you can explore the full guided program when you’re ready.</p>
            <div className="max-w-md mx-auto [&_input::placeholder]:text-emerald-100">
            <EmailCapture />
            </div>
            <p className="text-sm text-emerald-200 mt-4">No spam. Just practical help and momentum.</p>
          </div>
        </section>
      </main>
      {/* Footer (mirrors MindMirror style) */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                <Flame className="w-5 h-5 text-white" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight">Unf*ck Your Eating</span>
            </div>
            <div className="text-center text-sm text-gray-500">
              A <span className="text-gray-700 font-medium">Swae OS</span> project
              <div className="text-xs text-gray-400 mt-1">
                &copy; {new Date().getFullYear()} All rights reserved
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}



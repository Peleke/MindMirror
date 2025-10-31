'use client';

import React, { useState, useEffect } from 'react';
import { Brain, HeartHandshake, BarChart3, Activity, Soup, Dumbbell, Moon, Shield, CheckCircle2, Sparkles, Leaf, XCircle, Check, CreditCard, Tag, NotebookPen, Focus, Layers3 } from 'lucide-react';

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
      const res = await fetch('/api/subscribe', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email, tag: 'swae' }) });
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
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-xl border" style={{ background: 'var(--clr-bg-alt)', color: 'var(--clr-fg)', borderColor: 'var(--clr-fg-alt)' }}>
          <CheckCircle2 className="w-5 h-5" />
          <span className="font-medium">You are in. Check your email to confirm.</span>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="flex gap-3 max-w-md mx-auto">
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
        required
        disabled={isSubmitting}
        className="px-6 py-4 text-lg rounded-xl outline-none transition-all duration-200 flex-1 border-2 focus:ring-2"
        style={{
          color: 'var(--clr-fg)',
          background: 'var(--clr-bg)',
          borderColor: 'var(--clr-fg-alt)',
          boxShadow: 'none'
        }}
      />
      <button
        type="submit"
        disabled={isSubmitting || !email}
        className="px-8 py-4 text-lg rounded-xl font-semibold transition-all duration-200 disabled:opacity-60"
        style={{ background: 'var(--clr-primary)', color: '#fff', boxShadow: 'var(--shadow)' }}
      >
        {isSubmitting ? 'Joining…' : 'Join early access'}
      </button>
    </form>
  );
}

function FeatureRow({ title, bullets, imgSrc, imgAlt, reverse }: { title: string; bullets: string[]; imgSrc: string; imgAlt: string; reverse?: boolean }) {
  return (
    <div className={`grid grid-cols-1 lg:grid-cols-2 gap-10 items-center ${reverse ? 'lg:[&>div:first-child]:order-2 lg:[&>div:last-child]:order-1' : ''}`}>
      <div>
        <h3 className="text-2xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>{title}</h3>
        <div className="space-y-3">
          {bullets.map((b) => (
            <div key={b} className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 mt-0.5" style={{ color: 'var(--clr-primary)' }} />
              <div className="text-base leading-relaxed" style={{ color: 'var(--clr-fg)' }}>{b}</div>
            </div>
          ))}
        </div>
      </div>
      <div className="relative w-full overflow-hidden rounded-2xl border" style={{ borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
        <img src={imgSrc} alt={imgAlt} className="w-full h-auto object-cover" />
      </div>
    </div>
  );
}

export default function SwaeLanding() {
  useEffect(() => {
    const animateHeroText = () => {
      const textElement = document.querySelector('#animated-text span') as HTMLElement;
      if (!textElement) return;

      const phrases = [
        'Move Forward',
        'Build Better',
        'Grow Steady', 
        'Live Gently',
        'Progress Naturally',
        'Thrive Daily'
      ];
      
      let currentIndex = 0;
      
      const animate = () => {
        // Fade out and slide up
        textElement.style.transform = 'translateY(-100%)';
        textElement.style.opacity = '0';
        
        setTimeout(() => {
          // Change text and reset position
          currentIndex = (currentIndex + 1) % phrases.length;
          textElement.textContent = phrases[currentIndex];
          textElement.style.transform = 'translateY(100%)';
          
          // Fade in and slide to center
          setTimeout(() => {
            textElement.style.transform = 'translateY(0)';
            textElement.style.opacity = '1';
          }, 50);
        }, 300);
      };
      
      // Start animation after initial load
      const timer = setTimeout(() => {
        const interval = setInterval(animate, 3000);
        return () => clearInterval(interval);
      }, 2000);
      
      return () => clearTimeout(timer);
    };

    animateHeroText();
  }, []);

  return (
    <div className="light flex flex-col min-h-screen" style={{ ['--clr-bg' as any]: '#ffffff', ['--clr-bg-alt' as any]: '#f9fafb', ['--clr-fg' as any]: '#111827', ['--clr-fg-alt' as any]: '#6b7280', ['--clr-primary' as any]: '#111827', ['--shadow' as any]: 'rgba(0, 0, 0, 0.08) 0px 8px 30px', background: 'var(--clr-bg)', color: 'var(--clr-fg)' }}>
      <header className="fixed top-0 left-0 right-0 z-50 backdrop-blur-sm border-b" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'color-mix(in oklab, var(--clr-fg-alt) 30%, transparent)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, var(--clr-fg), var(--clr-fg-alt))', boxShadow: 'var(--shadow)' }}>
                <Brain className="w-5 h-5" color="#fff" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight">Swae OS</span>
            </div>
            <div className="flex items-center gap-2">
              <a href="/projects/swae-os" className="px-4 py-2 text-sm font-medium rounded-lg transition-colors" style={{ background: 'color-mix(in oklab, var(--clr-primary) 15%, white)', color: 'var(--clr-fg)' }}>For Investors</a>
              <a href="#get" className="px-4 py-2 text-sm font-medium rounded-lg transition-colors" style={{ background: 'var(--clr-primary)', color: '#fff', boxShadow: 'var(--shadow)' }}>Get early access</a>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-16">
        {/* Hero with right-side media slot for banner/device images */}
        <section className="px-4 pt-16 pb-12" style={{ background: 'var(--clr-bg)' }}>
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-6" style={{ color: 'var(--clr-fg)' }}>
                <div id="animated-text" className="relative overflow-hidden">
                  <span className="block transition-all duration-500 ease-in-out">Move Forward</span>
                </div>
                <span className="text-4xl sm:text-5xl font-normal opacity-80">with Swae</span>
              </h1>
              <p className="text-xl mb-8" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
                Swae gently coordinates daily habits, journaling, movement, and meals into a rhythm you can trust for less tech and more nourishment.
              </p>
              <div id="get" className="mb-6">
                <EmailCapture />
              </div>
              <div className="text-sm" style={{ color: 'color-mix(in oklab, var(--clr-fg) 75%, black)' }}>
                No spam. Just steady, human-first progress notes and early-access invites.
              </div>
            </div>
            <div>
              <div className="relative w-full overflow-hidden rounded-3xl border aspect-[16/10]" style={{ borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)', background: 'var(--clr-bg-alt)' }}>
                <div className="absolute inset-0 grid place-items-center text-center p-6">
                  <div>
                    <div className="inline-flex items-center gap-2 text-sm px-3 py-1 rounded-full mb-3" style={{ background: 'color-mix(in oklab, var(--clr-bg-alt) 70%, white)', color: 'var(--clr-fg)' }}>
                      <Sparkles className="w-4 h-4" /> Preview
                    </div>
                    <div className="text-lg" style={{ color: 'var(--clr-fg)' }}>
                      Hero banner or device mockups land here tomorrow ✨
                    </div>
                    <div className="text-sm mt-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 70%, black)' }}>
                      Swap this slot with a wide banner image or iPhone screenshots.
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Conversational Sales Section */}
        <section className="px-4 pt-8 pb-20">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-lg max-w-none" style={{ ['--tw-prose-body' as any]: 'var(--clr-fg)' }}>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>Swae: Your Life, Not Your Checklist</h2>
              <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                You don't need another app telling you to do more—you need a system that moves with you. 
              </p>
              <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Swae meets you where you are, weaving habits, journaling, meals, and movement into a rhythm that fits your life. Progress isn't punishment; it's momentum made effortless, guided by insight, not shame.
              </p>
              <p className="mt-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Start with one habit, one prompt, or one reflection. Swae handles the rest—stacking small wins into lasting change.
              </p>
            </div>
          </div>
        </section>

        {/* Comparison Section */}
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>The Old Way vs. The Swae Way</h2>
              <p className="text-xl max-w-4xl mx-auto" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
                Most wellness tools assume you'll bend your life to fit their program. We do the opposite: we shape the system around your life. Every habit, check-in, and suggestion is designed to work with your schedule, your energy, and your goals—so growth feels natural, resilient, and human.
              </p>
            </div>
            
            <div className="relative rounded-2xl overflow-hidden" style={{ background: 'var(--clr-bg-alt)', boxShadow: 'var(--shadow)' }}>
              <div className="p-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                  {/* The Hustle App Stack */}
                  <div className="rounded-xl p-6" style={{ background: 'color-mix(in oklab, var(--clr-fg) 8%, var(--clr-bg))', border: '1px solid color-mix(in oklab, var(--clr-fg-alt) 20%, transparent)' }}>
                    <h4 className="font-semibold mb-6 text-center" style={{ color: 'var(--clr-fg)' }}>The Hustle App Stack</h4>
                    <div className="space-y-4">
                      {[
                        "Fragmented tools, endless dashboards, decision fatigue",
                        "Shame-first nudges, perfection or bust", 
                        "Track everything or feel like you are failing",
                        "Short sprints, long burnouts, Monday restarts",
                        "Data you can't feel, progress you can't trust",
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-lg" style={{ background: 'color-mix(in oklab, var(--clr-fg) 4%, var(--clr-bg))' }}>
                          <XCircle className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: '#ef4444' }} />
                          <span className="text-sm leading-relaxed" style={{ color: 'color-mix(in oklab, var(--clr-fg) 90%, black)' }}>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* With Swae */}
                  <div className="rounded-xl p-6" style={{ background: 'color-mix(in oklab, var(--clr-primary) 8%, var(--clr-bg))', border: '1px solid color-mix(in oklab, var(--clr-primary) 20%, transparent)' }}>
                    <h4 className="font-semibold mb-6 text-center" style={{ color: 'var(--clr-fg)' }}>With Swae</h4>
                    <div className="space-y-4">
                      {[
                        'One gentle habit at a time; practical wins, steady momentum',
                        'Real life first—travel, kids, chaos welcome',
                        'Simple check-ins for consistency (not perfection)',
                        'Tiny actions, stacked wins, resilient growth',
                        'Human signals + smart data you can actually feel',
                      ].map((item, i) => (
                        <div key={i} className="flex items-start gap-3 p-3 rounded-lg" style={{ background: 'color-mix(in oklab, var(--clr-primary) 4%, var(--clr-bg))' }}>
                          <Check className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: '#22c55e' }} />
                          <span className="text-sm leading-relaxed" style={{ color: 'color-mix(in oklab, var(--clr-fg) 90%, black)' }}>{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* There's a better way */}
        <section className="py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>There's a better way</h2>
              <p className="text-xl" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>A habit-first system that fits your life and compounds over time.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ background: 'linear-gradient(135deg, var(--clr-primary), color-mix(in oklab, var(--clr-primary) 70%, white))', boxShadow: 'var(--shadow)' }}>
                  <Layers3 className="w-8 h-8" color="#fff" />
                </div>
                <h3 className="text-xl font-semibold mb-3" style={{ color: 'var(--clr-fg)' }}>Learn one habit</h3>
                <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  Focus on just one habit each week so change feels doable and sticks.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ background: 'linear-gradient(135deg, var(--clr-primary), color-mix(in oklab, var(--clr-primary) 70%, white))', boxShadow: 'var(--shadow)' }}>
                  <NotebookPen className="w-8 h-8" color="#fff" />
                </div>
                <h3 className="text-xl font-semibold mb-3" style={{ color: 'var(--clr-fg)' }}>Practice daily</h3>
                <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  Tiny actions add up. Use gentle check-ins to build momentum without perfection.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ background: 'linear-gradient(135deg, var(--clr-primary), color-mix(in oklab, var(--clr-primary) 70%, white))', boxShadow: 'var(--shadow)' }}>
                  <CheckCircle2 className="w-8 h-8" color="#fff" />
                </div>
                <h3 className="text-xl font-semibold mb-3" style={{ color: 'var(--clr-fg)' }}>Stack wins</h3>
                <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  Week over week, the habits compound into confident, sustainable change.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6" style={{ background: 'linear-gradient(135deg, var(--clr-primary), color-mix(in oklab, var(--clr-primary) 70%, white))', boxShadow: 'var(--shadow)' }}>
                  <Shield className="w-8 h-8" color="#fff" />
                </div>
                <h3 className="text-xl font-semibold mb-3" style={{ color: 'var(--clr-fg)' }}>Own your data</h3>
                <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Clear exports and granular permissions—privacy as a feature, not a footnote.</p>
              </div>
            </div>
          </div>
        </section>

        {/* FEATURES (new) */}
        <section className="px-4 py-24">
          <div className="max-w-6xl mx-auto">
            <div className="text-center max-w-3xl mx-auto mb-14">
              <div className="inline-flex items-center gap-2 text-sm px-3 py-1 rounded-full mb-3" style={{ background: 'color-mix(in oklab, var(--clr-primary) 20%, white)', color: 'var(--clr-fg)' }}>
                <Sparkles className="w-4 h-4" /> Features
              </div>
              <h2 className="text-4xl font-bold mb-3" style={{ color: 'var(--clr-fg)' }}>What's inside Swae (and why you'll feel it)</h2>
              <p className="text-lg" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
                A gentle little chorus of tools—supportive, not shouty. The vibe? Cozy clarity. Less hustle, more harmony.
              </p>
            </div>

            <div className="space-y-16">
              <FeatureRow
                title="Habits & Programs"
                bullets={[
                  'Weekly habit focus with simple, loving guardrails',
                  'Guided lessons you can read on a walk',
                  'Streaks and adherence rings that whisper, not yell',
                ]}
                imgSrc="https://placehold.co/1000x600/ede0d4/7f5539?text=Habits+%26+Programs"
                imgAlt="Swae habits and programs preview"
              />

              <FeatureRow
                title="Journaling & Insights"
                bullets={[
                  "Structured prompts when you want them, freeform when you don't",
                  "Patterns surface gently—next steps offered, not forced",
                  "Privacy-forward by default",
                ]}
                imgSrc="https://placehold.co/1000x600/ede0d4/7f5539?text=Journaling+%26+Insights"
                imgAlt="Swae journaling preview"
                reverse
              />

              <FeatureRow
                title="Meals (early)"
                bullets={[
                  'Quick, flexible logging—no spreadsheets required',
                  'A living library of meals you actually eat',
                  'Future: optional estimates via computer vision',
                ]}
                imgSrc="https://placehold.co/1000x600/ede0d4/7f5539?text=Meals"
                imgAlt="Swae meals preview"
              />

              <FeatureRow
                title="Movement (next)"
                bullets={[
                  'Programs with progressions and kind regressions',
                  'Smart substitutions when equipment or time changes',
                  'Built on a movement graph for real-world flexibility',
                ]}
                imgSrc="https://placehold.co/1000x600/ede0d4/7f5539?text=Movement"
                imgAlt="Swae movement preview"
                reverse
              />
            </div>
          </div>
        </section>

        {/* Why Swae is different */}
        <section className="py-24 px-4" style={{ background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
              <div>
                <h2 className="text-4xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>
                  Why Swae is different
                </h2>
                <p className="text-xl mb-8" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
                  Not another tracker. A gentle, coordinated system that helps you live well—confidently, enjoyably, and for good.
                </p>
              </div>

              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                    <Leaf className="w-6 h-6" color="var(--clr-primary)" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--clr-fg)' }}>Struture &gt; Grind</h3>
                    <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                      One habit, one workout, one meal at a time—real growth, no burnout.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                    <Shield className="w-6 h-6" color="var(--clr-primary)" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--clr-fg)' }}>Compassion over shame</h3>
                    <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                      Progress thrives with psychological safety. Swae keeps it kind, practical, and judgment-free.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                    <NotebookPen className="w-6 h-6" color="var(--clr-primary)" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--clr-fg)' }}>Built for real life</h3>
                    <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                      Fit habits and notes to your context. No performance theater, no moralizing.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                    <Sparkles className="w-6 h-6" color="var(--clr-primary)" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2" style={{ color: 'var(--clr-fg)' }}>Part of something bigger</h3>
                    <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                      Swae is a suite—start small, then stitch in meals, movement, and sleep when you are ready.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials */}
        <section className="py-16 px-4" style={{ background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
              <div>
                <h3 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>It's already working for people like you.</h3>
                <p className="mb-6" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>And it'll work for you—because you won't have to white-knuckle it.</p>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <Leaf className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Habit-first beats hype</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>No hacks. No grand promises. Just humane structure that sticks.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <NotebookPen className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Fits your real life</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Travel, kids, messy weeks—Swae helps, and doesn't judge.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <Focus className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Progress you can feel</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Steadier mood, clearer head, deeper sleep. Not more numbers: The things that matter.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <Shield className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Privacy-forward</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>You own your data. Clear export and granular permissions.</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-6">
                {[
                  { name: 'Jordan M. — Busy Parent', quote: 'I stopped fighting with my calendar. Swae made space for meals and breath.' },
                  { name: 'Riley L. — Founder', quote: 'I finally got out of the productivity guilt loop. Softer, but somehow stronger.' },
                  { name: 'Sam S. — Returning to Fitness', quote: 'The momentum is sneaky. I blinked and had a routine I actually like.' },
                ].map((p, i) => (
                  <div key={p.name} className="p-6 rounded-2xl border" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
                    <div className="flex items-center gap-3 mb-3">
                      <img
                        src={`https://i.pravatar.cc/80?img=${[12,27,35][i % 3]}`}
                        alt={`${p.name} avatar`}
                        className="w-10 h-10 rounded-full object-cover"
                      />
                      <div className="font-medium" style={{ color: 'var(--clr-fg)' }}>{p.name}</div>
                    </div>
                    <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>“{p.quote}”</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* FAQ */}
        <section className="py-24 px-4" style={{ background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
          <div className="max-w-5xl mx-auto">
            <h3 className="text-3xl font-bold text-center mb-10" style={{ color: 'var(--clr-fg)' }}>Frequently asked questions</h3>
            <div className="rounded-2xl border" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
              {[
                { q: 'Do I need to track everything?', a: 'No. Swae favors simple check-ins and gentle accountability over exhaustive tracking.' },
                { q: 'Will this fit a busy, messy life?', a: 'Yes. We design for humans with responsibilities, not robots. Imperfect days are expected.' },
                { q: 'Is my data private?', a: 'Privacy is a first-class feature. You own your data, with clear export and granular permissions.' },
                { q: 'What does early access include?', a: 'Habits, journaling, and the UYE program first—meals and movement soon after.' },
              ].map((item, i) => (
                <details key={i} className="group border-t first:border-t-0" style={{ borderColor: 'color-mix(in oklab, var(--clr-fg-alt) 35%, transparent)' }}>
                  <summary className="flex items-center justify-between px-6 py-4 cursor-pointer select-none">
                    <span className="font-semibold" style={{ color: 'var(--clr-fg)' }}>{item.q}</span>
                    <span className="ml-4 transition-transform" style={{ color: 'color-mix(in oklab, var(--clr-fg) 70%, black)' }}>▾</span>
                  </summary>
                  <div className="px-6 pb-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>{item.a}</div>
                </details>
              ))}
            </div>
          </div>
        </section>

        {/* Offer / Mock Stripe */}
        <section className="py-24 px-4">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-3xl border overflow-hidden" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
              <div className="grid grid-cols-1 md:grid-cols-2">
                <div className="p-8 md:p-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm" style={{ background: 'color-mix(in oklab, var(--clr-primary) 20%, white)', color: 'var(--clr-fg)' }}>
                    <Tag className="w-4 h-4" /> Early access
                  </div>
                  <h3 className="text-2xl font-bold mt-4" style={{ color: 'var(--clr-fg)' }}>Swae OS — Early Access Pass</h3>
                  <p className="mt-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Get the habit system, journaling, and a trial to UYE in Swae. Meals and movement roll out next.</p>
                  <div className="flex items-end gap-3 mt-6">
                    <div className="text-4xl font-extrabold" style={{ color: 'var(--clr-fg)' }}>$0</div>
                    <div className="line-through" style={{ color: 'color-mix(in oklab, var(--clr-fg) 50%, black)' }}>$49</div>
                    <div className="font-medium" style={{ color: 'var(--clr-primary)' }}>Limited time</div>
                  </div>
                  <div className="mt-6 space-y-2 text-sm" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> Instant access to the habit system</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> Journaling with prompts and freeform</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> UYE trial inside Swae</div>
                  </div>
                </div>
                <div className="p-8 md:p-10 border-t md:border-t-0 md:border-l flex flex-col justify-center" style={{ borderColor: 'var(--clr-fg-alt)', background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
                  <div className="space-y-3">
                    <button className="w-full px-6 py-4 font-semibold rounded-xl transition-colors inline-flex items-center justify-center gap-2" style={{ background: 'var(--clr-primary)', color: '#fff', boxShadow: 'var(--shadow)' }}>
                      <CreditCard className="w-5 h-5" /> Join Early Access (Free)
                    </button>
                    <div className="text-xs text-center" style={{ color: 'color-mix(in oklab, var(--clr-fg) 65%, black)' }}>Mock checkout — button for design only</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Premium Offer / Mock Stripe */}
        <section className="py-6 px-4 -mt-12">
          <div className="max-w-4xl mx-auto">
            <div className="rounded-3xl border overflow-hidden" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
              <div className="grid grid-cols-1 md:grid-cols-2">
                <div className="p-8 md:p-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm" style={{ background: 'color-mix(in oklab, var(--clr-primary) 20%, white)', color: 'var(--clr-fg)' }}>
                    <Tag className="w-4 h-4" /> Premium bundle
                  </div>
                  <h3 className="text-2xl font-bold mt-4" style={{ color: 'var(--clr-fg)' }}>Swae Premium — Early Access + Guided Programs</h3>
                  <p className="mt-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Everything in early access, plus a longer UYE trial and priority features.</p>
                  <div className="flex items-end gap-3 mt-6">
                    <div className="text-4xl font-extrabold" style={{ color: 'var(--clr-fg)' }}>$19</div>
                    <div className="line-through" style={{ color: 'color-mix(in oklab, var(--clr-fg) 50%, black)' }}>$99</div>
                    <div className="font-medium" style={{ color: 'var(--clr-primary)' }}>Limited time</div>
                  </div>
                  <div className="mt-6 space-y-2 text-sm" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> Extended UYE program access</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> Priority tips and extras</div>
                    <div className="flex items-center gap-2"><Check className="w-4 h-4" color="var(--clr-primary)" /> Future exclusive programs</div>
                  </div>
                </div>
                <div className="p-8 md:p-10 border-t md:border-t-0 md:border-l flex flex-col justify-center" style={{ borderColor: 'var(--clr-fg-alt)', background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
                  <div className="space-y-3">
                    <button className="w-full px-6 py-4 font-semibold rounded-xl cursor-not-allowed inline-flex items-center justify-center gap-2" style={{ background: 'color-mix(in oklab, var(--clr-fg) 25%, black)', color: 'color-mix(in oklab, var(--clr-bg) 40%, white)' }}>
                      <CreditCard className="w-5 h-5" /> Get the Premium Bundle (Coming soon)
                    </button>
                    <div className="text-xs text-center" style={{ color: 'color-mix(in oklab, var(--clr-fg) 65%, black)' }}>Mock layout — checkout coming later</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Testimonial */}
        <section className="py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <blockquote className="text-2xl sm:text-3xl font-medium mb-8 leading-relaxed" style={{ color: 'var(--clr-fg)' }}>
              “Swae didn't ask me to become a different person. It helped me become a consistent one.”
            </blockquote>
            <div className="flex items-center justify-center gap-4">
              <img src="https://i.pravatar.cc/96?img=15" alt="Taylor Morgan avatar" className="w-12 h-12 rounded-full object-cover" />
              <div className="text-left">
                <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Taylor Morgan</div>
                <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Early Participant</div>
              </div>
            </div>
          </div>
        </section>

        {/* Bottom Email Capture CTA */}
        <section className="py-24 px-4" style={{ background: 'color-mix(in oklab, var(--clr-fg) 10%, var(--clr-bg))' }}>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl sm:text-5xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>Get early access to Swae OS</h2>
            <p className="text-xl mb-10 max-w-2xl mx-auto" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Start gentle. We'll invite you as features roll out—first habits and journaling, then meals and movement.</p>
            <div className="max-w-md mx-auto">
              <EmailCapture />
            </div>
            <p className="text-sm mt-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 70%, black)' }}>Unsubscribe anytime.</p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t" style={{ background: 'var(--clr-bg)', borderColor: 'color-mix(in oklab, var(--clr-fg-alt) 30%, transparent)' }}>
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, var(--clr-fg), var(--clr-fg-alt))', boxShadow: 'var(--shadow)' }}>
                <Brain className="w-5 h-5" color="#fff" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight" style={{ color: 'var(--clr-fg)' }}>Swae OS</span>
            </div>
            <div className="text-center text-sm" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
              A <span className="font-medium" style={{ color: 'var(--clr-fg)' }}>Swae</span> project
              <div className="text-xs mt-1" style={{ color: 'color-mix(in oklab, var(--clr-fg) 65%, black)' }}>
                &copy; {new Date().getFullYear()} All rights reserved
              </div>
            </div>
    </div>
    </div>
      </footer>
    </div>
  )
}



'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Brain, HeartHandshake, BarChart3, Activity, Soup, Dumbbell, Moon, Shield, CheckCircle2, Sparkles, Leaf, XCircle, Check, CreditCard, Tag, NotebookPen, Focus, Layers3 } from 'lucide-react';

export default function SwaeInvestorPage() {
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleContactSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    
    const formData = new FormData(e.currentTarget);
    const data = {
      name: formData.get('name') as string,
      email: formData.get('email') as string,
      message: formData.get('message') as string,
      source: 'Investor Page'
    };

    try {
      const response = await fetch('/api/contact-form', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to send message');
      }

      setSubmitted(true);
    } catch (err: any) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

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
              <Link href="/landing-swae" className="px-4 py-2 text-sm font-medium rounded-lg transition-colors" style={{ background: 'color-mix(in oklab, var(--clr-primary) 15%, white)', color: 'var(--clr-fg)' }}>Home</Link>
              <Link href="/landing-swae#get" className="px-4 py-2 text-sm font-medium rounded-lg transition-colors" style={{ background: 'var(--clr-primary)', color: '#fff', boxShadow: 'var(--shadow)' }}>Get early access</Link>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-16">
        {/* Hero without email capture */}
        <section className="px-4 pt-16 pb-12" style={{ background: 'var(--clr-bg)' }}>
          <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-10 items-center">
            <div>
              <div className="inline-flex items-center gap-2 text-xs px-2.5 py-1 rounded-full mb-4" style={{ background: 'color-mix(in oklab, var(--clr-primary) 15%, white)', color: 'var(--clr-fg)' }}>
                Case Study • Swae OS
              </div>
              <h1 className="text-5xl sm:text-6xl font-bold tracking-tight leading-tight mb-6" style={{ color: 'var(--clr-fg)' }}>
                Swae OS
              </h1>
              <p className="text-xl mb-8" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>
                The operating system for your embodied life
              </p>
              <div className="text-sm" style={{ color: 'color-mix(in oklab, var(--clr-fg) 75%, black)' }}>
                Building a coordinated system for habits, journaling, meals, and movement. Privacy-first, compassion-forward.
              </div>
            </div>
            <div>
              <div className="relative w-full overflow-hidden rounded-3xl border aspect-[16/10]" style={{ borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)', background: 'var(--clr-bg-alt)' }}>
                <div className="absolute inset-0 grid place-items-center text-center p-6">
                  <div>
                    <div className="inline-flex items-center gap-2 text-sm px-3 py-1 rounded-full mb-3" style={{ background: 'color-mix(in oklab, var(--clr-bg-alt) 70%, white)', color: 'var(--clr-fg)' }}>
                      <Sparkles className="w-4 h-4" /> Project Snapshot
                    </div>
                    <div className="text-lg" style={{ color: 'var(--clr-fg)' }}>
                      Coordinated habits, journaling, meals, and movement—gently stitched into a rhythm you can trust.
                    </div>
                    <div className="text-sm mt-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 70%, black)' }}>
                      Early signups: 2.8k • Conversion: 38% • Release: ~14d
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Investor Overview (was Conversational Sales) */}
        <section className="px-4 pt-8 pb-20">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-lg max-w-none" style={{ ['--tw-prose-body' as any]: 'var(--clr-fg)' }}>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>Investor Overview</h2>
              <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Everyone knows what to do — eat better, move more, sleep — but nobody's cracked the code on doing it consistently. Swae OS is the system that makes behavior change stick. We've built a progression model that blends evidence-based habit design, motivational interviewing, and personalized coaching into something that feels less like homework and more like leveling up in a game.
              </p>
              <p className="mt-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                The market is crowded with apps that give tips, track workouts, or log meals — but none of them connect the dots into a single, cohesive experience. Swae unifies the core health verticals of habits, workouts, meals, and journaling into one platform, then layers in AI-powered coaching to create the first true operating system for sustainable change.
              </p>
              <p className="mt-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Under the hood, Swae is backed by world-class architecture: a React Native app powered by a modular service mesh, with Qdrant for vector search, PostgreSQL for structured movement data, and LangGraph orchestrating tool-based AI workflows. While still pre-revenue, it's engineered from day one to support both individual coaching journeys and scalable, hyper-personalized transformation programs.
              </p>
            </div>
          </div>
        </section>

        {/* Engineering Overview */}
        <section className="px-4 pb-20">
          <div className="max-w-3xl mx-auto">
            <div className="prose prose-lg max-w-none" style={{ ['--tw-prose-body' as any]: 'var(--clr-fg)' }}>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>Engineering Overview</h2>
              <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                At its core, Swae OS is an agentic platform. The Agent service is a fully modern LangGraph/LangSmith–orchestrated system, designed for multi-source RAG across PostgreSQL, Qdrant, and (soon) Memgraph graph data. It manages dynamic prompt generation, weekly summaries, daily affirmations, and tool orchestration via MCP — effectively giving every user their own adaptive, multi-modal coach. This isn't an "add AI to an app" story; the AI system is the beating heart of the product.
              </p>
              <p className="mt-4" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Around that core, Swae OS runs a distributed, service-mesh architecture centered on a Hive GraphQL gateway for stitching and federation. The React Native frontend consumes a unified schema that wraps specialized services for workouts, meals, habits, journaling, and movements. A worker service maintains real-time indexing pipelines into Qdrant to keep the agent current, while movement data federates relational (Postgres) and graph (Memgraph) sources. All user-facing experiences resolve through the gateway and bind to user context, ensuring a clean contract from data through intelligence to UI.
              </p>
            </div>
          </div>
        </section>

        {/* Architecture Overview */}
        <section className="px-4 pb-24">
          <div className="max-w-6xl mx-auto">
            <div className="prose prose-lg max-w-none mb-10" style={{ ['--tw-prose-body' as any]: 'var(--clr-fg)' }}>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6" style={{ color: 'var(--clr-fg)' }}>Architecture Overview</h2>
              <p style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                Swae's architecture reflects its AI-first philosophy: a distributed service mesh where the agent service orchestrates personalized experiences across specialized domain services, all unified through a GraphQL gateway that makes the complexity invisible to users.
              </p>
            </div>
            
            {/* Architecture Diagram */}
            <div className="relative mb-10">
              <div className="relative rounded-2xl overflow-hidden border" style={{ borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
                <img 
                  src="/swae-arch.png" 
                  alt="Swae OS Architecture Diagram - Service mesh with AI-first orchestration" 
                  className="w-full h-auto object-contain"
                />
              </div>
            </div>

            <div className="max-w-3xl mx-auto">
              <div className="rounded-2xl border p-6" style={{ borderColor: 'var(--clr-fg-alt)', background: 'color-mix(in oklab, var(--clr-bg) 90%, white)', boxShadow: 'var(--shadow)' }}>
                <p className="text-lg leading-relaxed" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  This is the kind of architecture you only get when the app is an excuse, not the end goal. Every piece — from Hive federation to MCP-wrapped agent tools — exists to keep the AI layer first-class, not bolted on. The mesh is modular, the RAG pipelines are live, and the gateway keeps it all feeling like one seamless system. It's production-grade, research-level tech masquerading as a mobile app.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Lessons Learned (was Social proof) */}
        <section className="py-16 px-4" style={{ background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
              <div>
                <h3 className="text-3xl sm:text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>Lessons Learned</h3>
                <p className="mb-6" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Key insights from building a compassion-forward habit system.</p>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <Leaf className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Lead with compassion</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Compassion-forward UX reduces churn more than stricter nudges.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <NotebookPen className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Design for change</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Isolation of domain services speeds iteration while protecting data.</div>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" style={{ background: 'color-mix(in oklab, var(--clr-primary) 30%, white)' }}>
                      <Focus className="w-6 h-6" color="var(--clr-primary)" />
                    </div>
                    <div>
                      <div className="font-semibold" style={{ color: 'var(--clr-fg)' }}>Retention is About Feels, not Progress</div>
                      <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>Users join to hit their goals; they stay because Swae is a partner, not an app.</div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="space-y-6">
                {[
                  { title: 'Progress is Consistency', desc: 'Changing one\'s lifestyle is about constant practice. Swae rewards and encourages users for every little win to keep them moving towards their best selves.' },
                  { title: 'System Architecture', desc: 'Domain services isolated but coordinated through application mesh for maximum flexibility and data protection.' },
                  { title: 'Product Strategy', desc: 'Start with habits, not hacks. Build momentum, not perfection. It turns out sustainable change beats flashy features every time.' },
                ].map((p, i) => (
                  <div key={p.title} className="p-6 rounded-2xl border" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full flex items-center justify-center" style={{ background: 'color-mix(in oklab, var(--clr-primary) 20%, white)' }}>
                        <span className="text-sm font-semibold" style={{ color: 'var(--clr-primary)' }}>{i + 1}</span>
                      </div>
                      <div className="font-medium" style={{ color: 'var(--clr-fg)' }}>{p.title}</div>
                    </div>
                    <div style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>{p.desc}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
                </section>

        {/* Musings - commented out for now */}
        {/* 
        <section className="py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>Musings</h2>
              <p className="text-xl" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Notes on product strategy, timing, and what we're learning about sustainable behavior change.</p>
            </div>

            <div className="max-w-4xl mx-auto">
              <div className="rounded-2xl border p-8" style={{ borderColor: 'var(--clr-fg-alt)', background: 'color-mix(in oklab, var(--clr-bg) 90%, white)', boxShadow: 'var(--shadow)' }}>
                <p className="text-lg leading-relaxed mb-6" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  We're learning that motivation is unreliable, but systems can be kind. The most successful users aren't the ones who track everything—they're the ones who find a rhythm that feels sustainable.
                </p>
                <p className="text-lg leading-relaxed mb-6" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  The architecture reflects this philosophy: isolated services that respect user agency while providing gentle coordination. No vendor lock-in, no data hostage situations. Just tools that help you live better.
                </p>
                <p className="text-lg leading-relaxed" style={{ color: 'color-mix(in oklab, var(--clr-fg) 85%, black)' }}>
                  What we're building isn't just another productivity app. It's infrastructure for human flourishing—technology that meets you where you are and grows with you.
                </p>
              </div>
            </div>
          </div>
        </section>
        */}

        {/* Contact (styled like landing page sections) */}
        <section className="py-24 px-4" style={{ background: 'color-mix(in oklab, var(--clr-bg) 92%, white)' }}>
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h2 className="text-4xl font-bold mb-4" style={{ color: 'var(--clr-fg)' }}>Want in? Get in touch.</h2>
              <p className="text-xl" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>We'll follow up promptly. No spam.</p>
            </div>
            
            {submitted ? (
              <div className="text-center">
                <div className="inline-flex items-center gap-2 px-6 py-4 rounded-xl border" style={{ background: 'var(--clr-bg-alt)', color: 'var(--clr-fg)', borderColor: 'var(--clr-fg-alt)' }}>
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="font-medium">Thanks! We'll be in touch shortly.</span>
                </div>
              </div>
            ) : (
              <div>
                {error && (
                  <div className="mb-4 p-4 rounded-xl border" style={{ background: '#fef2f2', borderColor: '#fecaca', color: '#dc2626' }}>
                    {error}
                  </div>
                )}
                <div className="rounded-3xl border overflow-hidden" style={{ background: 'color-mix(in oklab, var(--clr-bg) 85%, white)', borderColor: 'var(--clr-fg-alt)', boxShadow: 'var(--shadow)' }}>
                <form onSubmit={handleContactSubmit} className="p-8 space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Name</label>
                      <input 
                        required 
                        name="name" 
                        className="w-full px-4 py-3 rounded-xl border focus:outline-none transition-all duration-200" 
                        style={{ borderColor: 'var(--clr-fg-alt)', background: 'var(--clr-bg)', color: 'var(--clr-fg)' }} 
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Email</label>
                      <input 
                        required 
                        type="email" 
                        name="email" 
                        className="w-full px-4 py-3 rounded-xl border focus:outline-none transition-all duration-200" 
                        style={{ borderColor: 'var(--clr-fg-alt)', background: 'var(--clr-bg)', color: 'var(--clr-fg)' }} 
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2" style={{ color: 'color-mix(in oklab, var(--clr-fg) 80%, black)' }}>Message</label>
                    <textarea 
                      required 
                      name="message" 
                      rows={5} 
                      className="w-full px-4 py-3 rounded-xl border focus:outline-none transition-all duration-200" 
                      style={{ borderColor: 'var(--clr-fg-alt)', background: 'var(--clr-bg)', color: 'var(--clr-fg)' }} 
                    />
                  </div>
                  <div className="flex justify-end">
                    <button 
                      type="submit" 
                      disabled={isSubmitting}
                      className="px-8 py-4 text-lg rounded-xl font-semibold transition-all duration-200 disabled:opacity-60"
                      style={{ background: 'var(--clr-primary)', color: '#fff', boxShadow: 'var(--shadow)' }}
                    >
                      {isSubmitting ? 'Sending...' : 'Send Message'}
                    </button>
                  </div>
                </form>
                </div>
              </div>
            )}
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
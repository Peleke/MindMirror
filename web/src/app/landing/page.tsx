import { ArrowRight, Star, Brain, MessageSquare, Zap, Shield, Code, Sparkles } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white text-gray-900">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight">MindMirror</span>
            </div>
            <a
              href="#early-access"
              className="px-4 py-2 text-sm font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 transition-colors"
            >
              Get Early Access
            </a>
          </div>
        </div>
      </header>

      <main className="flex-grow pt-16">
        {/* Hero Section */}
        <section className="relative pt-20 pb-32 px-4">
          <div className="max-w-4xl mx-auto text-center">
            {/* Narrative Hook */}
            <div className="mb-8">
              <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
                You write in your journal every day. But when did it last write back? 
                When did it challenge your assumptions, connect patterns you missed, 
                or ask the questions you didn't know you needed?
              </p>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight text-gray-900 leading-tight mb-6">
              The journal that
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                thinks with you
              </span>
            </h1>

            {/* Subhead */}
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-12 leading-relaxed">
              MindMirror is a self-aware journaling companion powered by advanced AI. 
              It doesn't just store your thoughts—it reflects them back, helping you think 
              more clearly and grow more deliberately.
            </p>

            {/* Primary CTA */}
            <div id="early-access" className="mb-8">
              <form className="max-w-md mx-auto flex gap-3">
                <input
                  type="email"
                  placeholder="you@example.com"
                  required
                  className="flex-1 px-4 py-3 text-base border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  type="submit"
                  className="px-6 py-3 text-base font-medium text-white bg-gray-900 rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-900 transition-colors flex items-center"
                >
                  Get Early Access
                  <ArrowRight className="ml-2 h-4 w-4" />
                </button>
              </form>
            </div>

            <p className="text-sm text-gray-500">
              Join the experiment in self-aware software • No spam, just updates
            </p>
          </div>
        </section>

        {/* Demo Section */}
        <section className="px-4 pb-32">
          <div className="max-w-6xl mx-auto">
            <div className="relative">
              {/* Gradient background */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-blue-500/10 rounded-3xl transform rotate-1"></div>
              
              {/* Main demo container */}
              <div className="relative bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
                <div className="p-8 text-center">
                  <div className="mb-6">
                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-full text-sm text-gray-300">
                      <Sparkles className="w-4 h-4" />
                      Live Demo Coming Soon
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                    {/* Before */}
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h4 className="text-white font-medium mb-4">Traditional Journaling</h4>
                      <div className="space-y-3 text-left">
                        <div className="bg-gray-700 rounded-lg p-3">
                          <p className="text-gray-300 text-sm">Today was stressful. Work deadlines, family stuff...</p>
                        </div>
                        <div className="text-gray-500 text-xs text-center">*silence*</div>
                      </div>
                    </div>
                    
                    {/* After */}
                    <div className="bg-gray-800 rounded-xl p-6">
                      <h4 className="text-white font-medium mb-4">With MindMirror</h4>
                      <div className="space-y-3 text-left">
                        <div className="bg-gray-700 rounded-lg p-3">
                          <p className="text-gray-300 text-sm">Today was stressful. Work deadlines, family stuff...</p>
                        </div>
                        <div className="bg-blue-600 rounded-lg p-3">
                          <p className="text-white text-sm">I notice you mentioned stress twice this week. What patterns do you see between work pressure and family time?</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Simple interface, sophisticated mind
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Powered by a multi-agent AI architecture that understands context, 
                recognizes patterns, and asks the right questions at the right time.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <MessageSquare className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Write naturally</h3>
                <p className="text-gray-600">
                  Journal however feels right—structured prompts, free-form thoughts, 
                  or quick voice notes. No rigid templates.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Brain className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">AI reflects back</h3>
                <p className="text-gray-600">
                  Advanced language models analyze your entries to identify themes, 
                  track emotional patterns, and surface insights you might miss.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Zap className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">Grow deliberately</h3>
                <p className="text-gray-600">
                  Get personalized questions, gentle challenges, and insights that 
                  help you understand yourself better over time.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Why It Matters */}
        <section className="bg-gray-50 py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
              <div>
                <h2 className="text-4xl font-bold text-gray-900 mb-6">
                  Why MindMirror is different
                </h2>
                <p className="text-xl text-gray-600 mb-8">
                  This isn't another note-taking app. It's a thinking partner 
                  built on the same architecture powering next-generation AI applications.
                </p>
              </div>

              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Brain className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Truly self-aware AI</h3>
                    <p className="text-gray-600">
                      Goes beyond simple summarization. Our system understands context, 
                      nuance, and even what you don't say.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Shield className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Private by design</h3>
                    <p className="text-gray-600">
                      Your thoughts are yours alone. End-to-end encryption, 
                      local processing options, and you own your data—always.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Code className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Production-grade architecture</h3>
                    <p className="text-gray-600">
                      Built on the same scalable, multi-agent infrastructure used 
                      in enterprise AI systems. This is real software, not a demo.
                    </p>
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center flex-shrink-0">
                    <Sparkles className="w-6 h-6 text-orange-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Part of something bigger</h3>
                    <p className="text-gray-600">
                      A glimpse into Swae OS—the future of human-AI collaboration. 
                      You're not just getting an app; you're joining an experiment.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof */}
        <section className="py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <div className="flex justify-center mb-6">
              {[...Array(5)].map((_, i) => (
                <Star key={i} className="h-6 w-6 text-yellow-400" fill="currentColor" />
              ))}
            </div>
            
            <blockquote className="text-2xl sm:text-3xl font-medium text-gray-900 mb-8 leading-relaxed">
              "MindMirror helped me connect dots I didn't even know were on the same page. 
              It's like having a superpower for self-reflection."
            </blockquote>
            
            <div className="flex items-center justify-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full"></div>
              <div className="text-left">
                <div className="font-semibold text-gray-900">Alex Chen</div>
                <div className="text-gray-600">Early Access User</div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="bg-gray-900 py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl sm:text-5xl font-bold text-white mb-6">
              Start reflecting with clarity
            </h2>
            <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
              Be among the first to experience the future of journaling. 
              Join our waitlist and we'll notify you when early access opens.
            </p>

            <form className="max-w-md mx-auto flex gap-3 mb-6">
              <input
                type="email"
                placeholder="you@example.com"
                required
                className="flex-1 px-4 py-3 text-base text-gray-900 border border-transparent rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="px-6 py-3 text-base font-medium text-gray-900 bg-white rounded-lg hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-white transition-colors"
              >
                Get Access
              </button>
            </form>

            <p className="text-sm text-gray-400">
              No spam. Just thoughtful updates as we build the future of reflection.
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="ml-3 text-xl font-semibold tracking-tight">MindMirror</span>
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
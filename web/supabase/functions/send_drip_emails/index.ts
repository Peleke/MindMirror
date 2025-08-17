// @ts-nocheck
// supabase/functions/send_drip_emails/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const resendApiKey = Deno.env.get("RESEND_API_KEY");
const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY");
const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

// Statically import templates (namespace) so the bundler includes them
import * as MM0 from './emails/mindmirror/0-welcome-email.tsx';
import * as MM1 from './emails/mindmirror/1-day.tsx';
import * as MM2 from './emails/mindmirror/2-day.tsx';
import * as MM3 from './emails/mindmirror/3-day.tsx';
import * as MM4 from './emails/mindmirror/4-day.tsx';
import * as MM5 from './emails/mindmirror/5-day.tsx';
import * as MM6 from './emails/mindmirror/6-day.tsx';
import * as MM7 from './emails/mindmirror/7-day.tsx';
import * as MM14 from './emails/mindmirror/14-day.tsx';
import * as UYE0 from './emails/uye/0-welcome-email.tsx';
import * as UYE1 from './emails/uye/1-day.tsx';
import * as UYE2 from './emails/uye/2-day.tsx';
import * as UYE3 from './emails/uye/3-day.tsx';
import * as UYE4 from './emails/uye/4-day.tsx';
import * as UYE5 from './emails/uye/5-day.tsx';
import * as UYE6 from './emails/uye/6-day.tsx';
import * as UYE7 from './emails/uye/7-day.tsx';
import * as UYE14 from './emails/uye/14-day.tsx';

// Email subjects for each day (default MindMirror)
const EMAIL_SUBJECTS: Record<number, string> = {
  0: "Welcome to MindMirror",
  1: "Your Brain Is a Forest",
  2: "Healing is nonlinear", 
  3: "Let's get reflective",
  4: "Growth is quiet, too",
  5: "You're doing better than you think",
  6: "Last of the week - a gift of perspective",
  7: "Week 2 begins",
  14: "We're still here",
};

const EMAIL_SUBJECTS_UYE: Record<number, string> = {
  0: "Welcome to Unf*ck Your Eating",
  1: "The easiest way to eat less—without changing your plate",
  2: "Slower eating for speedier progress",
  3: "The Okinawan habit that keeps you light on your feet",
  4: "The nutrient you’re probably only getting half of",
  5: "Psst—why you’re hungry again an hour later",
  6: "The sneaky calories your brain doesn’t count",
  7: "The swap that keeps you full for hours",
  14: "Still with you—ready for the next step?",
};

// Function to load email template by day
async function loadEmailTemplate(day: number, campaign?: string): Promise<{ html: string, text: string }> {
  const map: Record<string, any> = {
    'mindmirror:0': MM0, 'mindmirror:1': MM1, 'mindmirror:2': MM2, 'mindmirror:3': MM3, 'mindmirror:4': MM4,
    'mindmirror:5': MM5, 'mindmirror:6': MM6, 'mindmirror:7': MM7, 'mindmirror:14': MM14,
    'uye:0': UYE0, 'uye:1': UYE1, 'uye:2': UYE2, 'uye:3': UYE3, 'uye:4': UYE4,
    'uye:5': UYE5, 'uye:6': UYE6, 'uye:7': UYE7, 'uye:14': UYE14,
  };
  const key = `${campaign || 'mindmirror'}:${day}`;
  const mod = map[key];
  if (!mod) throw new Error(`No template module found for ${key}`);

  // Prefer default export, else first function export
  const Component = mod.default || Object.values(mod).find((v: any) => typeof v === 'function');
  if (!Component) throw new Error(`No component export found for ${key}`);

  const React = await import('npm:react');
  const { renderToStaticMarkup } = await import('npm:react-dom/server');
  const html = renderToStaticMarkup(React.createElement(Component, {}));
  const text = htmlToText(html);
  return { html, text };
}

// Simple text extraction from React Email templates
function htmlToText(html: string): string {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<br\s*\/>/gi, '\n')
    .replace(/<\/(p|h\d|li|tr)>/gi, '\n')
    .replace(/<li>/gi, '- ')
    .replace(/<[^>]+>/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

// Fallback email content if template loading fails
function getFallbackEmail(day: number): string {
  const fallbacks = {
    0: `Welcome to MindMirror! We're excited to have you join us on this journey of self-reflection and growth.`,
    1: `Your mind is doing the best it can with what it has. Be patient with yourself today.`,
    2: `Healing isn't a straight line. That's okay. That's normal. That's human.`,
    3: `Take a moment to pause and breathe. What's one thing you're grateful for right now?`,
    4: `Growth happens in the quiet moments. Your growth is valid, even when it's invisible to others.`,
    5: `You're doing better than you think. Trust the process. Trust yourself.`,
    6: `Remember that you are not your thoughts. You are the awareness behind it all.`,
    7: `Week 2 begins! Keep going, keep growing, keep being kind to yourself.`,
    14: `Whenever you're ready. We're here when you want to reconnect.`,
  };
  
  return fallbacks[day] || fallbacks[0];
}

function diffCalendarDaysUTC(fromIso: string, toDate: Date): number {
  const from = new Date(fromIso);
  const to = toDate;
  const fromUTC = Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate());
  const toUTC = Date.UTC(to.getUTCFullYear(), to.getUTCMonth(), to.getUTCDate());
  const msPerDay = 24 * 60 * 60 * 1000;
  return Math.floor((toUTC - fromUTC) / msPerDay);
}

serve(async (_req: Request) => {
  console.log('[send_drip_emails] invoked at', new Date().toISOString())
  // Direct-send path for onboarding (no cron auth required). Allows immediate day-0 sends.
  try {
    const body = await _req.clone().json().catch(() => null) as any;
    if (body && body.forceSendForEmail && typeof body.day === 'number') {
      const targetEmail = String(body.forceSendForEmail);
      const campaign = (body.campaign || 'mindmirror').toString();
      const day = Number(body.day);
      const { html, text } = await loadEmailTemplate(day, campaign);
      const subject = (campaign === 'uye' ? EMAIL_SUBJECTS_UYE : EMAIL_SUBJECTS)[day as keyof typeof EMAIL_SUBJECTS] || 'Welcome';
      const resendResponse = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: { Authorization: `Bearer ${resendApiKey}`, "Content-Type": "application/json" },
        body: JSON.stringify({ from: campaign === 'uye' ? "uye@emails.peleke.me" : "mindmirror@emails.peleke.me", to: targetEmail, subject, text, html })
      });
      return new Response(JSON.stringify({ message: 'sent-once', ok: resendResponse.ok }), { status: 200, headers: { 'content-type': 'application/json' } });
    }
  } catch (_) { /* ignore */ }
  const cronSecret = Deno.env.get('CRON_SECRET')
  if (cronSecret) {
    const provided = _req.headers.get('x-cron-secret') || ''
    if (provided !== cronSecret) {
      return new Response(JSON.stringify({ error: 'unauthorized' }), { status: 401, headers: { 'content-type': 'application/json' } })
    }
  }
  try {
    // Fetch active subscriber-campaigns (campaign-scoped rows) for any day < 14
    const url = `${supabaseUrl}/rest/v1/subscriber_campaigns?status=eq.active&drip_day_sent=lt.14&select=id,subscriber_id,campaign,drip_day_sent,subscribed_at,subscriber:subscribers(id,email)`;
    console.log('[send_drip_emails] fetching', url)
    const resp = await fetch(
      url,
      {
        headers: {
          apikey: supabaseAnonKey!,
          Authorization: `Bearer ${supabaseServiceRoleKey}`,
          'Accept-Profile': 'waitlist',
        },
      }
    );

    if (!resp.ok) {
      const body = await resp.text();
      console.error("Error fetching subscribers:", resp.status, body);
      return new Response(JSON.stringify({ error: "Failed to fetch subscribers" }), { status: 500 });
    }

    const subs: Array<{ id: number; subscriber_id: number; campaign: string; drip_day_sent: number; subscribed_at: string; subscriber: { id: number; email: string } }>= await resp.json();

    if (!subs || subs.length === 0) {
      console.log('[send_drip_emails] no subscribers to process')
      return new Response(JSON.stringify({ message: "No new emails to send" }), { status: 200 });
    }

    let emailsSent = 0;
    let errors = 0;

    for (const sub of subs) {
      // Use calendar-day differences to align with daily schedule regardless of time-of-day subscribed
      const daysSince = diffCalendarDaysUTC(sub.subscribed_at, new Date());
      const campaign = (sub.campaign || 'mindmirror').toLowerCase();
      const subjects = campaign === 'uye' ? EMAIL_SUBJECTS_UYE : EMAIL_SUBJECTS;

      // Send only if we have a template for this day and haven't already sent it
      const lastSent = (sub.drip_day_sent ?? -1);
      if (daysSince <= lastSent) continue;
      if (!subjects[daysSince as keyof typeof subjects]) continue;

      try {
        // Load email template for this day
        const { html, text } = await loadEmailTemplate(daysSince, campaign);
        const subject = subjects[daysSince as keyof typeof subjects];

        // Send email via Resend
        const resendResponse = await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${resendApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: campaign === 'uye' ? "uye@emails.peleke.me" : "mindmirror@emails.peleke.me",
            to: sub.subscriber.email,
            subject: subject,
            text,
            html,
          }),
        });

        if (!resendResponse.ok) {
          console.error(`Failed to send email to ${sub.email}:`, await resendResponse.text());
          errors++;
          continue;
        }

        // Update subscriber's drip_day_sent
        const updateResponse = await fetch(
          `${supabaseUrl}/rest/v1/subscriber_campaigns?id=eq.${sub.id}`,
          {
            method: "PATCH",
            headers: {
              apikey: supabaseAnonKey!,
              Authorization: `Bearer ${supabaseServiceRoleKey}`,
              "Content-Type": "application/json",
              'Content-Profile': 'waitlist',
            },
            body: JSON.stringify({ drip_day_sent: daysSince }),
          }
        );

        if (!updateResponse.ok) {
          console.error(`Failed to update subscriber ${sub.id}:`, await updateResponse.text());
          errors++;
          continue;
        }

        emailsSent++;
        console.log(`[send_drip_emails] sent day ${daysSince} email to`, sub.email);

      } catch (err) {
        console.error(`Error processing subscriber ${sub.id}:`, err);
        errors++;
      }
    }

    return new Response(JSON.stringify({ 
      message: "Drip emails processed", 
      emailsSent, 
      errors 
    }), { status: 200 });

  } catch (err) {
    console.error("Function error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), { status: 500 });
  }
}); 
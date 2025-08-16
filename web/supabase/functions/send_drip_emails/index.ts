// supabase/functions/send_drip_emails/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const resendApiKey = Deno.env.get("RESEND_API_KEY");
const supabaseUrl = Deno.env.get("SUPABASE_URL");
const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY");
const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

// Email subjects for each day (default MindMirror)
const EMAIL_SUBJECTS = {
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
  1: "The easiest way to eat less—without changing your plate",
  2: "Slower eating for speedier progress",
  3: "The Okinawan habit that keeps you light on your feet",
  4: "The nutrient you’re probably only getting half of",
  5: "Psst—why you’re hungry again an hour later",
  6: "The sneaky calories your brain doesn’t count",
  7: "The swap that keeps you full for hours",
};

// Function to load email template by day
async function loadEmailTemplate(day: number, campaign?: string): Promise<string> {
  const templateFiles = {
    0: "0-welcome-email.tsx",
    1: "1-day.tsx", 
    2: "2-day.tsx",
    3: "3-day.tsx",
    4: "4-day.tsx",
    5: "5-day.tsx",
    6: "6-day.tsx",
    7: "7-day.tsx",
    14: "14-day.tsx",
  };

  const fileName = templateFiles[day];
  if (!fileName) {
    throw new Error(`No template found for day ${day}`);
  }

  try {
    // Load the React Email template (support subdirectories per campaign)
    const baseDir = campaign ? `./emails/${campaign}` : `./emails`;
    const templatePath = `${baseDir}/${fileName}`;
    const templateContent = await Deno.readTextFile(templatePath);
    
    // For now, we'll use a simple text extraction approach
    // In production, you might want to use a React Email renderer
    return extractTextFromTemplate(templateContent);
  } catch (error) {
    console.error(`Failed to load template for day ${day}:`, error);
    // Fallback to simple text
    return getFallbackEmail(day);
  }
}

// Simple text extraction from React Email templates
function extractTextFromTemplate(templateContent: string): string {
  // Extract text content from JSX, removing React components
  let text = templateContent
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/import.*?from.*?;?\n?/g, '') // Remove imports
    .replace(/export.*?{.*?}.*?=.*?\(.*?\)\s*=>\s*\(/s, '') // Remove component definition start
    .replace(/\);[\s\S]*$/, '') // Remove component definition end
    .replace(/const.*?=.*?{[\s\S]*?};/g, '') // Remove style objects
    .replace(/interface.*?{[\s\S]*?}/g, '') // Remove interfaces
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim();

  // Clean up common React Email patterns
  text = text
    .replace(/<Text[^>]*>/g, '')
    .replace(/<\/Text>/g, '\n')
    .replace(/<Heading[^>]*>/g, '')
    .replace(/<\/Heading>/g, '\n')
    .replace(/<Section[^>]*>/g, '')
    .replace(/<\/Section>/g, '\n')
    .replace(/<Container[^>]*>/g, '')
    .replace(/<\/Container>/g, '\n')
    .replace(/<Body[^>]*>/g, '')
    .replace(/<\/Body>/g, '\n')
    .replace(/<Html[^>]*>/g, '')
    .replace(/<\/Html>/g, '\n');

  return text || getFallbackEmail(0);
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

serve(async (_req) => {
  try {
    // Get subscribers who haven't completed the drip sequence
    const { data: subs, error } = await fetch(
      `${supabaseUrl}/rest/v1/subscribers?drip_day_sent=lt.7&select=id,email,subscribed_at,drip_day_sent,source`,
      {
        headers: {
          apikey: supabaseAnonKey!,
          Authorization: `Bearer ${supabaseServiceRoleKey}`,
        },
      }
    ).then(res => res.json());

    if (error) {
      console.error("Error fetching subscribers:", error);
      return new Response(JSON.stringify({ error: "Failed to fetch subscribers" }), { status: 500 });
    }

    if (!subs || subs.length === 0) {
      return new Response(JSON.stringify({ message: "No new emails to send" }), { status: 200 });
    }

    let emailsSent = 0;
    let errors = 0;

    for (const sub of subs) {
      const daysSince = Math.floor(
        (Date.now() - new Date(sub.subscribed_at).getTime()) / (1000 * 60 * 60 * 24)
      );

      // Determine campaign from source (e.g., 'landing_page:uye')
      const source: string = sub.source || '';
      const campaign = source.includes(':') ? source.split(':')[1].trim() : '';
      const subjects = campaign === 'uye' ? EMAIL_SUBJECTS_UYE : EMAIL_SUBJECTS;

      // Check if we have a template for this day
      if (!subjects[daysSince as keyof typeof subjects]) continue;

      try {
        // Load email template for this day
        const emailBody = await loadEmailTemplate(daysSince, campaign);
        const subject = subjects[daysSince as keyof typeof subjects];

        // Send email via Resend
        const resendResponse = await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${resendApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: "mirror@mindmirror.app",
            to: sub.email,
            subject: subject,
            text: emailBody,
          }),
        });

        if (!resendResponse.ok) {
          console.error(`Failed to send email to ${sub.email}:`, await resendResponse.text());
          errors++;
          continue;
        }

        // Update subscriber's drip_day_sent
        const updateResponse = await fetch(
          `${supabaseUrl}/rest/v1/subscribers?id=eq.${sub.id}`,
          {
            method: "PATCH",
            headers: {
              apikey: supabaseAnonKey!,
              Authorization: `Bearer ${supabaseServiceRoleKey}`,
              "Content-Type": "application/json",
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
        console.log(`Sent day ${daysSince} email to ${sub.email}`);

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
import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';
import { render } from '@react-email/render';
// UYE welcome email is handled by the drip day-0 template; keep Next.js welcome MindMirror-only
import { createServiceRoleClient } from '../../../../lib/supabase/server';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: NextRequest) {
  try {
    const { email, source = 'landing_page', tag } = await request.json();

    if (!email) {
      return NextResponse.json(
        { error: 'Email is required' },
        { status: 400 }
      );
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return NextResponse.json(
        { error: 'Invalid email format' },
        { status: 400 }
      );
    }

    const supabase = createServiceRoleClient();

    // Check if email already exists
    const { data: existingSubscriber } = await supabase
      .schema('waitlist')
      .from('subscribers')
      .select('id, email, source, drip_day_sent')
      .eq('email', email.toLowerCase())
      .single();

    const finalSource = tag ? `${source}:${String(tag).toLowerCase()}` : source

    // If already exists, append campaign tag to source if new and proceed to send appropriate welcome
    let subscriberId: number | undefined = existingSubscriber?.id as unknown as number | undefined;
    if (existingSubscriber) {
      if (tag && !String(existingSubscriber.source || '').includes(`:${String(tag).toLowerCase()}`)) {
        await supabase
          .schema('waitlist')
          .from('subscribers')
          .update({ source: `${existingSubscriber.source || source}:${String(tag).toLowerCase()}` })
          .eq('id', existingSubscriber.id);
      }
      // Ensure campaign row exists for parallel drip
      const campaignName = (tag ? String(tag).toLowerCase() : 'mindmirror');
      await supabase
        .schema('waitlist')
        .from('subscriber_campaigns')
        .upsert({ subscriber_id: existingSubscriber.id as unknown as number, campaign: campaignName }, { onConflict: 'subscriber_id,campaign' });
    } else {
      // Insert new subscriber
      const { data: newSubscriber, error: insertError } = await supabase
        .schema('waitlist')
        .from('subscribers')
        .insert([
          {
            email: email.toLowerCase(),
            source: finalSource,
            status: 'active'
          }
        ])
        .select()
        .single();

      if (insertError) {
        console.error('Database insert error:', insertError);
        return NextResponse.json(
          { error: 'Failed to save subscription' },
          { status: 500 }
        );
      }
      subscriberId = newSubscriber.id as unknown as number;

      // Create campaign row for initial campaign
      const campaignName = (tag ? String(tag).toLowerCase() : 'mindmirror');
      await supabase
        .schema('waitlist')
        .from('subscriber_campaigns')
        .insert({ subscriber_id: subscriberId, campaign: campaignName });
    }

    // Decide whether to send immediate welcome
    const isUYE = (tag && String(tag).toLowerCase() === 'uye') || (finalSource?.includes(':uye'));
    let emailData: { id?: string } | undefined;
    // Helper to resolve the correct Functions URL (local vs hosted)
    const resolveFunctionsUrl = () => {
      const envFn = process.env.SUPABASE_FUNCTIONS_URL || process.env.NEXT_PUBLIC_SUPABASE_FUNCTIONS_URL;
      if (envFn) return envFn.replace(/\/$/, '');
      const supa = (process.env.SUPABASE_URL || '').replace(/\/$/, '');
      if (!supa) return '';
      if (supa.includes('localhost')) return `${supa}/functions/v1`;
      // Derive hosted functions domain
      try {
        const u = new URL(supa);
        const host = u.host.replace('.supabase.co', '.functions.supabase.co');
        return `${u.protocol}//${host}`;
      } catch {
        return supa; // fallback
      }
    };

    const functionsBase = resolveFunctionsUrl();
    const makeFnUrl = (path: string) => {
      if (!functionsBase) return '';
      // Local uses /functions/v1, hosted uses direct path
      return functionsBase.includes('localhost')
        ? `${functionsBase}${path.startsWith('/functions/v1') ? path : '/functions/v1' + path}`
        : `${functionsBase}${path.startsWith('/') ? path : '/' + path}`;
    };

    if (!isUYE) {
      // MindMirror: trigger campaign day-0 via Supabase functions (same flow as UYE)
      const url = makeFnUrl('/send_drip_emails');
      try {
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'x-cron-secret': process.env.CRON_SECRET || '',
            'content-type': 'application/json',
          },
          body: JSON.stringify({ forceSendForEmail: email, day: 0, campaign: 'mindmirror' })
        });
        if (!resp.ok) {
          const text = await resp.text().catch(() => '');
          console.error('MindMirror day-0 trigger failed', resp.status, text);
        }
      } catch (e: any) {
        console.error('MindMirror day-0 trigger error', e?.message || e);
      }
    } else {
      const url = makeFnUrl('/send_drip_emails');
      try {
        const resp = await fetch(url, {
          method: 'POST',
          headers: {
            'x-cron-secret': process.env.CRON_SECRET || '',
            'content-type': 'application/json',
          },
          body: JSON.stringify({ forceSendForEmail: email, day: 0, campaign: 'uye' })
        });
        if (!resp.ok) {
          const text = await resp.text().catch(() => '');
          console.error('UYE day-0 trigger failed', resp.status, text);
        }
      } catch (e: any) {
        console.error('UYE day-0 trigger error', e?.message || e);
      }
    }

    // If UYE, we skipped immediate welcome; no further error handling needed here

    // Record successful email send event
    // Note: immediate welcome is triggered via functions; no direct email id to record here

    console.log(`Signup processed: ${email} (subscriberId: ${subscriberId}, Source: ${finalSource})`);

    return NextResponse.json(
      { 
        message: isUYE ? 'Successfully subscribed to UYE updates' : 'Successfully subscribed to MindMirror updates',
        subscriberId,
        emailId: emailData?.id 
      },
      { status: 200 }
    );

  } catch (error) {
    console.error('Subscription error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 

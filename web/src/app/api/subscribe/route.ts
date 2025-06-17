import { NextRequest, NextResponse } from 'next/server';
import { Resend } from 'resend';
import { render } from '@react-email/render';
import { WelcomeEmail } from '../../../../emails/welcome-email';
import { createServiceRoleClient } from '../../../../lib/supabase/server';

const resend = new Resend(process.env.RESEND_API_KEY);

export async function POST(request: NextRequest) {
  try {
    const { email, source = 'landing_page' } = await request.json();

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
      .from('subscribers')
      .select('id, email')
      .eq('email', email.toLowerCase())
      .single();

    if (existingSubscriber) {
      return NextResponse.json(
        { message: 'You are already subscribed to MindMirror updates' },
        { status: 200 }
      );
    }

    // Insert new subscriber
    const { data: newSubscriber, error: insertError } = await supabase
      .from('subscribers')
      .insert([
        {
          email: email.toLowerCase(),
          source: source,
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

    // Generate the email HTML
    const emailHtml = await render(WelcomeEmail({ userEmail: email }));

    // Send welcome email
    const { data: emailData, error: emailError } = await resend.emails.send({
      from: 'MindMirror <onboarding@resend.dev>',
      to: [email],
      subject: 'Welcome to MindMirror - Your self-aware journaling journey begins 🧠',
      html: emailHtml,
      replyTo: 'hello@swae.dev',
    });

    if (emailError) {
      console.error('Resend error:', emailError);
      // Don't fail the whole request if email fails - subscriber is still saved
      
      // Record failed email event
      await supabase
        .from('email_events')
        .insert([
          {
            subscriber_id: newSubscriber.id,
            event_type: 'failed',
            event_data: { error: emailError.message }
          }
        ]);

      return NextResponse.json(
        { 
          message: 'Successfully subscribed, but welcome email may be delayed',
          subscriberId: newSubscriber.id 
        },
        { status: 200 }
      );
    }

    // Record successful email send event
    if (emailData?.id) {
      await supabase
        .from('email_events')
        .insert([
          {
            subscriber_id: newSubscriber.id,
            email_id: emailData.id,
            event_type: 'sent',
            event_data: { subject: 'Welcome to MindMirror - Your self-aware journaling journey begins 🧠' }
          }
        ]);
    }

    console.log(`New MindMirror signup saved: ${email} (ID: ${newSubscriber.id}, Source: ${source})`);

    return NextResponse.json(
      { 
        message: 'Successfully subscribed to MindMirror updates',
        subscriberId: newSubscriber.id,
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
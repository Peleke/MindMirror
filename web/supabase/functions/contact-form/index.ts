import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { corsHeaders } from "../_shared/cors.ts"

interface ContactFormData {
  name: string
  email: string
  message: string
  source?: string
}

interface ResendEmailPayload {
  from: string
  to: string[]
  subject: string
  html: string
}

const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

const sanitizeInput = (input: string): string => {
  return input.trim().replace(/[<>]/g, '')
}

const createEmailTemplate = (data: ContactFormData): string => {
  const { name, email, message, source } = data
  
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>New Contact Form Submission</title>
      <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        .field { margin-bottom: 15px; }
        .label { font-weight: bold; color: #555; }
        .value { margin-top: 5px; padding: 10px; background: #f9f9f9; border-radius: 4px; }
        .message { white-space: pre-wrap; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #666; }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>New Contact Form Submission</h2>
        ${source ? `<p><strong>Source:</strong> ${source}</p>` : ''}
      </div>
      
      <div class="field">
        <div class="label">Name:</div>
        <div class="value">${sanitizeInput(name)}</div>
      </div>
      
      <div class="field">
        <div class="label">Email:</div>
        <div class="value">${sanitizeInput(email)}</div>
      </div>
      
      <div class="field">
        <div class="label">Message:</div>
        <div class="value message">${sanitizeInput(message)}</div>
      </div>
      
      <div class="footer">
        <p>This email was sent from your Swae contact form.</p>
        <p>Timestamp: ${new Date().toISOString()}</p>
      </div>
    </body>
    </html>
  `
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Only allow POST requests
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ error: 'Method not allowed' }),
        { 
          status: 405, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Get environment variables
    const resendApiKey = Deno.env.get('RESEND_API_KEY')
    const contactEmail = Deno.env.get('CONTACT_EMAIL')

    if (!resendApiKey || !contactEmail) {
      console.error('Missing required environment variables')
      return new Response(
        JSON.stringify({ error: 'Server configuration error' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Parse request body
    let formData: ContactFormData
    try {
      formData = await req.json()
    } catch {
      return new Response(
        JSON.stringify({ error: 'Invalid JSON payload' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate required fields
    const { name, email, message, source = 'Unknown' } = formData

    if (!name || !email || !message) {
      return new Response(
        JSON.stringify({ error: 'Missing required fields: name, email, and message are required' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate email format
    if (!validateEmail(email)) {
      return new Response(
        JSON.stringify({ error: 'Invalid email format' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Validate field lengths
    if (name.length > 100 || email.length > 100 || message.length > 5000) {
      return new Response(
        JSON.stringify({ error: 'Field length limits exceeded' }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Prepare email payload
    const emailPayload: ResendEmailPayload = {
      from: 'Contact Form <noreply@swae.co>', // Update with your domain
      to: [contactEmail],
      subject: `New Contact: ${sanitizeInput(name)} from ${source}`,
      html: createEmailTemplate(formData)
    }

    // Send email via Resend
    const resendResponse = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${resendApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(emailPayload),
    })

    if (!resendResponse.ok) {
      const errorData = await resendResponse.text()
      console.error('Resend API error:', errorData)
      return new Response(
        JSON.stringify({ error: 'Failed to send email' }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const resendData = await resendResponse.json()
    console.log('Email sent successfully:', resendData.id)

    // Return success response
    return new Response(
      JSON.stringify({ 
        success: true, 
        message: 'Contact form submitted successfully',
        emailId: resendData.id 
      }),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('Unexpected error:', error)
    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
}) 
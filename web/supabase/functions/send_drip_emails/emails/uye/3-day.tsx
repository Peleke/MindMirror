import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day3UYE() {
  return (
    <Html>
      <Head />
      <Preview>The Okinawan habit that keeps you light on your feet</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 3: The Okinawan habit that keeps you light on your feet</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>In Okinawa, many stop eating when they’re no longer hungry—not when they’re stuffed. Ending around ~80% full keeps energy steady and awareness sharp.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>At one meal, leave 2–3 bites on your plate.</strong> Check how you feel an hour later—lighter, not foggy.</Text>
            <Text style={p as any}><Link href="https://example.com/uye.pdf">Download the PDF + tracker</Link> or <Link href="/landing-swae#features">Practice in Swae</Link>—get gentle daily cues and streaks.</Text>
          </Section>
        </Container>
      </Body>
    </Html>
  )
}

const main = { backgroundColor: '#ffffff', fontFamily: 'Inter, Arial, sans-serif' }
const container = { margin: '0 auto', padding: '24px', width: '560px' }
const h1 = { fontSize: '22px', lineHeight: '28px', margin: '0 0 12px', color: '#111827' }
const h3 = { fontSize: '16px', lineHeight: '22px', margin: '16px 0 6px', color: '#111827' }
const p = { fontSize: '14px', lineHeight: '20px', margin: '10px 0', color: '#374151' }



import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day1UYE() {
  return (
    <Html>
      <Head />
      <Preview>The easiest way to eat less—without changing your plate</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 1: The easiest way to eat less—without changing your plate</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Ever sat down to eat, scrolled your phone… and suddenly your food’s gone, but you barely remember eating it?</Text>
            <Text style={p as any}>When we’re glued to a screen, we eat on autopilot. That means fewer taste buds firing, more calories sliding in unnoticed, and almost zero chance of realizing we’re full until it’s too late.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>At one meal today, keep your phone out of reach.</strong> No checking messages, no “just one scroll.” Notice the smell, texture, and how your stomach feels as you eat.</Text>
            <Text style={p as any}>Want the full habit playbook with practice variations and prompts?</Text>
            <Text style={p as any}><Link href="https://example.com/uye.pdf">Download the PDF + tracker</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> to get guided daily cards.</Text>
            <Text style={small as any}>Swae is the premiere platform for behavior change. Track habits, get bite‑sized lessons, and stay accountable—starting with UYE.</Text>
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
const small = { fontSize: '12px', lineHeight: '18px', color: '#6b7280', marginTop: '10px' }



import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day2UYE() {
  return (
    <Html>
      <Head />
      <Preview>Slower eating for speedier progress</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 2: Slower eating for speedier progress</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Your body needs ~20 minutes to send the “I’m full” signal. Eating fast outruns that signal—so you eat past comfortable without noticing.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>At dinner, take one extra breath between bites.</strong> No counting chews—just a tiny pause. Notice the flavor and your hunger changing.</Text>
            <Text style={p as any}><Link href="https://example.com/uye.pdf">Download the PDF + tracker</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> for daily pacing prompts.</Text>
            <Text style={small as any}>Swae guides your daily habit practice with bite‑sized lessons and streaks.</Text>
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



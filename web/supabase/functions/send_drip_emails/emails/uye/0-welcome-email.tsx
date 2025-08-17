import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day0UYE() {
  return (
    <Html>
      <Head />
      <Preview>Welcome to Unf*ck Your Eating — your 7‑day reset starts now</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Welcome to Unf*ck Your Eating</Heading>
            <Text style={p as any}>You’re in. Over the next 7 days, you’ll stack simple eating wins that actually stick.</Text>
            <Text style={p as any}><Link href="https://example.com/uye.pdf">Download your PDF + tracker</Link>—and if you want guided daily cards with streaks, <Link href="/landing-swae#features">Practice in Swae</Link>.</Text>
          </Section>
        </Container>
      </Body>
    </Html>
  )
}

const main = { backgroundColor: '#ffffff', fontFamily: 'Inter, Arial, sans-serif' }
const container = { margin: '0 auto', padding: '24px', width: '560px' }
const h1 = { fontSize: '22px', lineHeight: '28px', margin: '0 0 12px', color: '#111827' }
const p = { fontSize: '14px', lineHeight: '20px', margin: '10px 0', color: '#374151' }



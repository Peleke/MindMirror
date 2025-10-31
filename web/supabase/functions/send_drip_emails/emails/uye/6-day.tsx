import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day6UYE() {
  return (
    <Html>
      <Head />
      <Preview>The sneaky calories your brain doesn’t count</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 6: The sneaky calories your brain doesn’t count</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Liquid calories don’t trigger fullness the same way—so you often eat the same later. Swapping them is an easy win.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>Swap your next soda/juice/sweetened latte</strong> for water or sparkling water with citrus or berries.</Text>
            <Text style={p as any}>The full guide includes zero‑cal ideas and “transition drinks.” <Link href="https://example.com/uye.pdf">Download the PDF</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> for daily cues.</Text>
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



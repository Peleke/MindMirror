import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day14UYE() {
  return (
    <Html>
      <Head />
      <Preview>Still with you—ready for the next step?</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Two weeks in—how’s it going?</Heading>
            <Text style={p as any}>If you’re still working through the habits, you’re doing it right. Tiny wins compound.</Text>
            <Text style={p as any}>When you’re ready: <Link href="https://example.com/uye.pdf">re‑download the PDF</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> for guided accountability.</Text>
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



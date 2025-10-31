import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day4UYE() {
  return (
    <Html>
      <Head />
      <Preview>The nutrient you’re probably only getting half of</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 4: The nutrient you’re probably only getting half of</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Most people get <strong>less than half</strong> the fiber they need each day. Fiber steadies blood sugar, improves satiety, and keeps you regular.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>Add one extra serving of fruit or veg</strong> to a meal—berries at breakfast, a side salad at lunch, or roasted veg at dinner.</Text>
            <Text style={p as any}><Link href="https://example.com/uye.pdf">Download the PDF + tracker</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> to stay consistent.</Text>
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



import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day7UYE() {
  return (
    <Html>
      <Head />
      <Preview>The swap that keeps you full for hours</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 7: The swap that keeps you full for hours</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Ultra‑processed foods hit fast and fade faster. Whole foods deliver slow‑burning, nutrient‑rich fuel—and your taste buds adapt.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>Replace one packaged snack</strong> with fruit, nuts, or plain yogurt. Notice the difference two hours later.</Text>
            <Text style={p as any}>The full guide includes easy swap ideas and a pantry checklist. <Link href="https://example.com/uye.pdf">Download the PDF</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> and keep your streak going.</Text>
            <Text style={small as any}>Finish strong—your trial voucher is inside your PDF email.</Text>
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



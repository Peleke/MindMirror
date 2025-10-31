import { Html, Head, Preview, Body, Container, Section, Heading, Text, Link } from 'npm:@react-email/components'
import * as React from 'npm:react'

export default function Day5UYE() {
  return (
    <Html>
      <Head />
      <Preview>Psst—why you’re hungry again an hour later</Preview>
      <Body style={main as any}>
        <Container style={container as any}>
          <Section>
            <Heading style={h1 as any}>Day 5: The reason you’re hungry again an hour later</Heading>
            <Text style={p as any}>Hi [First Name],</Text>
            <Text style={p as any}>Protein increases satiety more than carbs or fat and helps preserve lean mass. If you crash between meals, you probably need more.</Text>
            <Heading as="h3" style={h3 as any}>Today’s mini‑action</Heading>
            <Text style={p as any}><strong>Add one palm‑sized portion of protein</strong> to your next meal—eggs, Greek yogurt, chicken, tofu, or lentils.</Text>
            <Text style={p as any}>The guide’s hand‑portion method makes this effortless. <Link href="https://example.com/uye.pdf">Download the PDF</Link> or <Link href="/landing-swae#features">Practice in Swae</Link> to lock it in.</Text>
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



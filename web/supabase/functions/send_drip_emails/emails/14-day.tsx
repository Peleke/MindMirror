import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Link,
  Preview,
  Text,
  Section,
  Button,
} from '@react-email/components';
import * as React from 'react';

interface WelcomeEmailProps {
  userEmail: string;
}

export const Day14Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>a little nudge — the page is still waiting for you.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 14: Still Here. Still Yours.</Heading>

          <Text style={text}>
            Two weeks ago, you chose to begin.
          </Text>
          <Text style={text}>
            Maybe you wrote every day. Maybe you haven’t touched the app since.
          </Text>
          <Text style={text}>
            Either way — <strong>you’re still welcome.</strong>
          </Text>
          <Text style={text}>
            There’s no shame. No penalty. Just a soft nudge back into your own orbit.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What do you need most today?</em><br />
            Don’t overthink it. Just name it. Start from need. The rest will follow.
          </Text>

          <Section style={ctaSection}>
            <Button style={button} href="https://mindmirror.app/journal">
              → Tap here to open your journal
            </Button>
          </Section>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>We’re still here. And the page still knows your name.</Text>
        </Section>
      </Container>
    </Body>
  </Html>
);


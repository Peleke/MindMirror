// @ts-nocheck
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
} from 'npm:@react-email/components';
import * as React from 'npm:react';

interface WelcomeEmailProps {
  userEmail: string;
}

export const Day5Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>you’re not “behind.” you’re becoming.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 5: Your Inner Voice Is Listening</Heading>

          <Text style={text}>
            Your self-talk is not background noise.
          </Text>
          <Text style={text}>
            It <em>builds</em> you. Shapes you. Wires your default.
          </Text>
          <Text style={text}>
            The good news? It’s rewireable. Writing is one of the fastest ways to shift it.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What would you say to yourself if you truly believed in your worth?</em><br />
            Even one line is enough. That’s how the mirror changes.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong> Neff (2003), <em>Self-Compassion Theory</em>; Beck (1976), <em>Cognitive Therapy</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>You’re already rewiring. One line at a time.</Text>
        </Section>
      </Container>
    </Body>
  </Html>
);


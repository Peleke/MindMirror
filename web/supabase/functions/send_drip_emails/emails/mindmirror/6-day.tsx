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

export const Day6Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>even the mess can be sacred.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 6: You Are the Meaning-Maker</Heading>

          <Text style={text}>
            Meaning isn’t handed to you. You shape it — with reflection, choice, and care.
          </Text>
          <Text style={text}>
            Writing gives you that chance. Even confusion can become clarity when you give it a voice.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What’s something confusing lately? What might it be trying to teach you?</em><br />
            Don’t force it. Just let possibility in.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong> Frankl (1946), <em>Man’s Search for Meaning</em>; Wong (2011), <em>Positive Psychology of Meaning</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>Let even the mess have meaning.</Text>
        </Section>
      </Container>
    </Body>
  </Html>
);


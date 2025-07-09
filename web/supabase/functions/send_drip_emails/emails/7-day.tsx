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

export const Day7Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>growth doesn’t have to be visible to be real.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 7: You’re Already Becoming</Heading>

          <Text style={text}>
            Maybe you didn’t journal every day. Maybe it didn’t feel profound.
          </Text>
          <Text style={text}>
            But if you paused even once — you’re already changing.
          </Text>
          <Text style={text}>
            This isn’t about becoming someone else. It’s about meeting yourself as you are.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What’s changed for you this week, even a little?</em><br />
            Write it down. Let it count.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong> Siegel (2012), <em>The Developing Mind</em>; Kabat-Zinn (1990), <em>Full Catastrophe Living</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>Change doesn’t need an audience. It just needs you.</Text>
        </Section>
      </Container>
    </Body>
  </Html>
);


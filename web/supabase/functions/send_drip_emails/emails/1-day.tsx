import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Link,
  Preview,
  Section,
  Text,
} from '@react-email/components';
import * as React from 'react';

interface DripEmailProps {
  userEmail: string;
}

export const Day1Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>writing helps you prune, pause, and rewire.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 1: Your Brain Is a Forest</Heading>

          <Text style={text}>
            Thoughts are like vines: They grow fast. Wild. Messy.
          </Text>
          <Text style={text}>
            Especially if you're sensitive. Or overextended. Or neurodivergent.
          </Text>
          <Text style={text}>
            Journaling is how you turn the jungle into a garden. It slows the loops. It clears the underbrush.
          </Text>
          <Text style={text}>
            And over time? It rewires the path your thoughts take.
          </Text>

          <Section style={highlight}>
            <Text style={highlightText}>
              …Literally. It’s not nonsense: It’s neuroplasticity.
            </Text>
          </Section>

          <Text style={text}>
            Even a few minutes a day helps prune harmful loops and strengthen the ones that help you grow.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What’s looping in your head lately?</em>
          </Text>
          <Text style={text}>
            Just notice it. Name it. Put your finger on it.
            <br />
            No fixing yet. You’re not pruning — you’re just noticing the overgrowth.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong>{' '}
            Kandel (2001), <em>Neural mechanisms of learning</em>; Davidson (2004), <em>Emotion and the Brain</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>
            You’re not alone. Just start where you are.
          </Text>
          <Text style={footerLink}>
            <Link href="https://mindmirror.app" style={link}>
              mindmirror.app
            </Link>
          </Text>
        </Section>
      </Container>
    </Body>
  </Html>
);


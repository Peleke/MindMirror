// @ts-nocheck
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
} from 'npm:@react-email/components';
import * as React from 'npm:react';

interface DripEmailProps {
  userEmail: string;
}

export const Day2Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>burnout isn’t failure. it’s feedback.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 2: You’re Not Lazy, You’re Overstimulated</Heading>

          <Text style={text}>You are not lazy.</Text>
          <Text style={text}>You are not broken.</Text>
          <Text style={text}>You are not “behind.”</Text>

          <Text style={text}>
            Probably, you’re just burnt the f*** out.
          </Text>

          <Section style={highlight}>
            <Text style={highlightText}>
              Writing gives your brain a place to go when the world won’t shut up.
            </Text>
          </Section>

          <Text style={text}>
            Everyone has something to say. And they all expect you to listen.
          </Text>
          <Text style={text}>
            Journaling is not about productivity. It’s about <strong>protection</strong>.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What’s draining you lately?</em>
            <br />
            Even just: “I’m tired of…”
          </Text>
          <Text style={text}>
            Let your page be your boundary.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong>{' '}
            Porges (1995), <em>Polyvagal Theory</em>; Barkley (1997), <em>ADHD and Self-Regulation</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>
            You don’t need to “get it together.” You just need space to be real.
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


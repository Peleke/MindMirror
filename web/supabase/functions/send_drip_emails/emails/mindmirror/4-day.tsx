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

export const Day4Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>your feelings aren’t problems. they’re messages.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 4: You Are Allowed to Feel This Way</Heading>

          <Text style={text}>
            Emotions aren’t errors.
          </Text>
          <Text style={text}>
            They’re signals. Messages. Nervous system notes.
          </Text>
          <Text style={text}>
            And writing them down — naming them gently — helps them soften.
          </Text>
          <Text style={text}>
            This isn’t about fixing.
            <br />
            It’s about witnessing.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What emotion is closest to the surface today?</em>
            <br />
            “I feel ___, and that’s okay.”
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong> Greenberg & Pascual-Leone (2006), <em>Emotion-Focused Therapy</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>You don’t need permission to feel.</Text>
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


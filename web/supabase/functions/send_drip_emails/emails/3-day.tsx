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

export const Day3Email = ({ userEmail }: DripEmailProps) => (
  <Html>
    <Head />
    <Preview>journaling gives you authorship over your life.</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>

        <Section style={content}>
          <Heading style={h2}>Day 3: Memory Is a Myth (Sort of)</Heading>

          <Text style={text}>
            Every time you recall a memory, your brain <em>rewrites</em> it.
          </Text>
          <Text style={text}>You’re not replaying.</Text>
          <Text style={text}>You’re remixing.</Text>

          <Text style={text}>
            Writing gives you agency. It lets you anchor the now — so Future You can look back with truth, not just trauma.
          </Text>

          <Heading style={h3}>📝 Prompt for Today:</Heading>
          <Text style={text}>
            <em>What do you want Future You to remember about today?</em>
            <br />
            A feeling. A win. A wound. It all matters.
          </Text>

          <Text style={text}>
            📚 <strong>For the curious:</strong> Bartlett (1932), <em>Remembering: A Study in Experimental and Social Psychology</em>
          </Text>
        </Section>

        <Section style={footer}>
          <Text style={footerText}>You are the author now. Not the editor of someone else’s story.</Text>
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


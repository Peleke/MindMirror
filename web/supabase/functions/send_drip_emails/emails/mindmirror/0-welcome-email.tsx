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

export const WelcomeEmail = ({ userEmail }: WelcomeEmailProps) => (
  <Html>
    <Head />
    <Preview>Welcome to MindMirror - Your self-aware journaling journey begins</Preview>
    <Body style={main}>
      <Container style={container}>
        <Section style={header}>
          <Heading style={h1}>🧠 MindMirror</Heading>
          <Text style={tagline}>The journal that thinks with you</Text>
        </Section>
        
        <Section style={content}>
          <Heading style={h2}>Welcome to the future of journaling</Heading>
          <Text style={text}>
            Hi there! 👋
          </Text>
          <Text style={text}>
            You've just joined the MindMirror early access list. You're now part of an exclusive group 
            that will be among the first to experience truly self-aware journaling.
          </Text>
          
          <Section style={highlight}>
            <Text style={highlightText}>
              "You write in your journal every day. But when did it last write back?"
            </Text>
          </Section>
          
          <Text style={text}>
            Here's what you can expect:
          </Text>
          
          <Text style={bulletPoint}>
            ✨ <strong>Early access</strong> to MindMirror when we launch
          </Text>
          <Text style={bulletPoint}>
            🧠 <strong>Behind-the-scenes</strong> updates on our multi-agent LLM architecture
          </Text>
          <Text style={bulletPoint}>
            🔒 <strong>Privacy-first</strong> design insights and security updates
          </Text>
          <Text style={bulletPoint}>
            🚀 <strong>Exclusive invites</strong> to beta testing and feedback sessions
          </Text>
          
          <Section style={ctaSection}>
            <Button style={button} href="https://swae.dev">
              Learn more about Swae OS
            </Button>
          </Section>
          
          <Text style={text}>
            MindMirror is proudly part of the Swae OS ecosystem - production-grade, 
            open-source infrastructure for the future of work and creativity.
          </Text>
        </Section>
        
        <Section style={footer}>
          <Text style={footerText}>
            Questions? Just reply to this email - we read every message.
          </Text>
          <Text style={footerText}>
            From the Swae team with ❤️
          </Text>
          <Text style={footerLink}>
            <Link href="https://swae.dev" style={link}>
              swae.dev
            </Link>
          </Text>
        </Section>
      </Container>
    </Body>
  </Html>
);

export default WelcomeEmail;

const main = {
  backgroundColor: '#ffffff',
  fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
};

const container = {
  margin: '0 auto',
  padding: '20px 0 48px',
  width: '580px',
};

const header = {
  textAlign: 'center' as const,
  marginBottom: '40px',
};

const h1 = {
  color: '#1f2937',
  fontSize: '32px',
  fontWeight: '700',
  textAlign: 'center' as const,
  margin: '0 0 8px',
};

const tagline = {
  color: '#6b7280',
  fontSize: '16px',
  textAlign: 'center' as const,
  margin: '0 0 24px',
};

const content = {
  padding: '0 24px',
};

const h2 = {
  color: '#1f2937',
  fontSize: '24px',
  fontWeight: '600',
  margin: '32px 0 16px',
};

const text = {
  color: '#374151',
  fontSize: '16px',
  lineHeight: '1.6',
  margin: '16px 0',
};

const highlight = {
  backgroundColor: '#f3f4f6',
  border: '1px solid #e5e7eb',
  borderRadius: '8px',
  padding: '24px',
  margin: '24px 0',
  textAlign: 'center' as const,
};

const highlightText = {
  color: '#1f2937',
  fontSize: '18px',
  fontWeight: '500',
  fontStyle: 'italic',
  margin: '0',
};

const bulletPoint = {
  color: '#374151',
  fontSize: '16px',
  lineHeight: '1.6',
  margin: '8px 0',
};

const ctaSection = {
  textAlign: 'center' as const,
  margin: '32px 0',
};

const button = {
  backgroundColor: '#3b82f6',
  borderRadius: '6px',
  color: '#ffffff',
  fontSize: '16px',
  fontWeight: '600',
  textDecoration: 'none',
  textAlign: 'center' as const,
  display: 'inline-block',
  padding: '12px 24px',
};

const footer = {
  borderTop: '1px solid #e5e7eb',
  marginTop: '48px',
  paddingTop: '24px',
  textAlign: 'center' as const,
};

const footerText = {
  color: '#6b7280',
  fontSize: '14px',
  margin: '8px 0',
};

const footerLink = {
  margin: '16px 0 0',
};

const link = {
  color: '#3b82f6',
  textDecoration: 'none',
}; 
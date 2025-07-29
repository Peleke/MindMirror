import * as Crypto from 'expo-crypto';

export async function getAvatarUrl(email: string | null | undefined, size: number = 300): Promise<string> {
  if (!email) {
    // Fallback for no email - use a default monsterid
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }
  
  // Generate MD5 hash of lowercase, trimmed email
  const hash = await Crypto.digestStringAsync(
    Crypto.CryptoDigestAlgorithm.MD5,
    email.toLowerCase().trim()
  );
  
  // Return Gravatar URL with monsterid fallback
  return `https://www.gravatar.com/avatar/${hash}?d=monsterid&s=${size}`;
}

// Synchronous version for immediate use (uses a simple hash fallback)
export function getAvatarUrlSync(email: string | null | undefined, size: number = 300): string {
  if (!email) {
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }
  
  // Simple string hash for immediate use
  let hash = 0;
  for (let i = 0; i < email.length; i++) {
    const char = email.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  const hashStr = Math.abs(hash).toString(16).padStart(32, '0');
  
  return `https://www.gravatar.com/avatar/${hashStr}?d=monsterid&s=${size}`;
} 
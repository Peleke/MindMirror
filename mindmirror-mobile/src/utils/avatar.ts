const md5 = require('js-md5');

export async function getAvatarUrl(email: string | null | undefined, size: number = 300): Promise<string> {
  if (!email) {
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }
  
  const cleanEmail = email.toLowerCase().trim();
  console.log('🎯 Real Avatar - Email:', cleanEmail);
  
  // Use proper MD5 hash for Gravatar
  const hash = md5(cleanEmail);
  console.log('✅ Using js-md5 hash:', hash);
  
  const url = `https://www.gravatar.com/avatar/${hash}?d=monsterid&s=${size}`;
  console.log('🎯 Final Gravatar URL:', url);
  
  return url;
}

// Synchronous version that now uses real MD5!
export function getAvatarUrlSync(email: string | null | undefined, size: number = 300): string {
  if (!email) {
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }
  
  const cleanEmail = email.toLowerCase().trim();
  console.log('🔍 Avatar Sync - Email:', cleanEmail);
  
  // Now using REAL MD5 hash
  const hash = md5(cleanEmail);
  const url = `https://www.gravatar.com/avatar/${hash}?d=monsterid&s=${size}`;
  
  console.log('✅ Sync MD5 Hash:', hash);
  console.log('🎯 Sync Gravatar URL:', url);
  
  return url;
} 
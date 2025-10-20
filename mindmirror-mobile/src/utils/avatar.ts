const md5 = require('js-md5');

export async function getAvatarUrl(email: string | null | undefined, size: number = 300): Promise<string> {
  if (!email) {
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }

  const cleanEmail = email.toLowerCase().trim();
  const hash = md5(cleanEmail);
  return `https://www.gravatar.com/avatar/${hash}?d=monsterid&s=${size}`;
}

export function getAvatarUrlSync(email: string | null | undefined, size: number = 300): string {
  if (!email) {
    return `https://www.gravatar.com/avatar/00000000000000000000000000000000?d=monsterid&s=${size}`;
  }

  const cleanEmail = email.toLowerCase().trim();
  const hash = md5(cleanEmail);
  return `https://www.gravatar.com/avatar/${hash}?d=monsterid&s=${size}`;
} 
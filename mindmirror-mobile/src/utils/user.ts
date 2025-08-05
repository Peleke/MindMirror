// Smart name extraction utility for user display
export const getUserDisplayName = (user: any): string => {
  // 1. Try full name from OAuth providers (Google, GitHub, etc.)
  if (user?.user_metadata?.full_name) {
    return user.user_metadata.full_name;
  }
  
  // 2. Fallback: Extract name from email
  if (user?.email) {
    const emailUsername = user.email.split('@')[0];
    
    // Clean up the username: replace dots/underscores with spaces, capitalize
    const cleanName = emailUsername
      .replace(/[._-]/g, ' ')
      .replace(/\b\w/g, (char: string) => char.toUpperCase());
    
    console.log('📧 Email fallback:', user.email, '→', cleanName);
    return cleanName;
  }
  
  return "User";
};

// Extract first name only (useful for more casual greetings)
export const getUserFirstName = (user: any): string => {
  const fullName = getUserDisplayName(user);
  return fullName.split(' ')[0];
}; 
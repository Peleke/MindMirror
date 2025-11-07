# Adding Screenshots to Landing Page

## Quick Guide

### 1. Generate Screenshots with shots.so

1. Go to [shots.so](https://shots.so)
2. Upload your app screenshots
3. Choose device frame (iPhone 14 Pro recommended)
4. Download the mockup images

### 2. Add Screenshots to Project

```bash
# Create assets directory if it doesn't exist
mkdir -p assets/landing

# Save your screenshots
# - assets/landing/hero-screenshot.png (main hero image)
# - assets/landing/feature-1.png (optional additional screens)
```

### 3. Use in Landing Page

**Option A: Single static screenshot**
```tsx
<DeviceMockup
  screenshot={require('@/assets/landing/hero-screenshot.png')}
  theme={isWarm ? 'warm' : 'cool'}
/>
```

**Option B: Rotating screenshots**
```tsx
const [currentScreen, setCurrentScreen] = useState(0);
const screenshots = [
  require('@/assets/landing/journal.png'),
  require('@/assets/landing/habits.png'),
  require('@/assets/landing/meals.png'),
];

useEffect(() => {
  const interval = setInterval(() => {
    setCurrentScreen((prev) => (prev + 1) % screenshots.length);
  }, 3000);
  return () => clearInterval(interval);
}, []);

<DeviceMockup
  screenshot={screenshots[currentScreen]}
  theme={isWarm ? 'warm' : 'cool'}
/>
```

### 4. Current Implementation

The mockup is in `app/index.tsx` around line 172:

```tsx
<DeviceMockup theme={isWarm ? 'warm' : 'cool'} />
```

Just add the `screenshot` prop to use your actual screenshots!

### DeviceMockup Props

```typescript
interface DeviceMockupProps {
  screenshot?: ImageSourcePropType;  // Optional: your app screenshot
  theme?: 'warm' | 'cool';          // Matches landing theme
}
```

### Styling Notes

- Device frame has realistic iPhone bezels
- Glow effect matches theme (warm = crimson, cool = blue)
- Drop shadow for depth
- Status bar and home indicator included
- Max width: 320px for optimal display
- Height: 600px content area

### Tips

- **Best screenshot dimensions**: 1170 x 2532 (iPhone 14 Pro native)
- **Or use shots.so**: Let it handle the sizing automatically
- **Multiple screens**: Create an array and rotate through them
- **Theme matching**: Screenshots look best with light backgrounds
- **Transparency**: PNG with transparency works great for themed backgrounds

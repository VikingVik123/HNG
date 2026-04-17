# Profile Card Component - Stage 1B

A fully accessible, responsive Profile Card component built with semantic HTML, modern CSS, and vanilla JavaScript.

## Features

### ✅ Required Content
- **Profile card container** - Semantic `<article>` with `data-testid="test-profile-card"`
- **User name** - `<h1>` heading with `data-testid="test-user-name"`
- **User bio** - `<p>` paragraph with `data-testid="test-user-bio"`
- **Current time** - Epoch time in milliseconds with `data-testid="test-user-time"`, updates every 500ms
- **Avatar image** - `<img>` with meaningful alt text and `data-testid="test-user-avatar"`
- **Social links** - `<nav>` with `<ul>` containing social links with `data-testid="test-user-social-links"`
  - Individual links: `test-user-social-twitter`, `test-user-social-github`, `test-user-social-linkedin`, `test-user-social-instagram`
- **Hobbies list** - `<section>` with `<ul>` with `data-testid="test-user-hobbies"`
- **Dislikes list** - `<section>` with `<ul>` with `data-testid="test-user-dislikes"`

### 🎨 Semantic HTML
- `<article>` - Root card container
- `<h1>` - Main name heading
- `<figure>` & `<figcaption>` - Avatar with descriptive caption
- `<nav>` - Social links navigation
- `<section>` - Thematic content sections (bio, hobbies, dislikes)
- `<ul>` & `<li>` - Lists for social links, hobbies, and dislikes
- `<time>` - Semantic time element with ISO datetime attribute

### ♿ Accessibility Features
- **Alt text** - Avatar includes meaningful alt text
- **WCAG AA color contrast** - All text meets WCAG AA standards
  - Dark text (#2c3e50) on white background (14.5:1 contrast)
  - White text on purple gradient (7.5:1+ contrast)
- **Keyboard navigation** - All links and interactive elements are tab-focusable
- **Focus styles** - Clear, visible focus indicators (2px outline with 2px offset)
- **Aria labels** - Social links have descriptive aria-labels
- **Aria-live region** - Time element supports screen reader announcements
- **Semantic markup** - Proper HTML structure for assistive technologies
- **Reduced motion support** - Respects `prefers-reduced-motion` preference

### 📱 Responsive Design
- **Mobile (320-480px)** - Single column, stacked avatar and content, 2-column grid for lists
- **Tablet (481-768px)** - Flex layout with side-by-side arrangement, 2-column grids
- **Desktop (769px+)** - Full layout with optimized spacing
- **Large screens (1200px+)** - Enhanced spacing and proportions

### 🕐 Time Management
- Displays current epoch time in milliseconds
- Updates every 500ms for real-time accuracy
- Semantic `<time>` element with ISO datetime attribute
- Screen reader friendly with aria-live support

### 🔐 Security
- Social links use `target="_blank"` with `rel="noopener noreferrer"` for safe external opening
- Placeholder image used for avatar

## Data-testid Reference

| Element | testid | Type |
|---------|--------|------|
| Card root | `test-profile-card` | article |
| User name | `test-user-name` | h1 |
| User bio | `test-user-bio` | p |
| Current time | `test-user-time` | time |
| Avatar image | `test-user-avatar` | img |
| Social links container | `test-user-social-links` | ul |
| Twitter link | `test-user-social-twitter` | a |
| GitHub link | `test-user-social-github` | a |
| LinkedIn link | `test-user-social-linkedin` | a |
| Instagram link | `test-user-social-instagram` | a |
| Hobbies list | `test-user-hobbies` | ul |
| Dislikes list | `test-user-dislikes` | ul |

## Keyboard Navigation
- **Tab** - Move to next focusable element
- **Shift+Tab** - Move to previous focusable element
- **Enter or Space** - Activate focused link
- All links are keyboard accessible with clear focus indicators

## Testing
Open the browser console to see accessibility check results including:
- All required data-testids presence
- Semantic HTML element verification
- Image alt text validation
- Link accessibility names
- Epoch time accuracy
- WCAG color contrast status

## Browser Support
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Supports reduced motion preference
- Supports high contrast mode
- Supports forced colors mode

## Files
- `index.html` - Semantic HTML structure
- `index.css` - Responsive styling with accessibility features
- `index.js` - Time management and accessibility validation

## Customization
- Update name, bio, avatar URL in HTML
- Modify social links and their URLs
- Change hobbies and dislikes list items
- Adjust colors in CSS variables or theme sections

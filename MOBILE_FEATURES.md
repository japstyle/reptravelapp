# Mobile & PWA Features

## Mobile-Responsive Design

### Layout Optimizations
- ✅ **Full-width mobile layout** - Removes padding and maximizes screen space
- ✅ **Sticky header** - Search form stays accessible while scrolling
- ✅ **Stacked form elements** - Vertical layout for better mobile UX
- ✅ **Touch-friendly buttons** - Minimum 44px tap targets
- ✅ **Optimized typography** - Larger text sizes for readability on small screens
- ✅ **Responsive route cards** - Simplified layout with better spacing

### Mobile-Specific Features
- ✅ **Prevents zoom on input focus** (iOS) - 16px font size prevents auto-zoom
- ✅ **Smooth scrolling** - `-webkit-overflow-scrolling: touch`
- ✅ **Overscroll behavior** - Prevents pull-to-refresh interference
- ✅ **Landscape mode support** - Adjusted autocomplete height
- ✅ **Small phone optimization** - Additional breakpoint for <375px screens

### Visual Enhancements
- ✅ **Improved route cards** - Border-left highlight for best route instead of full border
- ✅ **Better spacing** - Reduced padding and margins for mobile
- ✅ **Larger touch targets** - Autocomplete items are 44px+ tall
- ✅ **Optimized icons** - Appropriately sized emojis and icons

## Progressive Web App (PWA) Features

### Installation
- ✅ **Web App Manifest** - `/static/manifest.json` with app metadata
- ✅ **App Icons** - 192x192 and 512x512 PNG icons
- ✅ **Install prompt** - Custom UI to encourage installation
- ✅ **Standalone mode** - Runs like a native app when installed
- ✅ **Theme color** - Branded status bar color (#0066cc)

### Offline Support
- ✅ **Service Worker** - Basic caching for offline functionality
- ✅ **Cache-first strategy** - Fast loading from cache
- ✅ **Network fallback** - Fetches from network when cache misses

### Native App Features
- ✅ **Apple mobile web app capable** - Full-screen on iOS
- ✅ **Status bar styling** - Native-looking status bar
- ✅ **App title** - Custom name when added to home screen
- ✅ **Viewport optimization** - Prevents unwanted scaling

## Testing on Mobile

### iOS (Safari)
1. Open the app in Safari
2. Tap the Share button
3. Select "Add to Home Screen"
4. The app will install with the custom icon

### Android (Chrome)
1. Open the app in Chrome
2. Tap the install prompt banner (or menu → "Install app")
3. Confirm installation
4. App appears on home screen

### Desktop (Chrome/Edge)
1. Look for install icon in address bar
2. Click to install as desktop app
3. Runs in standalone window

## Mobile Breakpoints

- **Desktop**: > 768px - Full layout with side-by-side elements
- **Tablet/Mobile**: ≤ 768px - Stacked layout, sticky header
- **Small phones**: ≤ 375px - Further reduced spacing and font sizes
- **Landscape mobile**: ≤ 768px + landscape - Adjusted dropdown heights

## Performance Optimizations

- **Font smoothing** - Better text rendering on mobile
- **Hardware acceleration** - Smooth animations and transitions
- **Minimal JavaScript** - Fast load times
- **Efficient caching** - Service worker reduces network requests
- **Optimized images** - Appropriately sized icons

## Future Mobile Enhancements

Consider adding:
- [ ] Geolocation to auto-detect nearest station
- [ ] Push notifications for route updates
- [ ] Offline route caching
- [ ] Dark mode support
- [ ] Haptic feedback for interactions
- [ ] Share route functionality
- [ ] Recent searches history
- [ ] Favorite routes
- [ ] Background sync for updates

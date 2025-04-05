# Afrobeats.no Web Frontend

This directory contains the Next.js frontend for the Afrobeats.no platform.

## Structure

- `/app` - Next.js app router pages and layout
- `/components` - Reusable UI components
- `/lib` - Utility functions and API clients
- `/public` - Static assets (images, fonts, etc.)
- `/styles` - Global styles and Tailwind configuration

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start
```

## Technologies

- **Next.js** - React framework
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Icons** - Icon components
- **TypeScript** - Type-safe JavaScript

## Connection to Backend

The frontend connects to the FastAPI backend running on port 8000. Make sure the backend server is running before using the web interface.

## Development Notes

- The frontend uses the API endpoint `/query` for all agent interactions
- Responsive design is implemented for mobile, tablet, and desktop views
- Theme customization is available through Tailwind configuration

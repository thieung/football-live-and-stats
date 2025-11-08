# Football Live Score - Frontend

Real-time football live scores frontend built with SvelteKit and TailwindCSS.

## Features

- ⚡ **SvelteKit** - Fast, modern web framework
- 🎨 **TailwindCSS** - Utility-first CSS framework
- 🔄 **Real-time Updates** - WebSocket integration
- 📱 **Responsive Design** - Works on all devices
- 🚀 **Server-Side Rendering** - Fast initial page loads

## Tech Stack

- **Framework**: SvelteKit
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Date Formatting**: date-fns
- **Build Tool**: Vite

## Project Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   ├── MatchCard.svelte
│   │   │   └── LoadingSpinner.svelte
│   │   ├── stores/
│   │   │   ├── websocket.ts
│   │   │   └── matches.ts
│   │   └── types/
│   │       └── match.ts
│   ├── routes/
│   │   ├── +layout.svelte
│   │   └── +page.svelte
│   ├── app.css
│   └── app.html
├── static/
├── package.json
├── svelte.config.js
├── tailwind.config.js
└── vite.config.ts
```

## Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies**
```bash
npm install
```

2. **Create environment file**
```bash
cp .env.example .env
```

Edit `.env` with your backend URL:
```
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

3. **Start development server**
```bash
npm run dev
```

4. **Access the app**
- Local: http://localhost:5173

### Build for Production

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run check` - Run Svelte type checking
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Features

### Live Scores Page

- Real-time score updates via WebSocket
- Live match indicator
- Auto-refresh for live matches
- Today's matches section
- Match details link

### Match Details Page (TODO)

- Full match statistics
- Event timeline (goals, cards, substitutions)
- Team lineups
- Match commentary

### Leagues Page (TODO)

- League standings/tables
- Top scorers
- League fixtures

## WebSocket Integration

The app automatically connects to WebSocket on mount and subscribes to live updates:

```typescript
// Subscribe to all live matches
websocketStore.subscribe('live:all');

// Subscribe to specific match
websocketStore.subscribe('match:12345');
```

## State Management

Using Svelte stores for global state:

- `matchesStore` - Manages match data
- `websocketStore` - WebSocket connection management

## Styling

Using TailwindCSS with custom components:

- `.btn` - Button styles
- `.card` - Card container
- `.match-card` - Match card with live indicator
- `.badge` - Status badges

## Deployment

### Vercel

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Upload the 'build' directory to Netlify
```

### Docker

Create `Dockerfile`:
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/build ./build
COPY --from=build /app/package*.json ./
RUN npm install --production
EXPOSE 4173
CMD ["npm", "run", "preview"]
```

Build and run:
```bash
docker build -t football-live-frontend .
docker run -p 4173:4173 football-live-frontend
```

## Environment Variables

- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

## License

MIT

## Contributing

Pull requests are welcome!

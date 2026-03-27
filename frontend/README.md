# Videogame Guru - Frontend

🎮 A modern, responsive chat interface for the Videogame Guru AI assistant.

## Overview

The Videogame Guru frontend provides a clean, user-friendly chat interface where users can ask questions about video games and receive AI-powered responses. The interface supports markdown rendering, maintains conversation history per browser tab, and provides a smooth chat experience.

## Features

- **Real-time Chat Interface** - Interactive messaging with the AI assistant
- **Markdown Rendering** - Rich text formatting in AI responses using react-markdown
- **Session Management** - Unique session ID per browser tab to maintain separate conversation histories
- **Auto-scroll** - Automatically scrolls to the latest message
- **Keyboard Shortcuts** - Press Enter to send, Shift+Enter for new lines
- **Loading States** - Visual feedback while waiting for AI responses
- **Error Handling** - Graceful error messages when the backend is unavailable

## Tech Stack

- **React 19** - Modern React with hooks
- **Vite** - Fast build tool and dev server
- **react-markdown** - Markdown rendering for AI responses
- **CSS** - Custom styling for chat interface

## Prerequisites

- Node.js (v16 or higher recommended)
- npm or yarn package manager
- **Backend API running** on `http://localhost:8000` (see `../chatbot/README.md`)

## Installation

```bash
# Install dependencies
npm install
```

## Running the Application

```bash
# Start development server
npm run dev
```

The application will be available at `http://localhost:5173` (default Vite port).

## Available Scripts

- `npm run dev` - Start development server with hot module replacement
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint to check code quality

## Project Structure

```
src/
├── App.jsx       # Main chat component with message handling
├── App.css       # Chat interface styling
├── main.jsx      # Application entry point
└── index.css     # Global styles
```

## API Integration

The frontend communicates with the FastAPI backend via:

- **Endpoint**: `POST http://localhost:8000/chat`
- **Payload**: `{ message: string, session_id: string }`
- **Response**: `{ response: string }`

Make sure the backend server is running before starting the frontend. See the main project README for instructions on starting the full application.

## Development Notes

- Built with Vite for fast HMR and optimal build performance
- Uses React hooks (useState, useRef, useEffect) for state management
- Session IDs are generated client-side using timestamps for simplicity
- Markdown support allows the AI to return formatted responses (lists, bold, links, etc.)

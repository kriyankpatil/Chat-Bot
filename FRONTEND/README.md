# Rule-Based Expert System Chatbot UI

A modern, responsive user interface for a rule-based expert system chatbot. This project provides a ChatGPT-like interface with unique styling and features specifically designed for rule-based AI systems.

## Features

- Clean, modern UI with responsive design
- Chat interface with user and bot messages
- File upload capability
- Chat history sidebar
- Profile icon and menu
- Rule-based response system
- Markdown support for bot responses

## Technologies Used

- React
- TypeScript
- Tailwind CSS
- Heroicons
- React Markdown

## Getting Started

### Prerequisites

- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:

```bash
npm install
```

3. Start the development server:

```bash
npm start
```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Project Structure

- `src/components/` - React components
  - `Header.tsx` - Top navigation bar with logo and profile
  - `Sidebar.tsx` - Chat history sidebar
  - `ChatContainer.tsx` - Main chat area
  - `ChatMessage.tsx` - Individual message component
  - `ChatInput.tsx` - User input area with send and upload buttons
- `src/App.tsx` - Main application component
- `src/index.css` - Tailwind CSS and custom styles

## Customization

You can customize the expert system's rules by modifying the `generateBotResponse` function in `App.tsx`. This function contains the logic for how the chatbot responds to different user inputs.

## License

MIT

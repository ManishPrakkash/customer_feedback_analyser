# Agent UI

This project is the frontend component of the Customer Feedback Analysis AI Agent. It is built using Next.js and integrates with the Vercel AI SDK to create generative user interfaces by streaming React Server Components to the client.

## Features

- Generative UI with React Server Components
- Integration with Vercel AI SDK
- Tailwind CSS for styling
- TypeScript support

## Getting Started

### Prerequisites

- Node.js
- npm, Yarn, or pnpm
- API keys for AI providers (e.g., OpenAI)

### Installation

1. Install the dependencies:

   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

2. Create a `.env.local` file and set your backend URL:

   ```bash
   echo NEXT_PUBLIC_AGENT_SERVICE_URL=http://127.0.0.1:8000 > .env.local
   ```

3. Run the development server:

   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. Open http://localhost:3000 with your browser to see the result.

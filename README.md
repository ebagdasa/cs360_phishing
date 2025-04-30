# OpenAI Assistant Server

A simple server for interacting with OpenAI's Assistant API.

## Features

- Express.js server to interact with OpenAI Assistant API
- Simple chat interface
- Persistent conversations using OpenAI Threads

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   npm install
   ```
3. Create a `.env` file in the root directory with your OpenAI API key and Assistant ID:
   ```
   OPENAI_API_KEY=your_api_key_here
   ASSISTANT_ID=asst_fh1JTqS8faXwsYZHNalfXR0L
   PORT=3000
   ```
4. Start the server:
   ```
   npm start
   ```
   Or for development with auto-restart:
   ```
   npm run dev
   ```

## Deployment

To deploy this on your VM:

1. Clone the repository on your VM
2. Install dependencies with `npm install`
3. Set up your `.env` file with your API key and Assistant ID
4. Start the server with `npm start` or use a process manager like PM2:
   ```
   npm install -g pm2
   pm2 start server.js --name "openai-assistant"
   ```
5. Set up a reverse proxy with Nginx or similar if needed

## Usage

- Visit `http://localhost:3000` (or your VM's address) to access the chat interface
- Type messages in the input field and press Send or hit Enter
- The assistant will respond based on how you've configured it in OpenAI

## API Endpoints

- `POST /api/threads` - Create a new thread
- `POST /api/threads/:threadId/messages` - Send a message to a thread
- `GET /api/threads/:threadId/messages` - Get all messages in a thread

## License

MIT

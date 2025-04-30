require('dotenv').config();
const express = require('express');
const OpenAI = require('openai');
const path = require('path');

const app = express();
const port = process.env.PORT || 3000;

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: process.env.MY_OPENAI_API_KEY,
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Store threads in memory
const threads = {};

// Create a new thread
app.post('/api/threads', async (req, res) => {
  try {
    const thread = await openai.beta.threads.create();
    res.json({ threadId: thread.id });
  } catch (error) {
    console.error('Error creating thread:', error);
    res.status(500).json({ error: 'Failed to create thread' });
  }
});

// Add a message to a thread and run the assistant
app.post('/api/threads/:threadId/messages', async (req, res) => {
  const { threadId } = req.params;
  const { message } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }
  
  try {
    // Add the message to the thread
    await openai.beta.threads.messages.create(threadId, {
      role: 'user',
      content: message,
    });
    
    // Run the assistant on the thread
    const run = await openai.beta.threads.runs.create(threadId, {
      assistant_id: process.env.ASSISTANT_ID,
    });
    
    // Poll for the run to complete
    let runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
    
    while (runStatus.status !== 'completed' && runStatus.status !== 'failed') {
      await new Promise(resolve => setTimeout(resolve, 1000));
      runStatus = await openai.beta.threads.runs.retrieve(threadId, run.id);
    }
    
    if (runStatus.status === 'failed') {
      return res.status(500).json({ error: 'Assistant run failed', details: runStatus });
    }
    
    // Get the messages
    const messages = await openai.beta.threads.messages.list(threadId);
    
    // Return the latest assistant message
    const assistantMessages = messages.data.filter(msg => msg.role === 'assistant');
    const latestMessage = assistantMessages.length > 0 ? assistantMessages[0] : null;
    
    res.json({ 
      message: latestMessage ? latestMessage.content.map(content => {
        if (content.type === 'text') return content.text.value;
        return `[${content.type} content]`;
      }).join('\\n') : null 
    });
  } catch (error) {
    console.error('Error processing message:', error);
    res.status(500).json({ error: 'Failed to process message' });
  }
});

// Get all messages in a thread
app.get('/api/threads/:threadId/messages', async (req, res) => {
  const { threadId } = req.params;
  
  try {
    const messages = await openai.beta.threads.messages.list(threadId);
    
    const formattedMessages = messages.data.map(msg => ({
      id: msg.id,
      role: msg.role,
      content: msg.content.map(content => {
        if (content.type === 'text') return content.text.value;
        return `[${content.type} content]`;
      }).join('\\n'),
      createdAt: msg.created_at
    }));
    
    res.json({ messages: formattedMessages });
  } catch (error) {
    console.error('Error retrieving messages:', error);
    res.status(500).json({ error: 'Failed to retrieve messages' });
  }
});

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
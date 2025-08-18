require('dotenv').config();
const express = require('express');
const OpenAI = require('openai');
const path = require('path');
const fs = require('fs');

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

// Store user sessions
const sessions = {};

// Load the questions from the offline verifier file
let puzzleQuestions;
try {
  const questionsData = fs.readFileSync(path.join(__dirname, 'public', 'offline_verifier_generation.json'), 'utf8');
  puzzleQuestions = JSON.parse(questionsData);
} catch (error) {
  console.error('Error loading puzzle questions:', error);
  puzzleQuestions = {};
}

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

// Puzzle page route
app.get('/puzzle', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'puzzle.html'));
});

// Helper to generate a session ID
const generateSessionId = () => {
  return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
};

// Helper to select random questions (without replacement)
const getRandomQuestions = (count) => {
  // Curated list (removed: '166', '167', '197')
  const questionIds = ['1', '154', '157', '159', '165', '168', '171', '173', '174', '178', '180', '182', '184', '185', '190', '191', '192', '200', '201', '202', '207', '208', '209', '212', '213'];
  console.log('Selecting random questions');
  console.log('Available question IDs:', questionIds);

  // Filter to only IDs that actually exist in the loaded questions
  const availableIds = questionIds.filter(id => Boolean(puzzleQuestions[id]));

  // Guard against requesting more than available
  const take = Math.min(count, availableIds.length);

  // Fisher–Yates shuffle for unbiased sampling without replacement
  const ids = availableIds.slice();
  for (let i = ids.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [ids[i], ids[j]] = [ids[j], ids[i]];
  }

  const selectedIds = ids.slice(0, take);

  return selectedIds.map(id => ({
    id,
    ...puzzleQuestions[id]
  }));
};

// Get a puzzle question
app.get('/api/get-puzzle', (req, res) => {
  try {
    // Generate a session ID if none exists
    let sessionId = req.query.sessionId;
    
    // Get the number of questions parameter (default to 5)
    const questionCount = parseInt(req.query.questionCount) || 5;
    
    // Get the required correct answers parameter (default to Math.ceil(questionCount * 0.4) or 2, whichever is higher)
    const minCorrectToReveal = parseInt(req.query.minCorrect);

    if (!sessionId || !sessions[sessionId]) {
      sessionId = generateSessionId();
      
      // Select the specified number of random questions for this session
      const randomQuestions = getRandomQuestions(questionCount);
      
      // Initialize the session
      sessions[sessionId] = {
        questions: randomQuestions,
        currentQuestionIndex: 0,
        correctAnswers: 0,
        completed: false,
        minCorrectToReveal: minCorrectToReveal
      };
    }
    
    const session = sessions[sessionId];
    
    // If session is already completed, return appropriate message
    if (session.completed) {
      return res.json({
        sessionId,
        completed: true,
        correctAnswers: session.correctAnswers,
        totalQuestions: session.questions.length,
        requiredCorrect: session.minCorrectToReveal,
        secretRevealed: session.correctAnswers >= session.minCorrectToReveal,
        secretMessage: session.correctAnswers >= session.minCorrectToReveal ? 'We are currently clean on OPSEC' : null
      });
    }
    
    // Get the current question
    const currentQuestion = session.questions[session.currentQuestionIndex];
    
    // Process the question text to make it more compact and wider
    let puzzleText = currentQuestion.question;
    
    // Remove extra horizontal lines if they exist
    puzzleText = puzzleText.replace(/\u2500{20,}/g, '_____');
    
    // Remove extra blank lines (keep only single blank lines)
    puzzleText = puzzleText.replace(/\n\s*\n\s*\n/g, '\n\n');
    
    // Format bullet points to be more compact
    puzzleText = puzzleText.replace(/\u2022\s*([^\n]+)/g, '• $1');
    
    // Make the numbered lists more compact if they exist
    puzzleText = puzzleText.replace(/(\d+)\.\s+([^\n]+)/g, '$1. $2');
    
    // Send the processed question text
    res.json({
      sessionId,
      questionNumber: session.currentQuestionIndex + 1,
      totalQuestions: session.questions.length,
      requiredCorrect: session.minCorrectToReveal,
      progress: {
        correctAnswers: session.correctAnswers,
        remainingQuestions: session.questions.length - session.currentQuestionIndex
      },
      puzzle: puzzleText
    });
  } catch (error) {
    console.error('Error retrieving puzzle question:', error);
    res.status(500).json({ error: 'Failed to get puzzle question' });
  }
});

// Puzzle answer verification endpoint
app.post('/api/check-answer', (req, res) => {
  const { answer, sessionId } = req.body;
  
  console.log('Received puzzle answer:', answer);
  
  if (!answer) {
    return res.status(400).json({ success: false, message: 'Please provide an answer' });
  }
  
  if (!sessionId || !sessions[sessionId]) {
    return res.status(400).json({ success: false, message: 'Invalid session. Please start a new puzzle.' });
  }
  
  try {
    const session = sessions[sessionId];
    
    // If session is already completed, return appropriate message
    if (session.completed) {
      return res.json({
        success: true,
        completed: true,
        correctAnswers: session.correctAnswers,
        totalQuestions: session.questions.length,
        requiredCorrect: session.minCorrectToReveal,
        secretRevealed: session.correctAnswers >= session.minCorrectToReveal,
        secretMessage: session.correctAnswers >= session.minCorrectToReveal ? 'We are currently clean on OPSEC' : null,
        message: session.correctAnswers >= session.minCorrectToReveal 
          ? 'You have solved enough puzzles! The secret is revealed!' 
          : `You have completed all puzzles, but did not solve enough correctly. You need at least ${session.minCorrectToReveal} correct answers.`
      });
    }
    
    // Get the current question
    const currentQuestion = session.questions[session.currentQuestionIndex];
    
    // Get correct answer
    const correctAnswer = currentQuestion.solution.toLowerCase().trim();
    const userAnswer = answer.trim().toLowerCase();
    
    console.log('Correct answer:', correctAnswer);
    console.log('User answer:', userAnswer);
    
    // Check if the answer is correct
    const isCorrect = userAnswer === correctAnswer;
    
    if (isCorrect) {
      console.log('Correct puzzle answer provided');
      session.correctAnswers++;
    } else {
      console.log('Incorrect puzzle answer provided:', answer);
    }
    
    // Move to the next question
    session.currentQuestionIndex++;
    
    // Check if all questions have been answered
    if (session.currentQuestionIndex >= session.questions.length) {
      session.completed = true;
      
      return res.json({
        success: true,
        correct: isCorrect,
        completed: true,
        correctAnswers: session.correctAnswers,
        totalQuestions: session.questions.length,
        requiredCorrect: session.minCorrectToReveal,
        secretRevealed: session.correctAnswers >= session.minCorrectToReveal,
        secretMessage: session.correctAnswers >= session.minCorrectToReveal ? 'We are currently clean on OPSEC' : null,
        message: session.correctAnswers >= session.minCorrectToReveal 
          ? 'You have solved enough puzzles! The secret is revealed!' 
          : `You have completed all puzzles, but did not solve enough correctly. You need at least ${session.minCorrectToReveal} correct answers.`
      });
    } else {
      // Send information about the next question
      const nextQuestion = session.questions[session.currentQuestionIndex];
      
      return res.json({
        success: true,
        correct: isCorrect,
        message: isCorrect ? 'Correct! Moving to the next puzzle.' : 'Incorrect. Moving to the next puzzle.',
        nextQuestion: {
          questionNumber: session.currentQuestionIndex + 1,
          totalQuestions: session.questions.length,
          progress: {
            correctAnswers: session.correctAnswers,
            remainingQuestions: session.questions.length - session.currentQuestionIndex
          }
        }
      });
    }
  } catch (error) {
    console.error('Error checking answer:', error);
    return res.status(500).json({ success: false, message: 'Error checking answer' });
  }
});

app.get('/api/get-secret-message', (req, res) => {
  res.json({ secretMessage: 'We are currently clean on OPSEC' });
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
// DOM elements
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

// Thread ID will be created per session
let threadId = null;

// Create a new thread
async function createThread() {
  try {
    const response = await fetch('/api/threads', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    threadId = data.threadId;
    return threadId;
  } catch (error) {
    console.error('Error creating thread:', error);
    displayErrorMessage('Failed to create a new chat thread. Please try again.');
  }
}

// Initialize the chat interface
async function initializeChat() {
  // Always create a new thread when the page loads
  await createThread();
  
  // Welcome message
  addMessageToDisplay('assistant', 'Hello! I\'m your AI assistant. How can I help you today?');
}

// Send a message and get a response
async function sendMessage(message) {
  // Don't send empty messages
  if (!message.trim()) return;
  
  // Add user message to display immediately
  addMessageToDisplay('user', message);
  
  // Clear input
  messageInput.value = '';
  
  // Create thread if needed (this should only happen if page was refreshed)
  if (!threadId) {
    await createThread();
  }
  
  // Show loading indicator
  const loadingElement = document.createElement('div');
  loadingElement.className = 'message assistant-message';
  loadingElement.innerHTML = 'Thinking...';
  chatMessages.appendChild(loadingElement);
  scrollToBottom();
  
  try {
    const response = await fetch(`/api/threads/${threadId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    });
    
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    
    const data = await response.json();
    
    // Remove loading indicator
    chatMessages.removeChild(loadingElement);
    
    // Add assistant response to display
    if (data.message) {
      addMessageToDisplay('assistant', data.message);
    }
  } catch (error) {
    console.error('Error sending message:', error);
    // Remove loading indicator
    chatMessages.removeChild(loadingElement);
    displayErrorMessage('Failed to get a response. Please try again.');
  }
}

// Add a message to the chat display
function addMessageToDisplay(role, content) {
  const messageElement = document.createElement('div');
  messageElement.className = `message ${role}-message`;
  
  // Process markdown (this is very basic, consider using a proper markdown library)
  let formattedContent = content
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
  
  messageElement.innerHTML = formattedContent;
  
  // Add timestamp
  const timeElement = document.createElement('span');
  timeElement.className = 'message-time';
  timeElement.textContent = new Date().toLocaleTimeString();
  messageElement.appendChild(timeElement);
  
  chatMessages.appendChild(messageElement);
  scrollToBottom();
}

// Display an error message
function displayErrorMessage(message) {
  const errorElement = document.createElement('div');
  errorElement.className = 'message error-message';
  errorElement.textContent = message;
  chatMessages.appendChild(errorElement);
  scrollToBottom();
}

// Scroll to the bottom of the chat
function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Start a new chat
async function startNewChat() {
  // Clear chat display
  chatMessages.innerHTML = '';
  
  // Create a new thread
  await createThread();
  
  // Add welcome message
  addMessageToDisplay('assistant', 'Hello! I\'m your AI assistant. How can I help you today?');
}

// Event listeners
sendButton.addEventListener('click', () => {
  sendMessage(messageInput.value);
});

messageInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage(messageInput.value);
  }
});

document.getElementById('newChatButton').addEventListener('click', startNewChat);

// Initialize
document.addEventListener('DOMContentLoaded', initializeChat);
import React, { useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import ChatContainer from './components/ChatContainer';
import { Message } from './components/ChatMessage';

// Interface for chat history
interface ChatHistory {
  id: string;
  title: string;
  date: string;
  messages: Message[];
}

// Add a new interface for file options
interface FileOption {
  id: string;
  name: string;
}

// Initial welcome message
const welcomeMessage: Message = {
  id: uuidv4(),
  content: "Hello! I'm ExpertBot, a rule-based expert system. How can I assist you today?",
  sender: 'bot',
  timestamp: new Date()
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>(() => {
    // Load chat history from localStorage if available
    const savedChats = localStorage.getItem('chatHistory');
    return savedChats ? JSON.parse(savedChats) : [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [fileOptions, setFileOptions] = useState<FileOption[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    // Check if user has a preference stored
    const savedMode = localStorage.getItem('darkMode');
    // Check if user prefers dark mode
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    return savedMode ? savedMode === 'true' : prefersDark;
  });
  
  // Save chat history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
  }, [chatHistory]);
  
  // Apply dark mode class to html element
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    // Save preference to localStorage
    localStorage.setItem('darkMode', isDarkMode.toString());
  }, [isDarkMode]);
  
  // Toggle dark mode
  const toggleDarkMode = () => {
    setIsDarkMode(!isDarkMode);
  };
  
  // Toggle sidebar visibility
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };
  
  // Handle new chat creation
  const handleNewChat = () => {
    // Save current chat if it has messages beyond the welcome message
    if (messages.length > 1) {
      saveChatToHistory();
    }
    
    // Reset messages to just the welcome message
    setMessages([welcomeMessage]);
    setSelectedChatId(null);
  };
  
  // Save current chat to history
  const saveChatToHistory = () => {
    if (messages.length <= 1) return; // Don't save empty chats
    
    // Find the first user message to use as the title
    const firstUserMessage = messages.find(msg => msg.sender === 'user');
    const title = firstUserMessage 
      ? firstUserMessage.content.substring(0, 30) + (firstUserMessage.content.length > 30 ? '...' : '')
      : 'New conversation';
    
    const now = new Date();
    
    if (selectedChatId) {
      // Update existing chat
      setChatHistory(prev => 
        prev.map(chat => 
          chat.id === selectedChatId 
            ? { ...chat, messages, title, date: formatDate(now) }
            : chat
        )
      );
    } else {
      // Create new chat
      const newChat: ChatHistory = {
        id: uuidv4(),
        title,
        date: formatDate(now),
        messages: [...messages]
      };
      
      setChatHistory(prev => [newChat, ...prev]);
      setSelectedChatId(newChat.id);
    }
  };
  
  // Format date for display
  const formatDate = (date: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
  };
  
  // Handle chat selection from history
  const handleSelectChat = (id: string) => {
    // Save current chat if it has messages and is different from the one we're selecting
    if (selectedChatId !== id && messages.length > 1) {
      saveChatToHistory();
    }
    
    setSelectedChatId(id);
    // Load the chat messages from the selected chat
    const selectedChat = chatHistory.find(chat => chat.id === id);
    if (selectedChat) {
      setMessages(selectedChat.messages);
    }
  };
  
  // Handle chat deletion
  const handleDeleteChat = (id: string, event: React.MouseEvent) => {
    // Stop the click event from bubbling up to the parent (which would select the chat)
    event.stopPropagation();
    
    // Remove the chat from history
    setChatHistory(prev => prev.filter(chat => chat.id !== id));
    
    // If the deleted chat was selected, reset to a new chat
    if (selectedChatId === id) {
      setMessages([welcomeMessage]);
      setSelectedChatId(null);
    }
  };
  
  // Check if a message is a greeting
  const isGreeting = (message: string): boolean => {
    const greetings = ['hi', 'hello', 'hey', 'hii', 'hiii', 'hiiii', 'helo', 'hallo', 'heya', 'howdy', 'greetings'];
    return greetings.some(greeting => 
      message.toLowerCase().trim() === greeting || 
      message.toLowerCase().trim().startsWith(greeting + ' '));
  };

  // Get fixed response for greeting
  const getGreetingResponse = (): string => {
    const responses = [
      "Hello! I'm your Gujarat Civil Services expert system. How can I help you with rules and regulations today?",
      "Hi there! I can assist you with Gujarat Civil Services rules, disciplinary procedures, and related information. What would you like to know?",
      "Greetings! I'm here to help you understand Gujarat Civil Services rules and regulations. What can I assist you with?",
      "Hello! I'm your expert system for Gujarat Civil Services. What questions do you have about the rules and regulations?",
      "Hi! I can help you with information about Gujarat Civil Services rules, disciplinary procedures, and related matters. How may I assist you?"
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };
  
  // Handle sending a message
  const handleSendMessage = (content: string) => {
    const userMessage: Message = {
      id: uuidv4(),
      content,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    
    // Check if message is a greeting
    if (isGreeting(content)) {
      const botResponse: Message = {
        id: uuidv4(),
        content: getGreetingResponse(),
        sender: 'bot',
        timestamp: new Date()
      };
      
      setMessages((prevMessages) => {
        const newMessages = [...prevMessages, botResponse];
        
        // Save chat to history
        setTimeout(() => {
          saveChatToHistory();
        }, 0);
        
        return newMessages;
      });
      return; // Don't proceed with API call
    }
    
    setIsLoading(true);
    
    // Log what we're sending to the backend
    const requestBody = { 
      query: content,
      selected_file: selectedFile 
    };
    console.log('Request body being sent to backend:', JSON.stringify(requestBody));
    
    // First try the test endpoint to see if request is being sent properly
    fetch('http://localhost:8002/api/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(requestBody),
    })
      .then(response => {
        console.log('Test endpoint response status:', response.status);
        if (!response.ok) {
          console.error('Test endpoint error:', response.status, response.statusText);
        }
        return response.json();
      })
      .then(data => {
        console.log('Test endpoint response data:', data);
        
        // Now try the real query endpoint
        return fetch('http://localhost:8002/api/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });
      })
      .then(response => {
        console.log('Query endpoint response status:', response.status);
        if (!response.ok) {
          throw new Error(`Network response error: ${response.status} - ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Query endpoint response data:', data);
        
        // Check if the response contains file options
        if (data && data.file_options && data.file_options.length > 0) {
          // Set the file options for user to select
          setFileOptions(data.file_options);
          
          // Add bot message asking to select a file
          const botResponse: Message = {
            id: uuidv4(),
            content: data.enhanced_response || "I found information in multiple files. Please select which one you want to use:",
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages, botResponse];
            
            // Save chat to history
            setTimeout(() => {
              saveChatToHistory();
            }, 0);
            
            return newMessages;
          });
        }
        // Check if the response contains the expected data
        else if (data && data.response) {
          // Reset file options and selected file if a response is received
          setFileOptions([]);
          setSelectedFile(null);
          
          const botResponse: Message = {
            id: uuidv4(),
            content: data.response,
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages, botResponse];
            
            // Save chat to history after receiving a response
            setTimeout(() => {
              saveChatToHistory();
            }, 0);
            
            return newMessages;
          });
        } else if (data && (data.exact_match || data.ai_response || data.enhanced_response)) {
          // Reset file options and selected file if a response is received
          setFileOptions([]);
          setSelectedFile(null);
          
          // Only display the enhanced response
          const responseContent = data.enhanced_response || "No enhanced response available.";
          
          const botResponse: Message = {
            id: uuidv4(),
            content: responseContent,
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages, botResponse];
            
            // Save chat to history after receiving a response
            setTimeout(() => {
              saveChatToHistory();
            }, 0);
            
            return newMessages;
          });
        } else {
          throw new Error('Invalid response format from server');
        }
      })
      .catch(error => {
        console.error('Error in API call chain:', error);
        
        // Fallback to local response in case of error
        const errorResponse: Message = {
          id: uuidv4(),
          content: "I'm having trouble connecting to my knowledge base. Please check the browser console for details and try again later.",
          sender: 'bot',
          timestamp: new Date()
        };
        
        setMessages((prevMessages) => {
          const newMessages = [...prevMessages, errorResponse];
          
          // Still save the chat even with an error response
          setTimeout(() => {
            saveChatToHistory();
          }, 0);
          
          return newMessages;
        });
      })
      .finally(() => {
        setIsLoading(false);
      });
  };
  
  // Handle file selection
  const handleFileSelect = (fileId: string) => {
    console.log(`File selected: ${fileId}`);
    setSelectedFile(fileId);
    
    // Send the same query again but with the selected file
    const lastUserMessage = messages.filter(m => m.sender === 'user').pop();
    
    if (lastUserMessage) {
      setIsLoading(true);
      
      // Create a message indicating which file was selected
      const fileOption = fileOptions.find(option => option.id === fileId);
      const fileName = fileOption ? fileOption.name : fileId;
      
      console.log(`Selected file: ${fileName} (${fileId})`);
      
      const selectionMessage: Message = {
        id: uuidv4(),
        content: `You selected: ${fileName}`,
        sender: 'user',
        timestamp: new Date()
      };
      
      setMessages((prevMessages) => [...prevMessages, selectionMessage]);
      
      // Log what we're sending to the backend
      const requestBody = { 
        query: lastUserMessage.content,
        selected_file: fileId 
      };
      console.log('File selection - Request body being sent to backend:', JSON.stringify(requestBody));
      
      // Send query with selected file
      fetch('http://localhost:8002/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })
        .then(response => {
          console.log('File selection - Response status:', response.status);
          if (!response.ok) {
            throw new Error(`Network response error: ${response.status} - ${response.statusText}`);
          }
          return response.json();
        })
        .then(data => {
          console.log('File selection - Response data:', data);
          
          // Clear file options and reset selected file after getting response
          setFileOptions([]);
          setSelectedFile(null);
          
          const botResponse: Message = {
            id: uuidv4(),
            content: data.enhanced_response || data.response || "No response available.",
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages((prevMessages) => {
            const newMessages = [...prevMessages, botResponse];
            
            // Save chat to history
            setTimeout(() => {
              saveChatToHistory();
            }, 0);
            
            return newMessages;
          });
        })
        .catch(error => {
          console.error('Error fetching response for selected file:', error);
          
          // Reset selected file on error
          setSelectedFile(null);
          setFileOptions([]);
          
          const errorResponse: Message = {
            id: uuidv4(),
            content: "I'm having trouble retrieving information from the selected file. Please check the browser console for details and try again.",
            sender: 'bot',
            timestamp: new Date()
          };
          
          setMessages((prevMessages) => [...prevMessages, errorResponse]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  };
  
  return (
    <div className="h-screen flex flex-col bg-background dark:bg-gray-900">
      <Header 
        toggleSidebar={toggleSidebar} 
        isDarkMode={isDarkMode} 
        toggleDarkMode={toggleDarkMode} 
      />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar for mobile - shown/hidden with state */}
        <div className={`fixed inset-0 z-20 transition-opacity duration-300 ${sidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
          <div className="absolute inset-0 bg-gray-600 opacity-75" onClick={toggleSidebar}></div>
          <div className="absolute inset-y-0 left-0 max-w-xs w-full">
            <Sidebar
              isOpen={true}
              chatHistory={chatHistory}
              onNewChat={handleNewChat}
              onSelectChat={handleSelectChat}
              onDeleteChat={handleDeleteChat}
              selectedChatId={selectedChatId}
            />
          </div>
        </div>
        
        {/* Sidebar for desktop - always visible */}
        <div className="hidden lg:block w-64 flex-shrink-0">
          <Sidebar
            isOpen={true}
            chatHistory={chatHistory}
            onNewChat={handleNewChat}
            onSelectChat={handleSelectChat}
            onDeleteChat={handleDeleteChat}
            selectedChatId={selectedChatId}
          />
        </div>
        
        {/* Main chat area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <ChatContainer
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
          />
          
          {/* File options panel */}
          {fileOptions.length > 0 && (
            <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
              <div className="mb-2 text-sm text-gray-600 dark:text-gray-400">
                Please select a file to get information from:
              </div>
              <div className="flex flex-wrap gap-2">
                {fileOptions.map((option) => (
                  <button
                    key={option.id}
                    onClick={() => handleFileSelect(option.id)}
                    className="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm"
                  >
                    {option.name}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;

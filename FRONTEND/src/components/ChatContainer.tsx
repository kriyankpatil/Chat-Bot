import React, { useRef, useEffect } from 'react';
import ChatMessage, { Message } from './ChatMessage';
import ChatInput from './ChatInput';

interface ChatContainerProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatContainer: React.FC<ChatContainerProps> = ({
  messages,
  onSendMessage,
  isLoading
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-white dark:bg-gray-800">
          <div className="h-16 w-16 rounded-full bg-secondary flex items-center justify-center text-white font-bold text-2xl mb-4">
            E
          </div>
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white mb-2">Welcome to ExpertBot</h2>
          <p className="text-gray-600 dark:text-gray-300 max-w-md mb-6">
            I'm a rule-based expert system designed to help you solve problems in my domain of expertise.
            Ask me anything!
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
            {[
              "What can you help me with?",
              "How does a rule-based system work?",
              "What are your capabilities?",
              "Show me an example of your reasoning"
            ].map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSendMessage(suggestion)}
                className="btn-outline text-left p-4 dark:bg-gray-700 dark:text-gray-100 dark:border-gray-600 dark:hover:bg-gray-600"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto p-4 bg-white dark:bg-gray-800">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          <div ref={messagesEndRef} />
          
          {isLoading && (
            <div className="flex justify-start mb-4">
              <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-white font-bold mr-2">
                E
              </div>
              <div className="bot-message dark:bg-gray-700 dark:text-gray-100">
                <div className="flex space-x-2">
                  <div className="h-2 w-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="h-2 w-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  <div className="h-2 w-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '600ms' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      <ChatInput
        onSendMessage={onSendMessage}
        isLoading={isLoading}
      />
    </div>
  );
};

export default ChatContainer; 
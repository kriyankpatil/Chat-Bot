import React, { useState, FormEvent, KeyboardEvent } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
      <form onSubmit={handleSubmit} className="flex flex-col">
        <div className="relative">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask the expert system..."
            className="w-full border border-gray-300 dark:border-gray-600 rounded-lg py-3 px-4 pr-16 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-100"
            rows={1}
            disabled={isLoading}
          />
          
          <div className="absolute right-2 bottom-2">
            <button
              type="submit"
              disabled={!message.trim() || isLoading}
              className={`p-2 rounded-full ${
                message.trim() && !isLoading
                  ? 'bg-primary text-white hover:bg-primary-dark'
                  : 'bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400 cursor-not-allowed'
              }`}
            >
              <PaperAirplaneIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
        
        <div className="text-xs text-gray-500 dark:text-gray-400 mt-2 text-center">
          The expert system uses rule-based reasoning to provide answers
        </div>
      </form>
    </div>
  );
};

export default ChatInput; 
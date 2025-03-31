import React from 'react';
import { PlusIcon, ChatBubbleLeftRightIcon, TrashIcon } from '@heroicons/react/24/solid';

interface ChatHistory {
  id: string;
  title: string;
  date: string;
  messages?: any[]; // Added to match the updated interface in App.tsx
}

interface SidebarProps {
  isOpen: boolean;
  chatHistory: ChatHistory[];
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
  onDeleteChat: (id: string, event: React.MouseEvent) => void;
  selectedChatId: string | null;
}

const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  chatHistory,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  selectedChatId
}) => {
  if (!isOpen) return null;

  return (
    <div className="w-64 bg-white dark:bg-gray-800 h-full border-r border-gray-200 dark:border-gray-700 flex flex-col">
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full btn-primary flex items-center justify-center"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          New Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="px-3 py-2">
          <h2 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Recent Chats</h2>
          <div className="space-y-1">
            {chatHistory.length > 0 ? (
              chatHistory.map((chat) => (
                <div
                  key={chat.id}
                  className={`sidebar-item group ${selectedChatId === chat.id ? 'active' : ''}`}
                >
                  <button
                    onClick={() => onSelectChat(chat.id)}
                    className="flex-1 flex items-center text-left py-2 px-2 rounded-md"
                  >
                    <ChatBubbleLeftRightIcon className="h-5 w-5 mr-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium dark:text-gray-200 truncate">{chat.title}</div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{chat.date}</div>
                    </div>
                  </button>
                  <button
                    onClick={(e) => onDeleteChat(chat.id, e)}
                    className="p-2 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                    aria-label="Delete chat"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              ))
            ) : (
              <div className="text-center py-4 text-sm text-gray-500 dark:text-gray-400">
                No recent chats
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-2">Rule-Based Expert System</div>
        <div className="text-xs text-gray-400 dark:text-gray-500">Version 1.0.0</div>
      </div>
    </div>
  );
};

export default Sidebar; 
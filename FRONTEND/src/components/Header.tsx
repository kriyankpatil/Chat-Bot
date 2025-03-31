import React, { useState } from 'react';
import { Bars3Icon } from '@heroicons/react/24/solid';
import DarkModeToggle from './DarkModeToggle';
import ShareButton from './ShareButton';

interface HeaderProps {
  toggleSidebar: () => void;
  isDarkMode: boolean;
  toggleDarkMode: () => void;
}

const Header: React.FC<HeaderProps> = ({ toggleSidebar, isDarkMode, toggleDarkMode }) => {
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  const handleShare = () => {
    console.log('Conversation shared!');
    // In a real app, this would trigger analytics or other actions
  };
  
  return (
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 py-3 px-4 flex items-center justify-between">
      <div className="flex items-center">
        <button 
          onClick={toggleSidebar}
          className="mr-4 p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 lg:hidden"
        >
          <Bars3Icon className="h-6 w-6 text-gray-500 dark:text-gray-300" />
        </button>
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-secondary flex items-center justify-center text-white font-bold mr-2">
            E
          </div>
          <h1 className="text-xl font-semibold text-gray-800 dark:text-white">ExpertBot</h1>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <ShareButton onShare={handleShare} />
        <DarkModeToggle isDarkMode={isDarkMode} toggleDarkMode={toggleDarkMode} />
        
        <div className="relative">
          <button 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
            className="h-10 w-10 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center text-white font-bold"
          >
            US
          </button>
          
          {showProfileMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-10 border border-gray-200 dark:border-gray-700">
              <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700">Your Profile</button>
              <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700">Settings</button>
              <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700">Sign out</button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header; 
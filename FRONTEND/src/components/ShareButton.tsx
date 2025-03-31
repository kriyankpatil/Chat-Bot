import React, { useState } from 'react';
import { ShareIcon, ClipboardDocumentIcon, CheckIcon } from '@heroicons/react/24/solid';

interface ShareButtonProps {
  onShare: () => void;
}

const ShareButton: React.FC<ShareButtonProps> = ({ onShare }) => {
  const [showShareOptions, setShowShareOptions] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopyLink = () => {
    // In a real app, this would generate a shareable link
    const dummyLink = 'https://expertbot.example.com/chat/' + Math.random().toString(36).substring(2, 10);
    navigator.clipboard.writeText(dummyLink);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowShareOptions(!showShareOptions)}
        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        aria-label="Share conversation"
      >
        <ShareIcon className="h-5 w-5 text-gray-500 dark:text-gray-300" />
      </button>

      {showShareOptions && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 z-10 border border-gray-200 dark:border-gray-700">
          <button 
            onClick={() => {
              handleCopyLink();
              onShare();
            }}
            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            {copied ? (
              <>
                <CheckIcon className="h-5 w-5 mr-2 text-green-500" />
                <span>Copied!</span>
              </>
            ) : (
              <>
                <ClipboardDocumentIcon className="h-5 w-5 mr-2" />
                <span>Copy link</span>
              </>
            )}
          </button>
        </div>
      )}
    </div>
  );
};

export default ShareButton; 
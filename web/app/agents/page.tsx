'use client';

import { useState, useRef, useEffect } from 'react';
import { FiSend, FiUser, FiCpu, FiLoader } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import { format } from 'date-fns';

interface Message {
  id: string;
  role: 'user' | 'system' | 'agent';
  content: string;
  timestamp: Date;
}

export default function AgentsPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'agent',
      content: 'Hello! I\'m your Afrobeats.no assistant. Ask me about DJs, events, playlists, or anything related to Afrobeats and Amapiano in Oslo!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Create a unique ID for the message
    const userMessageId = Date.now().toString();

    // Add user message to the chat
    const userMessage: Message = {
      id: userMessageId,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send query to API
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: input }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from agent system');
      }

      const data = await response.json();

      // Add agent response to chat
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'agent',
        content: data.response || 'Sorry, I couldn\'t process your request. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error communicating with agent system:', error);

      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'system',
        content: 'Sorry, there was an error processing your request. Please try again later.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date: Date) => {
    return format(date, 'HH:mm');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-800 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-2 text-center">Afrobeats.no AI Assistant</h1>
        <p className="text-xl text-center mb-8 opacity-80">
          Your guide to Afrobeats and Amapiano in Oslo
        </p>

        <div className="max-w-4xl mx-auto bg-black/30 backdrop-blur-lg rounded-xl overflow-hidden shadow-2xl border border-white/10">
          {/* Messages area */}
          <div className="h-[60vh] overflow-y-auto p-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`mb-4 flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-md ${
                      message.role === 'user'
                        ? 'bg-purple-600 text-white ml-12'
                        : message.role === 'agent'
                          ? 'bg-indigo-900/70 text-white border border-indigo-600/50 mr-12'
                          : 'bg-red-900/70 text-white border border-red-600/50 mr-12'
                    }`}
                  >
                    <div className="flex items-center gap-2 text-sm opacity-75 mb-1">
                      {message.role === 'user' ? (
                        <>
                          <span>You</span>
                          <FiUser />
                        </>
                      ) : message.role === 'agent' ? (
                        <>
                          <FiCpu />
                          <span>Afrobeats.no Assistant</span>
                        </>
                      ) : (
                        <>
                          <span>System</span>
                        </>
                      )}
                      <span className="ml-auto text-xs">{formatTime(message.timestamp)}</span>
                    </div>
                    <div className="whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                </motion.div>
              ))}

              {isLoading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex justify-start mb-4"
                >
                  <div className="bg-indigo-900/70 text-white border border-indigo-600/50 rounded-2xl px-4 py-3 shadow-md mr-12 flex items-center gap-2">
                    <FiLoader className="animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-white/10 p-4 bg-black/40">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={isLoading}
                placeholder="Ask about DJs, events, music recommendations..."
                className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500 text-white placeholder:text-white/50"
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800/50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors duration-200 flex items-center gap-2"
              >
                <FiSend />
                <span className="hidden sm:inline">Send</span>
              </button>
            </form>
          </div>
        </div>

        <div className="max-w-4xl mx-auto mt-8 text-center text-white/70 text-sm">
          <p>You can ask about DJ bookings, upcoming events, playlist recommendations, or general information about Afrobeats and Amapiano music.</p>
        </div>
      </div>
    </div>
  );
}
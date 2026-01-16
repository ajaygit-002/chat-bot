import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import ChatBox from './components/ChatBox'
import LanguageSelect from './components/LanguageSelect'

const BACKEND_URL = 'http://localhost:8000'

export default function App() {
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [language, setLanguage] = useState('English')
  const [error, setError] = useState(null)
  const [apiConnected, setApiConnected] = useState(false)
  const messagesEndRef = useRef(null)

  // Check backend connection on mount
  useEffect(() => {
    checkBackendConnection()
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const checkBackendConnection = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/health`)
      setApiConnected(true)
      setError(null)
    } catch (err) {
      setApiConnected(false)
      setError('Backend is not running. Please start the FastAPI server.')
    }
  }

  const handleSendMessage = async (message) => {
    if (!message.trim()) return

    // Clear error on new message
    setError(null)

    // Add user message to state
    const userMessage = { role: 'user', content: message }
    setMessages(prev => [...prev, userMessage])
    setLoading(true)

    try {
      // Prepare conversation history (last 10 messages)
      const conversationHistory = messages.slice(-9).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Send request to backend
      const response = await axios.post(`${BACKEND_URL}/chat`, {
        message: message,
        language: language,
        conversation_history: conversationHistory
      })

      // Add bot response
      const botMessage = {
        role: 'assistant',
        content: response.data.reply
      }

      setMessages(prev => {
        const updated = [...prev, botMessage]
        // Keep only last 10 messages
        return updated.slice(-10)
      })
    } catch (err) {
      console.error('Error sending message:', err)
      
      if (!apiConnected) {
        setError('Backend connection failed. Please ensure the FastAPI server is running on http://localhost:8000')
      } else if (err.response?.status === 429) {
        setError('⚠️ API Rate Limited: You\'ve exceeded your OpenAI quota. Please check your plan and billing at https://platform.openai.com/account/billing/overview')
      } else if (err.response?.status === 400) {
        setError(`Invalid request: ${err.response.data?.detail || 'Please try again.'}`)
      } else if (err.response?.status === 401) {
        setError('❌ Authentication Error: Invalid OpenAI API key. Please check your .env file.')
      } else if (err.response?.status === 500) {
        const errorDetail = err.response.data?.detail || 'Unknown error'
        // Extract OpenAI error message
        if (errorDetail.includes('quota')) {
          setError('❌ OpenAI Quota Exceeded: You\'ve reached your API usage limit. Visit https://platform.openai.com/account/billing/overview to upgrade.')
        } else if (errorDetail.includes('Unauthorized')) {
          setError('❌ OpenAI Authentication Failed: Invalid or missing API key. Check your .env file.')
        } else {
          setError(`Server error: ${errorDetail}`)
        }
      } else if (err.code === 'ERR_NETWORK') {
        setError('Network error. Please check your connection and ensure the backend server is running.')
      } else {
        setError(`Error: ${err.message}`)
      }

      // Remove the user message if there's an error
      setMessages(prev => prev.slice(0, -1))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full h-screen flex flex-col bg-gradient-to-br from-slate-900 via-slate-900 to-slate-800">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/20 rounded-full mix-blend-multiply filter blur-3xl animate-fade-in"></div>
        <div className="absolute -bottom-8 right-1/4 w-80 h-80 bg-pink-500/20 rounded-full mix-blend-multiply filter blur-3xl animate-fade-in" style={{ animationDelay: '2s' }}></div>
      </div>

      {/* Header */}
      <header className="relative z-10 glass-md border-b border-white/10 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center">
              <span className="text-xl font-bold text-white">✨</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold gradient-text">NovaChat AI</h1>
              <p className="text-xs text-slate-400">Powered by Ollama (Free Local AI)</p>
            </div>
          </div>
          <LanguageSelect language={language} onChange={setLanguage} />
        </div>

        {/* Connection Status */}
        <div className="px-4 py-2 text-xs">
          {apiConnected ? (
            <span className="text-green-400 flex items-center space-x-1">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
              <span>Connected to backend</span>
            </span>
          ) : (
            <span className="text-yellow-400 flex items-center space-x-1">
              <span className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></span>
              <span>Connecting to backend...</span>
            </span>
          )}
        </div>
      </header>

      {/* Main Chat Container */}
      <main className="relative z-10 flex-1 overflow-hidden flex flex-col">
        {/* Error Message */}
        {error && (
          <div className="mx-4 mt-4 p-4 glass rounded-xl border border-red-500/50 bg-red-500/10 text-red-300 text-sm animate-slide-up">
            <div className="flex items-start space-x-3">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="font-semibold">Connection Error</p>
                <p className="text-xs mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Messages Container */}
        <ChatBox messages={messages} loading={loading} />

        {/* Reference to auto-scroll */}
        <div ref={messagesEndRef} />
      </main>

      {/* Message Input */}
      <footer className="relative z-10 border-t border-white/10 glass-md backdrop-blur-md">
        <div className="max-w-4xl mx-auto w-full px-4 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              placeholder="Type your message here... (Press Enter to send)"
              className="flex-1 bg-white/10 border border-white/20 rounded-full px-6 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              onKeyPress={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage(e.target.value)
                  e.target.value = ''
                }
              }}
              disabled={!apiConnected || loading}
            />
            <button
              onClick={(e) => {
                const input = e.target.previousElementSibling
                handleSendMessage(input.value)
                input.value = ''
              }}
              disabled={!apiConnected || loading}
              className="btn-glass bg-gradient-to-br from-indigo-600 to-pink-600 hover:from-indigo-700 hover:to-pink-700 text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '...' : 'Send'}
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-2 text-center">
            Messages are stored in Pinecone for context awareness • Last 10 messages kept in memory
          </p>
        </div>
      </footer>
    </div>
  )
}

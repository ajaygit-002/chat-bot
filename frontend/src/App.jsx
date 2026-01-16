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
      // Prepare conversation history (REDUCED to last 5 messages for speed)
      const conversationHistory = messages.slice(-5).map(msg => ({
        role: msg.role,
        content: msg.content
      }))

      // Use streaming endpoint for real-time response
      const response = await fetch(`${BACKEND_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          language: language,
          conversation_history: conversationHistory
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      // Create an empty bot message and stream tokens into it
      let botContent = ''
      setMessages(prev => [...prev, { role: 'assistant', content: '' }])

      // Read the streaming response
      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                if (data.token) {
                  // Stream token into the bot message
                  botContent += data.token
                  setMessages(prev => {
                    const updated = [...prev]
                    updated[updated.length - 1].content = botContent
                    return updated
                  })
                } else if (data.error) {
                  setError(`Error: ${data.error}`)
                }
              } catch (e) {
                // Skip invalid JSON
              }
            }
          }
        }
      } finally {
        reader.releaseLock()
      }

      // Keep only last 10 messages
      setMessages(prev => prev.slice(-10))
    } catch (err) {
      console.error('Error sending message:', err)
      
      if (!apiConnected) {
        setError('Backend connection failed. Please ensure the FastAPI server is running on http://localhost:8000')
      } else if (err.message.includes('401')) {
        setError('❌ Authentication Error: Invalid Ollama configuration.')
      } else if (err.message.includes('500')) {
        setError(`Server error: ${err.message}`)
      } else if (err.message.includes('ERR_NETWORK') || err.name === 'TypeError') {
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

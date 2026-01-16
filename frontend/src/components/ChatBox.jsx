import React, { useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import Loader from './Loader'

export default function ChatBox({ messages, loading }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  return (
    <div className="flex-1 overflow-y-auto px-4 py-8 space-y-4 max-w-4xl mx-auto w-full">
      {messages.length === 0 ? (
        <div className="h-full flex flex-col items-center justify-center text-center">
          <div className="w-20 h-20 mb-6 rounded-full bg-gradient-to-br from-indigo-600/20 to-pink-600/20 flex items-center justify-center border border-indigo-500/30">
            <span className="text-4xl">💬</span>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Start Your Conversation</h2>
          <p className="text-slate-400 max-w-sm">
            Chat with NovaChat AI - an intelligent assistant powered by GPT-3.5 with memory awareness and multi-language support.
          </p>
        </div>
      ) : (
        <>
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              message={message}
              isUser={message.role === 'user'}
            />
          ))}
          
          {loading && <Loader />}
          
          <div ref={endRef} />
        </>
      )}
    </div>
  )
}

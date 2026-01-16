import React from 'react'

export default function MessageBubble({ message, isUser }) {
  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-slide-up`}
    >
      {!isUser && (
        <div className="mr-3 flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-600 to-pink-600 flex items-center justify-center text-sm font-bold">
            AI
          </div>
        </div>
      )}
      
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-gradient-to-br from-indigo-600 to-pink-600 text-white rounded-br-none'
            : 'glass text-slate-100 rounded-bl-none'
        }`}
      >
        <p className="text-sm lg:text-base leading-relaxed break-words">
          {message.content}
        </p>
      </div>

      {isUser && (
        <div className="ml-3 flex-shrink-0">
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold">
            👤
          </div>
        </div>
      )}
    </div>
  )
}

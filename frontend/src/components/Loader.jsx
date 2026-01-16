import React from 'react'

export default function Loader() {
  return (
    <div className="flex justify-start animate-slide-up">
      <div className="mr-3 flex-shrink-0">
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-600 to-pink-600 flex items-center justify-center text-sm font-bold">
          AI
        </div>
      </div>
      
      <div className="glass text-slate-100 rounded-2xl rounded-bl-none px-4 py-3 flex items-center space-x-2">
        <span className="text-sm">Bot is typing</span>
        <div className="flex space-x-1">
          <span className="w-2 h-2 bg-slate-300 rounded-full dot-pulse"></span>
          <span className="w-2 h-2 bg-slate-300 rounded-full dot-pulse"></span>
          <span className="w-2 h-2 bg-slate-300 rounded-full dot-pulse"></span>
        </div>
      </div>
    </div>
  )
}

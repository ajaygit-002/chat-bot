import React, { useState, useRef, useEffect } from 'react'

const languages = [
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi' },
  { code: 'te', name: 'Telugu' },
  { code: 'ta', name: 'Tamil' },
  { code: 'kn', name: 'Kannada' },
  { code: 'ml', name: 'Malayalam' },
  { code: 'fr', name: 'French' },
  { code: 'es', name: 'Spanish' },
  { code: 'de', name: 'German' },
  { code: 'ja', name: 'Japanese' },
  { code: 'ko', name: 'Korean' },
  { code: 'ar', name: 'Arabic' },
]

export default function LanguageSelect({ language, onChange }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="glass px-4 py-2 rounded-full text-sm font-medium flex items-center space-x-2 hover:bg-white/10 transition-all"
      >
        <span>🌐</span>
        <span>{language}</span>
        <span className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 glass rounded-xl border border-white/10 shadow-lg z-20 animate-slide-up">
          <div className="max-h-64 overflow-y-auto p-2">
            {languages.map((lang) => (
              <button
                key={lang.code}
                onClick={() => {
                  onChange(lang.name)
                  setIsOpen(false)
                }}
                className={`w-full text-left px-4 py-2 rounded-lg transition-all ${
                  language === lang.name
                    ? 'bg-gradient-to-r from-indigo-600 to-pink-600 text-white'
                    : 'text-slate-300 hover:bg-white/10'
                }`}
              >
                <span className="mr-2">{lang.name === 'English' ? '🇺🇸' : lang.name === 'Hindi' ? '🇮🇳' : lang.name === 'Telugu' ? '🇮🇳' : lang.name === 'Tamil' ? '🇮🇳' : lang.name === 'Kannada' ? '🇮🇳' : lang.name === 'Malayalam' ? '🇮🇳' : lang.name === 'French' ? '🇫🇷' : lang.name === 'Spanish' ? '🇪🇸' : lang.name === 'German' ? '🇩🇪' : lang.name === 'Japanese' ? '🇯🇵' : lang.name === 'Korean' ? '🇰🇷' : lang.name === 'Arabic' ? '🇸🇦' : '🌍'}</span>
                {lang.name}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

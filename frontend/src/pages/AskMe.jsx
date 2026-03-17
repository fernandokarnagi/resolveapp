import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react'
import api from '../api/axios'

export default function AskMe() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hi! I'm your facility management assistant. Ask me anything about cleaning schedules, preventive or corrective maintenance, security roster, cases, vendors, customers, contracts, or buildings.",
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const question = input.trim()
    if (!question || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: question }])
    setInput('')
    setLoading(true)

    try {
      const { data } = await api.post('/api/ask', { question })
      setMessages((prev) => [...prev, { role: 'assistant', content: data.answer }])
    } catch (err) {
      const detail = err.response?.data?.detail || 'Something went wrong. Please try again.'
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${detail}`, error: true },
      ])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-4rem)]">
      {/* Header */}
      <div className="flex items-center gap-3 px-6 py-4 border-b border-slate-200 bg-white flex-shrink-0">
        <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center">
          <Sparkles size={18} className="text-white" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-slate-800">Ask Me</h1>
          <p className="text-xs text-slate-500">AI-powered facility management assistant</p>
        </div>
        <span className="ml-auto flex items-center gap-1.5 text-xs text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full font-medium">
          <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
          Gemini 2.0 Flash Lite
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-4 bg-slate-50">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 bg-white border-t border-slate-200 px-4 py-3">
        <div className="flex items-end gap-2 bg-slate-100 rounded-xl px-4 py-2">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about your facility data…"
            disabled={loading}
            className="flex-1 bg-transparent text-sm text-slate-800 placeholder-slate-400 resize-none outline-none min-h-[24px] max-h-32 py-0.5 disabled:opacity-50"
            style={{ lineHeight: '1.5rem' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 w-8 h-8 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed rounded-lg flex items-center justify-center transition-colors"
          >
            {loading ? (
              <Loader2 size={14} className="text-white animate-spin" />
            ) : (
              <Send size={14} className="text-white" />
            )}
          </button>
        </div>
        <p className="text-center text-xs text-slate-400 mt-2">
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}

function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? 'bg-blue-600' : 'bg-slate-700'
        }`}
      >
        {isUser ? (
          <User size={14} className="text-white" />
        ) : (
          <Bot size={14} className="text-white" />
        )}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[75%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? 'bg-blue-600 text-white rounded-tr-sm'
            : message.error
            ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-sm'
            : 'bg-white text-slate-800 shadow-sm border border-slate-100 rounded-tl-sm'
        }`}
      >
        {message.content}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
        <Bot size={14} className="text-white" />
      </div>
      <div className="bg-white border border-slate-100 shadow-sm rounded-2xl rounded-tl-sm px-4 py-3 flex items-center gap-1">
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
        <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
      </div>
    </div>
  )
}

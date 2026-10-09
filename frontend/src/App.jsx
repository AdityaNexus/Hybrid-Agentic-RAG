import { useState, useRef, useEffect } from 'react'
import { Send, FileUp, Loader2, Sparkles, Database, ShieldCheck, Activity, Route, Code, Trash2, X, List } from 'lucide-react'
import './index.css'

function App() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isDocManagerOpen, setIsDocManagerOpen] = useState(false)
  const [documents, setDocuments] = useState([])
  const [isLoadingDocs, setIsLoadingDocs] = useState(false)
  const fileInputRef = useRef(null)
  const chatEndRef = useRef(null)

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchDocuments = async () => {
    setIsLoadingDocs(true)
    try {
      const response = await fetch('http://localhost:8000/api/documents')
      const data = await response.json()
      setDocuments(data)
    } catch (error) {
      console.error('Failed to fetch docs:', error)
    } finally {
      setIsLoadingDocs(false)
    }
  }

  const handleDeleteDocument = async (filename) => {
    try {
      await fetch(`http://localhost:8000/api/documents/${filename}`, { method: 'DELETE' })
      fetchDocuments()
    } catch (error) {
      console.error('Failed to delete doc:', error)
    }
  }

  useEffect(() => {
    if (isDocManagerOpen) {
      fetchDocuments()
    }
  }, [isDocManagerOpen])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleChat = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setQuery('')
    setIsLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.content }),
      })
      const data = await response.json()
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.answer,
        cacheHit: data.cache_hit,
        route: data.route,
        processedQuery: data.processed_query
      }])
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection failed. Please ensure the backend is running.', isError: true }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await fetch('http://localhost:8000/api/upload', {
        method: 'POST',
        body: formData,
      })
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `Successfully uploaded ${file.name}. Indexing in background...`
      }])
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: `Upload failed: ${file.name}`, isError: true }])
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white font-sans selection:bg-purple-500/30">
      {/* Background Orbs */}
      <div className="fixed top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-purple-600/20 blur-[120px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-blue-600/20 blur-[120px] pointer-events-none" />

      <div className="max-w-5xl mx-auto p-4 md:p-8 flex flex-col h-screen relative z-10">
        
        {/* Header */}
        <header className="flex items-center justify-between py-6 border-b border-white/10 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                Agentic Hybrid RAG
              </h1>
              <p className="text-xs text-white/40">Adaptive Knowledge Intelligence</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button 
              onClick={() => setIsDocManagerOpen(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all active:scale-95"
            >
              <List className="w-4 h-4" />
              <span className="text-sm font-medium hidden sm:inline">Manage Docs</span>
            </button>
            <button 
              onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 transition-all active:scale-95 disabled:opacity-50"
          >
            {isUploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileUp className="w-4 h-4" />}
            <span className="text-sm font-medium hidden sm:inline">Upload Policy</span>
          </button>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleUpload} 
            className="hidden" 
            accept=".pdf,.txt,.md" 
          />
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar flex flex-col gap-6 pb-24">
          {messages.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center text-center max-w-lg mx-auto opacity-60">
              <Database className="w-16 h-16 mb-6 text-white/20" />
              <h2 className="text-2xl font-semibold mb-2">Welcome to your Knowledge Base</h2>
              <p className="text-sm text-white/60">
                Upload a document using the button above, then ask a question. The system will adaptively choose between Vector, Graph, or Web retrieval.
              </p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
              <div 
                className={`max-w-[85%] rounded-2xl p-5 shadow-lg backdrop-blur-md ${
                  msg.role === 'user' 
                    ? 'bg-gradient-to-br from-purple-600/80 to-blue-600/80 border border-white/10 rounded-tr-none' 
                    : msg.role === 'system'
                    ? 'bg-green-500/10 border border-green-500/20 text-green-400 mx-auto'
                    : 'bg-white/5 border border-white/10 rounded-tl-none'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <div className="flex flex-col gap-2">
                    <div className="flex items-center flex-wrap gap-2 mb-2 text-xs font-medium text-white/40">
                      <div className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3" />
                        Assistant
                      </div>
                      {msg.cacheHit && (
                        <span className="flex items-center gap-1 text-green-400/80 bg-green-400/10 px-2 py-0.5 rounded-full ml-1">
                          <ShieldCheck className="w-3 h-3" /> Cached
                        </span>
                      )}
                      {msg.route && (
                        <span className="flex items-center gap-1 text-blue-400/80 bg-blue-400/10 px-2 py-0.5 rounded-full ml-1 uppercase">
                          <Route className="w-3 h-3" /> {msg.route} Route
                        </span>
                      )}
                    </div>
                    
                    {msg.processedQuery && (
                      <div className="bg-black/20 rounded-xl p-3 border border-white/5 text-xs text-white/60 mb-2">
                        <div className="flex items-center gap-2 mb-2 text-white/80 font-medium">
                          <Activity className="w-3 h-3" /> Preprocessing Steps
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                          <div><span className="text-white/40">Normalized:</span> {msg.processedQuery.normalized}</div>
                          <div><span className="text-white/40">Keywords:</span> {msg.processedQuery.keywords?.join(', ') || 'None'}</div>
                          <div><span className="text-white/40">Entities:</span> {msg.processedQuery.entities?.join(', ') || 'None'}</div>
                          <div><span className="text-white/40">Temporal:</span> {msg.processedQuery.temporal ? 'Yes' : 'No'}</div>
                        </div>
                      </div>
                    )}
                    
                    <div className={`text-sm leading-relaxed ${msg.isError ? 'text-red-400' : 'text-white/90'} whitespace-pre-wrap`}>
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div className={`text-sm leading-relaxed ${msg.isError ? 'text-red-400' : 'text-white/90'} whitespace-pre-wrap`}>
                    {msg.content}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="max-w-[85%] rounded-2xl p-5 rounded-tl-none bg-white/5 border border-white/10 backdrop-blur-md flex items-center gap-3">
                <Loader2 className="w-4 h-4 animate-spin text-purple-400" />
                <span className="text-sm text-white/60">Reasoning over documents...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Area */}
        <div className="absolute bottom-6 left-4 right-4 md:left-8 md:right-8">
          <form onSubmit={handleChat} className="relative max-w-4xl mx-auto flex items-center">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a question about the policy..."
              disabled={isLoading}
              className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-16 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-transparent backdrop-blur-xl transition-all disabled:opacity-50 shadow-2xl"
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="absolute right-2 p-2.5 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 text-white hover:shadow-lg hover:shadow-purple-500/25 disabled:opacity-50 disabled:hover:shadow-none transition-all active:scale-95"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>

      {isDocManagerOpen && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-[#1a1a1a] border border-white/10 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-6 border-b border-white/10 bg-white/5">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Database className="w-5 h-5 text-purple-400" /> Document Registry
              </h2>
              <button onClick={() => setIsDocManagerOpen(false)} className="text-white/40 hover:text-white transition-colors">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
              {isLoadingDocs ? (
                <div className="flex justify-center py-12"><Loader2 className="w-8 h-8 animate-spin text-purple-500" /></div>
              ) : documents.length === 0 ? (
                <div className="text-center py-12 text-white/40">No documents stored. Upload a policy!</div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div key={doc.id} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                      <div className="flex flex-col gap-1 overflow-hidden">
                        <div className="font-medium text-sm truncate">{doc.filename}</div>
                        <div className="flex items-center gap-3 text-xs text-white/40">
                          <span className="bg-white/10 px-2 py-0.5 rounded text-white/60 uppercase">{doc.type}</span>
                          <span className="font-mono truncate max-w-[150px]" title={doc.hash}>Hash: {doc.hash.substring(0, 8)}...</span>
                        </div>
                      </div>
                      <button 
                        onClick={() => handleDeleteDocument(doc.filename)}
                        className="p-2 text-red-400/70 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors flex-shrink-0 ml-4"
                        title="Delete Document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App

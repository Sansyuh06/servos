import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChatMessage, getCases, type ChatResponse, type CaseSummary } from '@/api/client'
import {
    Send, Bot, User, Paperclip, FileText, Shield, Database,
    Loader2, Search, FolderOpen, Upload, X, Sparkles,
    BookOpen, FileSearch, AlertTriangle, Clock
} from 'lucide-react'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: ChatResponse['sources']
    timestamp: Date
    attachment?: string
}

/* ── AI Loader — animated gradient orb ── */
function AILoader() {
    return (
        <div className="flex items-center gap-3">
            <div className="relative w-6 h-6">
                <div className="absolute inset-0 rounded-full bg-accent/40 animate-ping" />
                <div className="absolute inset-0.5 rounded-full bg-gradient-to-br from-accent via-[#6c5ce7] to-[#a29bfe] animate-spin" style={{ animationDuration: '3s' }} />
                <div className="absolute inset-1.5 rounded-full bg-[#1E1F24]" />
            </div>
            <span className="text-[13px] text-cream-dim animate-pulse">Analyzing evidence...</span>
        </div>
    )
}

/* ── Suggestion Chips ── */
const SUGGESTIONS = [
    { icon: FileSearch, label: 'Analyze Document', prompt: 'Analyze the uploaded document for forensic indicators' },
    { icon: AlertTriangle, label: 'Find Threats', prompt: 'What malware or suspicious activity was found in recent investigations?' },
    { icon: BookOpen, label: 'Summarize Evidence', prompt: 'Provide an executive summary of all investigation findings' },
    { icon: Clock, label: 'Timeline Analysis', prompt: 'Show me the timeline of events from the latest investigation' },
]

export default function ChatPage() {
    const navigate = useNavigate()
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [cases, setCases] = useState<CaseSummary[]>([])
    const [selectedCase, setSelectedCase] = useState<string | undefined>()
    const [sidebarSources, setSidebarSources] = useState<ChatResponse['sources']>([])
    const [attachedFile, setAttachedFile] = useState<string | null>(null)
    const chatEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        getCases().then(r => setCases(r.cases)).catch(() => { })
    }, [])

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async (overrideInput?: string) => {
        const text = overrideInput || input.trim()
        if(!text || isLoading) return

        let content = text
        if(attachedFile) {
            content = `[Document: ${attachedFile}]\n${text}`
        }

        const userMsg: Message = {
            id: `u-${Date.now()}`,
            role: 'user',
            content: text,
            attachment: attachedFile || undefined,
            timestamp: new Date(),
        }
        setMessages(prev => [...prev, userMsg])
        setInput('')
        setAttachedFile(null)
        setIsLoading(true)

        try {
            const res = await sendChatMessage(content, selectedCase)
            const aiMsg: Message = {
                id: `a-${Date.now()}`,
                role: 'assistant',
                content: res.response,
                sources: res.sources,
                timestamp: new Date(),
            }
            setMessages(prev => [...prev, aiMsg])
            if(res.sources.length > 0) {
                setSidebarSources(prev => [...res.sources, ...prev].slice(0, 20))
            }
        } catch(err: any) {
            setMessages(prev => [...prev, {
                id: `e-${Date.now()}`,
                role: 'assistant',
                content: `Connection error: ${err.message}`,
                timestamp: new Date(),
            }])
        }
        setIsLoading(false)
        inputRef.current?.focus()
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if(e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if(file) setAttachedFile(file.name)
    }

    const hasMessages = messages.length > 0

    return (
        <div className="h-full flex overflow-hidden">
            {/* ── Main Chat Area ── */}
            <div className="flex-1 flex flex-col overflow-hidden relative">
                {/* Subtle radial glow background */}
                <div className="absolute inset-0 pointer-events-none" style={{
                    background: 'radial-gradient(ellipse at 50% 35%, rgba(143,125,186,0.08) 0%, transparent 55%)',
                }} />

                {/* Edge glow */}
                <div className="absolute inset-0 pointer-events-none border border-accent/5 rounded-none" />

                {!hasMessages ? (
                    /* ── Empty State: Centered greeting (1904 style) ── */
                    <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
                        <motion.h1
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6 }}
                            className="text-3xl font-bold font-heading text-cream-bright/80 text-center mb-2"
                        >
                            How can I help today?
                        </motion.h1>
                        <motion.p
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2, duration: 0.5 }}
                            className="text-[13px] text-cream-dim/40 text-center mb-10"
                        >
                            Upload a document or ask a forensic question
                        </motion.p>

                        {/* Input Card */}
                        <motion.div
                            initial={{ opacity: 0, y: 15 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3, duration: 0.5 }}
                            className="w-full max-w-2xl"
                        >
                            {renderInputCard()}
                        </motion.div>

                        {/* Suggestion Chips */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5, duration: 0.4 }}
                            className="flex flex-wrap gap-2 mt-6 justify-center"
                        >
                            {SUGGESTIONS.map(({ icon: Icon, label, prompt }) => (
                                <button
                                    key={label}
                                    onClick={() => handleSend(prompt)}
                                    className="flex items-center gap-2 px-3 py-2 rounded-lg border border-white/[0.06] bg-white/[0.02] text-[12px] text-cream-dim hover:bg-white/[0.06] hover:text-cream hover:border-white/[0.12] transition-all"
                                >
                                    <Icon size={13} />
                                    {label}
                                </button>
                            ))}
                        </motion.div>

                        {/* Case selector */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.7 }}
                            className="mt-6"
                        >
                            <select
                                value={selectedCase || ''}
                                onChange={(e) => setSelectedCase(e.target.value || undefined)}
                                className="bg-transparent border border-white/[0.08] rounded-lg px-3 py-1.5 text-[11px] text-cream-dim focus:border-accent/40 focus:outline-none"
                            >
                                <option value="">All Investigations</option>
                                {cases.map(c => (
                                    <option key={c.id} value={c.id}>{c.id}</option>
                                ))}
                            </select>
                        </motion.div>
                    </div>
                ) : (
                    /* ── Chat Messages ── */
                    <>
                        {/* Header */}
                        <div className="relative z-10 flex items-center gap-3 px-6 py-3 border-b border-servos-border-dim shrink-0">
                            <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/20 flex items-center justify-center">
                                <Sparkles size={14} className="text-accent" />
                            </div>
                            <div>
                                <h1 className="text-sm font-semibold text-cream-bright">SERVOS AI</h1>
                                <p className="text-[10px] text-cream-dim">Offline Forensic Assistant</p>
                            </div>
                            <select
                                value={selectedCase || ''}
                                onChange={(e) => setSelectedCase(e.target.value || undefined)}
                                className="ml-auto bg-servos-surface border border-servos-border rounded-md px-2 py-1 text-[11px] text-cream focus:border-accent focus:outline-none"
                            >
                                <option value="">All Cases</option>
                                {cases.map(c => (
                                    <option key={c.id} value={c.id}>{c.id.slice(0, 20)}</option>
                                ))}
                            </select>
                        </div>

                        {/* Messages */}
                        <div className="relative z-10 flex-1 overflow-y-auto px-6 py-4 space-y-4">
                            <AnimatePresence>
                                {messages.map((msg) => (
                                    <motion.div
                                        key={msg.id}
                                        initial={{ opacity: 0, y: 8 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        transition={{ duration: 0.25, ease: [0.4, 0, 0.2, 1] }}
                                        className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        {msg.role === 'assistant' && (
                                            <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/20 flex items-center justify-center shrink-0 mt-0.5">
                                                <Bot size={14} className="text-accent" />
                                            </div>
                                        )}
                                        <div className={`max-w-[70%] rounded-2xl px-4 py-3 ${msg.role === 'user'
                                            ? 'bg-accent text-white rounded-br-md'
                                            : 'bg-servos-surface border border-servos-border rounded-bl-md'
                                            }`}>
                                            {msg.attachment && (
                                                <div className="flex items-center gap-1.5 mb-2 text-[10px] opacity-70">
                                                    <FileText size={10} />
                                                    <span>{msg.attachment}</span>
                                                </div>
                                            )}
                                            <p className="text-[13px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                                            {msg.sources && msg.sources.length > 0 && (
                                                <div className="mt-2 pt-2 border-t border-white/10">
                                                    <p className="text-[9px] text-cream-dim uppercase tracking-wider mb-1">Retrieved Sources</p>
                                                    <div className="flex flex-wrap gap-1">
                                                        {msg.sources.map((s, i) => (
                                                            <span key={i} className="inline-flex items-center gap-1 px-1.5 py-0.5 bg-accent/15 text-accent rounded text-[9px] font-medium">
                                                                <Database size={8} />
                                                                {s.label}
                                                            </span>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                        {msg.role === 'user' && (
                                            <div className="w-7 h-7 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-0.5">
                                                <User size={14} className="text-cream-dim" />
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </AnimatePresence>

                            {isLoading && (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex gap-3"
                                >
                                    <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/20 flex items-center justify-center shrink-0">
                                        <Bot size={14} className="text-accent" />
                                    </div>
                                    <div className="bg-servos-surface border border-servos-border rounded-2xl rounded-bl-md px-4 py-3">
                                        <AILoader />
                                    </div>
                                </motion.div>
                            )}

                            <div ref={chatEndRef} />
                        </div>

                        {/* Bottom Input */}
                        <div className="relative z-10 px-6 py-3 border-t border-servos-border-dim shrink-0">
                            {renderInputCard()}
                        </div>
                    </>
                )}
            </div>

            {/* ── Right Sidebar: Retrieved Sources ── */}
            <div className="w-60 bg-servos-surface border-l border-servos-border overflow-y-auto shrink-0">
                <div className="px-4 py-3 border-b border-servos-border-dim">
                    <div className="flex items-center gap-2">
                        <FileSearch size={13} className="text-accent" />
                        <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Retrieved Context</p>
                    </div>
                </div>

                {sidebarSources.length === 0 ? (
                    <div className="p-4 text-center">
                        <Search size={18} className="text-cream-dim/20 mx-auto mb-2" />
                        <p className="text-[11px] text-cream-dim/40 leading-relaxed">Ask a question to see retrieved evidence sources here</p>
                    </div>
                ) : (
                    <div className="p-3 space-y-2">
                        {sidebarSources.map((source, i) => (
                            <div key={i} className="bg-servos-bg border border-servos-border-dim rounded-lg p-2.5">
                                <div className="flex items-center gap-1.5 mb-1">
                                    {source.type === 'findings' && <FolderOpen size={10} className="text-accent" />}
                                    {source.type === 'interpretation' && <Shield size={10} className="text-warning" />}
                                    {source.type === 'case_summary' && <Database size={10} className="text-success" />}
                                    {source.type === 'device_info' && <Database size={10} className="text-cream-dim" />}
                                    <span className="text-[10px] font-semibold text-cream truncate">{source.label}</span>
                                </div>
                                <div className="text-[9px] text-cream-dim space-y-0.5">
                                    {source.data && typeof source.data === 'object' && Object.entries(source.data).slice(0, 3).map(([k, v]) => (
                                        <div key={k} className="flex justify-between">
                                            <span className="capitalize">{k.replace(/_/g, ' ')}</span>
                                            <span className="text-cream font-mono truncate max-w-[55%] text-right">
                                                {typeof v === 'string' ? v.slice(0, 30) : JSON.stringify(v).slice(0, 20)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Hidden file input */}
            <input
                ref={fileInputRef}
                type="file"
                className="hidden"
                accept=".txt,.log,.csv,.json,.pdf,.doc,.docx,.xml,.html,.eml,.evt,.evtx"
                onChange={handleFileSelect}
            />
        </div>
    )

    function renderInputCard() {
        return (
            <div className="bg-white/[0.03] border border-white/[0.08] rounded-2xl overflow-hidden focus-within:border-accent/30 transition-colors">
                {/* Attached file badge */}
                {attachedFile && (
                    <div className="flex items-center gap-2 px-4 pt-3">
                        <span className="inline-flex items-center gap-1.5 px-2 py-1 bg-accent/15 text-accent rounded-lg text-[11px]">
                            <FileText size={11} />
                            {attachedFile}
                            <button onClick={() => setAttachedFile(null)} className="ml-1 hover:text-white">
                                <X size={10} />
                            </button>
                        </span>
                    </div>
                )}

                {/* Text area */}
                <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask SERVOS about your investigation..."
                    rows={2}
                    className="w-full bg-transparent text-[13px] text-cream placeholder:text-cream-dim/30 resize-none focus:outline-none px-4 pt-3 pb-1"
                />

                {/* Toolbar */}
                <div className="flex items-center justify-between px-4 py-2">
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="p-1.5 rounded-md text-cream-dim/40 hover:text-cream-dim hover:bg-white/[0.05] transition-colors"
                            title="Attach document"
                        >
                            <Paperclip size={15} />
                        </button>
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            className="p-1.5 rounded-md text-cream-dim/40 hover:text-cream-dim hover:bg-white/[0.05] transition-colors"
                            title="Upload evidence file"
                        >
                            <Upload size={15} />
                        </button>
                    </div>
                    <button
                        onClick={() => handleSend()}
                        disabled={!input.trim() || isLoading}
                        className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white/[0.08] hover:bg-white/[0.14] text-cream text-[12px] font-medium disabled:opacity-20 disabled:cursor-not-allowed transition-colors"
                    >
                        <Send size={12} />
                        Send
                    </button>
                </div>
            </div>
        )
    }
}

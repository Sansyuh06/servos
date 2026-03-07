import { useState, useRef, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { sendChatMessage, type ChatResponse, type ChatAction } from '@/api/client'
import {
    Send, Bot, User, Paperclip, FileText,
    Loader2, Search, X, Sparkles, MessageSquare,
    Lightbulb, PenTool, Brain, BookOpen, Cpu, MessagesSquare, Plus
} from 'lucide-react'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    sources?: ChatResponse['sources']
    actions?: ChatAction[]
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
            <span className="text-[13px] text-cream-dim animate-pulse">Thinking...</span>
        </div>
    )
}

/* ── Suggestion Chips ── */
const SUGGESTIONS = [
    { icon: Search, label: 'Scan for Malware', prompt: 'Scan my system for malware and suspicious files' },
    { icon: Brain, label: 'Analyze Logs', prompt: 'Analyze system logs for suspicious activity' },
    { icon: Cpu, label: 'System Info', prompt: 'Show me current system processes and resource usage' },
    { icon: BookOpen, label: 'Cyber Law', prompt: 'What sections of the IT Act apply to unauthorized access?' },
]

export default function ChatPage() {
    const navigate = useNavigate()
    const [searchParams, setSearchParams] = useSearchParams()

    const initialCaseId = searchParams.get('case') || ''
    const [selectedCaseId, setSelectedCaseId] = useState<string>(initialCaseId)

    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [sidebarSources, setSidebarSources] = useState<ChatResponse['sources']>([])
    const [attachedFile, setAttachedFile] = useState<string | null>(null)
    const [showCasePicker, setShowCasePicker] = useState(false)
    const [caseList, setCaseList] = useState<Array<{ id: string, investigator?: string }>>([])
    const chatEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLTextAreaElement>(null)
    const fileInputRef = useRef<HTMLInputElement>(null)

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Keep selectedCaseId synced with URL
    useEffect(() => {
        const caseParam = searchParams.get('case')
        if (caseParam !== null && caseParam !== selectedCaseId) {
            setSelectedCaseId(caseParam)
        }
    }, [searchParams])

    // Load cases on mount so the dropdown population works even if navigated directly
    useEffect(() => {
        loadCases()
    }, [])

    const handleSend = async (overrideInput?: string) => {
        const text = overrideInput || input.trim()
        if (!text || isLoading) return

        let content = text
        if (attachedFile) {
            content = `[Attached: ${attachedFile}]\n${content}`
        }

        // Auto-inject case context if selected
        if (selectedCaseId && !content.includes(`[Case:${selectedCaseId}]`) && !content.includes('[Case:')) {
            content = `[Case:${selectedCaseId}] ${content}`
        }

        const userMsg: Message = {
            id: `u-${Date.now()}`,
            role: 'user',
            content: text,
            attachment: attachedFile || undefined,
            timestamp: new Date(),
        }
        const newMessages = [...messages, userMsg]
        setMessages(newMessages)
        setInput('')
        setAttachedFile(null)
        setIsLoading(true)

        try {
            // Build conversation history for multi-turn context
            const history = newMessages.map(m => ({
                role: m.role,
                content: m.content,
            }))

            const res = await sendChatMessage(content, history)
            const aiMsg: Message = {
                id: `a-${Date.now()}`,
                role: 'assistant',
                content: res.response,
                sources: res.sources,
                actions: res.actions,
                timestamp: new Date(),
            }
            setMessages(prev => [...prev, aiMsg])
            if (res.sources && res.sources.length > 0) {
                setSidebarSources(prev => [...res.sources, ...prev].slice(0, 20))
            }
        } catch (err: any) {
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
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (file) setAttachedFile(file.name)
    }

    const loadCases = async () => {
        try {
            const resp = await fetch('/api/cases')
            const d = await resp.json()
            setCaseList(d.cases || [])
        } catch {
            // ignore
        }
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

                {/* ── Always-visible Header with Case Context Dropdown ── */}
                <div className="relative z-10 flex items-center justify-between px-6 py-3 border-b border-servos-border-dim shrink-0">
                    <div className="flex items-center gap-3">
                        <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/20 flex items-center justify-center">
                            <Sparkles size={14} className="text-accent" />
                        </div>
                        <div>
                            <h1 className="text-sm font-semibold text-cream-bright">SERVOS AI</h1>
                            <p className="text-[10px] text-cream-dim">AI Assistant</p>
                        </div>
                        {hasMessages && (
                            <div className="ml-4 flex items-center gap-2 text-[11px] text-cream-dim/50 hidden md:flex">
                                <MessagesSquare size={12} />
                                <span>{messages.length} messages</span>
                            </div>
                        )}
                    </div>

                    {/* Case Context Dropdown */}
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-cream-dim">Case:</span>
                        <select
                            className="bg-servos-bg border border-servos-border text-cream-bright text-xs rounded-lg px-2 py-1.5 outline-none focus:border-accent/50 min-w-[180px]"
                            value={selectedCaseId}
                            onChange={(e) => {
                                const newCase = e.target.value;
                                setSelectedCaseId(newCase);
                                if (newCase) {
                                    searchParams.set('case', newCase);
                                } else {
                                    searchParams.delete('case');
                                }
                                setSearchParams(searchParams);
                            }}
                            onClick={() => { if (caseList.length === 0) loadCases() }}
                        >
                            <option value="">Global (No Case)</option>
                            {caseList.map(c => (
                                <option key={c.id} value={c.id}>
                                    Case {c.id.slice(0, 8)} {c.investigator ? `- ${c.investigator}` : ''}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {!hasMessages ? (
                    /* ── Empty State: Centered greeting ── */
                    <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-6">
                        {selectedCaseId && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.95 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="mb-6 px-4 py-2 rounded-lg border border-accent/30 bg-accent/10 text-accent text-sm font-medium"
                            >
                                📂 Case Context: <span className="font-mono">{selectedCaseId.slice(0, 12)}</span>
                            </motion.div>
                        )}
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
                            {selectedCaseId ? 'Ask about this case or start a new topic' : 'Start a conversation on any topic'}
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
                    </div>
                ) : (
                    /* ── Chat Messages ── */
                    <>
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
                                            {/* Action Cards — shown when agent auto-executed tools */}
                                            {msg.actions && msg.actions.length > 0 && (
                                                <div className="mb-3 space-y-1.5">
                                                    <div className="text-[10px] uppercase tracking-wider text-accent font-semibold mb-1.5">🤖 Agent Actions</div>
                                                    {msg.actions.map((action, i) => (
                                                        <div key={i}
                                                            className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-[12px] ${action.status === 'completed'
                                                                ? 'border-accent/30 bg-accent/5 text-cream'
                                                                : 'border-red-500/30 bg-red-500/5 text-red-300'
                                                                }`}
                                                        >
                                                            <span className="text-base">{action.icon}</span>
                                                            <div className="flex-1 min-w-0">
                                                                <div className="font-medium">{action.tool_name}</div>
                                                                <div className="text-[11px] opacity-70 truncate">{action.summary}</div>
                                                            </div>
                                                            <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${action.status === 'completed'
                                                                ? 'bg-green-500/20 text-green-400'
                                                                : 'bg-red-500/20 text-red-400'
                                                                }`}>{action.status === 'completed' ? '✓' : '✗'}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                            <p className="text-[13px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
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

            {/* ── Right Sidebar: Conversation Info ── */}
            <div className="w-60 bg-servos-surface border-l border-servos-border overflow-y-auto shrink-0">
                <div className="px-4 py-3 border-b border-servos-border-dim">
                    <div className="flex items-center gap-2">
                        <MessageSquare size={13} className="text-accent" />
                        <p className="text-[10px] font-semibold text-cream-dim uppercase tracking-wider">Conversation Info</p>
                    </div>
                </div>

                {/* Session stats */}
                <div className="p-4 border-b border-servos-border-dim">
                    <div className="space-y-2">
                        <div className="flex justify-between text-[11px]">
                            <span className="text-cream-dim/60">Messages</span>
                            <span className="text-cream font-mono">{messages.length}</span>
                        </div>
                        <div className="flex justify-between text-[11px]">
                            <span className="text-cream-dim/60">Session</span>
                            <span className="text-cream font-mono">Active</span>
                        </div>
                    </div>
                </div>

                {sidebarSources.length === 0 ? (
                    <div className="p-4 text-center">
                        <Search size={18} className="text-cream-dim/20 mx-auto mb-2" />
                        <p className="text-[11px] text-cream-dim/40 leading-relaxed">Start a conversation to see context info here</p>
                    </div>
                ) : (
                    <div className="p-3 space-y-2">
                        {sidebarSources.map((source, i) => (
                            <div key={i} className="bg-servos-bg border border-servos-border-dim rounded-lg p-2.5">
                                <div className="flex items-center gap-1.5 mb-1">
                                    {source.type === 'conversation' && <MessagesSquare size={10} className="text-accent" />}
                                    {source.type === 'model_info' && <Cpu size={10} className="text-success" />}
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
                accept=".txt,.log,.csv,.json,.pdf,.doc,.docx,.xml,.html,.md,.py,.js,.ts,.jsx,.tsx,.png,.jpg,.jpeg"
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
                {showCasePicker && (
                    <div className="absolute bottom-14 left-4 right-4 max-h-48 overflow-auto bg-servos-bg border border-servos-border rounded-lg p-2 z-20">
                        {caseList.length === 0 ? (
                            <p className="text-xs text-cream-dim">No cases found</p>
                        ) : (
                            caseList.map(c => (
                                <button key={c.id}
                                    onClick={() => {
                                        setInput(prev => prev + `[Case:${c.id}] `);
                                        setShowCasePicker(false);
                                    }}
                                    className="w-full text-left text-xs text-cream py-1 hover:bg-servos-hover rounded"
                                >{c.id.slice(0, 8)} {c.investigator && `– ${c.investigator}`}</button>
                            ))
                        )}
                    </div>
                )}

                {/* Text Input Area */}
                <textarea
                    ref={inputRef}
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={selectedCaseId ? `Ask about case ${selectedCaseId.slice(0, 8)}...` : "Type a message..."}
                    rows={1}
                    className="w-full px-4 py-3 bg-transparent text-cream text-[13px] placeholder:text-cream-dim/30 outline-none resize-none min-h-[44px] max-h-[120px]"
                    style={{ overflow: 'auto' }}
                    autoFocus
                />

                {/* Toolbar */}
                <div className="flex items-center justify-between px-4 py-2">
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => { fileInputRef.current?.click() }}
                            className="p-1.5 rounded-md text-cream-dim/40 hover:text-cream-dim hover:bg-white/[0.05] transition-colors"
                            title="Attach file"
                        >
                            <Paperclip size={15} />
                        </button>
                        <button
                            onClick={() => { setShowCasePicker(!showCasePicker); if (!showCasePicker) loadCases() }}
                            className="p-1.5 rounded-md text-cream-dim/40 hover:text-cream-dim hover:bg-white/[0.05] transition-colors"
                            title="Insert case reference"
                        >
                            <Plus className="" size={15} />
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

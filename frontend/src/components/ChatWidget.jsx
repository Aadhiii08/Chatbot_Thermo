import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { X, Send, Paperclip, ChevronLeft, CheckCircle2, ChevronDown, Zap, Globe, Shield, MessageCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- CONFIGURATION ---
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";
const LOGO_PATH = "/logo.png";

// --- WELCOME FEATURES ---
const FEATURES = [
  { icon: MessageCircle, title: 'Chat smarter', desc: 'AI-powered responses', color: 'from-amber-500 to-yellow-600' },
  { icon: Zap, title: 'Instant Support', desc: '24/7 availability', color: 'from-blue-600 to-indigo-700' },
  { icon: Globe, title: 'Global Reach', desc: 'Multi-language support', color: 'from-amber-400 to-orange-500' },
  { icon: Shield, title: 'Secure', desc: 'Enterprise security', color: 'from-slate-700 to-slate-900' },
];

// --- COMPONENT: TYPEWRITER EFFECT ---
const Typewriter = ({ text, onComplete }) => {
  const [displayedText, setDisplayedText] = useState("");

  useEffect(() => {
    let index = 0;
    if (!text) {
      onComplete?.();
      return;
    }

    const interval = setInterval(() => {
      setDisplayedText(text.slice(0, index + 1));
      index++;
      if (index === text.length) {
        clearInterval(interval);
        setTimeout(() => onComplete?.(), 500); // Small pause after finishing
      }
    }, 15); // Typing speed

    return () => clearInterval(interval);
  }, []);

  return <span dangerouslySetInnerHTML={{ __html: displayedText.replace(/\*\*(.*?)\*\*/g, '<b class="font-bold text-white">$1</b>').replace(/\n/g, '<br />') }} />;
};

// --- COMPONENT: CHAT HEADER (Liquid Style) ---
const ChatHeader = ({ onClose, isEmbedMode }) => (
  <div
    className="px-6 py-5 flex items-center justify-between relative overflow-hidden shrink-0 z-20"
    style={{
      background: 'linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(30, 41, 59, 0.4) 50%, rgba(15, 23, 42, 0.6) 100%)',
      backdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(251, 191, 36, 0.2)',
    }}
  >
    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer pointer-events-none" />

    <div className="flex items-center gap-3 relative z-10">
      <div
        className="w-12 h-12 rounded-2xl flex items-center justify-center p-2 shadow-lg relative overflow-hidden bg-white"
        style={{
          border: '1px solid rgba(255, 255, 255, 0.3)',
        }}
      >
        <img src={LOGO_PATH} alt="DM Thermoformer & RA Vacform Industries" className="w-full h-full object-cover" />
      </div>
      <div>
        <h3 className="text-white font-display tracking-tight font-bold drop-shadow-md leading-tight text-sm">
          DM Thermoformer &<br />RA Vacform Industries
        </h3>
        <div className="flex items-center gap-2 mt-0.5">
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [1, 0.8, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="w-2 h-2 rounded-full"
            style={{
              background: 'linear-gradient(135deg, #f59e0b, #fbce03)',
              boxShadow: '0 0 10px rgba(245, 158, 11, 0.8)',
            }}
          />
          <span className="text-white/80 text-xs font-display tracking-wider">AI AGENT ONLINE</span>
        </div>
      </div>
    </div>

    {!isEmbedMode && (
      <motion.button
        whileHover={{ scale: 1.1, rotate: 90 }}
        whileTap={{ scale: 0.9 }}
        onClick={onClose}
        className="relative z-10 p-2 text-white/80 hover:text-white rounded-xl transition-all"
        style={{ background: 'rgba(255, 255, 255, 0.1)' }}
      >
        <X className="w-5 h-5" />
      </motion.button>
    )}
  </div>
);

// --- COMPONENT: WELCOME SCREEN ---
const WelcomeScreen = () => (
  <motion.div
    key="welcome"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="flex-1 flex flex-col items-center justify-center p-6 space-y-6 relative z-10"
  >
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ delay: 0.2 }}
      className="relative"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-400 via-purple-400 to-pink-400 rounded-full blur-3xl opacity-60 animate-pulse" />
      <div className="w-32 h-32 rounded-full bg-white flex items-center justify-center p-2 relative z-10 shadow-[0_0_50px_rgba(255,255,255,0.4)] overflow-hidden border-4 border-white/30">
        <img src={LOGO_PATH} alt="Logo" className="w-[85%] h-[85%] object-contain scale-110" />
      </div>
    </motion.div>

    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.4 }}
      className="text-center space-y-2"
    >
      <h2 className="font-display text-white text-2xl font-bold">Hey there! 👋</h2>
      <p className="text-white/70 text-sm italic">Welcome to</p>
      <div className="flex flex-col gap-1 mt-1">
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 font-bold text-lg">DM Thermoformer</span>
        <span className="text-white/40 text-[10px] font-bold uppercase tracking-widest">&</span>
        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 font-bold text-lg">RA Vacform Industries</span>
      </div>
    </motion.div>

    <motion.div
      initial={{ y: 20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ delay: 0.6 }}
      className="grid grid-cols-2 gap-3 w-full"
    >
      {FEATURES.map((feature, index) => (
        <div key={index} className="p-3 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm hover:bg-white/10 transition-colors group">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${feature.color} flex items-center justify-center mb-2 shadow-lg`}>
            <feature.icon size={16} className="text-white" />
          </div>
          <div className="text-white text-xs font-bold">{feature.title}</div>
          <div className="text-white/50 text-[10px]">{feature.desc}</div>
        </div>
      ))}
    </motion.div>
  </motion.div>
);

// --- MAIN WIDGET ---
export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isEmbedMode, setIsEmbedMode] = useState(false);

  useEffect(() => {
    // Check both search params and hash (WordPress sometimes uses hashes)
    const params = new URLSearchParams(window.location.search || window.location.hash.replace('#', '?'));
    if (params.get('mode') === 'embed') {
      setIsEmbedMode(true);
      setIsOpen(true);
    }
  }, []);

  const [showWelcome, setShowWelcome] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [hasStarted, setHasStarted] = useState(false);

  const [chatState, setChatState] = useState({ stage: 'get_name', user_details: { stage_history: [] } });
  const [uiElements, setUiElements] = useState(null);

  // TYPING EFFECT STATE
  const [messageQueue, setMessageQueue] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [pendingUiElements, setPendingUiElements] = useState(null);

  const messagesEndRef = useRef(null);

  useEffect(() => messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }), [messages, uiElements, isLoading]);

  useEffect(() => {
    if (isOpen) {
      setShowWelcome(true);
      if (!hasStarted) {
        handleSendMessage("new proposal", "command", null, true);
        setHasStarted(true);
      }
      const timer = setTimeout(() => setShowWelcome(false), 2500);
      return () => clearTimeout(timer);
    }
  }, [isOpen]);

  // --- QUEUE PROCESSOR ---
  useEffect(() => {
    if (!isTyping && messageQueue.length > 0) {
      const nextMsg = messageQueue[0];
      setMessageQueue(prev => prev.slice(1));
      setIsTyping(true);
      setMessages(prev => [...prev, { role: 'assistant', content: nextMsg }]);
    } else if (!isTyping && messageQueue.length === 0) {
      // FIX: Stop loading even if there are no UI elements
      if (pendingUiElements) {
        setUiElements(pendingUiElements);
        setPendingUiElements(null);
      }
      // Always stop loading when queue is empty and not typing
      setIsLoading(false);
    }
  }, [messageQueue, isTyping, pendingUiElements]);

  const handleClose = () => {
    // COMMUNICATION: Tell parent (WordPress) to close the iframe
    window.parent.postMessage('close-chat', '*');

    setIsOpen(false);
    setTimeout(() => {
      setMessages([]);
      setChatState({ stage: 'get_name', user_details: { stage_history: [] } });
      setUiElements(null);
      setHasStarted(false);
    }, 300);
  };

  const handleSendMessage = async (textOverride = null, type = 'text', displayInput = null, isHiddenCommand = false) => {
    const userMessage = textOverride || input;
    if (!userMessage.trim()) return;

    if (!isHiddenCommand && userMessage !== '__GO_BACK__') {
      setMessages(prev => [...prev, { role: 'user', content: displayInput || userMessage }]);
    }

    setInput("");
    setUiElements(null);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        stage: chatState.stage,
        user_details: chatState.user_details,
        user_input: userMessage
      }, { timeout: 30000 });
      const data = response.data;

      setChatState(prev => ({ ...prev, stage: data.next_stage, user_details: data.user_details }));

      // QUEUE MESSAGES
      if (data.bot_messages && data.bot_messages.length > 0) {
        setMessageQueue(prev => [...prev, ...data.bot_messages]);
      } else if (data.bot_message) {
        setMessageQueue(prev => [...prev, data.bot_message]);
      }

      // QUEUE UI ELEMENTS
      if (data.ui_elements) {
        setPendingUiElements(data.ui_elements);
      } else {
        // If no UI elements, stop loading when queue finishes (handled in effect)
        // But if queue is empty (rare), stop now
        if ((!data.bot_messages || data.bot_messages.length === 0) && !data.bot_message) {
          setIsLoading(false);
        }
      }

      // No longer need to trigger proposal generation separately

    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ **Connection Error**\n\nI couldn't reach the server at: \`${API_URL}\`\n\n**Please check:**\n1. Is your Render backend active?\n2. Did you set the \`VITE_API_URL\` correctly in Render settings?`
      }]);
      setIsLoading(false);
    }
  };

  // triggerProposalGeneration removed - Sales PDF is now handled in the main background task

  const renderUiElements = () => {
    if (!uiElements) return null;

    switch (uiElements.type) {
      case 'buttons':
      case 'dropdown':
        return (
          <div className="flex flex-wrap justify-center gap-3 mt-4 w-full px-4 pb-2 animate-fade-in">
            {uiElements.options.map((option, idx) => (
              <motion.button
                key={idx}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => handleSendMessage(option, 'button')}
                // FIGMA STYLE PILL
                className="px-5 py-2 bg-white/10 backdrop-blur-md border border-white/20 text-white rounded-full hover:bg-cyan-500/20 hover:border-cyan-400 transition-all flex items-center gap-2 text-sm shadow-sm"
              >
                {option}
              </motion.button>
            ))}
          </div>
        );

      case 'file_upload':
        return (
          <div className="mt-4 p-6 border border-dashed border-white/20 rounded-2xl bg-white/5 text-center hover:bg-white/10 transition-colors cursor-pointer group">
            <input type="file" id="file-upload" className="hidden" onChange={(e) => handleFileUpload(e.target.files[0])} />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center gap-3">
              <div className="p-3 bg-white/10 rounded-full group-hover:scale-110 transition-transform">
                <Paperclip className="w-5 h-5 text-cyan-400" />
              </div>
              <span className="text-sm text-white font-medium">Upload Drawing</span>
              <span className="text-xs text-white/40">PDF, JPG, PNG, CAD</span>
            </label>
          </div>
        );

      case 'form':
        return (
          <div className="mt-4 p-5 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-md">
            <label className="block text-[10px] font-bold text-white/40 uppercase tracking-widest mb-3">Contact Details</label>
            <div className="flex gap-3">
              <div className="relative w-[35%]">
                <select id="country-select" className="w-full appearance-none p-3 bg-white/5 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-cyan-500 transition-colors">
                  {uiElements.options.length > 0 ? uiElements.options.map(opt => <option key={opt} value={opt} className="bg-slate-900">{opt}</option>) : <option value="India" className="bg-slate-900">India</option>}
                </select>
                <ChevronDown className="absolute right-3 top-3.5 w-4 h-4 text-white/30 pointer-events-none" />
              </div>
              <input id="phone-input" type="tel" placeholder="9876543210" className="w-[65%] p-3 bg-white/5 border border-white/10 rounded-xl text-sm font-medium text-white focus:outline-none focus:border-cyan-500 placeholder:text-white/20 transition-colors" />
            </div>
            <button onClick={() => {
              const c = document.getElementById('country-select').value;
              const p = document.getElementById('phone-input').value;
              if (p) handleSendMessage(`${c}:${p}`, 'form', `Selected ${c}`);
            }}
              className="w-full mt-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold py-3 rounded-xl text-sm hover:shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all"
            >
              Confirm <CheckCircle2 className="w-4 h-4 inline ml-1" />
            </button>
          </div>
        )
      default: return null;
    }
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('email', uiElements.user_email);
    setMessages(prev => [...prev, { role: 'assistant', content: `Uploading **${file.name}**...` }]);
    setIsLoading(true);
    try {
      await axios.post(`${API_URL}${uiElements.upload_to}`, formData);
      setTimeout(() => {
        handleSendMessage(`Uploaded: ${file.name}`, 'file');
        setIsLoading(false);
      }, 2000);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', content: "❌ Upload failed." }]);
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full h-full z-50 flex flex-col items-end font-sans overflow-hidden bg-transparent" style={{ background: 'transparent' }}>
      <AnimatePresence mode="wait">

        {isOpen && (
          <motion.div
            key="chat-window"
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            // --- CSS FIX: Fill container, avoid fixed offsets ---
            className={`
              flex flex-col overflow-hidden z-20 
              ${isEmbedMode
                ? 'w-full h-full'
                : 'fixed bottom-0 right-0 w-full h-full md:bottom-6 md:right-6 md:w-[380px] md:h-[600px] md:max-h-[85vh] md:rounded-[32px] border border-white/10 shadow-2xl transition-all duration-300 ease-in-out'
              }
            `}
            style={{
              background: '#0F172A', // Dark base
              boxShadow: '0 40px 80px -12px rgba(0, 0, 0, 0.8)',
            }}
          >
            <AnimatePresence mode="wait">
              {showWelcome ? (
                <WelcomeScreen key="welcome" />
              ) : (
                <motion.div
                  key="chat-interface"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex-1 flex flex-col h-full"
                >
                  <ChatHeader onClose={handleClose} isEmbedMode={isEmbedMode} />

                  <div className="flex-1 p-6 overflow-y-auto space-y-6 scrollbar-thin scrollbar-thumb-white/10 relative">
                    {/* LIQUID BACKGROUND GLOWS */}
                    <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none opacity-20">
                      <div className="absolute top-[-10%] left-[-10%] w-[300px] h-[300px] bg-purple-600 rounded-full blur-[100px]" />
                      <div className="absolute bottom-[-10%] right-[-10%] w-[300px] h-[300px] bg-cyan-600 rounded-full blur-[100px]" />
                    </div>

                    {messages.map((msg, idx) => (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        key={idx}
                        className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} items-end gap-3 relative z-10`}
                      >
                        {msg.role === 'assistant' && (
                          <div className="w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg bg-white p-1.5 border border-white/10">
                            <img src={LOGO_PATH} className="w-full h-full object-contain" />
                          </div>
                        )}
                        <div className={`max-w-[85%] p-4 text-[15px] leading-relaxed shadow-lg backdrop-blur-md ${msg.role === 'assistant'
                          ? 'rounded-2xl rounded-bl-none text-white bg-[#0EA5E9] border-l-[4px] border-l-[#FFB000] font-medium'
                          : 'rounded-2xl rounded-br-none text-slate-900 bg-[#FFB000] font-bold'
                          }`}>
                          {msg.role === 'assistant' && idx === messages.length - 1 && isTyping ? (
                            <Typewriter text={msg.content} onComplete={() => setIsTyping(false)} />
                          ) : (
                            <div dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.*?)\*\*/g, '<b class="font-bold text-white">$1</b>').replace(/\n/g, '<br />') }} />
                          )}
                        </div>
                      </motion.div>
                    ))}

                    {/* --- FIX: LOADING STATE WITH LOGO --- */}
                    {isLoading && (
                      <div className="flex gap-3 items-end">
                        <div className="w-10 h-10 rounded-2xl bg-white flex items-center justify-center p-1.5 border border-white/10">
                          <img src={LOGO_PATH} className="w-full h-full object-contain opacity-80" />
                        </div>
                        <div className="bg-white/5 border border-white/10 px-4 py-3 rounded-2xl rounded-bl-none flex items-center gap-1">
                          <span className="w-1.5 h-1.5 bg-yellow-400 rounded-full animate-bounce"></span>
                          <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-bounce [animation-delay:0.2s]"></span>
                          <span className="w-1.5 h-1.5 bg-yellow-600 rounded-full animate-bounce [animation-delay:0.4s]"></span>
                        </div>
                      </div>
                    )}

                    {!isLoading && renderUiElements()}
                    <div ref={messagesEndRef} />
                  </div>

                  <div className="p-5 border-t border-white/10 bg-black/20 backdrop-blur-xl relative z-20">
                    {chatState.user_details.stage_history?.length > 0 && (
                      <button onClick={() => handleSendMessage('__GO_BACK__', 'command')} className="flex items-center gap-1 text-[10px] font-bold text-white/40 hover:text-cyan-400 mb-2 transition-colors uppercase">
                        <ChevronLeft size={12} /> Back Step
                      </button>
                    )}
                    <form onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }} className="flex gap-3">
                      <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={isLoading}
                        placeholder="Type a message..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 text-sm text-white focus:outline-none focus:border-amber-500/50 placeholder:text-white/30 transition-all font-medium"
                      />
                      <motion.button
                        whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                        type="submit" disabled={!input.trim()}
                        className="p-3 bg-gradient-to-r from-yellow-500 to-amber-600 rounded-2xl text-slate-900 shadow-lg shadow-yellow-500/20 disabled:opacity-50"
                      >
                        <Send size={20} />
                      </motion.button>
                    </form>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {!isOpen && !isEmbedMode && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setIsOpen(true)}
            // CHANGED: Fixed -> Absolute for internal container
            className="absolute bottom-5 right-5 w-20 h-20 rounded-full shadow-[0_0_40px_rgba(255,255,255,0.5)] flex items-center justify-center z-50 overflow-hidden group border-2 border-white/20 bg-white"
            style={{
              background: 'white',
              boxShadow: '0 0 30px rgba(255, 255, 255, 0.4), inset 0 0 20px rgba(0,0,0,0.05)'
            }}
          >
            <div className="absolute inset-0 bg-gradient-to-br from-white via-slate-50 to-white opacity-80" />
            <img src={LOGO_PATH} alt="Chat" className="w-14 h-14 relative z-10 drop-shadow-sm transform group-hover:scale-110 transition-transform duration-300" />
            <div className="absolute inset-0 bg-black/5 rounded-full scale-0 group-hover:scale-100 transition-transform duration-300" />
          </motion.button>
        )}

      </AnimatePresence>
    </div>
  );
}
import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Paperclip, X, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type: 'text' | 'image';
  imageUrl?: string;
}

const DemoInterface = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', role: 'assistant', content: 'Hello! I am Jude. How can I help you today?', timestamp: new Date(), type: 'text' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<'idle' | 'listening' | 'thinking'>('idle');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null); // 保存当前播放的音频

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize Speech Recognition
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognitionRef.current = new SpeechRecognition();
        recognitionRef.current.continuous = true;
        recognitionRef.current.interimResults = true;
        recognitionRef.current.lang = 'zh-CN'; // 中文普通话（如需粤语改为 'yue-Hant-HK'）

        recognitionRef.current.onstart = () => {
            setStatus('listening');
        };

        recognitionRef.current.onend = () => {
            if (status === 'listening') {
                setStatus('idle');
            }
        };

        recognitionRef.current.onresult = (event: any) => {
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; ++i) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript;
                }
            }
            
            if (finalTranscript) {
                 setInput(prev => prev + (prev ? ' ' : '') + finalTranscript);
            }
        };
        
        recognitionRef.current.onerror = (event: any) => {
            console.error("Speech recognition error", event.error);
            setStatus('idle');
        };
    }
  }, []);

  const toggleListening = () => {
    if (status === 'listening') {
        recognitionRef.current?.stop();
        setStatus('idle');
    } else {
        if (recognitionRef.current) {
            try {
                recognitionRef.current.start();
            } catch (e) {
                 recognitionRef.current?.stop();
                 setTimeout(() => recognitionRef.current?.start(), 100);
            }
        } else {
            alert("Speech recognition not supported in this browser. Please use Chrome.");
        }
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  // 开发环境：使用Vite proxy（相对路径 /api 会自动转发到 localhost:5555）
  // 生产环境：使用环境变量或回退到相对路径
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
  const USE_SIMULATION_MODE = false;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if ((!input.trim() && !selectedImage) || isLoading) return;
    
    if (status === 'listening') {
        recognitionRef.current?.stop();
        setStatus('idle');
    }

    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
      type: selectedImage ? 'image' : 'text',
      imageUrl: imagePreview || undefined
    };

    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setSelectedImage(null);
    setImagePreview(null);
    setIsLoading(true);
    setStatus('thinking');

    if (USE_SIMULATION_MODE) {
        setTimeout(() => {
            const responseMsg: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "I see you're asking about " + (newUserMsg.content || "an image") + ". \n\n( Simulation Mode )",
                timestamp: new Date(),
                type: 'text'
            };
            setMessages(prev => [...prev, responseMsg]);
            setIsLoading(false);
            setStatus('idle');
        }, 1500);
        return;
    }

    try {
        let responseData;
        
        if (newUserMsg.type === 'image' && newUserMsg.imageUrl) {
            const base64Image = newUserMsg.imageUrl.split(',')[1];
            
            const res = await fetch(`${API_BASE_URL}/api/multimodal/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: newUserMsg.content || "Analyze this image",
                    images: [base64Image],
                    session_id: "demo-session-1"
                })
            });
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            responseData = await res.json();
            
        } else {
            const res = await fetch(`${API_BASE_URL}/api/agent_query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: newUserMsg.content,
                    use_search: true,
                    use_rag: true
                })
            });
            if (!res.ok) throw new Error(`Server error: ${res.status}`);
            responseData = await res.json();
        }

        const responseContent = responseData.answer || responseData.response || JSON.stringify(responseData);

        const responseMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: responseContent,
            timestamp: new Date(),
            type: 'text'
        };
        
        setMessages(prev => [...prev, responseMsg]);
        setStatus('idle');

        // 🎤 智能 TTS：如果 should_speak 为 true 且有 audio_url，立即播放
        console.log('📊 Response data:', { 
            should_speak: responseData.should_speak, 
            has_audio: !!responseData.audio_url 
        });
        
        if (responseData.should_speak && responseData.audio_url) {
            console.log('🎤 Playing pre-generated TTS audio...');
            try {
                // 停止并清理之前的音频
                if (audioRef.current) {
                    console.log('⏹️ Stopping previous audio...');
                    audioRef.current.pause();
                    audioRef.current.currentTime = 0;
                    audioRef.current = null;
                }
                
                // 直接使用后端返回的 audio_url（base64编码的音频）
                const audio = new Audio(responseData.audio_url);
                audioRef.current = audio;
                
                // 播放结束后清理
                audio.onended = () => {
                    console.log('✅ Audio playback finished');
                    audioRef.current = null;
                };
                
                audio.play().then(() => {
                    console.log('✅ TTS 播放成功！');
                }).catch((playErr) => {
                    console.error('❌ Audio play() failed:', playErr);
                    alert('浏览器阻止了自动播放。请点击页面任意位置后重试。');
                    audioRef.current = null;
                });
            } catch (ttsErr) {
                console.error('❌ TTS error:', ttsErr);
            }
        } else {
            console.log('ℹ️ should_speak = false 或无音频数据，跳过 TTS');
        }

    } catch (err) {
        console.error("API Error:", err);
        const errorMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: 'assistant',
            content: `Sorry, connection failed. Error: ${err}`,
            timestamp: new Date(),
            type: 'text'
        };
        setMessages(prev => [...prev, errorMsg]);
        setStatus('idle');
    } finally {
        setIsLoading(false);
    }
  };

  return (
    <div 
      className="flex h-screen text-gray-900 font-sans overflow-hidden bg-gradient-to-br from-pink-100 via-purple-100 to-pink-200"
      style={{
        backgroundImage: 'url("/demo-bg.png")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      
      {/* Sidebar */}
      <div className="w-72 border-r border-white/30 bg-white/25 backdrop-blur-md p-6 flex flex-col hidden md:flex">
        <div className="mb-8">
            <h1 className="text-xl font-semibold text-gray-900 mb-1">Jude</h1>
            <div className="text-xs text-gray-700">Your intelligent assistant</div>
        </div>

        <div className="flex-1">
            <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wider mb-4">System Status</h3>
            <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-white/30 backdrop-blur-sm rounded-xl border border-white/40">
                    <span className="text-sm text-gray-800">Agent Core</span>
                    <span className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg"></span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/30 backdrop-blur-sm rounded-xl border border-white/40">
                    <span className="text-sm text-gray-800">HKGAI V1</span>
                    <span className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg"></span>
                </div>
                <div className="flex items-center justify-between p-3 bg-white/30 backdrop-blur-sm rounded-xl border border-white/40">
                    <span className="text-sm text-gray-800">Doubao Vision</span>
                    <span className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-lg"></span>
                </div>
            </div>
        </div>

        <div className="mt-auto">
            <div className={`p-4 rounded-xl flex items-center gap-3 transition-colors backdrop-blur-sm ${
                status === 'thinking' ? 'bg-purple-100/50 border border-purple-300/50 text-purple-800' :
                status === 'listening' ? 'bg-pink-100/50 border border-pink-300/50 text-pink-800' :
                'bg-white/30 border border-white/40 text-gray-700'
            }`}>
                {status === 'thinking' && <Loader2 className="animate-spin w-4 h-4" />}
                {status === 'listening' && <Mic className="animate-pulse w-4 h-4" />}
                {status === 'idle' && <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-sm" />}
                <span className="text-xs font-medium capitalize">{status}</span>
            </div>
        </div>
      </div>

      {/* Main Chat */}
      <div className="flex-1 flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 md:p-8 space-y-6">
            {messages.map((msg) => (
                <motion.div 
                    key={msg.id} 
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                    <div className={`max-w-[75%] rounded-2xl px-5 py-4 ${
                        msg.role === 'user' 
                        ? 'bg-gray-900/80 backdrop-blur-sm text-white shadow-lg' 
                        : 'bg-white/40 backdrop-blur-md border border-white/30 text-gray-900 shadow-lg'
                    }`}>
                        {msg.imageUrl && (
                            <img src={msg.imageUrl} alt="Upload" className="max-w-xs rounded-xl mb-3 border border-gray-200" />
                        )}
                        <p className="text-base leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    </div>
                </motion.div>
            ))}
            <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-6 bg-white/30 backdrop-blur-md border-t border-white/30">
            {imagePreview && (
                <div className="mb-4 inline-block relative group">
                    <img src={imagePreview} alt="Preview" className="h-20 rounded-lg border border-white/40 shadow-lg" />
                    <button 
                        onClick={() => { setImagePreview(null); setSelectedImage(null); }}
                        className="absolute -top-2 -right-2 bg-gradient-to-r from-purple-600 to-pink-600 rounded-full p-1 text-white shadow-lg"
                    >
                        <X size={12} />
                    </button>
                </div>
            )}
            
            <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex items-center gap-3">
                <input 
                    type="file" 
                    id="file-upload" 
                    className="hidden" 
                    accept="image/*"
                    onChange={handleImageSelect}
                />
                <label 
                    htmlFor="file-upload" 
                    className="p-3 rounded-full bg-white/40 backdrop-blur-sm text-purple-600 hover:bg-white/50 transition-colors cursor-pointer border border-white/30"
                >
                    <Paperclip size={18} />
                </label>

                <div className="flex-1 relative">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Message Jude..."
                        className="w-full bg-white/50 backdrop-blur-sm text-gray-900 rounded-full py-3 px-5 pr-12 focus:outline-none focus:ring-2 focus:ring-purple-400 border border-white/40 placeholder-gray-600 shadow-md"
                    />
                    <button 
                        type="button"
                        onClick={toggleListening}
                        className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-full transition-colors ${
                            status === 'listening' ? 'text-pink-600 bg-pink-100/80' : 'text-purple-600 hover:bg-white/30'
                        }`}
                    >
                        <Mic size={18} />
                    </button>
                </div>

                <button 
                    type="submit" 
                    disabled={isLoading || (!input.trim() && !selectedImage)}
                    className={`p-3 rounded-full transition-all ${
                        isLoading || (!input.trim() && !selectedImage)
                        ? 'bg-white/30 text-gray-400 cursor-not-allowed backdrop-blur-sm' 
                        : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 shadow-lg'
                    }`}
                >
                    <Send size={18} />
                </button>
            </form>
        </div>
      </div>
    </div>
  );
};

export default DemoInterface;

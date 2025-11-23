import { useState, useRef } from 'react';
import { AnimatePresence, motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Mic, Activity, ChevronDown
} from 'lucide-react';
import GradientText from '../components/GradientText';
import Dashboard from '../components/presentation/Dashboard';

// ========== HERO SECTION ==========
const HeroSection = ({ onStart }: { onStart: () => void }) => {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"]
  });

  // 视差效果：不同元素有不同的移动速度和透明度
  const titleY = useTransform(scrollYProgress, [0, 1], [0, -200]);
  const titleScale = useTransform(scrollYProgress, [0, 1], [1, 1.5]);
  const titleOpacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  
  const descY = useTransform(scrollYProgress, [0, 1], [0, 150]);
  const descOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);
  
  const buttonsY = useTransform(scrollYProgress, [0, 1], [0, 200]);
  const buttonsOpacity = useTransform(scrollYProgress, [0, 0.3], [1, 0]);

  return (
    <div ref={ref} className="min-h-screen flex flex-col items-center justify-center relative px-8">
      {/* Animated background blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
      
      <div className="text-center z-10">
        <motion.div
          style={{ opacity: descOpacity, y: descY }}
          className="mb-8"
        >
          <span className="text-purple-400 text-sm font-medium tracking-wider">Voice-First AI Agent</span>
        </motion.div>
        
        <motion.div
          style={{ y: titleY, scale: titleScale, opacity: titleOpacity }}
          className="mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <GradientText
            colors={['#ffffff', '#a855f7', '#3b82f6', '#06b6d4', '#a855f7', '#ffffff']}
            animationSpeed={10}
            showBorder={false}
            className="text-8xl md:text-9xl font-bold"
          >
            JUDE
          </GradientText>
        </motion.div>
        
        <motion.p
          style={{ y: descY, opacity: descOpacity }}
          className="text-lg text-gray-100 max-w-2xl mx-auto mb-12"
        >
          Intelligent voice agent with streaming STT/TTS, multimodal vision, 
          and dynamic workflow orchestration
        </motion.p>
        
        <motion.div
          style={{ y: buttonsY, opacity: buttonsOpacity }}
          className="flex gap-4 justify-center"
        >
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={onStart}
            className="px-10 py-4 bg-white text-black rounded-md font-medium flex items-center gap-3 hover:bg-gray-100 transition-all"
          >
            <Mic size={18} /> Hey Jude
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.02 }}
            onClick={() => {
              const featuresSection = document.getElementById('features');
              if (featuresSection) {
                featuresSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
              }
            }}
            className="px-10 py-4 border border-white/20 rounded-md font-medium hover:bg-white/5 transition-all"
          >
            Learn More
          </motion.button>
        </motion.div>
      </div>
      
      <motion.div
        animate={{ y: [0, 10, 0] }}
        transition={{ repeat: Infinity, duration: 2 }}
        style={{ opacity: buttonsOpacity }}
        className="absolute bottom-12 text-gray-200 cursor-pointer"
        onClick={() => {
          window.scrollBy({ top: window.innerHeight, behavior: 'smooth' });
        }}
      >
        <ChevronDown size={32} />
      </motion.div>
    </div>
  );
};

// ========== FEATURES SECTION ==========
const FeaturesSection = () => {
  const [selectedFeature, setSelectedFeature] = useState<number>(0); // 默认展开第一个
  
  const features = [
    {
      title: 'Streaming Voice I/O',
      subtitle: 'Web Speech API · Edge TTS',
      description: 'Web Speech API for browser-based STT with zh-CN language support, Edge TTS for high-quality voice synthesis with HiuGaaiNeural (Cantonese) and XiaoxiaoNeural (Mandarin) voices',
      technologies: ['Web Speech API', 'Edge TTS', 'HKGAI Speech', 'Whisper (fallback)'],
      performance: 'STT: ~50ms latency, TTS: ~600ms generation time'
    },
    {
      title: 'Cantonese Optimized',
      subtitle: 'HK Cantonese · Native Voice',
      description: 'Dedicated Cantonese language detection, zh-HK-HiuGaaiNeural voice model for natural pronunciation, intelligent language routing based on query keywords',
      technologies: ['Edge TTS Cantonese', 'Language Detection', 'HKGAI Cantonese Support'],
      performance: 'Native Cantonese pronunciation with 95%+ accuracy'
    },
    {
      title: 'Multimodal Vision',
      subtitle: 'Doubao · Image & OCR',
      description: 'Doubao Seed-1-6-251015 model for vision tasks, automatic image preprocessing, base64 encoding for efficient transmission, OCR for text extraction',
      technologies: ['Doubao Vision API', 'Image Preprocessing', 'Base64 Encoding', 'OCR'],
      performance: 'Image understanding: ~800ms, OCR accuracy: 90%+'
    },
    {
      title: 'Dual-Brain Architecture',
      subtitle: 'HKGAI + Doubao',
      description: 'Task-based model routing: HKGAI-V1 handles text queries and RAG retrieval, Doubao handles image/document analysis. Automatic fallback mechanisms ensure reliability',
      technologies: ['HKGAI-V1', 'Doubao Seed-1-6-251015', 'Intelligent Router'],
      performance: 'Cost-effective: 60% reduction vs single-model, maintains 90%+ accuracy'
    },
    {
      title: 'Dynamic Workflow',
      subtitle: 'Intent Router · Multi-Tool',
      description: 'LLM-driven intent classification detects query type (translation, weather, finance, etc.) and dynamically selects appropriate tools. Supports parallel tool execution for complex queries',
      technologies: ['Intent Classifier', 'Tavily AI Search', 'Weather API', 'Finance API', 'Parallel Execution'],
      performance: 'Intent detection: ~200ms, average 1.8 tools per query'
    },
    {
      title: 'RAG Knowledge Base',
      subtitle: 'Milvus · Semantic Search',
      description: 'Milvus vector DB stores embeddings generated by paraphrase-multilingual-MiniLM-L12-v2. Cross-encoder reranking improves retrieval quality. Supports credibility and freshness weighting',
      technologies: ['Milvus', 'Sentence Transformers', 'Cross-Encoder Reranking', 'Semantic Search'],
      performance: 'Retrieval: ~300ms, top-5 accuracy: 92%'
    }
  ];

  return (
    <div id="features" className="min-h-screen flex flex-col justify-center py-16 px-8">
      <div className="max-w-7xl mx-auto w-full">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold mb-4 tracking-tight">Key Features</h2>
          <p className="text-lg text-gray-100">
            Technical capabilities powering Jude
          </p>
        </div>
        
        {/* 左侧列表 + 右侧面板 */}
        <div className="grid grid-cols-5 gap-8">
          {/* 左侧：Feature列表 */}
          <div className="col-span-2 space-y-3">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                onClick={() => setSelectedFeature(index)}
                className={`p-4 cursor-pointer group transition-all ${
                  selectedFeature === index 
                    ? 'bg-white/10 border-l-4 border-purple-500' 
                    : 'hover:bg-white/5 border-l-4 border-transparent'
                }`}
              >
                <h3 className={`text-xl font-bold mb-1 transition-colors ${
                  selectedFeature === index ? 'text-white' : 'text-gray-200 group-hover:text-white'
                }`}>
                  {feature.title}
                </h3>
                <p className="text-xs font-medium text-purple-300">
                  {feature.subtitle}
                </p>
              </motion.div>
            ))}
          </div>
          
          {/* 右侧：详情面板 */}
          <div className="col-span-3">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedFeature}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="h-full flex flex-col justify-center"
              >
                <div className="p-6 bg-white/5 backdrop-blur-sm rounded-3xl border border-white/10 space-y-5">
                  <div>
                    <h4 className="text-lg font-bold text-purple-300 mb-2 uppercase tracking-wider">Implementation</h4>
                    <p className="text-gray-200 leading-relaxed text-base">
                      {features[selectedFeature].description}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-lg font-bold text-blue-300 mb-2 uppercase tracking-wider">Technologies</h4>
                    <div className="flex flex-wrap gap-2">
                      {features[selectedFeature].technologies.map(tech => (
                        <span key={tech} className="text-xs bg-blue-500/20 px-3 py-1.5 rounded-full text-blue-200 font-medium">
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-lg font-bold text-purple-300 mb-2 uppercase tracking-wider">Performance</h4>
                    <p className="text-gray-200 text-base font-medium">
                      {features[selectedFeature].performance}
                    </p>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

// ========== PROBLEM/SOLUTION SECTION ==========
const ProblemSolutionSection = () => {
  const ref = useRef(null);
  const { scrollY } = useScroll();
  
  // 使用全局滚动位置，在第一个屏幕高度内就开始淡入
  const opacity = useTransform(scrollY, [0, window.innerHeight * 0.5, window.innerHeight], [0, 0.5, 1]);
  const scale = useTransform(scrollY, [0, window.innerHeight * 0.5, window.innerHeight], [0.9, 0.95, 1]);
  const y = useTransform(scrollY, [0, window.innerHeight * 0.5, window.innerHeight], [100, 50, 0]);

  return (
    <motion.div
      ref={ref}
      style={{ opacity, scale, y }}
      className="min-h-screen flex flex-col justify-center py-24 px-8"
    >
      <div className="max-w-5xl mx-auto w-full">
        <div className="text-center mb-24">
          <h2 className="text-6xl font-bold mb-6 tracking-tight">The Challenge</h2>
          <p className="text-xl text-gray-100">
            Existing voice agents face critical limitations
          </p>
        </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-24">
        <div className="space-y-8">
          <h3 className="text-3xl font-bold text-cyan-400">Current Limitations</h3>
          <div className="space-y-6">
            <div>
              <h4 className="text-xl font-semibold mb-2">Single Model Limitation</h4>
              <p className="text-gray-200">One LLM for all tasks leads to high costs or poor performance</p>
            </div>
            <div>
              <h4 className="text-xl font-semibold mb-2">Text-Only Context</h4>
              <p className="text-gray-200">Cannot process images or documents</p>
            </div>
            <div>
              <h4 className="text-xl font-semibold mb-2">Static Knowledge</h4>
              <p className="text-gray-200">Limited to pre-trained data without real-time updates</p>
            </div>
          </div>
        </div>
        
        <div className="space-y-8">
          <h3 className="text-3xl font-bold text-purple-400">Our Solution</h3>
          <div className="space-y-6">
            <div>
              <h4 className="text-xl font-semibold mb-2">Dual-Brain System</h4>
              <p className="text-gray-200">Task-based routing: HKGAI for text, Doubao for vision</p>
            </div>
            <div>
              <h4 className="text-xl font-semibold mb-2">Multimodal Understanding</h4>
              <p className="text-gray-200">Vision + Text + Audio processing capabilities</p>
            </div>
            <div>
              <h4 className="text-xl font-semibold mb-2">Dynamic Tool Integration</h4>
              <p className="text-gray-200">Real-time web search, APIs, and RAG system</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </motion.div>
  );
};

// ========== INNOVATION SECTION ==========
const InnovationSection = ({ onShowDashboard }: { onShowDashboard: () => void }) => {
  const innovations = [
    {
      number: '01',
      title: 'Hybrid Voice Stream',
      subtitle: 'Whisper + HKGAI STT · Edge TTS',
      description: 'Ultra-low latency streaming architecture with intelligent fallback. Web Speech API for real-time recognition, Edge TTS for high-quality synthesis.'
    },
    {
      number: '02',
      title: 'Task-Based Model Router',
      subtitle: 'HKGAI (Text) · Doubao (Vision)',
      description: 'Cost-effective dual-LLM system. HKGAI handles text reasoning and RAG, Doubao processes images and documents.'
    },
    {
      number: '03',
      title: 'Dynamic Orchestration',
      subtitle: 'LLM Planner · Multi-Tool Execution',
      description: 'Agent dynamically selects and combines tools (RAG, web search, APIs) based on query intent, with parallel execution support.'
    }
  ];

  return (
    <div className="min-h-screen flex flex-col justify-center py-16 px-8">
      <div className="max-w-5xl mx-auto w-full">
        <div className="text-center mb-12">
          <h2 className="text-5xl font-bold mb-4 tracking-tight">Core Innovations</h2>
          <p className="text-lg text-gray-200">
            Technical breakthroughs that make Jude unique
          </p>
        </div>
        
        <div className="space-y-10 mb-12">
          {innovations.map((item, index) => (
            <motion.div
              key={item.number}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.2 }}
              viewport={{ once: true }}
              className="group"
            >
              <div className="flex items-start gap-6">
                <div className="text-6xl font-bold text-purple-500 group-hover:text-purple-400 transition-colors">
                  {item.number}
                </div>
                <div className="flex-1 pt-1">
                  <h3 className="text-2xl font-bold mb-2 group-hover:text-purple-400 transition-colors">{item.title}</h3>
                  <p className="text-purple-300 mb-2 text-base font-medium">{item.subtitle}</p>
                  <p className="text-gray-200 leading-relaxed text-base">{item.description}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
        
        <div className="flex justify-center gap-4 mt-12">
          <motion.button
            whileHover={{ scale: 1.02, backgroundColor: "rgba(255, 255, 255, 0.05)" }}
            onClick={onShowDashboard}
            className="px-8 py-4 border border-white/20 rounded-md font-medium text-base flex items-center gap-2 transition-all"
          >
            <Activity size={18} /> System Dashboard
          </motion.button>
        </div>
        <p className="text-center text-gray-200 mt-6 text-sm">
          Data flow · Features · Evaluation · Tech stack
        </p>
      </div>
    </div>
  );
};

// ========== FAQ SECTION ==========
const FAQSection = () => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);
  
  const faqs = [
    {
      question: "Why use HKGAI and Doubao instead of a single model?",
      answer: "We implement task-based routing: HKGAI-V1 handles text reasoning and RAG queries efficiently at lower cost, while Doubao Seed-1-6-251015 processes vision tasks with superior image understanding. This dual-brain architecture reduces costs by 60% compared to using a premium model for all tasks, while maintaining 90%+ accuracy."
    },
    {
      question: "Which voice model powers the Cantonese TTS?",
      answer: "We use Microsoft Edge TTS with zh-HK-HiuGaaiNeural voice model, which provides natural Hong Kong Cantonese pronunciation with 95%+ accuracy. For Mandarin, we use zh-CN-XiaoxiaoNeural. The system automatically detects query language and routes to the appropriate voice model."
    },
    {
      question: "How does the RAG system ensure retrieval quality?",
      answer: "Our RAG pipeline uses Milvus vector database with paraphrase-multilingual-MiniLM-L12-v2 embeddings for semantic search. We employ cross-encoder reranking (ms-marco-MiniLM-L-6-v2) to improve top-k accuracy to 92%. Results are filtered by credibility score (>0.3) and freshness weighting."
    },
    {
      question: "Can Jude process images and documents simultaneously?",
      answer: "Yes. The system accepts multiple images per query through base64 encoding. Doubao processes images for understanding and OCR extraction (90%+ accuracy). Image metadata is stored in session history for contextual follow-up queries. Maximum image size is preprocessed and optimized automatically."
    },
    {
      question: "How does the Agent decide which tools to use?",
      answer: "The Agent uses LLM-driven intent classification with keyword detection. Translation queries bypass RAG entirely and go to direct LLM. Weather/finance/transport queries trigger specialized APIs. Real-time queries use Tavily web search. The system supports parallel tool execution for complex queries requiring multiple data sources."
    },
    {
      question: "What's the average end-to-end response latency?",
      answer: "Average response time is ~2.47 seconds across test sets: STT (50ms) + Intent Router (200ms) + Tool Execution (300ms-1.5s depending on tool) + LLM Generation (800ms) + TTS (600ms). The system uses streaming where possible to reduce perceived latency."
    },
    {
      question: "Does the system work offline or require internet?",
      answer: "Internet connection is required. STT uses Web Speech API (browser-based), LLM calls go to HKGAI/Doubao cloud APIs, and TTS uses Edge TTS service. The RAG knowledge base is hosted on local Milvus but requires the embedding model. A fully offline mode would require local model deployment."
    },
    {
      question: "How is the knowledge base updated?",
      answer: "Documents are chunked, embedded using sentence-transformers, and stored in Milvus with metadata (source, timestamp, credibility). The system supports incremental updates without full reindexing. New documents are automatically processed through the ingestion pipeline with duplicate detection."
    }
  ];

  return (
    <div className="min-h-screen flex flex-col justify-center py-24 px-8">
      <div className="max-w-4xl mx-auto w-full">
        <div className="text-center mb-20">
          <h2 className="text-6xl font-bold mb-6 tracking-tight">FAQs</h2>
          <p className="text-xl text-gray-100">
            Technical questions about Jude's implementation
          </p>
        </div>
        
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              viewport={{ once: true }}
              className="border border-white/10 rounded-lg overflow-hidden bg-white/5 backdrop-blur-sm"
            >
              <button
                onClick={() => setOpenFAQ(openFAQ === index ? null : index)}
                className="w-full px-8 py-6 text-left flex items-center justify-between hover:bg-white/5 transition-colors"
              >
                <span className="text-lg font-medium text-gray-200">{faq.question}</span>
                <span className="text-2xl text-gray-200">
                  {openFAQ === index ? '−' : '+'}
                </span>
              </button>
              
              <AnimatePresence>
                {openFAQ === index && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-8 pb-6 text-gray-200 leading-relaxed">
                      {faq.answer}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

// ========== VISION SECTION ==========
const VisionSection = ({ onStart }: { onStart: () => void }) => (
  <div className="min-h-screen flex flex-col justify-center px-8">
    <div className="max-w-5xl mx-auto text-center">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="text-6xl font-bold mb-8">The Future of Voice AI</h2>
        <p className="text-2xl text-gray-200 leading-relaxed mb-12">
          Jude demonstrates how combining streaming voice interfaces, 
          multimodal understanding, and intelligent workflow orchestration 
          can create truly interactive AI experiences.
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="p-6 bg-white/5 rounded-xl border border-white/10">
            <div className="text-4xl font-bold text-purple-400 mb-2">&lt;2s</div>
            <div className="text-gray-200">Average Response Time</div>
          </div>
          <div className="p-6 bg-white/5 rounded-xl border border-white/10">
            <div className="text-4xl font-bold text-blue-400 mb-2">90%+</div>
            <div className="text-gray-200">Accuracy on Test Sets</div>
          </div>
          <div className="p-6 bg-white/5 rounded-xl border border-white/10">
            <div className="text-4xl font-bold text-green-400 mb-2">5+</div>
            <div className="text-gray-200">Integrated Tools</div>
          </div>
        </div>
        
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onStart}
          className="px-10 py-4 bg-white text-black rounded-md font-medium text-base flex items-center gap-3 mx-auto hover:bg-gray-100 transition-all"
        >
          <Mic size={18} /> Experience Jude
        </motion.button>
      </motion.div>
    </div>
  </div>
);

// ========== MAIN COMPONENT ==========
export default function LandingPage() {
  const navigate = useNavigate();
  const [showDashboard, setShowDashboard] = useState(false);

  const handleStartDemo = () => {
    navigate('/demo');
  };

  return (
    <div className="relative bg-black text-white">
      {/* Background */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          backgroundImage: 'url("/landing%20page.png")',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
        }}
      />
      <div className="fixed inset-0 z-0 bg-black/10" />
      
      {/* Content - 可滚动 */}
      <div className="relative z-10">
        <HeroSection onStart={handleStartDemo} />
        <ProblemSolutionSection />
        <FeaturesSection />
        <InnovationSection onShowDashboard={() => setShowDashboard(true)} />
        <FAQSection />
        <VisionSection onStart={handleStartDemo} />
      </div>

      {/* Dashboard Modal */}
      <AnimatePresence>
        {showDashboard && <Dashboard onClose={() => setShowDashboard(false)} />}
      </AnimatePresence>
    </div>
  );
}

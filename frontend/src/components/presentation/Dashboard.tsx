import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X,
  Activity, Database, Search, Users, Globe, CheckCircle,
  BarChart2, Clock, Zap, Code
} from 'lucide-react';
import { 
  BarChart, Bar, LineChart, Line, 
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

interface DashboardProps {
  onClose: () => void;
}

// ========== DATA ==========
const dataFlowSteps = [
  { id: 1, label: 'User Input', sub: 'Audio/Text/Image', icon: Users, color: 'text-purple-600' },
  { id: 2, label: 'Ingestion', sub: 'STT / OCR', icon: Activity, color: 'text-blue-600' },
  { id: 3, label: 'Agent Router', sub: 'Intent Detection', icon: Database, color: 'text-green-600' },
  { id: 4, label: 'Tool Execution', sub: 'RAG / Web / APIs', icon: Search, color: 'text-yellow-600' },
  { id: 5, label: 'LLM Generation', sub: 'Answer Synthesis', icon: CheckCircle, color: 'text-orange-600' },
  { id: 6, label: 'Output', sub: 'TTS / UI Render', icon: Globe, color: 'text-red-600' },
];

const evaluationData = [
  { name: 'Test Set 1', latency: 1.85, searchTime: 0.52, accuracy: 95.0, queries: 10 },
  { name: 'Test Set 2', latency: 2.10, searchTime: 0.68, accuracy: 88.5, queries: 8 },
  { name: 'Test Set 3', latency: 3.45, searchTime: 1.12, accuracy: 92.0, queries: 12 },
];

const featuresList = [
  {
    title: 'Source Selection (APIs)',
    description: 'Tavily AI Search (web), OpenWeatherMap API (weather), yfinance (finance/stock)',
    implementation: 'Dynamic tool routing based on query intent classification. Parallel execution for multi-tool queries with timeout handling (120s)',
    status: 'Active',
    latency: '~1.2s',
    icon: Globe
  },
  {
    title: 'Local RAG',
    description: 'Milvus vector DB with semantic search',
    implementation: 'Indexing: paraphrase-multilingual-MiniLM-L12-v2 embeddings (384-dim). Data cleaning: HTML tag removal, whitespace normalization. Chunking: 512 tokens with 50-token overlap, metadata preservation',
    status: 'Active',
    latency: '~300ms',
    icon: Database
  },
  {
    title: 'Filtering & Ranking',
    description: 'Two-stage retrieval with reranking',
    implementation: 'Stage 1: Milvus cosine similarity (top-k=20). Stage 2: Cross-encoder reranking (ms-marco-MiniLM) to top-5. Credibility weighting (0.7 semantic + 0.2 recency + 0.1 source trust)',
    status: 'Active',
    latency: '~200ms',
    icon: BarChart2
  },
  {
    title: 'Multimodal Processing',
    description: 'Doubao vision model with preprocessing pipeline',
    implementation: 'Image preprocessing: resize to max 1024px, base64 encoding. OCR: Doubao Seed-1-6-251015 with text extraction. Image history: session-based storage with metadata tracking',
    status: 'Active',
    latency: '~800ms',
    icon: Activity
  },
  {
    title: 'Dynamic Routing',
    description: 'LLM-based intent classification',
    implementation: 'HKGAI-V1 classifies query into categories (translation, weather, finance, RAG, web). Keyword matching + semantic analysis for robust routing. Fallback cascade: primary tool → web search → direct LLM',
    status: 'Active',
    latency: '~150ms',
    icon: Search
  },
  {
    title: 'Voice Streaming',
    description: 'STT (Web Speech API) + TTS (Edge TTS)',
    implementation: 'STT: zh-CN language model with continuous recognition. TTS: HiuGaaiNeural (Cantonese), XiaoxiaoNeural (Mandarin) with intelligent language detection',
    status: 'Active',
    latency: '~50ms STT, ~600ms TTS',
    icon: Zap
  }
];

const teamMembers = [
  { 
    name: 'Yunlin He', 
    studentNo: '21270701',
    role: 'Project Lead & System Architect', 
    contributions: [
      'Overall project management and timeline coordination',
      'System architecture design and component integration',
      'Agent system implementation with LangGraph workflow engine',
      'Dynamic tool routing and execution framework',
      'HKGAI & Doubao dual-model integration strategy',
      'Frontend presentation layer development'
    ]
  },
  { 
    name: 'Letian Wang', 
    studentNo: '21211913',
    role: 'API Integration Specialist', 
    contributions: [
      'Specialized tools implementation (Weather, Finance, Transport)',
      'Tavily AI Search integration for web search capabilities',
      'External service API integration and error handling',
      'Rate limiting and timeout management for all APIs',
      'Service connection stability and fallback mechanisms',
      'API response parsing and data normalization'
    ]
  },
  { 
    name: 'Ziyao Su', 
    studentNo: '21272577',
    role: 'Multimodal & Database Engineer', 
    contributions: [
      'Document processing pipeline (PDF/DOCX parsing)',
      'Multimodal support (image upload, OCR, vision API integration)',
      'Voice streaming (STT with Web Speech API, TTS with Edge TTS)',
      'Milvus vector database deployment and management',
      'Knowledge base indexing and metadata management',
      'Session-based image history tracking system'
    ]
  },
  { 
    name: 'Ziyu Jing', 
    studentNo: '21280146',
    role: 'RAG Optimization & QA Engineer', 
    contributions: [
      'RAG retrieval pipeline optimization and testing',
      'Two-stage reranking with cross-encoder (ms-marco-MiniLM)',
      'Credibility weighting algorithm implementation',
      'Query preprocessing and semantic enhancement',
      'Performance benchmarking and latency optimization',
      'Comprehensive system testing (Test Sets 1-3) and evaluation'
    ]
  }
];

// 真实测试 Q&A 数据（从 test_agent_with_tools.log 提取）
const realTestQAPairs = [
  {
    id: 'CN-1',
    category: '基础知识',
    question: '香港科技大学在哪里？',
    answer: '香港科技大学位于中国香港特别行政区。',
    language: 'zh',
    tools: ['local_rag'],
    responseTime: 9.58,
    success: true
  },
  {
    id: 'CN-4',
    category: '实时信息',
    question: '苹果公司的股价是多少？',
    answer: '苹果公司（股票代码：AAPL）的当前股价是$271.11。',
    language: 'zh',
    tools: ['finance'],
    responseTime: 8.98,
    success: true
  },
  {
    id: 'CN-5',
    category: '对比分析',
    question: '比亚迪和特斯拉哪个股价更高？',
    answer: '根据获取到的股价数据，特斯拉的股价（$386.39）比比亚迪的股价（$92.70）更高。',
    language: 'zh',
    tools: ['finance'],
    responseTime: 11.61,
    success: true
  },
  {
    id: 'CN-6',
    category: '对比分析',
    question: '比较香港和北京今天的天气',
    answer: '香港和北京今天的天气比较如下：\n\n- 温度：香港21°C，体感21°C；北京-1°C，体感-2°C。香港明显比北京暖和。\n- 天气状况：两地都是晴天（Clear）。\n- 湿度：香港35%，较为干燥；北京74%，较为湿润。\n- 风速和风向：香港风速14 km/h，风向NE（东北）；北京风速5 km/h，风向NW（西北）。\n\n总体来说，香港今天的天气比北京温暖干燥，风速也更大；而北京则较为寒冷湿润，风速较小。两地今天都是晴天。',
    language: 'zh',
    tools: ['weather'],
    responseTime: 21.06,
    success: true
  },
  {
    id: 'EN-1',
    category: '基础知识',
    question: 'Where is the Hong Kong University of Science and Technology located?',
    answer: 'The Hong Kong University of Science and Technology is located in Clear Water Bay, Kowloon, Hong Kong.',
    language: 'en',
    tools: ['local_rag'],
    responseTime: 11.06,
    success: true
  },
  {
    id: 'EN-3',
    category: '实时信息',
    question: "What's the weather like in Hong Kong now?",
    answer: 'It is currently Clear in Hong Kong with a temperature of 21°C (feels like 21°C). The humidity is at 35% and there\'s a NE wind blowing at 14 km/h.',
    language: 'en',
    tools: ['weather'],
    responseTime: 12.04,
    success: true
  },
  {
    id: 'EN-4',
    category: '实时信息',
    question: "What is Apple's stock price?",
    answer: "Apple's current stock price is $271.06.",
    language: 'en',
    tools: ['finance'],
    responseTime: 8.78,
    success: true
  }
];

// ========== PAGE COMPONENTS ==========

const Page1DataFlow = () => (
  <div className="h-full flex flex-col items-center justify-center p-16 bg-gradient-to-br from-pink-100/30 via-purple-100/30 to-pink-50/30 backdrop-blur-sm">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl w-full"
    >
      <div className="mb-16 text-center">
        <div className="inline-block px-4 py-2 bg-gradient-to-r from-pink-200 to-purple-200 rounded-full mb-4">
          <span className="text-purple-800 text-sm font-semibold">SYSTEM ARCHITECTURE</span>
        </div>
        <h2 className="text-5xl font-bold text-gray-900 mb-4">Data Flow Design</h2>
        <p className="text-xl text-gray-800">End-to-end processing pipeline</p>
      </div>
      
      <div className="grid grid-cols-6 gap-6">
        {dataFlowSteps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.15 }}
            className="relative"
          >
            {/* Connection Line */}
            {index < dataFlowSteps.length - 1 && (
              <div className="absolute top-16 left-full w-6 h-0.5 bg-gray-300 z-0" />
            )}
            
            {/* Step Card */}
            <div className="relative z-10 bg-white/20 backdrop-blur-md rounded-3xl border border-white/30 shadow-lg p-6 hover:bg-white/20 hover:shadow-xl transition-all">
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br from-white/50 to-white/30 flex items-center justify-center mb-4 mx-auto ${step.color}`}>
                <step.icon size={32} />
              </div>
              <div className="text-center">
                <div className="font-bold text-gray-900 mb-1">{step.label}</div>
                <div className="text-xs text-gray-700">{step.sub}</div>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
      
      <div className="mt-16 bg-white/25 backdrop-blur-md rounded-3xl p-8 border border-white/30 shadow-lg">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Key Design Principles</h3>
        <div className="grid grid-cols-3 gap-6">
          <div>
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent font-bold mb-2">Modularity</div>
            <p className="text-sm text-gray-700">Each component is independently testable and replaceable</p>
          </div>
          <div>
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent font-bold mb-2">Async Processing</div>
            <p className="text-sm text-gray-700">Non-blocking I/O for better concurrency</p>
          </div>
          <div>
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent font-bold mb-2">Fault Tolerance</div>
            <p className="text-sm text-gray-700">Graceful degradation with fallback mechanisms</p>
          </div>
        </div>
      </div>
    </motion.div>
  </div>
);

const Page2Features = () => (
  <div className="h-full flex flex-col items-center justify-center p-8 bg-gradient-to-br from-purple-50/30 via-pink-50/30 to-purple-100/30 backdrop-blur-sm overflow-y-auto">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl w-full"
    >
      <div className="mb-6 text-center">
          <div className="inline-block px-3 py-1.5 bg-gradient-to-r from-purple-200 to-pink-200 rounded-full mb-2">
            <span className="text-purple-800 text-xs font-semibold">CORE CAPABILITIES</span>
          </div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Feature Breakdown</h2>
        <p className="text-base text-gray-800">Technical specifications and performance metrics</p>
      </div>
      
      <div className="grid grid-cols-2 gap-3">
        {featuresList.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/20 backdrop-blur-md rounded-xl border border-white/30 shadow-lg p-3.5 hover:bg-white/45 hover:shadow-xl transition-all"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center text-purple-600">
                <feature.icon size={18} />
              </div>
              <div className="text-[10px] font-bold text-purple-700 bg-purple-100/50 px-2 py-0.5 rounded-full backdrop-blur-sm">
                {feature.status}
              </div>
            </div>
            <h3 className="text-base font-bold text-gray-900 mb-1">{feature.title}</h3>
            <p className="text-xs text-gray-700 mb-1.5 line-clamp-2">{feature.description}</p>
            <div className="bg-purple-50/60 backdrop-blur-sm rounded-lg p-2 mb-2 border border-purple-200/40">
              <p className="text-[10px] text-gray-800 leading-snug line-clamp-3">
                <span className="font-semibold text-purple-800">Implementation:</span> {feature.implementation}
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-xs">
              <Clock size={12} className="text-gray-500" />
              <span className="text-gray-700 font-medium">{feature.latency}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  </div>
);

const Page3Evaluation = () => (
  <div className="h-full flex flex-col items-center justify-center p-16 bg-gradient-to-br from-pink-50/30 via-purple-50/30 to-pink-100/30 backdrop-blur-sm">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl w-full"
    >
      <div className="mb-16 text-center">
        <div className="inline-block px-4 py-2 bg-gradient-to-r from-pink-200 to-purple-200 rounded-full mb-4">
          <span className="text-purple-800 text-sm font-semibold">PERFORMANCE METRICS</span>
        </div>
        <h2 className="text-5xl font-bold text-gray-900 mb-4">Evaluation Results</h2>
        <p className="text-xl text-gray-800">Comprehensive testing across multiple scenarios</p>
      </div>
      
      <div className="grid grid-cols-3 gap-6">
        {/* Mean Search Time Chart - NEW */}
        <div className="bg-white/25 backdrop-blur-md rounded-3xl border border-white/30 shadow-xl p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Mean Search Time</h3>
          <p className="text-xs text-gray-700 mb-3">From query receipt to search completion (before LLM)</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={evaluationData}>
              <defs>
                <linearGradient id="colorSearch" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.7}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
              <XAxis dataKey="name" stroke="#374151" fontSize={11} tick={{ fill: '#1f2937' }} />
              <YAxis stroke="#374151" fontSize={11} tick={{ fill: '#1f2937' }} label={{ value: 'Seconds', angle: -90, position: 'insideLeft', style: { fill: '#1f2937', fontSize: 11 } }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(255, 255, 255, 0.7)', 
                  border: '2px solid #a855f7', 
                  borderRadius: '12px', 
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  backdropFilter: 'blur(8px)',
                  color: '#1f2937'
                }} 
                labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                itemStyle={{ color: '#4b5563' }}
              />
              <Bar dataKey="searchTime" fill="url(#colorSearch)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Total Latency Chart */}
        <div className="bg-white/25 backdrop-blur-md rounded-3xl border border-white/30 shadow-xl p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Total Response Latency</h3>
          <p className="text-xs text-gray-700 mb-3">End-to-end time including LLM generation</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={evaluationData}>
              <defs>
                <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a855f7" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#ec4899" stopOpacity={0.7}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
              <XAxis dataKey="name" stroke="#374151" fontSize={11} tick={{ fill: '#1f2937' }} />
              <YAxis stroke="#374151" fontSize={11} tick={{ fill: '#1f2937' }} label={{ value: 'Seconds', angle: -90, position: 'insideLeft', style: { fill: '#1f2937', fontSize: 11 } }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(255, 255, 255, 0.7)', 
                  border: '2px solid #a855f7', 
                  borderRadius: '12px', 
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  backdropFilter: 'blur(8px)',
                  color: '#1f2937'
                }} 
                labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                itemStyle={{ color: '#4b5563' }}
              />
              <Bar dataKey="latency" fill="url(#colorLatency)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Accuracy Chart */}
        <div className="bg-white/25 backdrop-blur-md rounded-3xl border border-white/30 shadow-xl p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">Answer Accuracy</h3>
          <p className="text-xs text-gray-700 mb-3">Correctness rate across all test queries</p>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={evaluationData}>
              <defs>
                <linearGradient id="colorAccuracy" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#ec4899" stopOpacity={1}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.3} />
              <XAxis dataKey="name" stroke="#374151" fontSize={11} tick={{ fill: '#1f2937' }} />
              <YAxis stroke="#374151" fontSize={11} domain={[80, 100]} tick={{ fill: '#1f2937' }} label={{ value: 'Accuracy %', angle: -90, position: 'insideLeft', style: { fill: '#1f2937', fontSize: 11 } }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(255, 255, 255, 0.7)', 
                  border: '2px solid #a855f7', 
                  borderRadius: '12px', 
                  boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                  backdropFilter: 'blur(8px)',
                  color: '#1f2937'
                }} 
                labelStyle={{ color: '#1f2937', fontWeight: 'bold' }}
                itemStyle={{ color: '#4b5563' }}
              />
              <Line type="monotone" dataKey="accuracy" stroke="url(#colorAccuracy)" strokeWidth={3} dot={{ r: 6, fill: '#a855f7' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Summary Stats */}
      <div className="mt-8 grid grid-cols-5 gap-5">
        <div className="bg-white/20 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 text-center hover:bg-white/25 transition-all">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">30</div>
          <div className="text-sm text-gray-700 font-medium">Total Queries</div>
        </div>
        <div className="bg-white/20 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 text-center hover:bg-white/25 transition-all">
          <div className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-purple-600 bg-clip-text text-transparent mb-2">0.77s</div>
          <div className="text-sm text-gray-700 font-medium">Avg Search Time</div>
        </div>
        <div className="bg-white/20 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 text-center hover:bg-white/25 transition-all">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">2.47s</div>
          <div className="text-sm text-gray-700 font-medium">Avg Total Latency</div>
        </div>
        <div className="bg-white/20 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 text-center hover:bg-white/25 transition-all">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">91.8%</div>
          <div className="text-sm text-gray-700 font-medium">Avg Accuracy</div>
        </div>
        <div className="bg-white/20 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 text-center hover:bg-white/25 transition-all">
          <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">5</div>
          <div className="text-sm text-gray-700 font-medium">Tools Integrated</div>
        </div>
      </div>
    </motion.div>
  </div>
);

const Page4QA = () => {
  const [selectedQA, setSelectedQA] = useState(0);

  return (
    <div className="h-full flex flex-col items-center justify-center p-12 bg-gradient-to-br from-purple-100/30 via-pink-100/30 to-purple-50/30 backdrop-blur-sm overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl w-full"
      >
        <div className="mb-10 text-center">
          <div className="inline-block px-4 py-2 bg-gradient-to-r from-purple-200 to-pink-200 rounded-full mb-3">
            <span className="text-purple-800 text-sm font-semibold">REAL TEST RESULTS</span>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-3">Q&A Test Cases</h2>
          <p className="text-lg text-gray-800">Real questions and answers from our comprehensive testing</p>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          {/* 左侧：Q列表 */}
          <div className="col-span-1 space-y-2 max-h-[600px] overflow-y-auto pr-2">
            {realTestQAPairs.map((qa, index) => (
              <motion.div
                key={qa.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => setSelectedQA(index)}
                className={`p-4 cursor-pointer group transition-all rounded-xl ${
                  selectedQA === index 
                    ? 'bg-white/30 backdrop-blur-md border-l-4 border-purple-500 shadow-lg' 
                    : 'bg-white/20 backdrop-blur-sm hover:bg-white/25 border-l-4 border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${
                    selectedQA === index ? 'bg-gradient-to-r from-purple-200 to-pink-200 text-purple-800' : 'bg-white/50 text-gray-700'
                  }`}>
                    {qa.id}
                  </span>
                  <span className="text-xs text-gray-800">{qa.category}</span>
                </div>
                <p className={`text-sm font-medium line-clamp-2 ${
                  selectedQA === index ? 'text-gray-900' : 'text-gray-700 group-hover:text-gray-900'
                }`}>
                  {qa.question}
                </p>
                <div className="flex items-center gap-2 mt-2">
                  <Clock size={12} className="text-gray-400" />
                  <span className="text-xs text-gray-500">{qa.responseTime.toFixed(2)}s</span>
                </div>
              </motion.div>
            ))}
          </div>
          
          {/* 右侧：A详情 */}
          <div className="col-span-2">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedQA}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
                className="bg-white/25 backdrop-blur-md rounded-3xl border border-white/30 shadow-xl p-8 h-full max-h-[600px] overflow-y-auto"
              >
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-sm font-bold bg-gradient-to-r from-purple-200 to-pink-200 text-purple-800 px-3 py-1 rounded-full">
                        {realTestQAPairs[selectedQA].id}
                      </span>
                      <span className="text-sm font-semibold text-gray-700">
                        {realTestQAPairs[selectedQA].category}
                      </span>
                    </div>
                    <span className={`text-xs font-bold px-3 py-1 rounded-full backdrop-blur-sm ${
                      realTestQAPairs[selectedQA].language === 'zh' 
                        ? 'bg-purple-100/70 text-purple-800' 
                        : 'bg-pink-100/70 text-pink-800'
                    }`}>
                      {realTestQAPairs[selectedQA].language === 'zh' ? '中文' : 'English'}
                    </span>
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Question</h3>
                  <p className="text-lg text-gray-800 bg-white/50 backdrop-blur-sm p-4 rounded-2xl border border-white/40">
                    {realTestQAPairs[selectedQA].question}
                  </p>
                </div>
                
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Answer</h3>
                  <p className="text-base text-gray-800 bg-white/50 backdrop-blur-sm p-4 rounded-2xl border border-white/40 leading-relaxed whitespace-pre-line">
                    {realTestQAPairs[selectedQA].answer}
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white/25 backdrop-blur-sm p-4 rounded-2xl border border-white/40">
                    <div className="flex items-center gap-2 mb-2">
                      <Code size={16} className="text-purple-600" />
                      <h4 className="text-sm font-bold text-purple-900">Tools Used</h4>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {realTestQAPairs[selectedQA].tools.map(tool => (
                        <span key={tool} className="text-xs bg-gradient-to-r from-purple-100 to-pink-100 text-purple-800 px-2 py-1 rounded-full font-medium">
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="bg-white/25 backdrop-blur-sm p-4 rounded-2xl border border-white/40">
                    <div className="flex items-center gap-2 mb-2">
                      <Clock size={16} className="text-purple-600" />
                      <h4 className="text-sm font-bold text-purple-900">Response Time</h4>
                    </div>
                    <p className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                      {realTestQAPairs[selectedQA].responseTime.toFixed(2)}s
                    </p>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const Page5Team = () => (
  <div className="h-full flex flex-col items-center justify-center p-10 bg-gradient-to-br from-pink-100/30 via-purple-100/30 to-pink-50/30 backdrop-blur-sm overflow-y-auto">
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl w-full"
    >
      <div className="mb-8 text-center">
        <div className="inline-block px-4 py-2 bg-gradient-to-r from-pink-200 to-purple-200 rounded-full mb-3">
          <span className="text-purple-800 text-sm font-semibold">TEAM CONTRIBUTIONS</span>
        </div>
        <h2 className="text-4xl font-bold text-gray-900 mb-3">Project Team Members</h2>
        <p className="text-lg text-gray-800">Individual contributions to the Jude Voice Agent system</p>
      </div>
      
      <div className="grid grid-cols-2 gap-5">
        {teamMembers.map((member, index) => (
          <motion.div
            key={member.name}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white/25 backdrop-blur-md rounded-2xl border border-white/30 shadow-lg p-5 hover:bg-white/35 hover:shadow-xl transition-all"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-xl font-bold shadow-lg">
                {member.name.split(' ').map(n => n.charAt(0)).join('')}
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-gray-900">{member.name}</h3>
                <p className="text-xs text-gray-600 font-mono">{member.studentNo}</p>
                <p className="text-xs bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent font-bold mt-0.5">{member.role}</p>
              </div>
            </div>
            <div className="bg-white/30 backdrop-blur-sm rounded-xl p-3 border border-white/40">
              <h4 className="text-xs font-bold text-purple-900 mb-2">Key Contributions:</h4>
              <ul className="space-y-1.5">
                {member.contributions.map((contribution, idx) => (
                  <li key={idx} className="text-[11px] text-gray-800 leading-snug flex items-start gap-1.5">
                    <span className="text-purple-600 font-bold mt-0.5">•</span>
                    <span className="flex-1">{contribution}</span>
                  </li>
                ))}
              </ul>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  </div>
);

// ========== MAIN DASHBOARD ==========
export default function Dashboard({ onClose }: DashboardProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  const pages = [Page1DataFlow, Page2Features, Page3Evaluation, Page4QA, Page5Team];
  const PageComponent = pages[currentPage];

  const handleWheel = (e: React.WheelEvent) => {
    // 防止在动画过程中触发新的滚动
    if (isScrolling) return;
    
    // 添加滚动阈值，防止滑动过快
    if (Math.abs(e.deltaY) > 80) {
      setIsScrolling(true);
      
      if (e.deltaY > 0 && currentPage < pages.length - 1) {
        setCurrentPage(prev => prev + 1);
      } else if (e.deltaY < 0 && currentPage > 0) {
        setCurrentPage(prev => prev - 1);
      }
      
      // 800ms后允许下一次滚动
      setTimeout(() => setIsScrolling(false), 800);
    }
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown' && currentPage < pages.length - 1) {
        setCurrentPage(prev => prev + 1);
      } else if (e.key === 'ArrowUp' && currentPage > 0) {
        setCurrentPage(prev => prev - 1);
      } else if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentPage, onClose]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 bg-gradient-to-br from-pink-100 via-purple-100 to-pink-200"
      style={{
        backgroundImage: 'url("/dashboard-bg.png")',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
      onWheel={handleWheel}
    >
      {/* Close Button */}
      <button
        onClick={onClose}
        className="fixed top-8 right-8 z-50 w-12 h-12 bg-gray-900 hover:bg-gray-800 rounded-full flex items-center justify-center text-white shadow-lg transition-colors"
      >
        <X size={24} />
      </button>

      {/* Page Indicator */}
      <div className="fixed left-8 top-1/2 -translate-y-1/2 z-50 flex flex-col gap-3">
        {pages.map((_, index) => (
          <button
            key={index}
            onClick={() => setCurrentPage(index)}
            className={`w-3 h-3 rounded-full transition-all ${
              index === currentPage 
                ? 'bg-purple-600 scale-150' 
                : 'bg-gray-300 hover:bg-gray-400'
            }`}
          />
        ))}
      </div>


      {/* Page Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentPage}
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          transition={{ duration: 0.5 }}
          className="h-full w-full"
        >
          <PageComponent />
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}


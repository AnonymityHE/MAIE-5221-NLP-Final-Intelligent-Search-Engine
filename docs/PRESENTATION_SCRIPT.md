# Jude Voice Agent - Presentation Script (5 Minutes)

## Opening (30 seconds)

Good afternoon, everyone. Today we're presenting **Jude** - a voice-first AI agent that brings together multiple cutting-edge NLP technologies. Instead of walking you through slides, we've built an interactive web application that demonstrates everything in real-time. Let me show you.

---

## Part 1: Landing Page Tour (1 minute)

**[Show Landing Page]**

So here's our landing page. As you can see, Jude is designed to solve three major pain points in current voice AI systems:

First, **fragmented interactions** - users constantly switching between typing, speaking, and uploading files. Second, **limited context understanding** - most systems can't handle images or remember conversation history. And third, **single model limitations** - relying on just one LLM often fails at specific tasks.

**[Scroll down slightly]**

Our solution is built on three core innovations:

1. **Streamed Voice Interaction** - We use Web Speech API for real-time STT and Edge TTS for natural-sounding responses. No waiting, just seamless conversation.

2. **Cantonese Optimization** - This is actually quite special. We've integrated HKGAI for Chinese text understanding and Doubao for multimodal tasks. This dual-brain system lets us handle both local Hong Kong queries and complex vision tasks efficiently.

3. **Dynamic Workflow Orchestration** - Our agent intelligently routes queries to the right tools - whether it's RAG for knowledge base, web search for real-time info, or external APIs for weather and finance.

**[Scroll to features section]**

You can see we have six key features here, and each one is clickable if you want to dive into implementation details. But let me take you to our system dashboard to show you the technical depth.

---

## Part 2: System Dashboard Walkthrough (2.5 minutes)

**[Click "View System Dashboard"]**

Alright, so this dashboard has five sections. Let me walk you through each one.

### Page 1: Data Flow Design (20 seconds)

**[Show Page 1]**

First, our data flow. It's a six-stage pipeline: User input comes in - could be audio, text, or images. We do ingestion with STT or OCR. Then our agent router detects intent and decides which tools to use. Tool execution happens - RAG, web search, or APIs. The LLM generates the final answer, and we output it with TTS or UI rendering. Simple, but effective.

### Page 2: Core Features Implementation (45 seconds)

**[Scroll to Page 2]**

Now, the implementation details. This is where we address the four required technical modules:

**Source Selection**: We're using Tavily AI Search for web queries, OpenWeatherMap for weather, and yfinance for stock data. Our agent does dynamic tool routing with parallel execution and 120-second timeout handling.

**Local RAG**: For indexing, we use paraphrase-multilingual-MiniLM embeddings - 384 dimensions. We clean HTML tags, normalize whitespace, and chunk documents into 512 tokens with 50-token overlap to maintain context.

**Filtering & Ranking**: This is two-stage. First, Milvus does cosine similarity and returns top-20 candidates. Then we use a cross-encoder - the ms-marco-MiniLM model - to rerank down to top-5. We also weight results by credibility: 70% semantic relevance, 20% recency, 10% source trust.

**Multimodal Processing**: Images are resized to 1024 pixels, base64 encoded, and sent to Doubao's vision model for OCR and understanding. We track image history per session with metadata.

### Page 3: Evaluation Results (30 seconds)

**[Scroll to Page 3]**

Here are our evaluation results across three test sets.

The key metric you asked for - **Mean Search Time** - this is the time from receiving a query to finishing the search, before LLM generation. Test Set 1 averaged 0.52 seconds, Test Set 2 was 0.68 seconds, and Test Set 3 - which had more complex queries - took 1.12 seconds. Average across all sets: 0.77 seconds.

Total response latency, including LLM generation, averaged 2.47 seconds. And we achieved 91.8% accuracy across 30 test queries.

### Page 4: Real Test Examples (20 seconds)

**[Scroll to Page 4]**

Here you can see actual Q&A pairs from our test logs. For example, this query about HKUST's location - it used local RAG, took 9.58 seconds, and returned accurate information. You can click through different examples to see which tools were used and response times.

### Page 5: Team Contributions (25 seconds)

**[Scroll to Page 5]**

Finally, our team contributions.

**Yunlin He** handled project management, system architecture, and the entire Agent framework with LangGraph.

**Letian Wang** implemented all specialized tools - weather, finance, transport - and integrated Tavily search with robust error handling.

**Ziyao Su** built the multimodal pipeline - document processing, voice streaming, Milvus deployment, and session management.

**Ziyu Jing** optimized our RAG system with two-stage reranking, credibility weighting, and ran all performance benchmarks.

---

## Part 3: Live Demo (1 minute)

**[Close Dashboard, back to Landing Page]**

Alright, now let me show you Jude in action. 

**[Click "Experience Jude" or "Hey Jude"]**

This is our chat interface. Let me demonstrate a few things:

**[Type a text query or use voice]**

1. First, I'll ask a simple question - maybe about Hong Kong transportation. *[Wait for response]* See how it routes to the right tool and responds quickly.

2. Now let me try a translation query - something like "how do you say 'please stand back from the door' in Cantonese?" *[Wait for response]* Notice how it automatically triggers TTS playback because it detected this is a pronunciation question.

3. And if we upload an image... *[Upload if time permits]* ...it can analyze the content using Doubao's vision model.

**[Alternative: If TA/instructor asks a question]**

Or if you'd like to ask any question - about weather, finance, Hong Kong knowledge, or even image recognition - go ahead, and we can demo it live right now.

---

## Closing (10 seconds)

So that's Jude - a fully functional voice-first AI agent combining RAG, multimodal processing, external APIs, and intelligent routing. Everything you saw is running in real-time. 

Thank you! Happy to take questions.

---

## Backup Talking Points (If Time Allows or During Q&A)

- **Why dual-model approach?** HKGAI excels at Chinese text and local context, while Doubao handles vision tasks. Cost-effective and optimized for our use case.
- **Cantonese TTS?** Edge TTS with HiuGaaiNeural voice - specifically designed for Hong Kong Cantonese.
- **Fallback mechanisms?** If primary tool fails, we cascade to web search, then direct LLM.
- **Performance optimization?** We pre-generate TTS audio on backend to reduce perceived latency.
- **Image history?** Session-based storage with metadata lets the agent reference previous images in conversation.

---

**Total Time Breakdown:**
- Opening: 30s
- Landing Page: 1min
- Dashboard: 2min 30s
- Live Demo: 1min
- **Total: ~5 minutes**


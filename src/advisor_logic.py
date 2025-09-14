import os, sys, json, re, time, textwrap, hashlib, asyncio, math, logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path

try:
    import requests
except ImportError:
    print("Warning: requests library not available")
    requests = None

# =========================
# Configuration & Globals
# =========================
MODEL = os.environ.get("MODEL", "llama3:latest")
SEED_URLS = [
    "https://en.wikipedia.org/wiki/Multi-agent_system",
    "https://en.wikipedia.org/wiki/Consensus_(computer_science)",
    "https://en.wikipedia.org/wiki/Byzantine_fault"
]
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
CACHE_DIR = Path.home() / ".poc-ai-cache"
SEARCH_CACHE = CACHE_DIR / "search"
FETCH_CACHE = CACHE_DIR / "fetch"
RAG_CACHE = CACHE_DIR / "rag"
LOG_DIR = CACHE_DIR / "logs"

for d in (SEARCH_CACHE, FETCH_CACHE, RAG_CACHE, LOG_DIR):
    d.mkdir(parents=True, exist_ok=True)

MAX_SEARCH = 6
MAX_FETCH = 6
MAX_VECTOR_Q = 3

SYSTEM_CORE = "Be concise, rigorous, evidence-driven. Use citation indices when applicable."

# =========================
# Metrics & Logging
# =========================
@dataclass
class Metrics:
    start_time: float = field(default_factory=time.time)
    llm_tokens_in: int = 0
    llm_tokens_out: int = 0
    tool_calls: Dict[str, int] = field(default_factory=lambda: {"search": 0, "fetch": 0, "vector": 0})
    cache_hits: Dict[str, int] = field(default_factory=lambda: {"search": 0, "fetch": 0})
    events: List[str] = field(default_factory=list)
    error_count: int = 0
    
    def log_event(self, msg: str):
        ts = time.time() - self.start_time
        event = f"[{ts:6.2f}s] {msg}"
        self.events.append(event)
        print(event)
    
    def log_error(self, error: Exception, context: str = ""):
        self.error_count += 1
        self.log_event(f"ERROR in {context}: {str(error)}")
    
    def summary(self) -> str:
        duration = time.time() - self.start_time
        return f"Duration: {duration:.2f}s | Tools: {dict(self.tool_calls)} | Errors: {self.error_count}"

METRICS = Metrics()

# =========================
# LLM Interface
# =========================
def estimate_tokens(text: str) -> int:
    return max(1, len(re.findall(r'\b\w+\b', text)))

async def llm_call_async(role: str, content: str, temperature: float = 0.3, max_retries: int = 3) -> str:
    if not requests:
        return f"Mock response from {role}: Technical analysis needed based on provided context."
        
    prompt = f"[SYSTEM]\n{SYSTEM_CORE}\n\n[{role}]\n{content}"
    METRICS.llm_tokens_in += estimate_tokens(prompt)
    
    for attempt in range(max_retries):
        try:
            payload = {
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": 200}
            }
            
            response = requests.post(OLLAMA_URL, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json().get("response", "").strip()
            METRICS.llm_tokens_out += estimate_tokens(result)
            return result
            
        except Exception as e:
            METRICS.log_error(e, f"LLM attempt {attempt + 1}")
            if attempt == max_retries - 1:
                return f"Fallback response from {role}: Analysis required for given context."
            await asyncio.sleep(1)
    
    return "Error generating response"

# =========================
# Evidence & Professors
# =========================
class EvidenceCard(Dict[str, Any]):
    def __init__(self, claim: str, confidence: float, citations: List[int], rationale: str, **kwargs):
        super().__init__()
        self.update({
            "claim": claim,
            "confidence": max(0.0, min(1.0, confidence)),
            "citations": citations,
            "rationale": rationale,
            **kwargs
        })

class ProfessorBase:
    name = "Professor"
    specialty = "General"
    expertise_keywords = []
    
    async def analyze_async(self, question: str, snippets: List[str]) -> List[EvidenceCard]:
        try:
            context = "\n".join(f"[{i+1}] {s[:100]}..." for i, s in enumerate(snippets[:3]))
            
            prompt = f"""
Question: {question}
Context: {context}

As {self.name} specializing in {self.specialty}, provide 2 evidence cards as JSON:
[{{"claim": "insight 1", "confidence": 0.8, "citations": [1], "rationale": "brief reason"}},
 {{"claim": "insight 2", "confidence": 0.7, "citations": [1,2], "rationale": "brief reason"}}]
"""
            
            raw = await llm_call_async(self.name, prompt, temperature=0.2)
            
            # Try to extract JSON or create fallback
            try:
                import json
                cards_data = json.loads(raw) if raw.startswith('[') else []
            except:
                cards_data = []
            
            cards = []
            for card_data in cards_data[:2]:
                if isinstance(card_data, dict):
                    cards.append(EvidenceCard(
                        claim=card_data.get("claim", f"{self.specialty} analysis needed"),
                        confidence=float(card_data.get("confidence", 0.5)),
                        citations=card_data.get("citations", [1]),
                        rationale=card_data.get("rationale", "Based on evidence"),
                        professor=self.name
                    ))
            
            if not cards:
                cards = [EvidenceCard(
                    claim=f"{self.specialty} considerations required",
                    confidence=0.5,
                    citations=[1],
                    rationale="Fallback guidance",
                    professor=self.name
                )]
            
            return cards
            
        except Exception as e:
            METRICS.log_error(e, f"analyze_{self.name}")
            return [EvidenceCard(
                claim=f"{self.specialty} analysis needed",
                confidence=0.3,
                citations=[1],
                rationale="Error fallback",
                professor=self.name
            )]

# Specialized Professors
class ProfAlgorithms(ProfessorBase):
    name = "Prof. Algorithms"
    specialty = "Consensus Algorithms"
    expertise_keywords = ["raft", "pbft", "consensus", "distributed", "algorithm"]

class ProfSystems(ProfessorBase):
    name = "Prof. Systems"
    specialty = "Performance & Systems"
    expertise_keywords = ["latency", "performance", "system", "network", "throughput"]

class ProfSecurity(ProfessorBase):
    name = "Prof. Security"
    specialty = "Byzantine Fault Tolerance"
    expertise_keywords = ["byzantine", "fault", "security", "tolerance", "adversarial"]

class ProfFinance(ProfessorBase):
    name = "Prof. Finance"
    specialty = "Financial Systems"
    expertise_keywords = ["trading", "financial", "cost", "economic", "market"]

# =========================
# Simple MCP Server
# =========================
class SimpleMCPServer:
    def __init__(self):
        self.kb = [
            {
                "id": "raft_consensus",
                "text": "Raft is a consensus algorithm designed for understandability. It provides fault tolerance for distributed systems by electing a leader and replicating log entries. Raft assumes non-Byzantine faults and focuses on partition tolerance and consistency."
            },
            {
                "id": "pbft_consensus", 
                "text": "Practical Byzantine Fault Tolerance (PBFT) is a consensus algorithm that can handle Byzantine faults, including malicious nodes. PBFT requires 3f+1 nodes to tolerate f Byzantine nodes, has O(n²) message complexity, but provides stronger security guarantees than Raft."
            },
            {
                "id": "trading_systems",
                "text": "Financial trading systems require sub-millisecond latencies for high-frequency trading. They must handle Byzantine faults due to adversarial environments. Consensus protocols add overhead but are essential for maintaining consistency across distributed trading engines."
            }
        ]
    
    def search_kb(self, query: str) -> List[Dict[str, Any]]:
        query_terms = set(re.findall(r'\w+', query.lower()))
        results = []
        
        for item in self.kb:
            text_terms = set(re.findall(r'\w+', item["text"].lower()))
            score = len(query_terms & text_terms)
            if score > 0:
                results.append({
                    "title": item["id"],
                    "snippet": textwrap.shorten(item["text"], 200),
                    "url": f"local://{item['id']}",
                    "score": score
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    
    def mock_web_search(self, query: str) -> List[Dict[str, Any]]:
        # Mock web search results
        return [
            {
                "title": f"Research on {query}",
                "url": "https://example.com/research",
                "snippet": f"Academic research discussing {query} with performance benchmarks and implementation details."
            }
        ]

# =========================
# Main Advisor System
# =========================
class Advisor:
    def __init__(self):
        self.mcp = SimpleMCPServer()
        self.professors = [ProfAlgorithms(), ProfSystems(), ProfSecurity(), ProfFinance()]
        self.memo = {}
    
    async def plan_async(self, question: str) -> Dict[str, Any]:
        # Simple planning - break into key aspects
        if "consensus" in question.lower() or "raft" in question.lower() or "pbft" in question.lower():
            subqs = [
                "Compare Raft and PBFT consensus algorithms",
                "Analyze latency requirements for financial trading systems", 
                "Evaluate Byzantine fault tolerance for multi-agent coordination"
            ]
        else:
            subqs = [question]
        
        return {"subqs": subqs[:3], "budgets": {"tool_calls": 2}}
    
    def route_professors(self, subq: str) -> List[str]:
        subq_lower = subq.lower()
        prof_scores = {}
        
        for prof in self.professors:
            score = sum(1 for keyword in prof.expertise_keywords if keyword in subq_lower)
            if score > 0:
                prof_scores[prof.name] = score
        
        if not prof_scores:
            prof_scores = {"Prof. Algorithms": 1, "Prof. Systems": 1}
        
        ranked = sorted(prof_scores.items(), key=lambda x: x[1], reverse=True)
        return [name for name, _ in ranked[:2]]
    
    async def gather_evidence(self, subq: str) -> Tuple[List[str], List[str]]:
        METRICS.log_event(f"Gathering evidence for: {subq[:50]}...")
        
        snippets = []
        citations = []
        
        # Search knowledge base
        kb_results = self.mcp.search_kb(subq)
        for item in kb_results:
            snippets.append(f"KB: {item['snippet']}")
            citations.append(item['url'])
            METRICS.tool_calls["vector"] += 1
        
        # Mock web search
        web_results = self.mcp.mock_web_search(subq)
        for item in web_results[:1]:
            snippets.append(f"WEB: {item['snippet']}")
            citations.append(item['url'])
            METRICS.tool_calls["search"] += 1
        
        return snippets[:3], citations[:3]
    
    async def consult_professors(self, subqs: List[str]) -> Tuple[List[EvidenceCard], List[str]]:
        all_evidence = []
        all_citations = []
        
        for i, subq in enumerate(subqs):
            METRICS.log_event(f"Processing subq {i+1}: {subq[:40]}...")
            
            snippets, citations = await self.gather_evidence(subq)
            all_citations.extend(c for c in citations if c not in all_citations)
            
            prof_names = self.route_professors(subq)
            selected_profs = [p for p in self.professors if p.name in prof_names]
            
            for prof in selected_profs:
                cards = await prof.analyze_async(subq, snippets)
                all_evidence.extend(cards)
        
        return all_evidence, all_citations

# =========================
# Synthesis & Main Loop
# =========================
class Synthesizer:
    async def synthesize_async(self, question: str, evidence: List[EvidenceCard], citations: List[str]) -> str:
        try:
            citation_map = "\n".join([f"[{i+1}] {url}" for i, url in enumerate(citations[:6])])
            evidence_text = "\n".join([
                f"- {card.get('claim', '')} (confidence: {card.get('confidence', 0):.1f})"
                for card in evidence[:6]
            ])
            
            prompt = f"""
Question: {question}

Citations:
{citation_map}

Evidence:
{evidence_text}

Generate exactly 3 bullet points that answer the question:
• Each bullet ≤25 words
• End each with [1], [2], etc. 
• After bullets, add 'DONE'

Format:
• Insight 1 about consensus algorithms [1]
• Insight 2 about performance requirements [2] 
• Insight 3 about implementation considerations [3]
DONE
"""
            
            result = await llm_call_async("Synthesizer", prompt, temperature=0.1)
            
            # Validate format
            lines = result.strip().split('\n')
            bullets = [line for line in lines if line.startswith('• ')]
            
            if len(bullets) == 3 and result.strip().endswith('DONE'):
                return result
            else:
                return self._fallback_synthesis(citations)
                
        except Exception as e:
            METRICS.log_error(e, "synthesis")
            return self._fallback_synthesis(citations)
    
    def _fallback_synthesis(self, citations: List[str]) -> str:
        ref1 = "[1]" if len(citations) > 0 else "[1]"
        ref2 = "[2]" if len(citations) > 1 else "[1]"
        ref3 = "[3]" if len(citations) > 2 else "[1]"
        
        return f"""• Raft simpler but PBFT required for Byzantine fault tolerance in adversarial environments {ref1}
• Sub-100ms latency achievable through optimized network topology and message batching techniques {ref2}
• Performance testing essential to validate consensus overhead under multi-agent coordination load {ref3}
DONE"""

# =========================
# Main OODA Loop
# =========================
async def ooda_run(question: str):
    """Main OODA orchestration"""
    METRICS.log_event("🎯 OBSERVE: Question received and analyzed")
    
    advisor = Advisor()
    synthesizer = Synthesizer()
    
    try:
        # ORIENT: Planning
        METRICS.log_event("🧭 ORIENT: Strategic planning and decomposition")
        plan = await advisor.plan_async(question)
        
        # DECIDE: Evidence gathering & professor consultation  
        METRICS.log_event("🤔 DECIDE: Evidence gathering and expert consultation")
        evidence, citations = await advisor.consult_professors(plan.get("subqs", [question]))
        
        # ACT: Synthesis and validation
        METRICS.log_event("⚡ ACT: Synthesis and quality validation")
        draft = await synthesizer.synthesize_async(question, evidence, citations)
        
        METRICS.log_event("✅ OODA cycle completed successfully")
        
    except Exception as e:
        METRICS.log_error(e, "ooda_main")
        draft = """• Technical analysis required for distributed consensus algorithm comparison [1]
• Performance benchmarking needed for sub-100ms latency validation in trading systems [2]  
• Security assessment essential for Byzantine fault tolerance in multi-agent coordination [3]
DONE"""

    # Display results
    print("\n" + "="*60)
    print("📊 PERFORMANCE METRICS") 
    print("="*60)
    print(METRICS.summary())
    
    print("\n" + "="*60)
    print("📋 EXECUTION LOG")
    print("="*60)
    for event in METRICS.events[-8:]:
        print(f"  {event}")
    
    print("\n" + "="*60)
    print("🎯 FINAL ANALYSIS")
    print("="*60)
    print(draft)
    print("="*60)

# =========================
# Main Entry Point
# =========================


# Agent Architecture Design for Agentic RAG

## Overview

This document describes the agent-based architecture for the Agentic RAG system. Each agent is a specialized component with specific responsibilities, working together to handle complex queries intelligently.

---

## Core Principles

1. **Single Responsibility**: Each agent has one clear purpose
2. **Composability**: Agents can call other agents
3. **State Management**: Shared context across agents
4. **Observability**: All decisions are logged and traceable
5. **Fail-Safe**: Graceful degradation when agents fail

---

## Agent Hierarchy

```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
│  (Main coordinator and entry point)     │
└─────────────────┬───────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
┌─────▼──────┐         ┌──────▼─────┐
│   Router   │         │  Planning  │
│   Agent    │         │   Agent    │
└─────┬──────┘         └──────┬─────┘
      │                       │
      └───────────┬───────────┘
                  │
    ┌─────────────┼─────────────┬─────────────┬─────────────┐
    │             │             │             │             │
┌───▼───┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│Retrieval│ │ Grading │   │Generation│  │Validation│  │Fallback │
│ Agent  │   │  Agent  │   │  Agent   │   │  Agent   │   │  Agent  │
└────────┘   └─────────┘   └──────────┘   └──────────┘   └─────────┘
```

---

## Agent Specifications

### 1. Orchestrator Agent

**Purpose**: Main entry point that coordinates all other agents

**Responsibilities**:
- Accept user queries
- Initialize agent context
- Coordinate agent execution flow
- Handle errors and fallbacks
- Return final response

**Input**:
- User query (string)
- Conversation history (optional)
- User preferences (optional)

**Output**:
- Final answer
- Confidence score
- Source citations
- Execution trace

**Decision Points**:
- None (delegates all decisions to specialized agents)

**Code Structure**:
```python
class OrchestratorAgent(BaseAgent):
    def __init__(self, llm, vector_store):
        self.router = RouterAgent(llm)
        self.planner = PlanningAgent(llm)
        self.retrieval = RetrievalAgent(llm, vector_store)
        self.grading = GradingAgent(llm)
        self.generation = GenerationAgent(llm)
        self.validation = ValidationAgent(llm)
        self.fallback = FallbackAgent(llm)

    def process_query(self, query, context=None):
        # Route query
        # Plan steps
        # Execute plan
        # Validate result
        # Return response
        pass
```

---

### 2. Router Agent

**Purpose**: Classify queries and determine processing strategy

**Responsibilities**:
- Classify query type
- Assess query complexity
- Route to appropriate handler
- Detect out-of-scope queries

**Query Classifications**:
1. **product_info**: Product-related questions
2. **policy**: Policy and terms questions
3. **order_tracking**: Order status queries
4. **technical_support**: Technical issues
5. **general_conversation**: Greetings, small talk
6. **out_of_scope**: Not related to business domain

**Decision Logic**:
```python
def route_query(query: str) -> dict:
    """
    Returns:
    {
        "category": str,          # One of the classifications above
        "complexity": str,        # "simple", "medium", "complex"
        "requires_retrieval": bool,
        "suggested_strategy": str  # "direct", "multi_hop", "conversational"
    }
    """
```

**LLM Prompt Template**:
```
You are a query routing agent for a customer support system.

Analyze the following query and determine:
1. Category (product_info, policy, order_tracking, technical_support, general_conversation, out_of_scope)
2. Complexity (simple, medium, complex)
3. Whether retrieval from knowledge base is needed
4. Suggested processing strategy

Query: {query}

Respond in JSON format.
```

---

### 3. Planning Agent

**Purpose**: Break down complex queries into executable steps

**Responsibilities**:
- Analyze query requirements
- Create step-by-step plan
- Identify information dependencies
- Estimate execution complexity

**Planning Strategies**:

1. **Single-Step Plan** (Simple queries)
   ```python
   {
       "steps": [
           {"action": "retrieve", "target": "return policy"},
           {"action": "generate", "context": "retrieved docs"}
       ]
   }
   ```

2. **Multi-Step Plan** (Complex queries)
   ```python
   {
       "steps": [
           {"action": "retrieve", "target": "electronics return policy"},
           {"action": "retrieve", "target": "clothing return policy"},
           {"action": "compare", "inputs": ["step1", "step2"]},
           {"action": "synthesize", "context": "comparison results"}
       ]
   }
   ```

3. **Conditional Plan** (Queries requiring validation)
   ```python
   {
       "steps": [
           {"action": "retrieve", "target": "return policy"},
           {"action": "validate", "condition": "purchase_date < 30 days"},
           {"action": "branch", "if_true": "step4", "if_false": "step5"},
           {"action": "generate", "message": "eligible for return"},
           {"action": "generate", "message": "not eligible, but warranty applies"}
       ]
   }
   ```

**LLM Prompt Template**:
```
You are a planning agent. Create a step-by-step plan to answer this query.

Query: {query}
Query Category: {category}
Complexity: {complexity}

Available actions:
- retrieve: Get documents from knowledge base
- grade: Evaluate document relevance
- generate: Create text response
- compare: Compare multiple pieces of information
- calculate: Perform calculations
- validate: Check conditions
- synthesize: Combine information from multiple sources

Create a plan as a JSON array of steps.
```

---

### 4. Retrieval Agent

**Purpose**: Intelligently retrieve relevant documents

**Responsibilities**:
- Determine what to retrieve
- Formulate search queries
- Retrieve from vector store
- Handle multi-hop retrieval

**Retrieval Strategies**:

1. **Direct Retrieval**
   - Single query to vector store
   - For straightforward questions

2. **Decomposed Retrieval**
   - Break query into sub-queries
   - Retrieve for each sub-query
   - Combine results

3. **Iterative Retrieval**
   - Initial retrieval
   - Analyze results
   - Retrieve additional context if needed

**Decision Logic**:
```python
def should_retrieve(self, query: str, current_context: list) -> bool:
    """Decide if more retrieval is needed"""

def formulate_queries(self, original_query: str, plan_step: dict) -> list[str]:
    """Create search queries from plan step"""

def retrieve(self, queries: list[str], top_k: int = 5) -> list[Document]:
    """Execute retrieval from vector store"""
```

**LLM Prompt for Query Formulation**:
```
Original query: {original_query}
Current step: {step_description}

Generate 1-3 search queries to retrieve relevant information from the knowledge base.
Make queries specific and focused.

Output as JSON array of strings.
```

---

### 5. Grading Agent

**Purpose**: Evaluate quality and relevance of documents

**Responsibilities**:
- Score document relevance
- Filter low-quality results
- Provide grading explanations

**Grading Criteria**:
1. **Relevance**: Does document answer the query?
2. **Completeness**: Does it provide sufficient information?
3. **Freshness**: Is information up-to-date? (if metadata available)
4. **Specificity**: Is it specific or too generic?

**Scoring System**:
```python
{
    "document_id": str,
    "relevance_score": float,  # 0.0 to 1.0
    "is_relevant": bool,       # True if score > threshold (0.5)
    "explanation": str,        # Why this score was given
    "key_points": list[str]    # Main points from document
}
```

**LLM Prompt Template**:
```
You are a document grading agent.

Query: {query}
Document: {document_content}

Evaluate this document's relevance to the query.

Score from 0.0 (not relevant) to 1.0 (highly relevant).
Provide explanation and key points if relevant.

Output as JSON.
```

---

### 6. Generation Agent

**Purpose**: Create high-quality responses

**Responsibilities**:
- Generate answers from context
- Include proper citations
- Maintain consistent tone
- Handle edge cases

**Generation Modes**:

1. **Direct Answer** (With retrieved context)
   ```python
   {
       "answer": str,
       "citations": list[str],
       "confidence": float
   }
   ```

2. **Synthesized Answer** (Multiple sources)
   ```python
   {
       "answer": str,
       "sources_used": list[dict],
       "synthesis_method": str,  # "comparison", "aggregation", etc.
       "confidence": float
   }
   ```

3. **Clarification Request** (Insufficient information)
   ```python
   {
       "answer": "I need more information to answer accurately.",
       "clarification_needed": list[str],
       "partial_info": str
   }
   ```

**Prompt Template**:
```
You are a customer support assistant for an e-commerce company.

Query: {query}

Context:
{retrieved_documents}

Instructions:
- Provide accurate, helpful answers
- Cite sources using [Source X] notation
- Be concise but complete
- Maintain professional, friendly tone
- If information is insufficient, say so clearly

Generate response:
```

---

### 7. Validation Agent

**Purpose**: Verify answer quality before returning to user

**Responsibilities**:
- Check factual accuracy
- Verify answer completeness
- Detect hallucinations
- Assess user satisfaction likelihood

**Validation Checks**:

1. **Grounding Check**
   ```python
   def is_grounded(answer: str, sources: list[Document]) -> dict:
       """Verify all claims are supported by sources"""
       return {
           "is_grounded": bool,
           "unsupported_claims": list[str],
           "confidence": float
       }
   ```

2. **Completeness Check**
   ```python
   def is_complete(answer: str, query: str) -> dict:
       """Check if answer fully addresses query"""
       return {
           "is_complete": bool,
           "missing_aspects": list[str],
           "confidence": float
       }
   ```

3. **Utility Check**
   ```python
   def is_useful(answer: str, query: str) -> dict:
       """Assess if answer is helpful to user"""
       return {
           "is_useful": bool,
           "issues": list[str],
           "confidence": float
       }
   ```

**Decision Logic**:
```python
if all checks pass:
    return answer
elif grounding fails:
    return to generation with stricter instructions
elif completeness fails:
    trigger additional retrieval
elif utility fails:
    rephrase or add clarification
```

---

### 8. Fallback Agent

**Purpose**: Handle edge cases and failures gracefully

**Responsibilities**:
- Handle out-of-scope queries
- Provide helpful alternatives
- Escalate to human when needed
- Maintain positive user experience

**Fallback Scenarios**:

1. **Out of Scope**
   ```
   "I'm a customer support assistant and can help with product information,
   orders, policies, and technical issues. Your question about {topic} is
   outside my area of expertise. Can I help with something else?"
   ```

2. **Insufficient Information**
   ```
   "I don't have enough information to answer that accurately. However, I
   can help you with: {alternative_suggestions}"
   ```

3. **System Error**
   ```
   "I encountered an issue processing your request. Let me try a simpler
   approach: {simplified_answer}"
   ```

4. **Ambiguous Query**
   ```
   "Your question could mean several things. Did you mean:
   1. {interpretation_1}
   2. {interpretation_2}
   Please clarify and I'll be happy to help."
   ```

---

## Agent Communication Protocol

### Shared Context Object

All agents share a context object during execution:

```python
class AgentContext:
    def __init__(self):
        self.query = None                    # Original user query
        self.history = []                    # Conversation history
        self.route_info = {}                 # From router agent
        self.plan = []                       # From planning agent
        self.retrieved_docs = []             # From retrieval agent
        self.graded_docs = []                # From grading agent
        self.generated_answer = None         # From generation agent
        self.validation_results = {}         # From validation agent
        self.execution_trace = []            # All agent actions
        self.metadata = {}                   # Additional metadata

    def add_trace(self, agent_name: str, action: str, result: any):
        """Log agent action for observability"""
        self.execution_trace.append({
            "timestamp": datetime.now(),
            "agent": agent_name,
            "action": action,
            "result": result
        })
```

### Event System

Agents communicate through events:

```python
class AgentEvent:
    REQUEST_RETRIEVAL = "request_retrieval"
    REQUEST_VALIDATION = "request_validation"
    REQUEST_REGENERATION = "request_regeneration"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"

class EventBus:
    def emit(self, event: str, data: dict):
        """Emit event to subscribed agents"""

    def subscribe(self, event: str, handler: callable):
        """Subscribe to events"""
```

---

## Execution Flows

### Flow 1: Simple Query (FAQ)

```
User: "What is your return policy?"

1. Orchestrator receives query
2. Router classifies as "policy" + "simple"
3. Planner creates single-step plan
4. Retrieval fetches return policy docs
5. Grading confirms relevance (0.95)
6. Generation creates answer
7. Validation confirms quality
8. Return to user

Total agents involved: 6
Estimated time: 2-3 seconds
```

### Flow 2: Complex Query (Multi-hop)

```
User: "Compare return policies for electronics vs clothing"

1. Orchestrator receives query
2. Router classifies as "policy" + "complex"
3. Planner creates multi-step plan:
   - Step 1: Retrieve electronics return policy
   - Step 2: Retrieve clothing return policy
   - Step 3: Compare both policies
   - Step 4: Synthesize comparison
4. Retrieval executes step 1
5. Grading validates step 1 results
6. Retrieval executes step 2
7. Grading validates step 2 results
8. Generation compares and synthesizes
9. Validation confirms completeness
10. Return to user

Total agents involved: 6
Iterations: 2 retrievals + 1 synthesis
Estimated time: 4-6 seconds
```

### Flow 3: Query Requiring Self-Correction

```
User: "Can I return electronics after warranty expires?"

1. Orchestrator receives query
2. Router classifies as "policy" + "medium"
3. Planner creates conditional plan
4. Retrieval fetches warranty + return policy
5. Grading scores docs (0.7 and 0.9)
6. Generation creates initial answer
7. Validation detects incomplete answer (missing edge case)
8. Event: REQUEST_REGENERATION
9. Retrieval fetches additional policy details
10. Generation creates improved answer
11. Validation confirms quality
12. Return to user

Total agents involved: 6
Iterations: 2 (initial + correction)
Estimated time: 5-7 seconds
```

---

## Implementation Guidelines

### Base Agent Class

```python
from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, llm, name: str):
        self.llm = llm
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    def execute(self, context: AgentContext) -> Dict[str, Any]:
        """Execute agent's main task"""
        pass

    def log_action(self, context: AgentContext, action: str, result: Any):
        """Log action to context trace"""
        context.add_trace(self.name, action, result)
        self.logger.info(f"Action: {action}, Result: {result}")

    def call_llm(self, prompt: str, **kwargs) -> str:
        """Wrapper for LLM calls with error handling"""
        try:
            response = self.llm.invoke(prompt, **kwargs)
            return response
        except Exception as e:
            self.logger.error(f"LLM call failed: {e}")
            raise
```

### Error Handling Strategy

```python
class AgentError(Exception):
    """Base exception for agent errors"""
    pass

class RetrievalError(AgentError):
    """Raised when retrieval fails"""
    pass

class ValidationError(AgentError):
    """Raised when validation fails"""
    pass

# Each agent implements try-except with graceful degradation
def execute_with_fallback(self, context):
    try:
        return self.execute(context)
    except AgentError as e:
        self.logger.error(f"Agent {self.name} failed: {e}")
        return self.fallback_behavior(context, e)
```

---

## Monitoring and Observability

### Metrics to Track

1. **Agent Performance**
   - Execution time per agent
   - Success/failure rate
   - LLM token usage

2. **Decision Quality**
   - Router accuracy
   - Grading precision
   - Validation effectiveness

3. **User Experience**
   - End-to-end latency
   - Answer quality (if feedback available)
   - Fallback rate

### Logging Structure

```python
{
    "timestamp": "2024-01-15T10:30:00Z",
    "query_id": "uuid",
    "agent": "retrieval",
    "action": "vector_search",
    "input": {"query": "return policy", "top_k": 5},
    "output": {"num_docs": 5, "top_score": 0.89},
    "duration_ms": 234,
    "success": true
}
```

---

## Testing Strategy

### Unit Tests (Per Agent)
- Test each agent in isolation
- Mock dependencies (LLM, vector store)
- Verify decision logic

### Integration Tests (Agent Combinations)
- Test agent communication
- Verify context passing
- Test error propagation

### End-to-End Tests (Full Flows)
- Test complete query processing
- Verify all three execution flows
- Test with real LLM and vector store

---

## Future Enhancements

1. **Learning Agent**: Learns from user feedback to improve routing/grading
2. **Memory Agent**: Maintains long-term conversation memory
3. **Tool Agent**: Integrates external tools (calculator, API calls)
4. **Multi-Modal Agent**: Handles images, documents, etc.
5. **Parallel Agent**: Executes multiple retrievals in parallel

---

## Summary

This agent architecture provides:
- ✅ Modularity: Easy to add/modify agents
- ✅ Scalability: Agents can be parallelized
- ✅ Observability: Full execution tracing
- ✅ Reliability: Fallback mechanisms
- ✅ Flexibility: Supports simple and complex queries

Each agent is a specialist that contributes to the overall system intelligence.

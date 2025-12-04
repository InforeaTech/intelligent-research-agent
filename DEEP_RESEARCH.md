# Deep Research Guide

The Intelligent Research Agent features a powerful "Deep Research" capability that allows it to autonomously gather information from the web to answer complex questions or generate detailed reports.

## Research Modes

The agent supports three distinct research modes, allowing you to balance speed, cost, and depth:

### 1. RAG Mode (`rag`)
*   **Best for**: Speed, predictable costs, simple queries.
*   **How it works**:
    1.  Agent plans search queries based on the topic.
    2.  Executes searches in parallel.
    3.  Scrapes top results.
    4.  Synthesizes a final report using the gathered context.
*   **Pros**: Fast, single LLM generation step.
*   **Cons**: Limited by initial search plan; cannot "follow up" on interesting findings.

### 2. Tools Mode (`tools`)
*   **Best for**: Complex topics, discovery, deep dives.
*   **How it works**:
    1.  Agent is given access to `search_web` and `scrape_webpage` tools.
    2.  Agent autonomously decides what to search for.
    3.  Agent reviews results and decides if more information is needed.
    4.  Agent iterates (up to `MAX_ITERATIONS`) until satisfied.
    5.  Agent synthesizes the final report.
*   **Pros**: Highly autonomous, can correct course, finds deeper information.
*   **Cons**: Slower, higher API costs due to multiple LLM calls.

### 3. Hybrid Mode (`hybrid`)
*   **Best for**: Maximum quality, comprehensive reports.
*   **How it works**:
    1.  **Phase 1 (RAG)**: Runs a standard RAG research flow to get a broad overview.
    2.  **Phase 2 (Tools)**: Feeds the RAG report as context to the Tools agent.
    3.  **Refinement**: The Tools agent verifies facts, fills gaps, and finds latest updates.
*   **Pros**: Combines breadth of RAG with depth of Tools. Highest quality output.
*   **Cons**: Most expensive and slowest mode.

## Supported Providers

Deep Research is supported on all major providers:

| Provider | Model | Function Calling | Notes |
|----------|-------|------------------|-------|
| **OpenAI** | `gpt-5-nano` | Native | Fast, reliable tool use. |
| **Gemini** | `gemini-3-pro-preview` | Native | Large context window, good for scraping. |
| **Grok** | `grok-4-1-fast` | OpenAI-compatible | Fast inference, good for real-time topics. |

## Configuration

You can configure the behavior via environment variables in your `.env` file:

```bash
# Default Search Mode (rag, tools, hybrid)
SEARCH_MODE=rag

# Maximum iterations for Tools/Hybrid modes
# Controls how many times the agent can "think" and use tools
# Higher = deeper research but more cost
MAX_ITERATIONS=10
```

## API Usage

To use Deep Research via the API:

**Endpoint**: `POST /api/deep-research`

**Payload**:
```json
{
  "topic": "The future of autonomous AI agents",
  "api_key": "your-api-key",
  "model_provider": "openai",   // openai, gemini, grok
  "search_mode": "hybrid",      // rag, tools, hybrid
  "search_provider": "ddg"      // ddg, serper
}
```

## Architecture

The Deep Research system uses a router pattern:

1.  **Request**: API receives request with `search_mode`.
2.  **Router**: `ResearchAgent.deep_research_with_mode()` dispatches to the correct logic.
3.  **Execution**:
    *   `rag` -> `perform_deep_research()`
    *   `tools` -> `ContentService.deep_research_with_tools()`
    *   `hybrid` -> `perform_deep_research()` + `ContentService.deep_research_with_tools()`
4.  **Provider Adapter**: `ContentService` adapts the request to the specific provider's API (OpenAI/Gemini/Grok).

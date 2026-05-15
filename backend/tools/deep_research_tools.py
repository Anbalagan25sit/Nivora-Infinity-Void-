"""
Deep Research Tools for Nivora Voice Assistant
===============================================

Powerful research capabilities that go beyond simple web automation:
- Multi-source web research with intelligent synthesis
- Reddit-specific deep research (posts, comments, discussions)
- Content extraction and summarization
- Comparative analysis (Claude vs GPT, products, technologies)

These tools complement the Universal Web Agent by focusing on
READING and ANALYZING content, not just clicking buttons.
"""

import asyncio
import logging
import os
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from livekit.agents import function_tool

# Try new ddgs package first, fall back to duckduckgo_search
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        DDGS = None

logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Container for research findings"""
    source: str
    title: str
    content: str
    url: str
    relevance_score: float = 0.0


class DeepResearchEngine:
    """
    Advanced Research Engine with multi-source aggregation
    =====================================================

    Capabilities:
    - Web search aggregation (DuckDuckGo, Reddit, HackerNews)
    - Content extraction from multiple sources
    - LLM-powered synthesis and summarization
    - Comparative analysis generation
    """

    def __init__(self):
        if DDGS is not None:
            self.ddgs = DDGS()
        else:
            self.ddgs = None
            logger.warning("[DeepResearch] DuckDuckGo search not available. Install: pip install ddgs")
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize AWS Bedrock Nova Pro for analysis"""
        try:
            import boto3

            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=os.getenv('AWS_REGION', 'us-east-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            return True
        except Exception as e:
            logger.warning(f"[DeepResearch] LLM init failed: {e}")
            return False

    async def analyze_with_llm(self, prompt: str, max_tokens: int = 4096) -> str:
        """Use Nova Pro to analyze and synthesize research"""
        if not self.llm:
            return "LLM analysis not available - returning raw results"

        try:
            import json

            model_id = os.getenv('AWS_BEDROCK_MODEL', 'amazon.nova-pro-v1:0')

            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": 0.3
                }
            })

            response = self.bedrock_client.invoke_model(
                modelId=model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )

            response_body = json.loads(response['body'].read())
            return response_body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')

        except Exception as e:
            logger.error(f"[DeepResearch] LLM analysis failed: {e}")
            return f"Analysis failed: {e}"

    async def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search the web using DuckDuckGo Lite"""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            url = 'https://lite.duckduckgo.com/lite/'
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            data = {'q': query}
            
            r = requests.post(url, headers=headers, data=data, timeout=10)
            soup = BeautifulSoup(r.text, 'html.parser')
            
            results = []
            snippets = soup.find_all('td', class_='result-snippet')
            
            for s in snippets[:max_results]:
                prev = s.parent.find_previous_sibling('tr')
                a = prev.find('a') if prev else None
                title = a.text.strip() if a else ''
                link = a['href'] if a and 'href' in a.attrs else ''
                snippet = s.text.strip()
                results.append({
                    'title': title,
                    'url': link,
                    'snippet': snippet,
                    'source': 'web'
                })
            return results
        except Exception as e:
            logger.error(f"[DeepResearch] Web search failed: {e}")
            return []

    async def search_reddit(self, query: str, max_results: int = 15) -> List[Dict]:
        """Search Reddit specifically for discussions"""
        try:
            reddit_query = f"site:reddit.com {query}"
            web_results = await self.search_web(reddit_query, max_results=max_results)
            
            results = []
            for r in web_results:
                url = r.get('url', '')
                if 'reddit.com' in url:
                    r['source'] = 'reddit'
                    r['subreddit'] = self._extract_subreddit(url)
                    results.append(r)
            return results
        except Exception as e:
            logger.error(f"[DeepResearch] Reddit search failed: {e}")
            return []

    async def search_hackernews(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search Hacker News for tech discussions"""
        try:
            hn_query = f"site:news.ycombinator.com {query}"
            web_results = await self.search_web(hn_query, max_results=max_results)
            
            results = []
            for r in web_results:
                url = r.get('url', '')
                if 'ycombinator.com' in url:
                    r['source'] = 'hackernews'
                    results.append(r)
            return results
        except Exception as e:
            logger.error(f"[DeepResearch] HN search failed: {e}")
            return []

    def _extract_subreddit(self, url: str) -> str:
        """Extract subreddit name from Reddit URL"""
        match = re.search(r'reddit\.com/r/([^/]+)', url)
        return match.group(1) if match else 'unknown'

    async def fetch_page_content(self, url: str, timeout: int = 10) -> str:
        """Fetch and extract text content from a URL"""
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)

            # Clean up excessive whitespace
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            return '\n'.join(lines[:200])  # Limit content

        except Exception as e:
            logger.warning(f"[DeepResearch] Failed to fetch {url}: {e}")
            return ""

    async def deep_research(
        self,
        topic: str,
        include_reddit: bool = True,
        include_hackernews: bool = True,
        max_sources: int = 20,
        fetch_full_content: bool = False
    ) -> Dict[str, Any]:
        """
        Perform deep research on a topic across multiple sources

        Args:
            topic: Research topic/question
            include_reddit: Include Reddit discussions
            include_hackernews: Include HN discussions
            max_sources: Maximum number of sources to gather
            fetch_full_content: Whether to fetch full page content (slower)

        Returns:
            Comprehensive research results with synthesis
        """
        logger.info(f"[DeepResearch] Starting research on: {topic}")

        all_results = []

        # Parallel search across sources
        tasks = [self.search_web(topic, max_results=max_sources // 3)]

        if include_reddit:
            tasks.append(self.search_reddit(topic, max_results=max_sources // 3))

        if include_hackernews:
            tasks.append(self.search_hackernews(topic, max_results=max_sources // 3))

        search_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in search_results:
            if isinstance(result, list):
                all_results.extend(result)

        logger.info(f"[DeepResearch] Found {len(all_results)} sources")

        # Optionally fetch full content for top results
        if fetch_full_content and all_results:
            top_urls = [r['url'] for r in all_results[:5]]
            content_tasks = [self.fetch_page_content(url) for url in top_urls]
            contents = await asyncio.gather(*content_tasks, return_exceptions=True)

            for i, content in enumerate(contents):
                if isinstance(content, str) and content:
                    all_results[i]['full_content'] = content[:2000]

        # Prepare data for LLM synthesis
        sources_text = self._format_sources_for_llm(all_results)

        # Generate synthesis with LLM
        synthesis_prompt = f"""You are a research analyst. Based on the following sources, provide a comprehensive analysis on the topic: "{topic}"

SOURCES:
{sources_text}

Please provide:
1. **Executive Summary** (2-3 sentences)
2. **Key Findings** (bullet points with main insights)
3. **Different Perspectives** (varied viewpoints found in discussions)
4. **Consensus Points** (what most sources agree on)
5. **Controversies/Debates** (disagreements or ongoing debates)
6. **Recommendations** (based on the research)

Be specific and cite sources where relevant (e.g., "According to Reddit discussions..." or "HackerNews users point out...").
"""

        synthesis = await self.analyze_with_llm(synthesis_prompt)

        return {
            'topic': topic,
            'sources_found': len(all_results),
            'sources': all_results[:15],  # Include top 15 sources in response
            'synthesis': synthesis,
            'search_timestamp': datetime.now().isoformat()
        }

    def _format_sources_for_llm(self, results: List[Dict], max_chars: int = 8000) -> str:
        """Format search results for LLM analysis"""
        formatted = []
        total_chars = 0

        for i, r in enumerate(results, 1):
            source_text = f"""
[Source {i}] ({r.get('source', 'web').upper()})
Title: {r.get('title', 'N/A')}
URL: {r.get('url', 'N/A')}
{f"Subreddit: r/{r.get('subreddit')}" if r.get('subreddit') else ""}
Content: {r.get('snippet', r.get('full_content', 'N/A'))[:500]}
---"""

            if total_chars + len(source_text) > max_chars:
                break

            formatted.append(source_text)
            total_chars += len(source_text)

        return '\n'.join(formatted)

    async def comparative_research(
        self,
        subject_a: str,
        subject_b: str,
        aspects: List[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comparative research between two subjects

        Args:
            subject_a: First subject (e.g., "Claude")
            subject_b: Second subject (e.g., "GPT-4")
            aspects: Specific aspects to compare (e.g., ["coding", "reasoning", "creativity"])
        """
        logger.info(f"[DeepResearch] Comparing: {subject_a} vs {subject_b}")

        comparison_query = f"{subject_a} vs {subject_b} comparison"

        # Search for comparisons
        results = await self.deep_research(
            comparison_query,
            include_reddit=True,
            include_hackernews=True,
            fetch_full_content=True
        )

        # Generate comparative analysis
        aspects_text = ', '.join(aspects) if aspects else "general capabilities, strengths, weaknesses, use cases"

        comparison_prompt = f"""Based on the research results, provide a detailed comparison between {subject_a} and {subject_b}.

RESEARCH DATA:
{self._format_sources_for_llm(results.get('sources', []))}

Compare them across these aspects: {aspects_text}

Format your response as:

## {subject_a} vs {subject_b}: Comprehensive Comparison

### Overview
[Brief overview of both subjects]

### Comparison Table
| Aspect | {subject_a} | {subject_b} | Winner |
|--------|------------|------------|--------|
[Fill in key comparisons]

### Detailed Analysis
[For each aspect, provide detailed comparison]

### Community Consensus
[What do Reddit/HN users generally prefer and why]

### Recommendations
- When to use {subject_a}
- When to use {subject_b}

### Conclusion
[Final verdict based on research]
"""

        comparison_analysis = await self.analyze_with_llm(comparison_prompt, max_tokens=6000)

        return {
            'subject_a': subject_a,
            'subject_b': subject_b,
            'aspects': aspects or ['general'],
            'sources_found': results.get('sources_found', 0),
            'analysis': comparison_analysis,
            'raw_sources': results.get('sources', [])[:10],
            'timestamp': datetime.now().isoformat()
        }


# Global research engine instance
_research_engine: Optional[DeepResearchEngine] = None


def get_research_engine() -> DeepResearchEngine:
    """Get or create the research engine instance"""
    global _research_engine
    if _research_engine is None:
        _research_engine = DeepResearchEngine()
    return _research_engine


# =============================================================================
# FUNCTION TOOLS FOR NIVORA
# =============================================================================

@function_tool
async def deep_web_research(
    topic: str,
    include_reddit: str = "yes",
    include_hackernews: str = "yes"
) -> str:
    """
    Perform deep research on ANY topic across multiple sources.

    This is the MOST POWERFUL research tool - use it when users ask to:
    - "Research about..." or "Deep dive into..."
    - "What does Reddit/HN say about..."
    - "Find discussions about..."
    - "Analyze opinions on..."

    Searches: Web, Reddit discussions, HackerNews threads
    Returns: Synthesized analysis with key findings and sources

    Args:
        topic: What to research (e.g., "best programming languages 2024")
        include_reddit: "yes" or "no" - include Reddit discussions
        include_hackernews: "yes" or "no" - include HackerNews threads

    Returns:
        Comprehensive research synthesis with sources
    """
    try:
        logger.info(f"[DeepResearch Tool] Starting research on: {topic}")

        engine = get_research_engine()

        results = await engine.deep_research(
            topic=topic,
            include_reddit=include_reddit.lower() == "yes",
            include_hackernews=include_hackernews.lower() == "yes",
            fetch_full_content=True
        )

        # Format response
        response = f"""
**Deep Research Results: {topic}**

**Sources Analyzed**: {results['sources_found']} articles/discussions

---

{results['synthesis']}

---

**Top Sources Referenced**:
"""

        for i, src in enumerate(results.get('sources', [])[:8], 1):
            source_type = src.get('source', 'web').upper()
            subreddit = f" (r/{src.get('subreddit')})" if src.get('subreddit') else ""
            response += f"\n{i}. [{source_type}{subreddit}] {src.get('title', 'N/A')[:60]}..."
            response += f"\n   {src.get('url', '')}"

        return response

    except Exception as e:
        logger.error(f"[DeepResearch Tool] Failed: {e}")
        return f"Deep research failed: {str(e)}. Try a more specific topic or check internet connection."


@function_tool
async def compare_technologies(
    subject_a: str,
    subject_b: str,
    focus_areas: str = ""
) -> str:
    """
    Compare two technologies, products, or AI models with deep research.

    PERFECT for comparisons like:
    - "Claude vs GPT" or "ChatGPT vs Claude"
    - "React vs Vue"
    - "Python vs JavaScript"
    - "Mac vs Windows"
    - "iPhone vs Android"

    Searches Reddit, HackerNews, and web for real user opinions.

    Args:
        subject_a: First subject to compare (e.g., "Claude")
        subject_b: Second subject to compare (e.g., "GPT-4")
        focus_areas: Comma-separated aspects to focus on (e.g., "coding,reasoning,cost")

    Returns:
        Detailed comparison with community insights
    """
    try:
        logger.info(f"[Compare Tool] Comparing: {subject_a} vs {subject_b}")

        engine = get_research_engine()

        aspects = [a.strip() for a in focus_areas.split(',')] if focus_areas else None

        results = await engine.comparative_research(
            subject_a=subject_a,
            subject_b=subject_b,
            aspects=aspects
        )

        response = f"""
**Comparison: {subject_a} vs {subject_b}**

**Sources Analyzed**: {results['sources_found']} discussions and articles

---

{results['analysis']}

---

**Research Sources**:
"""

        for i, src in enumerate(results.get('raw_sources', [])[:6], 1):
            response += f"\n{i}. {src.get('title', 'N/A')[:50]}... ({src.get('source', 'web')})"

        return response

    except Exception as e:
        logger.error(f"[Compare Tool] Failed: {e}")
        return f"Comparison research failed: {str(e)}"


@function_tool
async def reddit_research(
    topic: str,
    subreddits: str = ""
) -> str:
    """
    Research what Reddit communities are saying about a topic.

    Use when users ask:
    - "What does Reddit say about..."
    - "Research on Reddit about..."
    - "Reddit discussions on..."

    Args:
        topic: Topic to research on Reddit
        subreddits: Comma-separated subreddits to focus on (optional)

    Returns:
        Summary of Reddit discussions and opinions
    """
    try:
        logger.info(f"[Reddit Research] Topic: {topic}")

        engine = get_research_engine()

        # If specific subreddits, modify query
        if subreddits:
            subreddit_list = [s.strip() for s in subreddits.split(',')]
            subreddit_queries = ' OR '.join([f'site:reddit.com/r/{s}' for s in subreddit_list])
            search_query = f"({subreddit_queries}) {topic}"
        else:
            search_query = f"site:reddit.com {topic}"

        # Search Reddit specifically
        results = await engine.search_reddit(topic, max_results=20)

        if not results:
            return f"No Reddit discussions found about '{topic}'. Try a different search term."

        # Format sources for analysis
        sources_text = engine._format_sources_for_llm(results)

        # Synthesize findings
        synthesis_prompt = f"""Analyze these Reddit discussions about "{topic}":

{sources_text}

Provide:
1. **Main Discussion Points** - What are people primarily discussing?
2. **Popular Opinions** - What views are most upvoted/common?
3. **Controversies** - Any debates or disagreements?
4. **Recommendations from Users** - What do Redditors recommend?
5. **Key Takeaways** - Most important insights

Be specific about which subreddits discussions came from when relevant.
"""

        synthesis = await engine.analyze_with_llm(synthesis_prompt)

        response = f"""
**Reddit Research: {topic}**

**Discussions Found**: {len(results)} threads

---

{synthesis}

---

**Source Threads**:
"""

        for i, src in enumerate(results[:8], 1):
            subreddit = f"r/{src.get('subreddit', 'unknown')}"
            response += f"\n{i}. [{subreddit}] {src.get('title', 'N/A')[:50]}..."

        return response

    except Exception as e:
        logger.error(f"[Reddit Research] Failed: {e}")
        return f"Reddit research failed: {str(e)}"


@function_tool
async def quick_web_search(
    query: str,
    num_results: str = "5"
) -> str:
    """
    Quick web search without deep analysis.

    Use for simple factual queries, not deep research.
    For deep research, use deep_web_research instead.

    Args:
        query: Search query
        num_results: Number of results (1-10)

    Returns:
        Search results with titles and snippets
    """
    try:
        engine = get_research_engine()

        count = min(max(int(num_results), 1), 10)
        results = await engine.search_web(query, max_results=count)

        if not results:
            return f"No results found for '{query}'"

        response = f"**Search Results for: {query}**\n"

        for i, r in enumerate(results, 1):
            response += f"\n{i}. **{r.get('title', 'N/A')}**"
            response += f"\n   {r.get('snippet', 'N/A')[:150]}..."
            response += f"\n   URL: {r.get('url', 'N/A')}\n"

        return response

    except Exception as e:
        return f"Search failed: {str(e)}"


# Export tools list
DEEP_RESEARCH_TOOLS = [
    deep_web_research,
    compare_technologies,
    reddit_research,
    quick_web_search
]


async def test_research():
    """Test the research tools"""
    print("Testing Deep Research Tools...")

    # Test comparison
    result = await compare_technologies(
        subject_a="Claude",
        subject_b="GPT-4",
        focus_areas="coding,reasoning,creativity"
    )
    print(result)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_research())

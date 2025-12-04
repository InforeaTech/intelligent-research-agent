import os
import json
import requests
from typing import List, Dict, Optional
from search_service import SearchService
from content_service import ContentService
from repositories import LogRepository
from sqlalchemy.orm import Session
from logger_config import get_logger, log_performance
from config import settings

logger = get_logger(__name__)


class ResearchAgent:
    def __init__(self):
        self.search_service = SearchService()
        self.content_service = ContentService()

    def search_serper(self, query: str, api_key: str, max_results: int = 10) -> List[Dict]:
        return self.search_service.search_serper(query, api_key, max_results)

    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        return self.search_service.search_web(query, max_results)

    def scrape_webpage(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        return self.search_service.scrape_webpage(url, max_chars)

    def gather_info(self, name: str, company: str = "", additional_info: str = "", serper_api_key: str = None, db: Session = None) -> Dict:
        """Orchestrates the research process."""
        search_query = f"{name} {company} linkedin profile professional bio".strip()
        if additional_info:
            search_query += f" {additional_info}"
        
        # 1. General Search
        if serper_api_key:
            source = "Serper"
        else:
            source = "DuckDuckGo"

        # Check cache for search query
        search_data_key = {"query": search_query, "source": source}
        cached_search = None
        
        if db:
            log_repo = LogRepository(db)
            cached_search = log_repo.check_cache(
                action_type="search_query",
                search_data=search_data_key
            )

        if cached_search:
            logger.info("Cache hit for gather_info search", extra={'extra_data': {'query': search_query}})
            general_results = json.loads(cached_search)
        else:
            if serper_api_key:
                general_results = self.search_serper(search_query, serper_api_key, max_results=5)
            else:
                general_results = self.search_web(search_query, max_results=5)
            
            # Log search results
            if db:
                log_repo = LogRepository(db)
                log_repo.create_log(
                    action_type="search_query",
                    search_data=search_data_key,
                    model_input=search_query,
                    model_output=json.dumps(general_results),
                    final_output=json.dumps(general_results)
                )
        
        return {
            "query": search_query,
            "general_results": general_results,
            "source": source
        }

    def generate_profile(self, research_data: Dict, api_key: str, provider: str = "openai", bypass_cache: bool = False, db: Session = None) -> tuple:
        """Uses LLM to compile a profile from research data. Returns (profile_text, from_cache, cached_note_dict)"""
        # Check cache
        cached_result = None
        cached_note = None
        
        if db:
            log_repo = LogRepository(db)
            if not bypass_cache:
                cached_result = log_repo.check_cache(
                    action_type="generate_profile",
                    search_data=research_data
                )
        
        from_cache = False
        
        if cached_result:
            from_cache = True
            response_text = cached_result
            # Try to find a cached note for this profile
            if db:
                log_repo = LogRepository(db)
                cached_note = log_repo.get_recent_note_for_profile(cached_result)
        else:
            response_text = self.content_service.generate_profile(research_data, api_key, provider)
            
            # Log interaction
            if db:
                log_repo = LogRepository(db)
                log_repo.create_log(
                    action_type="generate_profile",
                    search_data=research_data,
                    model_input="Delegated to ContentService", 
                    model_output=response_text,
                    final_output=response_text
                )
        
        return (response_text, from_cache, cached_note)

    def generate_profile_with_mode(self, name: str, company: str = "", additional_info: str = "", 
                                   api_key: str = "", provider: str = "openai", 
                                   serper_api_key: str = None, bypass_cache: bool = False,
                                   search_mode: str = None, db: Session = None) -> tuple:
        """
        Generate profile using specified search mode.
        
        Args:
            name: Person's name
            company: Company name
            additional_info: Additional context
            api_key: LLM API key
            provider: LLM provider
            serper_api_key: Optional Serper API key
            bypass_cache: Skip cache lookup
            search_mode: Override for search mode ('rag', 'tools', 'hybrid'). Uses config default if None.
            db: Database session
            
        Returns:
            Tuple of (profile_text, research_data, from_cache, cached_note)
        """
        # Determine search mode
        mode = search_mode or settings.SEARCH_MODE
        logger.info(f"Generating profile with mode: {mode}", 
                   extra={'extra_data': {'name': name, 'mode': mode, 'provider': provider}})
        
        if mode == "tools":
            # Function calling mode - LLM decides when to search
            profile_text = self.content_service.generate_profile_with_tools(
                name=name,
                company=company,
                additional_info=additional_info,
                api_key=api_key,
                provider=provider,
                serper_api_key=serper_api_key
            )
            # Function calling doesn't use traditional cache, so no cached note
            # Return minimal research data
            research_data = {"mode": "tools", "query": f"{name} {company}"}
            return (profile_text, research_data, False, None)
        
        elif mode == "hybrid":
            # Hybrid mode - RAG + function calling
            # First gather info via RAG
            research_data = self.gather_info(name, company, additional_info, serper_api_key, db)
            research_data["mode"] = "hybrid"
            
            # Then use function calling with initial context
            # For now, pass research data in the additional_info
            context = f"Initial research: {json.dumps(research_data)}\n\n{additional_info}"
            profile_text = self.content_service.generate_profile_with_tools(
                name=name,
                company=company,
                additional_info=context,
                api_key=api_key,
                provider=provider,
                serper_api_key=serper_api_key
            )
            return (profile_text, research_data, False, None)
        
        else:  # Default to RAG mode
            # Traditional RAG mode
            research_data = self.gather_info(name, company, additional_info, serper_api_key, db)
            research_data["mode"] = "rag"
            profile_text, from_cache, cached_note = self.generate_profile(research_data, api_key, provider, bypass_cache, db)
            return (profile_text, research_data, from_cache, cached_note)


    def generate_note(self, profile_text: str, length: int, tone: str, context: str, api_key: str, provider: str = "openai", bypass_cache: bool = False, db: Session = None) -> tuple:
        """Generates a LinkedIn connection note. Returns (note_text, from_cache)"""
        # Check cache
        user_input = {"profile_text": profile_text, "length": length, "tone": tone, "context": context}
        cached_result = None
        
        if db and not bypass_cache:
            log_repo = LogRepository(db)
            cached_result = log_repo.check_cache_fuzzy(
                action_type="generate_note",
                user_input=user_input
            )
        
        from_cache = False
        
        if cached_result:
            from_cache = True
            response_text = cached_result
        else:
            response_text = self.content_service.generate_note(profile_text, length, tone, context, api_key, provider)
            
            if db:
                log_repo = LogRepository(db)
                log_repo.create_log(
                    action_type="generate_note",
                    user_input=user_input,
                    model_input="Delegated to ContentService",
                    model_output=response_text,
                    final_output=response_text
                )
        
        return (response_text, from_cache)

    @log_performance()
    def perform_deep_research(self, topic: str, api_key: str, serper_api_key: str = None, bypass_cache: bool = False, db: Session = None) -> str:
        """Performs deep research using Gemini 3 Pro and multiple search iterations."""
        if not api_key:
            return "Error: API Key is required for deep research."

        logger.info("Starting deep research", extra={'extra_data': {'topic': topic}})
        
        # Check cache (Topic level)
        if db and not bypass_cache:
            log_repo = LogRepository(db)
            cached_result = log_repo.check_cache_fuzzy(
                action_type="deep_research",
                user_input={"topic": topic}
            )
            if cached_result:
                logger.info("Cache hit for deep research", extra={'extra_data': {'topic': topic}})
                return cached_result
        
        # Step 1: Plan Research
        queries, planning_prompt, planning_text = self.content_service.plan_research(topic, api_key)
        logger.info("Generated queries", extra={'extra_data': {'query_count': len(queries), 'queries': queries}})
        
        # Log planning interaction
        if db:
            log_repo = LogRepository(db)
            log_repo.create_log(
                action_type="deep_research_planning",
                user_input={"topic": topic},
                model_input=planning_prompt,
                model_output=planning_text,
                final_output=json.dumps(queries)
            )

        # Step 2: Execute Searches
        all_results = []
        for q in queries:
            # Check cache for each query
            source = "Serper" if serper_api_key else "DuckDuckGo"
            search_data_key = {"query": q, "source": source}
            cached_search = None
            
            if db and not bypass_cache:
                log_repo = LogRepository(db)
                cached_search = log_repo.check_cache(
                    action_type="search_query",
                    search_data=search_data_key
                )

            if cached_search:
                results = json.loads(cached_search)
            else:
                if serper_api_key:
                    results = self.search_service.search_serper(q, serper_api_key, max_results=10)
                else:
                    results = self.search_service.search_web(q, max_results=10)
                
                # Log search results
                if db:
                    log_repo = LogRepository(db)
                    log_repo.create_log(
                        action_type="search_query",
                        search_data=search_data_key,
                        model_input=q,
                        model_output=json.dumps(results),
                        final_output=json.dumps(results)
                    )
            all_results.extend(results)
        
        # Deduplicate results based on URL
        unique_results = {r['href']: r for r in all_results if r.get('href')}.values()
        unique_results = list(unique_results)
        
        # Step 3: Scrape Webpage Content
        logger.info("Scraping webpages", extra={'extra_data': {'count': len(unique_results)}})
        scraped_data = []
        for result in unique_results:
            scraped = self.search_service.scrape_webpage(result['href'])
            if scraped['success']:
                scraped_data.append({
                    'title': result.get('title', ''),
                    'url': scraped['url'],
                    'snippet': result.get('body', ''),
                    'content': scraped['content']
                })
            else:
                # Include result even if scraping failed
                scraped_data.append({
                    'title': result.get('title', ''),
                    'url': result['href'],
                    'snippet': result.get('body', ''),
                    'content': '(Content not available)'
                })
        
        context_str = json.dumps(scraped_data, indent=2)
        
        # Step 4: Synthesize Report
        report_text, report_prompt = self.content_service.synthesize_report(topic, context_str, api_key)
        
        # Log interaction
        if db:
            log_repo = LogRepository(db)
            log_repo.create_log(
                action_type="deep_research",
                user_input={"topic": topic},
                search_data=scraped_data,
                model_input=report_prompt,
                model_output=report_text,
                final_output=report_text
            )
        return report_text

    def deep_research_with_mode(self, topic: str, api_key: str, provider: str = "openai",
                               serper_api_key: str = None, bypass_cache: bool = False,
                               search_mode: str = None, db: Session = None) -> str:
        """
        Perform deep research using specified search mode.
        
        Args:
            topic: Research topic
            api_key: LLM API key
            provider: LLM provider ('openai', 'gemini', 'grok')
            serper_api_key: Optional Serper API key
            bypass_cache: Skip cache lookup
            search_mode: Override for search mode ('rag', 'tools', 'hybrid'). Uses config default if None.
            db: Database session
            
        Returns:
            Research report text
        """
        # Determine search mode
        mode = search_mode or settings.SEARCH_MODE
        logger.info(f"Starting deep research with mode: {mode}",
                   extra={'extra_data': {'topic': topic, 'mode': mode, 'provider': provider}})
        
        if mode == "tools":
            # Tools mode - LLM autonomously decides when to search
            report_text = self.content_service.deep_research_with_tools(
                topic=topic,
                api_key=api_key,
                provider=provider,
                serper_api_key=serper_api_key
            )
            
            # Log the research (no cache for tools mode currently)
            if db:
                log_repo = LogRepository(db)
                log_repo.create_log(
                    action_type="deep_research_tools",
                    user_input={"topic": topic, "mode": "tools"},
                    model_input=f"Tools mode research: {topic}",
                    model_output=report_text,
                    final_output=report_text
                )
            
            return report_text
        
        elif mode == "hybrid":
            # Hybrid mode - RAG first, then tools for refinement
            # Step 1: Execute traditional RAG research
            logger.info("Hybrid mode: Starting with RAG research")
            rag_report = self.perform_deep_research(
                topic=topic,
                api_key=api_key,
                serper_api_key=serper_api_key,
                bypass_cache=bypass_cache,
                db=db
            )
            
            # Step 2: Pass RAG results as context to tools mode
            logger.info("Hybrid mode: Refining with tools")
            enhanced_topic = f"""{topic}

Initial Research Context:
{rag_report}

Please review the above research and use tools to:
1. Verify key facts
2. Find any missing information
3. Get more recent updates if needed
4. Provide an enhanced final report"""
            
            final_report = self.content_service.deep_research_with_tools(
                topic=enhanced_topic,
                api_key=api_key,
                provider=provider,
                serper_api_key=serper_api_key
            )
            
            # Log hybrid research
            if db:
                log_repo = LogRepository(db)
                log_repo.create_log(
                    action_type="deep_research_hybrid",
                    user_input={"topic": topic, "mode": "hybrid"},
                    model_input=f"Hybrid mode: RAG + Tools",
                    model_output=final_report,
                    final_output=final_report
                )
            
            return final_report
        
        else:  # Default to RAG mode
            # Traditional RAG mode (existing implementation)
            return self.perform_deep_research(
                topic=topic,
                api_key=api_key,
                serper_api_key=serper_api_key,
                bypass_cache=bypass_cache,
                db=db
            )

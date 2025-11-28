import os
import json
import requests
from typing import List, Dict, Optional
from search_service import SearchService
from content_service import ContentService
from database import DatabaseManager


class ResearchAgent:
    def __init__(self):
        self.search_service = SearchService()
        self.content_service = ContentService()
        self.db = DatabaseManager()

    def search_serper(self, query: str, api_key: str, max_results: int = 10) -> List[Dict]:
        return self.search_service.search_serper(query, api_key, max_results)

    def search_web(self, query: str, max_results: int = 10) -> List[Dict]:
        return self.search_service.search_web(query, max_results)

    def scrape_webpage(self, url: str, max_chars: int = 5000) -> Dict[str, str]:
        return self.search_service.scrape_webpage(url, max_chars)

    def gather_info(self, name: str, company: str = "", additional_info: str = "", serper_api_key: str = None) -> Dict:
        """Orchestrates the research process."""
        search_query = f"{name} {company} linkedin profile professional bio".strip()
        if additional_info:
            search_query += f" {additional_info}"
        
        # 1. General Search
        if serper_api_key:
            general_results = self.search_serper(search_query, serper_api_key, max_results=5)
        else:
            general_results = self.search_web(search_query, max_results=5)
        
        return {
            "query": search_query,
            "general_results": general_results,
            "source": "Serper" if serper_api_key else "DuckDuckGo"
        }

    def generate_profile(self, research_data: Dict, api_key: str, provider: str = "openai", bypass_cache: bool = False) -> tuple:
        """Uses LLM to compile a profile from research data. Returns (profile_text, from_cache, cached_note_dict)"""
        # Check cache
        cached_result = self.db.check_existing_log(
            action_type="generate_profile",
            search_data=research_data,
            bypass_cache=bypass_cache
        )
        
        from_cache = False
        cached_note = None
        
        if cached_result:
            from_cache = True
            response_text = cached_result
            # Try to find a cached note for this profile
            cached_note = self.db.get_recent_note_for_profile(cached_result)
        else:
            response_text = self.content_service.generate_profile(research_data, api_key, provider)
            
            # Log interaction
            # Note: We reconstruct the prompt here for logging purposes, or we could update the service to return it.
            # For simplicity in this refactor, we'll log the inputs we have.
            self.db.log_interaction(
                action_type="generate_profile",
                search_data=research_data,
                model_input="Delegated to ContentService", 
                model_output=response_text,
                final_output=response_text
            )
        
        return (response_text, from_cache, cached_note)

    def generate_note(self, profile_text: str, length: int, tone: str, context: str, api_key: str, provider: str = "openai", bypass_cache: bool = False) -> tuple:
        """Generates a LinkedIn connection note. Returns (note_text, from_cache)"""
        # Check cache
        user_input = {"profile_text": profile_text, "length": length, "tone": tone, "context": context}
        cached_result = self.db.check_existing_log(
            action_type="generate_note",
            user_input=user_input,
            bypass_cache=bypass_cache
        )
        
        from_cache = False
        
        if cached_result:
            from_cache = True
            response_text = cached_result
        else:
            response_text = self.content_service.generate_note(profile_text, length, tone, context, api_key, provider)
            
            self.db.log_interaction(
                action_type="generate_note",
                user_input={"profile_text": profile_text, "length": length, "tone": tone, "context": context},
                model_input="Delegated to ContentService",
                model_output=response_text,
                final_output=response_text
            )
        
        return (response_text, from_cache)

    def perform_deep_research(self, topic: str, api_key: str, serper_api_key: str = None, bypass_cache: bool = False) -> str:
        """Performs deep research using Gemini 3 Pro and multiple search iterations."""
        if not api_key:
            return "Error: API Key is required for deep research."

        print(f"Starting deep research on: {topic}")
        
        # Check cache (Topic level)
        cached_result = self.db.check_existing_log(
            action_type="deep_research",
            user_input={"topic": topic},
            bypass_cache=bypass_cache
        )
        if cached_result:
            print(f"Cache hit for deep_research: {topic}")
            return cached_result
        
        # Step 1: Plan Research
        queries, planning_prompt, planning_text = self.content_service.plan_research(topic, api_key)
        print(f"Generated queries: {queries}")
        
        # Log planning interaction
        self.db.log_interaction(
            action_type="deep_research_planning",
            user_input={"topic": topic},
            model_input=planning_prompt,
            model_output=planning_text,
            final_output=json.dumps(queries)
        )

        # Step 2: Execute Searches
        all_results = []
        for q in queries:
            if serper_api_key:
                results = self.search_service.search_serper(q, serper_api_key, max_results=10)
            else:
                results = self.search_service.search_web(q, max_results=10)
            all_results.extend(results)
        
        # Deduplicate results based on URL
        unique_results = {r['href']: r for r in all_results if r.get('href')}.values()
        unique_results = list(unique_results)
        
        # Step 3: Scrape Webpage Content
        print(f"Scraping {len(unique_results)} webpages...")
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
        self.db.log_interaction(
            action_type="deep_research",
            user_input={"topic": topic},
            search_data=scraped_data,
            model_input=report_prompt,
            model_output=report_text,
            final_output=report_text
        )
        return report_text

import json
import time
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, Any, List
from logger_config import get_logger

logger = get_logger(__name__)

class ContentService:
    def generate_profile(self, research_data: Dict, api_key: str, provider: str = "openai") -> str:
        """Uses LLM to compile a profile from research data."""
        logger.info("Starting profile generation", extra={'extra_data': {'provider': provider}})
        
        if not api_key:
            logger.error("Missing API key for profile generation", extra={'extra_data': {'provider': provider}})
            return "Error: API Key is required for profile generation."

        if api_key == "mock":
            return """# Marius Poskus (Mock)
## Current Position
CEO, MP Cybersecurity Services

## Professional Summary
Marius Poskus is an experienced cybersecurity leader based in London. He currently serves as the CEO of MP Cybersecurity Services.

## Career History
- CEO, MP Cybersecurity Services (Present)

## Sources
- Mock Data
"""

        context_str = json.dumps(research_data, indent=2)
        
        prompt = f"""
        You are an expert research assistant hat gathers information about individuals and creates comprehensive professional profiles.
        Agent Capabilities
        1. Information Gathering & Research
        When provided with a person's information (name, company, location, or any identifying details), you will:

        Conduct web searches across multiple sources
        Query professional databases and platforms (LinkedIn, GitHub, company websites)
        Gather information from news articles, press releases, and professional publications
        Compile educational background, career history, and achievements
        Identify professional associations and speaking engagements
        Research recent projects, publications, or notable work
        
        
        
        
        Create a comprehensive professional profile based on the following raw search data.
        
        Raw Data:
        {context_str}
        

        Format the output exactly as follows:
        
        # [Name]
        ## Current Position
        [Title, Company]

        ## Company and Industry
        [Company Name, Industry]

        ## Location
        [Location]

        ## Professional Summary
        [2-3 sentences]
        
        ## Career History (Last 5-10 Years)
        - [Role, Company, Dates if available]
        
        ## Education and Credentials
        - [Degree, Institution]
        
        ## Key Achievements and Recognition
        - [Achievement 1]
        - [Achievement 2]
        
        ## Areas of Expertise
        - [Expertise 1]
        - [Expertise 2]
        
        ## Recent Work/Projects
        - [Project/Work]

        ## Recent Publications and Thought Leadership
        - [Publication]

        ##Industry Recognition
        - [Recognition 1]
        - [Recognition 2]

        #Notable Connections and Affiliations
        - [Connection 1]
        - [Connection 2]    

        ## Professional Associations
        - [Association 1]
        - [Association 2]

        ## Speaking Engagements
        - [Engagement 1]
        - [Engagement 2]

        ## Sources
        [List URLs used]
        
        If information is missing, then ignore it."
        """

        start_time = time.time()
        try:
            if provider == "gemini":
                logger.info("Calling Gemini API", extra={'extra_data': {'model': 'gemini-3-pro-preview', 'prompt_length': len(prompt)}})
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                response = model.generate_content(prompt)
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Profile generation completed", extra={'extra_data': {'provider': 'gemini', 'duration_ms': round(duration_ms, 2), 'response_length': len(response.text)}})
                return response.text
            else:
                logger.info("Calling OpenAI API", extra={'extra_data': {'model': 'gpt-4o', 'prompt_length': len(prompt)}})
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful professional research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                duration_ms = (time.time() - start_time) * 1000
                response_text = response.choices[0].message.content
                logger.info("Profile generation completed", extra={'extra_data': {'provider': 'openai', 'duration_ms': round(duration_ms, 2), 'response_length': len(response_text)}})
                return response_text
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Profile generation failed", extra={'extra_data': {'provider': provider, 'duration_ms': round(duration_ms, 2), 'error': str(e)}}, exc_info=True)
            return f"Error generating profile: {str(e)}"

    def generate_note(self, profile_text: str, length: int, tone: str, context: str, api_key: str, provider: str = "openai") -> str:
        """Generates a LinkedIn connection note."""
        logger.info("Starting note generation", extra={'extra_data': {'provider': provider, 'length': length, 'tone': tone}})
        
        if not api_key:
            logger.error("Missing API key for note generation", extra={'extra_data': {'provider': provider}})
            return "Error: API Key is required for note generation."

        if api_key == "mock":
            return f"Hi Marius, I see you are doing great work at MP Cybersecurity Services. I'd love to connect. Best, [My Name]"

        prompt = f"""
        Write a LinkedIn connection note based on this profile:
        
        {profile_text}
        
        Constraints:
        - Length: Approximately {length} characters (strict limit).
        - Tone: {tone}
        - Context/Reason: {context if context else "General professional connection"}
        
        Output ONLY the message text.
        """

        start_time = time.time()
        try:
            if provider == "gemini":
                logger.info("Calling Gemini API", extra={'extra_data': {'model': 'gemini-3-pro-preview', 'prompt_length': len(prompt)}})
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                response = model.generate_content(prompt)
                duration_ms = (time.time() - start_time) * 1000
                logger.info("Note generation completed", extra={'extra_data': {'provider': 'gemini', 'duration_ms': round(duration_ms, 2), 'response_length': len(response.text)}})
                return response.text
            else:
                logger.info("Calling OpenAI API", extra={'extra_data': {'model': 'gpt-4o', 'prompt_length': len(prompt)}})
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert networking assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                duration_ms = (time.time() - start_time) * 1000
                response_text = response.choices[0].message.content
                logger.info("Note generation completed", extra={'extra_data': {'provider': 'openai', 'duration_ms': round(duration_ms, 2), 'response_length': len(response_text)}})
                return response_text
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Note generation failed", extra={'extra_data': {'provider': provider, 'duration_ms': round(duration_ms, 2), 'error': str(e)}}, exc_info=True)
            return f"Error generating note: {str(e)}"

    def plan_research(self, topic: str, api_key: str) -> List[str]:
        """Generates search queries for deep research."""
        logger.info("Starting research planning", extra={'extra_data': {'topic': topic}})
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        planning_prompt = f"""
        You are a senior research analyst. I need to research the following topic deeply:
        "{topic}"
        
        check if the person is a director in a company or not.
        Generate 4 specific search queries that will help gather comprehensive information on this topic.
        Return ONLY the queries as a JSON list of strings.
        Example: ["query 1", "query 2", ...]
        """
        
        start_time = time.time()
        try:
            logger.info("Calling Gemini API for research planning", extra={'extra_data': {'model': 'gemini-3-pro-preview'}})
            plan_response = model.generate_content(planning_prompt)
            text = plan_response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            queries = json.loads(text)
            duration_ms = (time.time() - start_time) * 1000
            logger.info("Research planning completed", extra={'extra_data': {'duration_ms': round(duration_ms, 2), 'query_count': len(queries)}})
            return queries, planning_prompt, text # Return prompt and raw text for logging
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Research planning failed", extra={'extra_data': {'duration_ms': round(duration_ms, 2), 'error': str(e)}}, exc_info=True)
            fallback_queries = [topic, f"{topic} details", f"{topic} analysis", f"{topic} latest news"]
            logger.warning("Using fallback queries", extra={'extra_data': {'query_count': len(fallback_queries)}})
            return fallback_queries, planning_prompt, str(e)

    def synthesize_report(self, topic: str, context_str: str, api_key: str) -> str:
        """Synthesizes a deep research report."""
        logger.info("Starting report synthesis", extra={'extra_data': {'topic': topic, 'context_length': len(context_str)}})
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        report_prompt = f"""
        You are a senior research analyst. Write a comprehensive deep research report on "{topic}" based on the gathered information below.
        
        Research Data:
        {context_str}
        
        The report should be detailed, structured, and professional. Use Markdown formatting.
        Include:
        - Executive Summary
        - Detailed Analysis
        - Key Findings
        - Sources (cited inline or at the end)
        """
        
        start_time = time.time()
        try:
            logger.info("Calling Gemini API for report synthesis", extra={'extra_data': {'model': 'gemini-3-pro-preview', 'prompt_length': len(report_prompt)}})
            report_response = model.generate_content(report_prompt)
            duration_ms = (time.time() - start_time) * 1000
            logger.info("Report synthesis completed", extra={'extra_data': {'duration_ms': round(duration_ms, 2), 'report_length': len(report_response.text)}})
            return report_response.text, report_prompt
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Report synthesis failed", extra={'extra_data': {'duration_ms': round(duration_ms, 2), 'error': str(e)}}, exc_info=True)
            return f"Error generating report: {str(e)}", report_prompt

import json
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, Any, List

class ContentService:
    def generate_profile(self, research_data: Dict, api_key: str, provider: str = "openai") -> str:
        """Uses LLM to compile a profile from research data."""
        if not api_key:
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
        You are an expert research assistant. Create a comprehensive professional profile based on the following raw search data.
        
        Raw Data:
        {context_str}
        
        Format the output exactly as follows:
        
        # [Name]
        ## Current Position
        [Title, Company]
        
        ## Professional Summary
        [2-3 sentences]
        
        ## Career History
        - [Role, Company, Dates if available]
        
        ## Education
        - [Degree, Institution]
        
        ## Key Achievements
        - [Achievement 1]
        - [Achievement 2]
        
        ## Recent Work/Projects
        - [Project/Work]
        
        ## Sources
        [List URLs used]
        
        If information is missing, state "Not found in available search results."
        """

        try:
            if provider == "gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                response = model.generate_content(prompt)
                return response.text
            else:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful professional research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating profile: {str(e)}"

    def generate_note(self, profile_text: str, length: int, tone: str, context: str, api_key: str, provider: str = "openai") -> str:
        """Generates a LinkedIn connection note."""
        if not api_key:
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

        try:
            if provider == "gemini":
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                response = model.generate_content(prompt)
                return response.text
            else:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert networking assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating note: {str(e)}"

    def plan_research(self, topic: str, api_key: str) -> List[str]:
        """Generates search queries for deep research."""
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
        
        try:
            plan_response = model.generate_content(planning_prompt)
            text = plan_response.text.strip()
            if text.startswith("```json"):
                text = text[7:-3]
            queries = json.loads(text)
            return queries, planning_prompt, text # Return prompt and raw text for logging
        except Exception as e:
            print(f"Planning error: {e}")
            return [topic, f"{topic} details", f"{topic} analysis", f"{topic} latest news"], planning_prompt, str(e)

    def synthesize_report(self, topic: str, context_str: str, api_key: str) -> str:
        """Synthesizes a deep research report."""
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
        
        try:
            report_response = model.generate_content(report_prompt)
            return report_response.text, report_prompt
        except Exception as e:
            return f"Error generating report: {str(e)}", report_prompt

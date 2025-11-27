import json
import google.generativeai as genai
from openai import OpenAI
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Content Service")

# Models
class ProfileRequest(BaseModel):
    research_data: Dict
    api_key: str
    provider: str = "openai"

class NoteRequest(BaseModel):
    profile_text: str
    length: int
    tone: str
    context: str
    api_key: str
    provider: str = "openai"

class ResearchPlanRequest(BaseModel):
    topic: str
    api_key: str

class ReportRequest(BaseModel):
    topic: str
    context_str: str
    api_key: str

# Service Logic (Migrated)
class ContentService:
    def generate_profile(self, research_data: Dict, api_key: str, provider: str = "openai") -> str:
        if not api_key: return "Error: API Key is required."
        if api_key == "mock": return "Mock Profile"

        context_str = json.dumps(research_data, indent=2)
        prompt = f"""
        You are an expert research assistant. Create a comprehensive professional profile based on the following raw search data.
        Raw Data: {context_str}
        Format: # [Name] ... (Standard Profile Format)
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
                    messages=[{"role": "system", "content": "You are a helpful professional research assistant."},
                              {"role": "user", "content": prompt}],
                    temperature=0.3
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating profile: {str(e)}"

    def generate_note(self, profile_text: str, length: int, tone: str, context: str, api_key: str, provider: str = "openai") -> str:
        if not api_key: return "Error: API Key is required."
        if api_key == "mock": return "Mock Note"

        prompt = f"""
        Write a LinkedIn connection note based on this profile:
        {profile_text}
        Constraints: Length: {length}, Tone: {tone}, Context: {context}
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
                    messages=[{"role": "system", "content": "You are an expert networking assistant."},
                              {"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"Error generating note: {str(e)}"

    def plan_research(self, topic: str, api_key: str):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        planning_prompt = f"""
        You are a senior research analyst. I need to research the following topic deeply: "{topic}"
        Generate 4 specific search queries. Return ONLY the queries as a JSON list of strings.
        """
        
        try:
            plan_response = model.generate_content(planning_prompt)
            text = plan_response.text.strip()
            if text.startswith("```json"): text = text[7:-3]
            queries = json.loads(text)
            return queries, planning_prompt, text
        except Exception as e:
            return [topic, f"{topic} details"], planning_prompt, str(e)

    def synthesize_report(self, topic: str, context_str: str, api_key: str):
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-pro-preview')
        
        report_prompt = f"""
        You are a senior research analyst. Write a comprehensive deep research report on "{topic}".
        Research Data: {context_str}
        """
        
        try:
            report_response = model.generate_content(report_prompt)
            return report_response.text, report_prompt
        except Exception as e:
            return f"Error generating report: {str(e)}", report_prompt

service = ContentService()

# Routes
@app.post("/generate/profile")
async def generate_profile(request: ProfileRequest):
    return {"result": service.generate_profile(request.research_data, request.api_key, request.provider)}

@app.post("/generate/note")
async def generate_note(request: NoteRequest):
    return {"result": service.generate_note(request.profile_text, request.length, request.tone, request.context, request.api_key, request.provider)}

@app.post("/research/plan")
async def plan_research(request: ResearchPlanRequest):
    queries, prompt, raw = service.plan_research(request.topic, request.api_key)
    return {"queries": queries, "prompt": prompt, "raw_response": raw}

@app.post("/research/synthesize")
async def synthesize_report(request: ReportRequest):
    text, prompt = service.synthesize_report(request.topic, request.context_str, request.api_key)
    return {"report": text, "prompt": prompt}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)

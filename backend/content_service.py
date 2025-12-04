import json
import time
import google.generativeai as genai
from openai import OpenAI
import httpx
from typing import Dict, Any, List, Optional
from logger_config import get_logger
from tool_definitions import get_tools_for_provider
from tool_executor import ToolExecutor

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
            elif provider == "grok":
                logger.info("Calling Grok API", extra={'extra_data': {'model': 'grok-4-1-fast', 'prompt_length': len(prompt)}})
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1",
                    http_client=httpx.Client()
                )
                response = client.chat.completions.create(
                    model="grok-4-1-fast",
                    messages=[
                        {"role": "system", "content": "You are a helpful professional research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                duration_ms = (time.time() - start_time) * 1000
                response_text = response.choices[0].message.content
                logger.info("Profile generation completed", extra={'extra_data': {'provider': 'grok', 'duration_ms': round(duration_ms, 2), 'response_length': len(response_text)}})
                return response_text
            else:
                logger.info("Calling OpenAI API", extra={'extra_data': {'model': 'gpt-5-nano', 'prompt_length': len(prompt)}})
                client = OpenAI(api_key=api_key, http_client=httpx.Client())
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": "You are a helpful professional research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1
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
            elif provider == "grok":
                logger.info("Calling Grok API", extra={'extra_data': {'model': 'grok-4-1-fast', 'prompt_length': len(prompt)}})
                client = OpenAI(
                    api_key=api_key,
                    base_url="https://api.x.ai/v1",
                    http_client=httpx.Client()
                )
                response = client.chat.completions.create(
                    model="grok-4-1-fast",
                    messages=[
                        {"role": "system", "content": "You are an expert networking assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8
                )
                duration_ms = (time.time() - start_time) * 1000
                response_text = response.choices[0].message.content
                logger.info("Note generation completed", extra={'extra_data': {'provider': 'grok', 'duration_ms': round(duration_ms, 2), 'response_length': len(response_text)}})
                return response_text
            else:
                logger.info("Calling OpenAI API", extra={'extra_data': {'model': 'gpt-5-nano', 'prompt_length': len(prompt)}})
                client = OpenAI(api_key=api_key, http_client=httpx.Client())
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=[
                        {"role": "system", "content": "You are an expert networking assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1
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

    def generate_profile_with_tools(self, name: str, company: str, additional_info: str, 
                   api_key: str, provider: str = "openai", 
                                   serper_api_key: Optional[str] = None,
                                   max_iterations: int = 5) -> str:
        """
        Generate profile using LLM function calling.
        LLM autonomously decides when to search/scrape.
        
        Args:
            name: Person's name
            company: Company name
            additional_info: Additional context
            api_key: LLM API key
            provider: LLM provider ('openai', 'gemini', 'grok')
            serper_api_key: Optional Serper API key for searches
            max_iterations: Maximum tool calling iterations
            
        Returns:
            Generated profile text
        """
        logger.info("Starting profile generation with tools", 
                   extra={'extra_data': {'provider': provider, 'name': name}})
        
        if provider == "openai":
            return self._generate_profile_with_tools_openai(
                name, company, additional_info, api_key, serper_api_key, max_iterations
            )
        elif provider == "gemini":
            return self._generate_profile_with_tools_gemini(
                name, company, additional_info, api_key, serper_api_key, max_iterations
            )
        elif provider == "grok":
            return self._generate_profile_with_tools_grok(
                name, company, additional_info, api_key, serper_api_key, max_iterations
            )
        else:
            logger.warning(f"Function calling not supported for {provider}, falling back to RAG")
            # Fallback to regular generation
            research_data = {"query": f"{name} {company}", "general_results": []}
            return self.generate_profile(research_data, api_key, provider)
    
    def _generate_profile_with_tools_openai(self, name: str, company: str, 
                                           additional_info: str, api_key: str,
                                           serper_api_key: Optional[str], 
                                           max_iterations: int) -> str:
        """OpenAI-specific function calling implementation."""
        start_time = time.time()
        
        try:
            # Initialize client and tool executor
            client = OpenAI(api_key=api_key, http_client=httpx.Client())
            tool_executor = ToolExecutor(serper_api_key=serper_api_key)
            tools = get_tools_for_provider("openai")
            
            # Initial prompt
            system_message = "You are an expert research assistant. Use the available tools to search for information and create a comprehensive professional profile."
            
            user_prompt = f"""
Create a comprehensive professional profile for:
Name: {name}
Company: {company}
{f"Additional Info: {additional_info}" if additional_info else ""}

Use the search_web and scrape_webpage tools to gather information.
Format the output as a detailed professional profile.
"""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
            
            iteration = 0
            
            # Function calling loop
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Function calling iteration {iteration}/{max_iterations}")
                
                # Call LLM with tools
                response = client.chat.completions.create(
                    model="gpt-5-nano",
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",  # LLM decides when to use tools
                    temperature=1
                )
                
                assistant_message = response.choices[0].message
                
                # Check if LLM wants to use tools
                if not assistant_message.tool_calls:
                    # LLM returned final answer
                    final_content = assistant_message.content or ""
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info("Profile generation with tools completed",
                               extra={'extra_data': {
                                   'provider': 'openai',
                                   'iterations': iteration,
                                   'duration_ms': round(duration_ms, 2),
                                   'response_length': len(final_content)
                               }})
                    return final_content
                
                # LLM wants to use tools
                messages.append(assistant_message)  # Add assistant's response with tool calls
                
                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM requested tool: {tool_name}",
                               extra={'extra_data': {'args': tool_args}})
                    
                    # Execute tool
                    result = tool_executor.execute_tool(tool_name, tool_args)
                    
                    # Format result for LLM
                    result_content = tool_executor.format_tool_result_for_llm(tool_name, result)
                    
                    # Add tool result to conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result_content
                    })
            
            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached, returning partial result")
            duration_ms = (time.time() - start_time) * 1000
            
            # Make one final call without tools to get best answer so far
            final_response = client.chat.completions.create(
                model="gpt-5-nano",
                messages=messages + [{"role": "user", "content": "Please provide the best profile you can create with the information gathered so far."}],
                temperature=1
            )
            
            final_content = final_response.choices[0].message.content or "Unable to generate profile"
            logger.info("Profile generation completed (max iterations)",
                       extra={'extra_data': {
                           'provider': 'openai',
                           'iterations': iteration,
                           'duration_ms': round(duration_ms, 2)
                       }})
            return final_content
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Profile generation with tools failed",
                        extra={'extra_data': {
                            'provider': 'openai',
                            'duration_ms': round(duration_ms, 2),
                            'error': str(e)
                        }},
                        exc_info=True)
            return f"Error generating profile with tools: {str(e)}"

    def _generate_profile_with_tools_gemini(self, name: str, company: str, 
                                           additional_info: str, api_key: str,
                                           serper_api_key: Optional[str], 
                                           max_iterations: int) -> str:
        """Gemini-specific function calling implementation."""
        start_time = time.time()
        
        try:
            genai.configure(api_key=api_key)
            tool_executor = ToolExecutor(serper_api_key=serper_api_key)
            
            # Get tools in Gemini format
            tools = get_tools_for_provider("gemini")
            
            # Initialize model with tools
            model = genai.GenerativeModel(
                model_name='gemini-3-pro-preview',
                tools=tools
            )
            
            # Start chat session
            chat = model.start_chat(enable_automatic_function_calling=False)
            
            system_prompt = "You are an expert research assistant. Use the available tools to search for information and create a comprehensive professional profile."
            
            user_prompt = f"""
{system_prompt}

Create a comprehensive professional profile for:
Name: {name}
Company: {company}
{f"Additional Info: {additional_info}" if additional_info else ""}

Use the search_web and scrape_webpage tools to gather information.
Format the output as a detailed professional profile.
"""
            
            iteration = 0
            
            # Send initial message
            response = chat.send_message(user_prompt)
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Function calling iteration {iteration}/{max_iterations}")
                
                # Check for function calls
                function_calls = []
                for part in response.parts:
                    if fn := part.function_call:
                        function_calls.append(fn)
                
                if not function_calls:
                    # No function calls, return text
                    final_content = response.text
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info("Profile generation with tools completed",
                               extra={'extra_data': {
                                   'provider': 'gemini',
                                   'iterations': iteration,
                                   'duration_ms': round(duration_ms, 2),
                                   'response_length': len(final_content)
                               }})
                    return final_content
                
                # Execute function calls
                function_responses = []
                for fn in function_calls:
                    tool_name = fn.name
                    tool_args = dict(fn.args)
                    
                    logger.info(f"LLM requested tool: {tool_name}",
                               extra={'extra_data': {'args': tool_args}})
                    
                    # Execute tool
                    result = tool_executor.execute_tool(tool_name, tool_args)
                    
                    # Format result for Gemini
                    # Gemini expects a specific response format for function calls
                    function_responses.append(
                        {
                            "function_response": {
                                "name": tool_name,
                                "response": {"result": result}  # Wrap in dict
                            }
                        }
                    )
                
                # Send function responses back to model
                response = chat.send_message(function_responses)
            
            # Max iterations reached
            logger.warning(f"Max iterations ({max_iterations}) reached, returning partial result")
            return response.text if response.parts else "Unable to generate profile (max iterations reached)"

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Profile generation with tools failed",
                        extra={'extra_data': {
                            'provider': 'gemini',
                            'duration_ms': round(duration_ms, 2),
                            'error': str(e)
                        }},
                        exc_info=True)
            return f"Error generating profile with tools: {str(e)}"

    def _generate_profile_with_tools_grok(self, name: str, company: str, 
                                         additional_info: str, api_key: str,
                                         serper_api_key: Optional[str], 
                                         max_iterations: int) -> str:
        """Grok-specific function calling implementation (OpenAI compatible)."""
        start_time = time.time()
        
        try:
            # Initialize client with Grok base URL
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.x.ai/v1",
                http_client=httpx.Client()
            )
            tool_executor = ToolExecutor(serper_api_key=serper_api_key)
            tools = get_tools_for_provider("grok")
            
            system_message = "You are an expert research assistant. Use the available tools to search for information and create a comprehensive professional profile."
            
            user_prompt = f"""
Create a comprehensive professional profile for:
Name: {name}
Company: {company}
{f"Additional Info: {additional_info}" if additional_info else ""}

Use the search_web and scrape_webpage tools to gather information.
Format the output as a detailed professional profile.
"""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ]
            
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"Function calling iteration {iteration}/{max_iterations}")
                
                response = client.chat.completions.create(
                    model="grok-4-1-fast",  # Use Grok model
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.8
                )
                
                assistant_message = response.choices[0].message
                
                if not assistant_message.tool_calls:
                    final_content = assistant_message.content or ""
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info("Profile generation with tools completed",
                               extra={'extra_data': {
                                   'provider': 'grok',
                                   'iterations': iteration,
                                   'duration_ms': round(duration_ms, 2),
                                   'response_length': len(final_content)
                               }})
                    return final_content
                
                messages.append(assistant_message)
                
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"LLM requested tool: {tool_name}",
                               extra={'extra_data': {'args': tool_args}})
                    
                    result = tool_executor.execute_tool(tool_name, tool_args)
                    result_content = tool_executor.format_tool_result_for_llm(tool_name, result)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": result_content
                    })
            
            # Max iterations reached
            final_response = client.chat.completions.create(
                model="grok-4-1-fast",
                messages=messages + [{"role": "user", "content": "Please provide the best profile you can create with the information gathered so far."}],
                temperature=0.8
            )
            
            return final_response.choices[0].message.content or "Unable to generate profile"

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Profile generation with tools failed",
                        extra={'extra_data': {
                            'provider': 'grok',
                            'duration_ms': round(duration_ms, 2),
                            'error': str(e)
                        }},
                        exc_info=True)
            return f"Error generating profile with tools: {str(e)}"

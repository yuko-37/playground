from agents import Agent
from myagents.search_agent import search_agent


SEARCH_MANAGER_PROMPT = """
I need you to follow the instructions very carefully. 
1. Given a query, come up with one web search request to perform to best answer the query.
2. Use websearch tool to perform web search and return response.
"""


search_tool = search_agent.as_tool(tool_name='websearch',
                                tool_description='Perform a web search using the query.')

search_manager_agent = Agent(
    name='SearchManagerAgent',
    instructions=SEARCH_MANAGER_PROMPT,
    model='gpt-5-nano',
    tools=[search_tool]
)
from dotenv import load_dotenv
load_dotenv()
from vida.agents.Base_agent import Base_Agent
from co_ordinator_tools.agent_tools import github_agent_tool_call as github_agent, yaml_agent_tool_call as yaml_agent, terraform_agent_tool_call as terraform_agent, failure_agent_tool_call as failure_agent
from vida.utils.prompt_manager_v2 import AgentInstructionPrompt
from agent_framework import InMemoryHistoryProvider #type: ignore
from vida.utils.config import Base_agent_config as baconfig

class CoOrdinatorAgent(Base_Agent):
    name = "Co_ordinator"
    # debug_context = True
    instructions = str(AgentInstructionPrompt("co-ordinator-instructions"))
    model = baconfig.model 
    AI_endpoint = baconfig.AI_endpoint
    tools = [yaml_agent, github_agent, terraform_agent, failure_agent]
    context_providers = [
        InMemoryHistoryProvider(load_messages=True),
        InMemoryHistoryProvider("audit", load_messages=False, store_context_messages=True),
    ]
# instruction = PromptManager()

# co_ordinator = Agent(
#     client=client,
#     name="Co_ordinator",
#     instructions=instruction.format("co_ordinator_instructions"),
#     tools=[yaml_agent, github_agent]
# )


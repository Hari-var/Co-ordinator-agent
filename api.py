from fastapi import APIRouter
from co_ordinator_agent import CoOrdinatorAgent
from vida.models.requests.Agents_requests import co_ordinator_agent_request
from vida.utils.preprocess import try_parse_json
from vida.utils.request_context import github_pat_ctx


router = APIRouter()

@router.post("/co_ordinator_agent")
async def co_ordinator_agent(request: co_ordinator_agent_request ):
    git_token = request.pat_token 
    if git_token:
        token_ref = github_pat_ctx.set(git_token)
    else:
        return {"message": "No git token provided"}
    try:
        agent = CoOrdinatorAgent.get_instance()

        response = await agent.run(prompt=request.prompt)
        if response:
            output, is_json = try_parse_json(response.text)
            return {
                    "response": f"Co-ordinator agent executed successfully",
                    "raw": response,
                    "is_json": is_json,
                    "output": output
                }

        print("Failed to get response from agent")         
        return {"message": "Failed to get response from agent"}
    finally:
        github_pat_ctx.reset(token_ref)
from fastapi import FastAPI
from api import router as co_ordinator_agent_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(co_ordinator_agent_router)
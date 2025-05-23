import logging

from fastapi import FastAPI

from database_agent import DatabaseAgent
from database_agent.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

setup_tracing()

app = FastAPI()
db_agent = DatabaseAgent()


@app.get("/")
def root():
    return {"message": "Database Agent API"}


@app.get("/health")
def health():
    return {"status": "healthy"}

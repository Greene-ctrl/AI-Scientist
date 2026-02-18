from fastapi import FastAPI
from app.api.router import router

app = FastAPI(title="CriticalThinking API")

app.include_router(router)

@app.get("/health")
async def health():
    return {"status": "healthy"}

Python 3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
# backend/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from utils import preprocess_texts, compute_user_sentiment, build_graph_and_eis

... 
... app = FastAPI(title="Influencer EIS API")
... 
... 
... class Tweet(BaseModel):
... user_id: str
... text: str
... mentions: List[str] = []
... is_retweet: bool = False
... likes: int = 0
... replies: int = 0
... 
... 
... class AnalyzeRequest(BaseModel):
... tweets: List[Tweet]
... 
... 
... @app.get("/health")
... async def health():
... return {"status": "ok"}
... 
... 
... @app.post("/analyze")
... async def analyze(req: AnalyzeRequest):
... try:
... # Convert incoming tweets to simple records
... records = [t.dict() for t in req.tweets]
... # 1) Preprocess texts (tokenize / basic cleaning)
... cleaned = preprocess_texts(records)
... # 2) Compute per-user sentiment (placeholder using rule-based or loaded model)
... user_sent = compute_user_sentiment(cleaned)
... # 3) Build graph and compute EIS
... nodes, edges, eis = build_graph_and_eis(cleaned, user_sent)
... 
... 
... # Return top influencers (sorted)
... top_k = sorted(eis.items(), key=lambda x: x[1], reverse=True)[:50]
... return {"top_influencers": top_k, "nodes": nodes, "edges": edges}
... except Exception as e:

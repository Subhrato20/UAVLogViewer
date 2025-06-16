from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
from mavlink_parser import MavlinkParser
from chat_agent import ChatAgent

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
mavlink_parser = MavlinkParser()
chat_agent = ChatAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post("/upload-log")
async def upload_log(file: UploadFile = File(...), session_id: Optional[str] = None):
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Parse the log file
        parsed_data = mavlink_parser.parse_log(contents)
        
        # Store flight data in chat agent if session_id is provided
        if session_id:
            chat_agent.set_flight_data(session_id, parsed_data)
        
        return {
            "status": "success",
            "data": parsed_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        # Process the message with the chat agent
        response = chat_agent.process_message(
            message.message,
            message.session_id
        )
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies")
async def get_anomalies(session_id: str):
    try:
        if session_id not in chat_agent.flight_data:
            raise HTTPException(status_code=404, detail="No flight data found for this session")
            
        anomalies = chat_agent.detect_anomalies(chat_agent.flight_data[session_id])
        return {
            "status": "success",
            "anomalies": anomalies
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 
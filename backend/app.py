from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import logging
import traceback
from mavlink_parser import MavlinkParser
from chat_agent import ChatAgent

# Configure logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
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
        logger.info(f"Received file upload request: {file.filename}")
        logger.info(f"Content type: {file.content_type}")
        
        # Read the uploaded file
        try:
            contents = await file.read()
            logger.info(f"File size: {len(contents)} bytes")
        except Exception as read_error:
            logger.error(f"Error reading file: {str(read_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"Error reading file: {str(read_error)}")
        
        if len(contents) == 0:
            logger.error("Empty file received")
            raise HTTPException(status_code=400, detail="Empty file received")
        
        # Parse the log file
        try:
            logger.info("Starting log file parsing...")
            parsed_data = mavlink_parser.parse_log(contents)
            logger.info(f"Successfully parsed log file. Message types: {list(parsed_data.keys())}")
            
            # Log some basic statistics
            for msg_type, messages in parsed_data.items():
                if messages:  # Only log if there are messages of this type
                    logger.info(f"Found {len(messages)} messages of type {msg_type}")
            
        except Exception as parse_error:
            logger.error(f"Error parsing log file: {str(parse_error)}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=400, detail=f"Error parsing log file: {str(parse_error)}")
        
        # Store flight data in chat agent if session_id is provided
        if session_id:
            try:
                chat_agent.set_flight_data(session_id, parsed_data)
                logger.info(f"Stored flight data for session: {session_id}")
            except Exception as store_error:
                logger.error(f"Error storing flight data: {str(store_error)}")
                logger.error(traceback.format_exc())
                # Continue even if storage fails, as we still want to return the parsed data
        
        return {
            "status": "success",
            "data": parsed_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in upload_log: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        logger.info(f"Received chat message: {message.message[:50]}...")
        
        # Process the message with the chat agent
        response = chat_agent.process_message(
            message.message,
            message.session_id
        )
        
        logger.info("Successfully processed chat message")
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/anomalies")
async def get_anomalies(session_id: str):
    try:
        logger.info(f"Received anomaly request for session: {session_id}")
        
        if session_id not in chat_agent.flight_data:
            logger.warning(f"No flight data found for session: {session_id}")
            raise HTTPException(status_code=404, detail="No flight data found for this session")
            
        anomalies = chat_agent.detect_anomalies(chat_agent.flight_data[session_id])
        logger.info(f"Found {len(anomalies)} anomalies")
        
        return {
            "status": "success",
            "anomalies": anomalies
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in anomalies endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug") 
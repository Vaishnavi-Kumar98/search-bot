import ast
import json
import logging
import os
import shutil
from typing import Optional
import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.params import Form
from pydantic import BaseModel

from app.api.agent.agent import agent
from app.api.services.call_api import call_api_based_on_intent
from app.api.services.parse_message import parse_query

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/chat")
async def chat(
    text: Optional[str] = Form(""),
    file: Optional[UploadFile] = File(None)
):
    print("IN CHAT ROUTER")
    try:
        tmp_path = None
        if file:
            print("File received: ", file.filename)
            suffix = os.path.splitext(file.filename)[-1].lower()
            if suffix != ".pdf":
                raise HTTPException(status_code=400, detail="Only PDF resumes are supported")
            
            async with aiofiles.tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                await tmp.write(content)
                tmp_path = tmp.name
        print("BEFORE AGENT RUN")
        response = await agent.arun(message=f"{text}, file_path:{tmp_path}", conversation_id="test_user")
        print("response: ",response)
        try:
            json_response = json.loads(json.dumps(response.content))
            json_response = ast.literal_eval(json_response)
            print("Response: ",json_response)
            return json_response
        except Exception:
            print("Response is not valid JSON")
            return response.content
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
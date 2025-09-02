import os
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware


from app.api.routers import (
    chat,
    health_check,
    search_candidate,
    feed_candidate,
    parse_resume
    
)

app = FastAPI()


BASE_URL = "/profile-search"
app.include_router(health_check.router, prefix=BASE_URL)
app.include_router(search_candidate.router, prefix=BASE_URL)
app.include_router(feed_candidate.router, prefix=BASE_URL)
app.include_router(parse_resume.router, prefix=BASE_URL)
app.include_router(chat.router, prefix=BASE_URL)


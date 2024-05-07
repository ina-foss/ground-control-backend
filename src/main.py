
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routers import projects,tasks,users,resources

app = FastAPI()


app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(resources.router)
app.servers = [
    {
        "url":"http://localhost:8000"
    }
] 

origins = [
    "http://localhost:3000",
    "https://localhost:3000",

    "http://frontend:3000",
    "https://frontend:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

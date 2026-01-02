from fastapi import FastAPI
from routes.task_routes import router as task_router
from routes.user_routes import router as user_router

app = FastAPI(
    title = "User Task Management API",
    description = "FastAPI project using Pydantic v2, CRUD operations, and JSON storage",
    version = "1.0.0"
)

app.include_router(user_router, prefix = "/users", tags = ["Users"])
app.include_router(task_router, prefix = "/tasks", tags = ["Tasks"])

@app.get("/", tags=["Health Check"])
def healthCheck():
    return {
        "status": "ok",
        "message": "User Task Management API is running"
    }
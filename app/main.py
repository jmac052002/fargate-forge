from fastapi import FastAPI
import os

app = FastAPI(
    title="fargate-forge",
    description="Production-grade FastAPI app deployed via CI/CD on ECS Fargate",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {
        "service": "fargate-forge",
        "version": os.getenv("APP_VERSION", "local"),
        "status": "running"
    }


@app.get("/info")
def info():
    return {
        "region": os.getenv("AWS_DEFAULT_REGION", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "local")
    } 
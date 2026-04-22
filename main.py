"""
RouteFlow Dispatch API - Main Application Entry Point.

A FastAPI-based microservice for receiving and processing
roadside assistance requests from external IoT platforms.

## Endpoints
- POST /webhook: Process incoming incident requests
- GET /health: Health check
- GET /: API information
- GET /docs: OpenAPI documentation

## Priority Routing
- HIGH: Immediate dispatch with high-visibility logging
- STANDARD: Queued for regular processing
"""

from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Optional

from router import router

app = FastAPI(
    title="RouteFlow Dispatch API",
    version="1.0.0",
    description="""
    Roadside assistance dispatch service for processing IoT platform requests.
    
    ## Features
    - Webhook receiver for incident requests
    - Priority-based routing (High/Standard)
    - JSON persistence for incidents and queues
    - Comprehensive request validation
    
    ## Supported Vehicle Types
    - Semi-Truck
    - Passenger Car
    - SUV
    - Van
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)


def _build_error_response(
    status_code: int,
    error_type: str,
    message: str,
    details: Optional[list] = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": error_type,
            "message": message,
            "details": details or []
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    errors: list = [
        {"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"]}
        for err in exc.errors()
    ]
    return _build_error_response(
        status_code=400,
        error_type="Bad Request",
        message="Validation failed - one or more required fields are missing or invalid",
        details=errors
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, 
    exc: Exception
) -> JSONResponse:
    return _build_error_response(
        status_code=500,
        error_type="Internal Server Error",
        message="An unexpected error occurred. Please try again later."
    )


@app.get(
    "/health",
    summary="Health check",
    description="Check if the service is running",
    tags=["Health"]
)
def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns:
        Dictionary with service status
    """
    return {"status": "healthy", "service": "routeflow-dispatch"}


@app.get(
    "/",
    summary="API information",
    description="Get API information and available endpoints",
    tags=["Info"]
)
def root() -> dict:
    """
    Root endpoint with API information.
    
    Returns:
        Dictionary with API details and endpoints
    """
    return {
        "service": "RouteFlow Dispatch API",
        "version": "1.0.0",
        "description": "Roadside assistance dispatch service",
        "endpoints": {
            "webhook": {
                "path": "POST /webhook",
                "description": "Process incident requests"
            },
            "health": {
                "path": "GET /health",
                "description": "Service health check"
            },
            "docs": {
                "path": "/docs",
                "description": "OpenAPI documentation"
            }
        }
    }


# Include webhook router
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
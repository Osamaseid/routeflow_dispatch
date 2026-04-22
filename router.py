"""
Webhook router for the RouteFlow Dispatch API.

 Handles incoming incident requests from external IoT platforms,
 validates payloads, and routes them based on priority levels.
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from typing import Optional

from models import (
    IncidentRequest,
    IncidentResponse,
    PriorityLevel
)
from logger import save_incident, route_incident, save_to_queue

router = APIRouter()


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


@router.post(
    "/webhook",
    response_model=IncidentResponse,
    summary="Process roadside assistance incident",
    description="""
    Receive and process a roadside assistance request from external IoT platforms.
    
    ## Request Body
    - **incident_id**: Unique identifier from the calling system
    - **vehicle_coordinates**: GPS coordinates (lat, long)
    - **vehicle_type**: Type of vehicle (Semi-Truck, Passenger Car, SUV, Van)
    - **priority_level**: Priority (High, Standard)
    - **customer_name**: (optional) Customer name
    - **customer_phone**: (optional) Contact phone
    - **description**: (optional) Incident description
    
    ## Response
    - **incident_id**: The processed incident ID
    - **status**: Processing status
    - **message**: Human-readable message
    
    ## Error Codes
    - 400: Malformed JSON or validation error
    - 405: Non-POST request
    - 500: Internal server error
    """,
    response_description="Incident processed successfully",
    tags=["Incidents"]
)
async def receive_webhook(request: Request) -> IncidentResponse:
    """
    Process an incoming incident webhook request.
    
    Args:
        request: FastAPI request object containing JSON body
        
    Returns:
        IncidentResponse: Acknowledgment with incident ID and status
        
    Raises:
        HTTPException: On validation errors (400, 405, 422, 500)
    """
    # Validate request method
    if request.method != "POST":
        return _build_error_response(
            status_code=405,
            error_type="Method Not Allowed",
            message="Only POST requests are accepted at this endpoint"
        )

    # Parse JSON body
    try:
        body: dict = await request.json()
    except Exception:
        return _build_error_response(
            status_code=400,
            error_type="Bad Request",
            message="Invalid JSON body - request must contain valid JSON"
        )

    # Validate request payload
    try:
        payload: IncidentRequest = IncidentRequest(**body)
    except ValidationError as e:
        errors: list = [
            {"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"]}
            for err in e.errors()
        ]
        return _build_error_response(
            status_code=400,
            error_type="Bad Request",
            message="Validation failed - one or more required fields are missing or invalid",
            details=errors
        )

    # Process incident
    try:
        incident_data: dict = payload.model_dump()
        incident_id: str = incident_data["incident_id"]
        priority: PriorityLevel = incident_data["priority_level"]

        # Log and route the incident
        route_incident(incident_data)
        save_incident(incident_data)

        # Queue standard priority incidents
        if priority == PriorityLevel.STANDARD:
            save_to_queue(incident_data)
            message: str = "Incident queued for standard processing"
        else:
            message: str = "High priority incident - immediate dispatch initiated"

        return JSONResponse(
            status_code=201,
            content={
                "incident_id": incident_id,
                "status": "processed",
                "message": message
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        return _build_error_response(
            status_code=500,
            error_type="Internal Server Error",
            message=f"An unexpected error occurred: {str(e)}"
        )
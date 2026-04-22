"""
Data models for the RouteFlow Dispatch API.

This module defines Pydantic models for request/response validation
and serialization of roadside assistance incidents.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class PriorityLevel(str, Enum):
    """
    Priority levels for incident dispatching.
    
    Attributes:
        HIGH: Immediate dispatch required (highway hazards, safety incidents)
        STANDARD: Queued for regular processing
    """
    HIGH = "High"
    STANDARD = "Standard"


class VehicleType(str, Enum):
    """
    Supported vehicle types for roadside assistance.
    
    Attributes:
        SEMI_TRUCK: Commercial trucks and semi-trailers
        PASSENGER_CAR: Standard consumer vehicles
        SUV: Sport utility vehicles
        VAN: Cargo vans and minivans
    """
    SEMI_TRUCK = "Semi-Truck"
    PASSENGER_CAR = "Passenger Car"
    SUV = "SUV"
    VAN = "Van"


class Coordinates(BaseModel):
    """
    Geographic coordinates for vehicle location.
    
    Attributes:
        lat: Latitude (-90 to 90 degrees)
        long: Longitude (-180 to 180 degrees)
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    lat: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    long: float = Field(..., ge=-180, le=180, description="Longitude in degrees")


class IncidentRequest(BaseModel):
    """
    Request model for incoming incident webhooks.
    
    Attributes:
        incident_id: Unique identifier from external system
        vehicle_coordinates: Geographic location of the vehicle
        vehicle_type: Type of vehicle requiring assistance
        priority_level: Urgency level (High or Standard)
        customer_name: Optional customer name
        customer_phone: Optional contact phone number
        description: Optional incident description
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    incident_id: str = Field(..., min_length=1, description="Unique incident identifier")
    vehicle_coordinates: Coordinates = Field(..., description="Vehicle GPS coordinates")
    vehicle_type: VehicleType = Field(
        ..., 
        examples=["Semi-Truck", "Passenger Car", "SUV", "Van"]
    )
    priority_level: PriorityLevel = Field(
        ..., 
        examples=["High", "Standard"]
    )
    customer_name: Optional[str] = Field(None, description="Customer name")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    description: Optional[str] = Field(None, description="Incident description")


class IncidentResponse(BaseModel):
    """
    Response model for incident webhook acknowledgments.
    
    Attributes:
        incident_id: The processed incident identifier
        status: Processing status (processed, error)
        message: Human-readable response message
    """
    incident_id: str = Field(..., description="Incident identifier")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Response message")
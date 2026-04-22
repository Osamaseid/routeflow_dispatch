"""
Logging and persistence utilities for the RouteFlow Dispatch API.

Handles:
- Incident logging with priority-based output formatting
- JSON file persistence for incidents and queues
"""

import json
import os
from typing import Any, List, Dict, Optional

from models import PriorityLevel

# File paths for data persistence
DATA_FILE: str = "data/incidents.json"
QUEUE_FILE: str = "data/queue.json"


def _read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Read and parse a JSON file, returning an empty list if invalid.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        List of parsed JSON objects
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content: str = f.read().strip()
            return json.loads(content) if content else []
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _write_json_file(file_path: str, data: List[Dict[str, Any]]) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: List of objects to serialize
    """
    os.makedirs(os.path.dirname(file_path) or "data", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def save_incident(incident: Dict[str, Any]) -> None:
    """
    Save an incident to the persistence file.
    
    Args:
        incident: Dictionary containing incident data
    """
    incidents: List[Dict[str, Any]] = _read_json_file(DATA_FILE)
    incidents.append(incident)
    _write_json_file(DATA_FILE, incidents)


def save_to_queue(incident: Dict[str, Any]) -> None:
    """
    Add a standard priority incident to the processing queue.
    
    Args:
        incident: Dictionary containing incident data
    """
    queue: List[Dict[str, Any]] = _read_json_file(QUEUE_FILE)
    queue.append(incident)
    _write_json_file(QUEUE_FILE, queue)


def route_incident(incident: Dict[str, Any]) -> None:
    """
    Log and route an incident based on its priority level.
    
    High priority incidents are logged with high visibility formatting.
    Standard priority incidents are logged to the queue.
    
    Args:
        incident: Dictionary containing:
            - incident_id: Unique identifier
            - vehicle_type: Type of vehicle
            - vehicle_coordinates: Dict with lat/long
            - priority_level: PriorityLevel enum value
    """
    priority: PriorityLevel = incident.get("priority_level", PriorityLevel.STANDARD)
    vehicle_type: str = incident.get("vehicle_type", "Unknown")
    coords: Dict[str, float] = incident.get("vehicle_coordinates", {})
    incident_id: str = incident.get("incident_id", "UNKNOWN")
    
    lat: float = coords.get("lat", 0.0)
    long: float = coords.get("long", 0.0)
    
    if priority == PriorityLevel.HIGH:
        print("\n" + "=" * 50)
        print("!!! HIGH PRIORITY ALERT !!!")
        print("=" * 50)
        print(f"Incident ID: {incident_id}")
        print(f"Vehicle Type: {vehicle_type}")
        print(f"  Location: ({lat}, {long})")
        if "Semi" in vehicle_type or "semi" in vehicle_type:
            print(f"  Commercial Vehicle: {vehicle_type} - Commercial tow required")
        elif vehicle_type in ["Passenger Car", "SUV", "Van"]:
            print(f"  Passenger Vehicle: {vehicle_type} - Standard tow unit assigned")
        else:
            print(f"  Classification: {vehicle_type}")
        print("Status: IMMEDIATE DISPATCH REQUIRED")
        print("Action: Notifying all available drivers...")
        print("=" * 50 + "\n")
    else:
        print(f"[QUEUE] Incident {incident_id} queued for processing")
        print(f"  Vehicle Type: {vehicle_type}")
        if "Semi" in vehicle_type or "semi" in vehicle_type:
            print(f"  Commercial: Heavy-duty tow requested | Location: ({lat}, {long})")
        elif vehicle_type in ["Passenger Car", "SUV", "Van"]:
            print(f"  Passenger: Standard tow unit available | Location: ({lat}, {long})")
        else:
            print(f"  Location: ({lat}, {long})")
        print("  Status: Pending dispatch\n")
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, Extra

class Geometry(BaseModel):
    type: Optional[str] = None
    coordinates: Optional[List[Union[int, float]]] = None
    class Config: extra = Extra.allow

class Properties(BaseModel):
    timestamp: Optional[Union[str, int, float]] = None
    speed: Optional[Union[int, float]] = None
    battery_state: Optional[str] = None
    motion: Optional[Union[str, List[str]]] = None
    battery_level: Optional[Union[int, float]] = None
    vertical_accuracy: Optional[Union[int, float]] = None
    horizontal_accuracy: Optional[Union[int, float]] = None
    pauses: Optional[Union[bool, str]] = None
    wifi: Optional[str] = None
    deferred: Optional[Union[bool, str, int]] = None
    significant_change: Optional[Union[bool, str, int]] = None
    locations_in_payload: Optional[int] = None
    activity: Optional[str] = None
    device_id: Optional[str] = None
    altitude: Optional[Union[int, float]] = None
    desired_accuracy: Optional[int] = None
    class Config: extra = Extra.allow

class LocationItem(BaseModel):
    type: Optional[str] = None
    geometry: Optional[Union[Geometry, Dict[str, Any], str]] = None
    properties: Optional[Union[Properties, Dict[str, Any], str]] = None
    class Config: extra = Extra.allow

class IngestPayload(BaseModel):
    user_id: Optional[str] = None
    device_id: Optional[str] = None
    locations: List[Union[LocationItem, Dict[str, Any]]] = Field(default_factory=list)

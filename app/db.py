from typing import Optional, Dict, Any
from neo4j import GraphDatabase, Driver
from .settings import settings

_driver: Optional[Driver] = None

def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver

UPSERT_CYPHER = """MERGE (p:PhoneLog {uid: $uid})
ON CREATE SET
  p.created_at = timestamp(),
  p.schema_version = 1
SET
  p.user_id = $user_id,
  p.device_id = $device_id,
  p.geom_type = $geom_type,
  p.coordinates = $coordinates,
  p.longitude = $longitude,
  p.latitude = $latitude,
  p.timestamp = $timestamp,
  p.epoch_millis = $epoch_millis,
  p.speed = $speed,
  p.battery_state = $battery_state,
  p.motion = $motion,
  p.battery_level = $battery_level,
  p.vertical_accuracy = $vertical_accuracy,
  p.horizontal_accuracy = $horizontal_accuracy,
  p.pauses = $pauses,
  p.wifi = $wifi,
  p.deferred = $deferred,
  p.significant_change = $significant_change,
  p.locations_in_payload = $locations_in_payload,
  p.activity = $activity,
  p.altitude = $altitude,
  p.desired_accuracy = $desired_accuracy,
  p.loc = CASE
            WHEN $latitude IS NOT NULL AND $longitude IS NOT NULL
            THEN point({latitude: toFloat($latitude), longitude: toFloat($longitude), crs: 'wgs-84'})
            ELSE p.loc
          END,
  p.updated_at = timestamp(),
  p.normalized = true
WITH p
FOREACH (_ IN CASE WHEN $user_id IS NOT NULL THEN [1] ELSE [] END |
  MERGE (u:User {id: $user_id})
  MERGE (p)-[:BY_USER]->(u)
)
FOREACH (_ IN CASE WHEN $device_id IS NOT NULL THEN [1] ELSE [] END |
  MERGE (d:Device {id: $device_id})
  MERGE (p)-[:FROM_DEVICE]->(d)
)
RETURN p.uid AS uid
"""

def upsert_phonelog(record: Dict[str, Any]) -> str:
    params = {k: record.get(k) for k in [
        "uid","user_id","device_id","geom_type","coordinates","longitude","latitude",
        "timestamp","epoch_millis","speed","battery_state","motion","battery_level",
        "vertical_accuracy","horizontal_accuracy","pauses","wifi","deferred",
        "significant_change","locations_in_payload","activity","altitude","desired_accuracy"
    ]}
    with get_driver().session(database=settings.NEO4J_DATABASE) as s:
        res = s.run(UPSERT_CYPHER, **params)
        return res.single()["uid"]

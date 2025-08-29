import json, re, hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union

JSON_TRUE_FALSE_NONE = (
    ("'", '"'),
    (" True", " true"),
    (" False", " false"),
    (" None", " null"),
    (": True", ": true"),
    (": False", ": false"),
    (": None", ": null"),
)

def _coerce_to_dict(v: Union[str, Dict[str, Any], None]) -> Optional[Dict[str, Any]]:
    if v is None:
        return None
    if isinstance(v, dict):
        return v
    if isinstance(v, str):
        s = v
        for a, b in JSON_TRUE_FALSE_NONE:
            s = s.replace(a, b)
        s = re.sub(r",\s*}", "}", s)
        s = re.sub(r",\s*]", "]", s)
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None
    return None

def _parse_timestamp(ts: Union[str, int, float, None]) -> Tuple[Optional[str], Optional[int]]:
    if ts is None:
        return None, None
    try:
        if isinstance(ts, (int, float)):
            millis = int(ts if ts > 10_000_000_000 else ts * 1000)
            dt = datetime.fromtimestamp(millis / 1000, tz=timezone.utc)
            return dt.isoformat(), millis
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat(), int(dt.timestamp() * 1000)
    except Exception:
        return None, None

def normalize_one(raw_item: Dict[str, Any], default_user: str, default_device: Optional[str]) -> Optional[Dict[str, Any]]:
    geom = _coerce_to_dict(raw_item.get("geometry"))
    props = _coerce_to_dict(raw_item.get("properties"))

    lon = lat = None
    if geom and isinstance(geom.get("coordinates"), (list, tuple)) and len(geom["coordinates"]) >= 2:
        try:
            lon = float(geom["coordinates"][0])
            lat = float(geom["coordinates"][1])
        except Exception:
            lon = lat = None

    ts_iso, epoch_millis = _parse_timestamp(props.get("timestamp") if props else None)

    user_id   = raw_item.get("user_id") or (props.get("user_id") if props else None) or default_user
    device_id = raw_item.get("device_id") or (props.get("device_id") if props else None) or default_device

    uid_source = f"{user_id}|{device_id}|{epoch_millis or ''}|{lon or ''}|{lat or ''}"
    uid = hashlib.sha1(uid_source.encode("utf-8")).hexdigest()

    out = {
        "uid": uid,
        "user_id": user_id,
        "device_id": device_id,
        "geom_type": (geom or {}).get("type"),
        "coordinates": (geom or {}).get("coordinates"),
        "longitude": lon,
        "latitude": lat,
        "timestamp": ts_iso,
        "epoch_millis": epoch_millis,
        "speed": (props or {}).get("speed"),
        "battery_state": (props or {}).get("battery_state"),
        "motion": (props or {}).get("motion"),
        "battery_level": (props or {}).get("battery_level"),
        "vertical_accuracy": (props or {}).get("vertical_accuracy"),
        "horizontal_accuracy": (props or {}).get("horizontal_accuracy"),
        "pauses": (props or {}).get("pauses"),
        "wifi": (props or {}).get("wifi"),
        "deferred": (props or {}).get("deferred"),
        "significant_change": (props or {}).get("significant_change"),
        "locations_in_payload": (props or {}).get("locations_in_payload"),
        "activity": (props or {}).get("activity"),
        "device_id_prop": (props or {}).get("device_id"),
        "altitude": (props or {}).get("altitude"),
        "desired_accuracy": (props or {}).get("desired_accuracy"),
        "raw_item": raw_item,
    }

    if epoch_millis is None or lon is None or lat is None:
        return None
    return out

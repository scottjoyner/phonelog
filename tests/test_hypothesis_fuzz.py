import json, random, string
from hypothesis import given, strategies as st, settings
from .utils import post_json

def py_stringify(d: dict) -> str:
    s = str(d)
    s = s.replace("True","True").replace("False","False").replace("None","None")
    return s

def coord_strategy():
    num = st.floats(min_value=-179.9999, max_value=179.9999, allow_nan=False, allow_infinity=False)
    return st.tuples(num, st.floats(min_value=-89.9999, max_value=89.9999, allow_nan=False, allow_infinity=False))

geom_dict = st.fixed_dictionaries({
    "type": st.just("Point"),
    "coordinates": coord_strategy().map(lambda t: [t[0], t[1]])
})

props_dict = st.fixed_dictionaries({
    "timestamp": st.one_of(
        st.dates().map(lambda d: f"{d}T12:00:00Z"),
        st.integers(min_value=1_600_000_000, max_value=2_000_000_000),
        st.floats(min_value=1_600_000_000, max_value=2_000_000_000)
    ),
    "speed": st.one_of(st.none(), st.floats(min_value=0, max_value=50))
}).filter(lambda d: True)

geom_strategy = st.one_of(geom_dict, geom_dict.map(py_stringify))
props_strategy = st.one_of(props_dict, props_dict.map(py_stringify))

item_strategy = st.fixed_dictionaries({
    "type": st.just("Feature"),
    "geometry": geom_strategy,
    "properties": props_strategy
})

payload_strategy = st.fixed_dictionaries({
    "user_id": st.just("kipnerter"),
    "device_id": st.just("hypothesis-device"),
    "locations": st.lists(item_strategy, min_size=1, max_size=20)
})

@settings(max_examples=25, deadline=None)
@given(payload_strategy)
def test_property_based_inputs(base_url, payload):
    status, rid, js = post_json(base_url, "/api/v1/locations", payload)
    assert status in (200, 400), js  # 400 when all invalid
    if status == 200:
        assert js.get("ingested", 0) >= 1

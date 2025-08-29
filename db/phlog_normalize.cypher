WITH 500 AS batchSize, 1 AS SCHEMA_VERSION
CALL apoc.periodic.iterate(
  '
  MATCH (n:PhoneLog)
  WHERE coalesce(n.normalized,false) = false OR coalesce(n.schema_version,0) < $SCHEMA_VERSION
  RETURN n
  ',
  '
  WITH n, n.properties AS props, n.geometry AS geom
  WITH n,
       replace(replace(replace(replace(geom, "\'", "\\\""), "True", "true"), "False", "false"), "None", "null") AS geomStr,
       replace(replace(replace(replace(props, "\'", "\\\""), "True", "true"), "False", "false"), "None", "null") AS propsStr

  WITH n,
       CASE WHEN geomStr IS NOT NULL AND geomStr STARTS WITH "{" THEN apoc.convert.fromJsonMap(geomStr) END AS geomMap,
       CASE WHEN propsStr IS NOT NULL AND propsStr STARTS WITH "{" THEN apoc.convert.fromJsonMap(propsStr) END AS propMap

  WITH n, geomMap, propMap,
       CASE WHEN geomMap IS NOT NULL THEN geomMap.coordinates END AS coords

  SET n.geom_type  = CASE WHEN geomMap IS NOT NULL THEN geomMap.type ELSE n.geom_type END,
      n.coordinates = CASE WHEN coords IS NOT NULL THEN coords ELSE n.coordinates END,
      n.longitude   = CASE WHEN coords IS NOT NULL THEN toFloat(coords[0]) ELSE n.longitude END,
      n.latitude    = CASE WHEN coords IS NOT NULL THEN toFloat(coords[1]) ELSE n.latitude END,

      n.speed               = CASE WHEN propMap IS NOT NULL THEN toFloat(propMap.speed)               ELSE n.speed END,
      n.battery_state       = CASE WHEN propMap IS NOT NULL THEN propMap.battery_state               ELSE n.battery_state END,
      n.motion              = CASE WHEN propMap IS NOT NULL THEN propMap.motion                       ELSE n.motion END,
      n.timestamp           = CASE WHEN propMap IS NOT NULL THEN propMap.timestamp                    ELSE n.timestamp END,
      n.battery_level       = CASE WHEN propMap IS NOT NULL THEN toFloat(propMap.battery_level)       ELSE n.battery_level END,
      n.vertical_accuracy   = CASE WHEN propMap IS NOT NULL THEN toFloat(propMap.vertical_accuracy)   ELSE n.vertical_accuracy END,
      n.horizontal_accuracy = CASE WHEN propMap IS NOT NULL THEN toFloat(propMap.horizontal_accuracy) ELSE n.horizontal_accuracy END,
      n.pauses              = CASE WHEN propMap IS NOT NULL THEN apoc.convert.toBoolean(propMap.pauses)      ELSE n.pauses END,
      n.wifi                = CASE WHEN propMap IS NOT NULL THEN propMap.wifi                         ELSE n.wifi END,
      n.deferred            = CASE WHEN propMap IS NOT NULL THEN apoc.convert.toBoolean(propMap.deferred)    ELSE n.deferred END,
      n.significant_change  = CASE WHEN propMap IS NOT NULL THEN apoc.convert.toBoolean(propMap.significant_change) ELSE n.significant_change END,
      n.locations_in_payload= CASE WHEN propMap IS NOT NULL THEN toInteger(propMap.locations_in_payload) ELSE n.locations_in_payload END,
      n.activity            = CASE WHEN propMap IS NOT NULL THEN propMap.activity                     ELSE n.activity END,
      n.device_id           = CASE WHEN propMap IS NOT NULL THEN propMap.device_id                    ELSE n.device_id END,
      n.altitude            = CASE WHEN propMap IS NOT NULL THEN toFloat(propMap.altitude)            ELSE n.altitude END,
      n.desired_accuracy    = CASE WHEN propMap IS NOT NULL THEN toInteger(propMap.desired_accuracy)  ELSE n.desired_accuracy END

  WITH n
  SET n.loc = CASE
                WHEN n.latitude IS NOT NULL AND n.longitude IS NOT NULL
                THEN point({latitude: n.latitude, longitude: n.longitude, crs: "wgs-84"})
                ELSE n.loc
              END
  WITH n, CASE WHEN n.timestamp IS NOT NULL THEN datetime(n.timestamp) END AS ts
  SET n.ts = CASE WHEN ts IS NOT NULL THEN ts ELSE n.ts END,
      n.epoch_millis = CASE WHEN ts IS NOT NULL THEN ts.epochMillis ELSE n.epoch_millis END,
      n.schema_version = $SCHEMA_VERSION,
      n.normalized = true
  RETURN count(*)
  ',
  {batchSize: batchSize, parallel: false, params: {SCHEMA_VERSION: SCHEMA_VERSION}}
)
YIELD batches, total, errorMessages
RETURN batches, total, errorMessages;

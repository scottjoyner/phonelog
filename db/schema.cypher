CREATE CONSTRAINT phone_uid IF NOT EXISTS FOR (p:PhoneLog) REQUIRE p.uid IS UNIQUE;
CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT device_id IF NOT EXISTS FOR (d:Device) REQUIRE d.id IS UNIQUE;
CREATE INDEX phone_ts IF NOT EXISTS FOR (p:PhoneLog) ON (p.timestamp);
CREATE INDEX phone_epoch IF NOT EXISTS FOR (p:PhoneLog) ON (p.epoch_millis);
CREATE INDEX phone_user IF NOT EXISTS FOR (p:PhoneLog) ON (p.user_id);
CREATE INDEX phone_device IF NOT EXISTS FOR (p:PhoneLog) ON (p.device_id);
CREATE INDEX phone_loc IF NOT EXISTS FOR (p:PhoneLog) ON (p.loc);

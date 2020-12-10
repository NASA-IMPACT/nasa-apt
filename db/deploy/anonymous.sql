-- Deploy nasa-apt:anonymous to pg

BEGIN;
--create role if not anonymous noinherit;
grant anonymous to masteruser;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA apt FROM anonymous;
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA apt FROM anonymous;
GRANT SELECT ON ALL TABLES IN SCHEMA apt TO anonymous;
GRANT USAGE ON SCHEMA apt TO anonymous;
GRANT EXECUTE ON FUNCTION apt.search_text TO anonymous;

ALTER TABLE  apt.atbd_versions ENABLE ROW LEVEL SECURITY;

CREATE POLICY anon ON apt.atbd_versions TO anonymous
 USING (status='Published');


GRANT ALL ON SCHEMA apt to app_user;
GRANT ALL ON ALL TABLES IN SCHEMA apt TO app_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA apt TO app_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA apt TO app_user;
CREATE POLICY appuser ON apt.atbd_versions TO app_user USING (true);
COMMIT;

CREATE ROLE app_user;
GRANT app_user TO masteruser;
DROP SCHEMA apt CASCADE;
CREATE SCHEMA apt;
GRANT USAGE ON SCHEMA apt TO app_user;
GRANT CONNECT ON DATABASE nasadb TO app_user;
GRANT USAGE ON SCHEMA apt TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA apt TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA apt TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA apt GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA apt GRANT USAGE, SELECT ON SEQUENCES TO app_user;
-- SET SCHEMA 'apt';

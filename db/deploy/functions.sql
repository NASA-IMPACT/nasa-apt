-- Deploy nasa-apt:functions to pg
-- requires: tables

CREATE FUNCTION apt.copy_atbd_version(val integer, OUT created_atbd apt.atbds, OUT created_version apt.atbd_versions)
 AS $$
  BEGIN
  INSERT INTO apt.atbds(title) select title from apt.atbds where atbd_id = val RETURNING * INTO created_atbd;
  INSERT INTO apt.atbd_versions(
	atbd_id, 
	atbd_version,
    status,
	scientific_theory,
    scientific_theory_assumptions,
    mathematical_theory,
    mathematical_theory_assumptions,
    introduction,
    historical_perspective,
    performance_assessment_validation_methods,
    performance_assessment_validation_uncertainties,
    performance_assessment_validation_errors,
    algorithm_usage_constraints)
  	SELECT
		created_atbd.atbd_id, 1, 'Draft',
		scientific_theory,
	    scientific_theory_assumptions,
	    mathematical_theory,
	    mathematical_theory_assumptions,
	    introduction,
	    historical_perspective,
	    performance_assessment_validation_methods,
	    performance_assessment_validation_uncertainties,
	    performance_assessment_validation_errors,
	    algorithm_usage_constraints
    FROM apt.atbd_versions where atbd_id = val
	RETURNING * INTO created_version;
  END; $$
LANGUAGE PLPGSQL;


BEGIN;
CREATE FUNCTION apt.create_atbd_version(OUT created_atbd apt.atbds, OUT created_version apt.atbd_versions)
  AS $$
  DECLARE
  BEGIN
  INSERT INTO apt.atbds(title) VALUES ('') RETURNING * INTO created_atbd;
  INSERT INTO apt.atbd_versions(atbd_id, atbd_version)
  VALUES (created_atbd.atbd_id, 1) RETURNING * INTO created_version;
  END;
  $$ LANGUAGE plpgsql
  VOLATILE;
COMMIT;

-- initial SQL for pg_trgm initialization
-- when using south (initial SQL is not run),
-- this is handled by 0002 schema migration
CREATE EXTENSION pg_trgm;
CREATE INDEX descripcion_trgm_idx ON precios_producto USING gist (descripcion gist_trgm_ops);
CREATE INDEX busqueda_trgm_idx ON precios_producto USING gist (busqueda gist_trgm_ops);

from django.db import migrations

APP_TABLE = "planners_addresscache"  # ← remplace par AddressCache._meta.db_table

SQL_CREATE = f"""
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS addresscache_name_trgm_idx
  ON {APP_TABLE} USING gin (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS addresscache_addr_trgm_idx
  ON {APP_TABLE} USING gin (formatted_address gin_trgm_ops);
"""

SQL_DROP = f"""
DROP INDEX IF EXISTS addresscache_name_trgm_idx;
DROP INDEX IF EXISTS addresscache_addr_trgm_idx;
-- (ne pas dropper l'extension en reverse, sauf besoin spécifique)
"""

class Migration(migrations.Migration):
    dependencies = [
        ("planners", "0008_rename_latitude_addresscache_lat_and_more"),
    ]
    # Si tu veux créer les index "CONCURRENTLY" en prod (gros volumes),
    # ajoute: atomic = False et remplace CREATE INDEX par CREATE INDEX CONCURRENTLY
    # atomic = False
    operations = [
        migrations.RunSQL(SQL_CREATE, SQL_DROP),
    ]

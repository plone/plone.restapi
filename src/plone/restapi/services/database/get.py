from plone.restapi.services import Service


class DatabaseGet(Service):
    def reply(self):
        db = self.context._p_jar.db()
        return {
            "@id": f"{self.context.absolute_url()}/@database",
            "cache_length": db.cacheSize(),
            "cache_length_bytes": db.getCacheSizeBytes(),
            "cache_detail_length": db.cacheDetailSize(),
            "cache_size": db.getCacheSize(),
            "database_size": db.objectCount(),
            "db_name": db.getName(),
            "db_size": db.getSize(),
        }

# -*- coding: utf-8 -*-
from plone.restapi.services import Service

from pathlib import Path

class DatabaseGet(Service):
    def reply(self):
        db = self.context._p_jar.db()
        blobstorage_size_in_mb = 0
        # test database has no fshelper attr, so we bail out here
        if hasattr(db._storage, "fshelper"):
            base_dir = db._storage.fshelper.base_dir
            root_directory = Path(base_dir)
            blobstorage_size_in_bytes = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())
            blobstorage_size_in_mb = (blobstorage_size_in_bytes/float(1<<20))
        return {
            "@id": "{}/@database".format(self.context.absolute_url()),
            "cache_length": db.cacheSize(),
            "cache_length_bytes": db.getCacheSizeBytes(),
            "cache_detail_length": db.cacheDetailSize(),
            "cache_size": db.getCacheSize(),
            "database_size": db.objectCount(),
            "blobstorage_size": blobstorage_size_in_mb,
            "db_name": db.getName(),
            "db_size": db.getSize(),
        }

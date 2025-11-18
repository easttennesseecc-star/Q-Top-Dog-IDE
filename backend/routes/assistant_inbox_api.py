"""DEPRECATED: Assistant Inbox API

This module is retained only as a stub for backward compatibility. The
assistant inbox has been replaced by the file-based spool ingestion system
(`spool_ingest_api` + `spool_dropbox`).

All former endpoints under `/assistant-inbox/*` have been retired. Tests
referencing them are skipped. Importing this module intentionally raises an
ImportError to prevent accidental usage.
"""

raise ImportError("assistant_inbox_api is deprecated; use /spool/* endpoints")

# Duplicate source audit

Local files use `source_key = file:<sha256>`, so identical content under another filename resolves to the same source identity. YouTube uses the canonical video ID in the existing URL path. The new-file processing report records duplicate decisions and existing IDs when applicable.

Historical storage still contains legacy records with incomplete IDs and duplicate source groups; those records were not rewritten automatically.

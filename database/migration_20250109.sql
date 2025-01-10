CREATE TYPE feedback AS ENUM ('unspecified', 'like', 'dislike');

ALTER TABLE IF EXISTS requests
    ADD COLUMN IF NOT EXISTS feedback feedback NOT NULL DEFAULT 'unspecified';

CREATE INDEX IF NOT EXISTS requests_feedback ON requests (feedback);
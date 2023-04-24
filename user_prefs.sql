CREATE TABLE IF NOT EXISTS user_prefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zulip_email TEXT NOT NULL,
    text_string TEXT NOT NULL,
    UNIQUE (zulip_email, text_string)
);

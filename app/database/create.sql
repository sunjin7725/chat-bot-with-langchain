CREATE chat (
    id SERIAL primary key,
    session_id text,
    username varchar(200),
    ip varchar(200),
    role varchar(200),
    content text,
    create_datetime timestamp
)
;
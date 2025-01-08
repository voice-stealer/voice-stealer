create type status as enum ('unspecified', 'pending', 'in_progress', 'done', 'failed');

create table if not exists users
(
    id       serial unique primary key not null,
    name     character varying unique  not null,
    password character varying         not null
);

create table if not exists speakers
(
    id      serial unique primary key not null,
    name    character varying         not null,
    user_id integer                   not null,
    foreign key (user_id) references users (id)
);

create index if not exists speakers_user_id on speakers (user_id);
create index if not exists speakers_name on speakers (name);

create table if not exists requests
(
    id         character varying unique not null,
    user_id    integer                  not null,
    speaker_id integer                  not null,
    status     status                   not null,
    foreign key (user_id) references users (id),
    foreign key (speaker_id) references speakers (id)
);

create index if not exists requests_status on requests (status);

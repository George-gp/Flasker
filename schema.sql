drop table if exists entries;
create table entried(
id INTEGER PRIMARY key autoincrement,
title string not null,
text string not null
);
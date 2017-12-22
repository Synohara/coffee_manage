drop table if exists coffee_manage;
create table coffee_manage (
  id integer primary key autoincrement,
  username string not null,
  coffee_num integer
);

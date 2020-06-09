drop table if exists threads;
create table threads(
	tid integer primary key autoincrement,
	title varchar not null,
	uid integer,
	username varchar,
	replies integer,
	views integer,
	displayorder integer,
	dateline integer,
	lastpost integer,
	lastpostuser varchar,
	ip varchar,
	attachment integer
);

drop table if exists posts;
create table posts (
	pid integer primary key autoincrement,
	tid integer,
	uid integer,
	username varchar,
	content text not null,
	floor integer,
	displayorder integer,
	dateline integer,
	ip varchar,
	attachment integer
);

drop table if exists attachments;
create table attachments (
	aid integer primary key autoincrement,
	tid integer,
	pid integer,
	uid integer,
	dateline integer,
	filename varchar,
	filesize integer,
	attachment varchar,
	downloads integer,
	isimage integer,
	width integer,
	thumb integer
);

drop table if exists users;
create table users (
	uid integer primary key autoincrement,
	username varchar not null COLLATE NOCASE,
	password varchar not null,
	groupid integer,
	email varchar not null COLLATE NOCASE,
	gender integer,
	regip varchar,
	lastloginip varchar,
	regdate integer,
	lastlogintime integer,
	salt integer
);

drop table if exists userfields;
create table userfields (
	uid integer,
	face varchar not null,
	sightml varchar not null,
	activate varchar not null
);

drop table if exists invites;
create table invites (
	iid integer primary key autoincrement,
	invite varchar not null,
	username varchar not null,
	comment varchar not null,
	createtime integer,
	usedtime integer
);

drop table if exists chat_msg;
create table chat_msg (
	mid integer primary key autoincrement,
	username varchar not null,
	msg text not null,
	dateline integer
);
	
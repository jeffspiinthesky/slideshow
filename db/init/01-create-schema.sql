use pictureframe;
create table pictures (id int primary key auto_increment, name varchar(2048));
CREATE TABLE picture_order (picture_id int NOT NULL, picture_order int NOT NULL, FOREIGN KEY (picture_id) REFERENCES pictures(id));
create table settings (key_name varchar(2048) NOT NULL, key_value int NOT NULL default 0);

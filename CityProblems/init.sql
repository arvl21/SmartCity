CREATE TABLE IF NOT EXISTS `Request` (
	`request_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`problem_id` int NOT NULL,
	`descr` text NOT NULL,
	`descr_long` text,
	`address` varchar(255) NOT NULL,
	`latitude` decimal(10,0) NOT NULL,
	`longitude` decimal(10,0) NOT NULL,
	`user_id` int NOT NULL DEFAULT '1',
	`status_id` int NOT NULL DEFAULT '1',
	`date_created` datetime NOT NULL,
	`date_solved` datetime,
	`commentary` varchar(255),
	PRIMARY KEY (`request_id`)
);

CREATE TABLE IF NOT EXISTS `Request_photos` (
	`photo_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`request_id` int NOT NULL,
	`file_path` varchar(255) NOT NULL UNIQUE,
	PRIMARY KEY (`photo_id`)
);

CREATE TABLE IF NOT EXISTS `AppUser` (
	`user_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`name` varchar(150) NOT NULL,
	`surname` varchar(150) NOT NULL,
	`email` VARCHAR(255) UNIQUE NOT NULL,
	`password_hash` VARCHAR(255),
	`is_admin` binary(1) NOT NULL DEFAULT FALSE,
	PRIMARY KEY (`user_id`)
);

CREATE TABLE IF NOT EXISTS `Status` (
	`status_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`status_name` varchar(200) NOT NULL,
	PRIMARY KEY (`status_id`)
);

CREATE TABLE IF NOT EXISTS `Problem` (
	`problem_id` int AUTO_INCREMENT NOT NULL UNIQUE,
	`problem_name` varchar(200) NOT NULL,
	PRIMARY KEY (`problem_id`)
);

ALTER TABLE `Request` ADD CONSTRAINT `Request_problem_fk1` FOREIGN KEY (`problem_id`) REFERENCES `Problem`(`problem_id`) ON DELETE SET DEFAULT;
ALTER TABLE `Request` ADD CONSTRAINT `Request_fk7` FOREIGN KEY (`user_id`) REFERENCES `AppUser`(`user_id`) ON DELETE SET DEFAULT;
ALTER TABLE `Request` ADD CONSTRAINT `Request_fk8` FOREIGN KEY (`status_id`) REFERENCES `Status`(`status_id`) ON DELETE SET DEFAULT;
ALTER TABLE `Request_photos` ADD CONSTRAINT `Request_photos_fk1` FOREIGN KEY (`request_id`) REFERENCES `Request`(`request_id`) ON DELETE CASCADE;

INSERT INTO Status (status_name) 
VALUES ('новая проблема'),
('в обработке'), 
('решена');

INSERT INTO Problem (problem_name)
VALUES ('яма на дороге'),
('мусор'),
('неработающее освещение'),
('другое');
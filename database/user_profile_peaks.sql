CREATE TABLE `user_profile_peaks` (
  `user_id` int NOT NULL,
  `mode` int NOT NULL,
  `rank` int NOT NULL,
  `achieved_at` datetime NOT NULL,
  PRIMARY KEY (`user_id`,`mode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

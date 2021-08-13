-- phpMyAdmin SQL Dump
-- version 5.0.4deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 13, 2021 at 01:20 PM
-- Server version: 10.5.11-MariaDB-1
-- PHP Version: 7.4.21

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `bank`
--

-- --------------------------------------------------------

--
-- Table structure for table `bank_chat_groups`
--

CREATE TABLE `bank_chat_groups` (
  `id` int(10) UNSIGNED NOT NULL,
  `date` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bank_chat_groups`
--

INSERT INTO `bank_chat_groups` (`id`, `date`) VALUES
(1, 1628872352),
(2, 0);

-- --------------------------------------------------------

--
-- Table structure for table `bank_chat_group_users`
--

CREATE TABLE `bank_chat_group_users` (
  `id` int(10) UNSIGNED NOT NULL,
  `group_id` int(10) UNSIGNED NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `is_owner` tinyint(1) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bank_chat_group_users`
--

INSERT INTO `bank_chat_group_users` (`id`, `group_id`, `user_id`, `is_owner`) VALUES
(1, 1, 1, 1),
(2, 1, 2, 0);

-- --------------------------------------------------------

--
-- Table structure for table `bank_chat_messages`
--

CREATE TABLE `bank_chat_messages` (
  `id` int(10) UNSIGNED NOT NULL,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `message` varchar(255) NOT NULL,
  `date` int(11) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bank_chat_messages`
--

INSERT INTO `bank_chat_messages` (`id`, `group_id`, `user_id`, `message`, `date`) VALUES
(1, 1, NULL, 'Conversation created.', 1628872352);

-- --------------------------------------------------------

--
-- Table structure for table `bank_log`
--

CREATE TABLE `bank_log` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `type` tinyint(1) UNSIGNED NOT NULL DEFAULT 0,
  `date` int(10) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bank_log`
--

INSERT INTO `bank_log` (`id`, `user_id`, `type`, `date`) VALUES
(1, 1, 1, 1628662819),
(2, 1, 0, 1628662823),
(3, 1, 1, 1628663050),
(4, 1, 1, 1628663050),
(5, 1, 0, 1628663054),
(6, 2, 1, 1628663079),
(7, 2, 0, 1628663081),
(8, 1, 1, 1628695188),
(9, 2, 1, 1628695188),
(10, 1, 1, 1628695188),
(11, 1, 0, 1628695191),
(12, 2, 1, 1628695206),
(13, 2, 0, 1628695209),
(14, 1, 1, 1628788536),
(15, 2, 1, 1628788536),
(16, 1, 1, 1628788536),
(17, 1, 0, 1628788591),
(18, 1, 1, 1628789543),
(19, 1, 1, 1628789543),
(20, 1, 0, 1628789547),
(21, 1, 1, 1628790109),
(22, 1, 1, 1628791309),
(23, 1, 0, 1628791312),
(24, 1, 1, 1628805472),
(25, 1, 1, 1628805472),
(26, 1, 0, 1628805476),
(27, 1, 1, 1628805661),
(28, 1, 1, 1628805661),
(29, 1, 0, 1628805665),
(30, 1, 1, 1628812846),
(31, 1, 1, 1628812846),
(32, 1, 0, 1628812899),
(33, 1, 1, 1628862888),
(34, 1, 1, 1628862888),
(35, 1, 0, 1628862890),
(36, 1, 1, 1628863162),
(37, 1, 1, 1628863162),
(38, 1, 0, 1628863168),
(39, 1, 1, 1628866527),
(40, 1, 1, 1628866527),
(41, 1, 0, 1628866530),
(42, 1, 1, 1628866654),
(43, 1, 1, 1628866654),
(44, 1, 0, 1628866657),
(45, 1, 1, 1628867545),
(46, 1, 1, 1628867545),
(47, 1, 0, 1628867548),
(48, 1, 1, 1628868381),
(49, 1, 1, 1628868381),
(50, 1, 0, 1628868384),
(51, 1, 1, 1628869496),
(52, 1, 1, 1628869496),
(53, 1, 0, 1628869499),
(54, 1, 1, 1628871529),
(55, 1, 1, 1628871529),
(56, 1, 0, 1628871996),
(57, 1, 1, 1628875023),
(58, 1, 1, 1628875023),
(59, 1, 0, 1628875025),
(60, 1, 1, 1628875062),
(61, 1, 0, 1628875065),
(62, 1, 1, 1628875577),
(63, 1, 1, 1628875577),
(64, 1, 0, 1628875580),
(65, 1, 1, 1628876515),
(66, 1, 1, 1628876515),
(67, 1, 0, 1628876518),
(68, 1, 1, 1628877033),
(69, 1, 1, 1628877033),
(70, 1, 0, 1628877036),
(71, 1, 1, 1628877356),
(72, 1, 1, 1628877356),
(73, 1, 0, 1628877359),
(74, 1, 1, 1628878501),
(75, 1, 1, 1628878501),
(76, 1, 0, 1628878504);

-- --------------------------------------------------------

--
-- Table structure for table `bank_transfers`
--

CREATE TABLE `bank_transfers` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `amount` double UNSIGNED NOT NULL,
  `balance` double UNSIGNED NOT NULL,
  `to_balance` double UNSIGNED DEFAULT NULL,
  `to_user_id` int(11) DEFAULT NULL,
  `reason` varchar(255) DEFAULT NULL,
  `type` tinyint(1) NOT NULL DEFAULT 0,
  `date` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bank_users`
--

CREATE TABLE `bank_users` (
  `id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `salt` varchar(88) NOT NULL,
  `balance` double UNSIGNED NOT NULL DEFAULT 0,
  `last_activity` int(10) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `bank_users`
--

INSERT INTO `bank_users` (`id`, `username`, `password`, `salt`, `balance`, `last_activity`) VALUES
(1, 'test', '7qnLcWebmLI2y9rDz3aat8K81WSZAXHQkcFXboHRu+06g6Y5E51CbwaMSFCP+t2gjWiyRPhS2w22mvyUgyz84g==', '5zjIVwhnQkU5yl2w0snzaKncrbtJgm588xmkBV3dT5ZREHvcW6y/F3HQ12J26pFT6CLl7hC02qRa0deeybH/8w==', 100, 1628878675),
(2, 'test2', '7qnLcWebmLI2y9rDz3aat8K81WSZAXHQkcFXboHRu+06g6Y5E51CbwaMSFCP+t2gjWiyRPhS2w22mvyUgyz84g==', '5zjIVwhnQkU5yl2w0snzaKncrbtJgm588xmkBV3dT5ZREHvcW6y/F3HQ12J26pFT6CLl7hC02qRa0deeybH/8w==', 0, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bank_chat_groups`
--
ALTER TABLE `bank_chat_groups`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bank_chat_group_users`
--
ALTER TABLE `bank_chat_group_users`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bank_chat_messages`
--
ALTER TABLE `bank_chat_messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bank_log`
--
ALTER TABLE `bank_log`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `bank_transfers`
--
ALTER TABLE `bank_transfers`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_index` (`user_id`);

--
-- Indexes for table `bank_users`
--
ALTER TABLE `bank_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bank_chat_groups`
--
ALTER TABLE `bank_chat_groups`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `bank_chat_group_users`
--
ALTER TABLE `bank_chat_group_users`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `bank_chat_messages`
--
ALTER TABLE `bank_chat_messages`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `bank_log`
--
ALTER TABLE `bank_log`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT for table `bank_transfers`
--
ALTER TABLE `bank_transfers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bank_users`
--
ALTER TABLE `bank_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

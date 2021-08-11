-- phpMyAdmin SQL Dump
-- version 5.0.4deb2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Aug 11, 2021 at 01:12 AM
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
-- Table structure for table `bank_log`
--

CREATE TABLE `bank_log` (
  `id` int(10) UNSIGNED NOT NULL,
  `user_id` int(10) UNSIGNED NOT NULL,
  `type` tinyint(1) UNSIGNED NOT NULL DEFAULT 0,
  `date` int(10) UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

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
(1, 'test', '7qnLcWebmLI2y9rDz3aat8K81WSZAXHQkcFXboHRu+06g6Y5E51CbwaMSFCP+t2gjWiyRPhS2w22mvyUgyz84g==', '5zjIVwhnQkU5yl2w0snzaKncrbtJgm588xmkBV3dT5ZREHvcW6y/F3HQ12J26pFT6CLl7hC02qRa0deeybH/8w==', 100, 0),
(2, 'test2', '7qnLcWebmLI2y9rDz3aat8K81WSZAXHQkcFXboHRu+06g6Y5E51CbwaMSFCP+t2gjWiyRPhS2w22mvyUgyz84g==', '5zjIVwhnQkU5yl2w0snzaKncrbtJgm588xmkBV3dT5ZREHvcW6y/F3HQ12J26pFT6CLl7hC02qRa0deeybH/8w==', 0, 0);

--
-- Indexes for dumped tables
--

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
-- AUTO_INCREMENT for table `bank_log`
--
ALTER TABLE `bank_log`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;

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

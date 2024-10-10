-- init_event_bot.sql

-- Создание базы данных server
CREATE DATABASE IF NOT EXISTS server;

-- Использование базы данных server
USE server;

-- Создание таблицы event
CREATE TABLE IF NOT EXISTS event (
    id BIGINT PRIMARY KEY,
    description VARCHAR(255) NOT NULL
);
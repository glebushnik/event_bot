-- Создание базы данных server
CREATE DATABASE IF NOT EXISTS event_bot;

-- Использование базы данных server
USE event_bot;

-- Создание таблицы event
CREATE TABLE IF NOT EXISTS event (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,  -- Автоинкрементный идентификатор
    event_name VARCHAR(255) NOT NULL,      -- Название мероприятия
    event_date VARCHAR(255) NOT NULL,      -- Дата и время мероприятия (в формате строки)
    event_style VARCHAR(50) NOT NULL,      -- Формат мероприятия (онлайн/офлайн/вебинар)
    event_location VARCHAR(255),            -- Местоположение (адрес или ссылка)
    event_description VARCHAR(500),         -- Описание мероприятия
    event_contacts VARCHAR(255),            -- Контактная информация (имя, email или телефон)
    event_url VARCHAR(255),                 -- Ссылка на регистрацию
    event_tags VARCHAR(255),                -- Ключевые слова (теги)
    group_name VARCHAR(100)
);
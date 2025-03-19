-- Создание таблицы Users
CREATE TABLE Users (
    id_user SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

-- Создание таблицы Category_photos
CREATE TABLE Category_photos (
    id_category SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

-- Создание таблицы Photo_users
CREATE TABLE Photo_users (
    id_photo SERIAL PRIMARY KEY,
    id_user INT REFERENCES Users(id_user),
    photo_path TEXT NOT NULL,  -- Путь к файлу или URL
    id_category INT REFERENCES Category_photos(id_category),
    is_cut BOOLEAN
);

-- Создание таблицы Category_clothes
CREATE TABLE Category_clothes (
    id_category SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

-- Создание таблицы Photo_clothes
CREATE TABLE Photo_clothes (
    id_clothes SERIAL PRIMARY KEY,
    id_user INT REFERENCES Users(id_user),
    photo_path TEXT NOT NULL,  -- Путь к файлу или URL
    id_category INT REFERENCES Category_clothes(id_category),
    is_cut BOOLEAN
);
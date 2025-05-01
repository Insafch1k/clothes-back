-- Создание таблицы Users
CREATE TABLE Users (
    id_user SERIAL PRIMARY KEY,
    tg_id TEXT,
    name TEXT,
    password TEXT
);

-- Создание таблицы Category_photos
CREATE TABLE Category_photos (
    id_category SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

-- Таблица хэшей фото пользователей
CREATE TABLE hash_photos_users (
    id_photo SERIAL PRIMARY KEY,
    hash TEXT NOT NULL
);

-- Создание таблицы Photo_users
CREATE TABLE Photo_users (
    id_photo SERIAL PRIMARY KEY,
    id_user INT REFERENCES Users(id_user),
    photo_path TEXT NOT NULL,  -- Путь к файлу или URL
    id_category INT REFERENCES Category_photos(id_category),
    is_cut BOOLEAN,
    deleted_at TIMESTAMP DEFAULT NULL
);

-- Создание таблицы Category_clothes
CREATE TABLE Category_clothes (
    id_category SERIAL PRIMARY KEY,
    category TEXT NOT NULL
);

-- Создание таблицы Subcategory_clothes
CREATE TABLE Subcategory_clothes (
    id_subcategory SERIAL PRIMARY KEY,
    subcategory TEXT NOT NULL
);

-- Создание таблицы Subcategory_clothes
CREATE TABLE Sub_subcategory_clothes (
    id_sub_subcategory SERIAL PRIMARY KEY,
    sub_subcategory TEXT NOT NULL
);

-- Таблица хэшей фото одежды
CREATE TABLE hash_photos_clothes (
    id_clothes SERIAL PRIMARY KEY,
    hash TEXT NOT NULL
);

-- Таблица хэшей фото каталога
CREATE TABLE hash_photos_catalog (
    id_clothes SERIAL PRIMARY KEY,
    hash TEXT NOT NULL UNIQUE
);

-- Создание таблицы Photo_clothes
CREATE TABLE Photo_clothes (
    id_clothes SERIAL PRIMARY KEY,
    id_user INT REFERENCES Users(id_user),
    photo_path TEXT NOT NULL,   -- Путь к файлу или URL
    id_category INT REFERENCES Category_clothes(id_category),  -- Новое поле
    id_subcategory INT REFERENCES Subcategory_clothes(id_subcategory),  -- Новое поле
    id_sub_subcategory INT REFERENCES Sub_subcategory_clothes(id_sub_subcategory),  -- Новое поле
    is_cut BOOLEAN,
    deleted_at TIMESTAMP DEFAULT NULL
);

-- Вставляем основные категории одежды
INSERT INTO category_clothes (category) VALUES
('Женская одежда'),
('Мужская одежда'),
('Детская одежда'),
('Аксессуары');

-- Вставляем подкатегории для женской одежды
INSERT INTO subcategory_clothes (subcategory) VALUES
('Платья'),
('Верхняя одежда'),
('Блузки и рубашки'),
('Юбки'),
('Брюки и джинсы'),
('Спортивная одежда'),
('Домашняя одежда'),
('Обувь');

-- Вставляем подподкатегории для женской одежды
INSERT INTO sub_subcategory_clothes (sub_subcategory) VALUES
-- Для платьев (id_subcategory = 1)
('Вечерние'), ('Повседневные'), ('Летние'), ('Офисные'),
-- Для верхней одежды (id_subcategory = 2)
('Пальто женское'), ('Куртки'), ('Пуховики'), ('Плащи'), ('Ветровки'),
-- Для блузок и рубашек (id_subcategory = 3)
('Блузки'), ('Рубашки'), ('Топы'),
-- Для юбок (id_subcategory = 4)
('Мини-юбки'), ('Миди-юбки'), ('Длинные'), ('Юбки-карандаш'),
-- Для брюк и джинсов (id_subcategory = 5)
('Джинсы'), ('Брюки'), ('Леггинсы'), ('Шорты'),
-- Для спортивной одежды (id_subcategory = 6)
('Спортивные костюмы'), ('Футболки'), ('Шорты'), ('Лосины'),
-- Для домашней одежды (id_subcategory = 7)
('Пижамы'), ('Халаты'), ('Комплекты'),
-- Для обуви (id_subcategory = 8)
('Кроссовки'), ('Туфли'), ('Сапоги'), ('Басоножки');

-- Вставляем подкатегории для мужской одежды
INSERT INTO subcategory_clothes (subcategory) VALUES
('Рубашки'),
('Футболки и поло'),
('Брюки и джинсы'),
('Верхняя одежда'),
('Спортивная одежда'),
('Домашняя одежда'),
('Обувь');

-- Вставляем подподкатегории для мужской одежды
INSERT INTO sub_subcategory_clothes (sub_subcategory) VALUES
-- Для рубашек (id_subcategory = 9)
('Повседневные'), ('Офисные'), ('Официальные'),
-- Для футболок и поло (id_subcategory = 10)
('Футболки'), ('Майки'), ('Поло'),
-- Для брюк и джинсов (id_subcategory = 11)
('Джинсы'), ('Класические брюки'), ('Шорты'),
-- Для верхней одежды (id_subcategory = 12)
('Куртки'), ('Пальто'), ('Пуховики'), ('Ветровки'),
-- Для спортивной одежды (id_subcategory = 13)
('Спортивные костюмы'), ('Футболки'), ('Шорты'),
-- Для домашней одежды (id_subcategory = 14)
('Пижамы'), ('Халаты'), ('Комплекты'),
-- Для обуви (id_subcategory = 15)
('Кроссовки'), ('Туфли'), ('Ботинки'), ('Сандалии');

-- Вставляем подкатегории для детской одежды
INSERT INTO subcategory_clothes (subcategory) VALUES
('Для девочек'),
('Для мальчиков'),
('Одежда для малышей'),
('Обувь');

-- Вставляем подподкатегории для детской одежды
INSERT INTO sub_subcategory_clothes (sub_subcategory) VALUES
-- Для девочек (id_subcategory = 16)
('Платья'), ('Юбки'), ('Блузки'), ('Верхняя одежда'),
-- Для мальчиков (id_subcategory = 17)
('Рубашки'), ('Футболки'), ('Брюки'), ('Верхняя одежда'),
-- Для малышей (id_subcategory = 18)
('Комбинезоны'), ('Ползунки'), ('Боди'), ('Пижамы'),
-- Для обуви (id_subcategory = 19)
('Кроссовки'), ('Сандалии'), ('Ботинки');

-- Вставляем подкатегории для аксессуаров
INSERT INTO subcategory_clothes (subcategory) VALUES
('Сумки'),
('Головные уборы'),
('Шарфы и перчатки'),
('Ремни'),
('Украшения');

-- Вставляем подподкатегории для аксессуаров
INSERT INTO sub_subcategory_clothes (sub_subcategory) VALUES
-- Для сумок (id_subcategory = 20)
('Рюкзаки'), ('Клатчи'), ('Сумки через плечо'),
-- Для головных уборов (id_subcategory = 21)
('Шапки'), ('Кепки'), ('Шляпы'),
-- Для шарфов и перчаток (id_subcategory = 22)
('Шарфы'), ('Перчатки'), ('Варежки'),
-- Для ремней (id_subcategory = 23)
('Кожанные'), ('Тканевые'),
-- Для украшений (id_subcategory = 24)
('Серьги'), ('Кольца'), ('Браслеты');
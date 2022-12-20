DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS item;
DROP TABLE IF EXISTS receipt;

CREATE TABLE user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT CHECK (type IN ('admin', 'user')),
    code TEXT UNIQUE NOT NULL,
    'name' TEXT UNIQUE NOT NULL,
    'password' TEXT NOT NULL,
    date_created INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE item(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    'name' TEXT UNIQUE NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    date_created INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE receipt(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    buyer_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    total REAL NOT NULL,
    date_bought INTEGER NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES item (id)
    FOREIGN KEY (buyer_id) REFERENCES user (id)
    
    
);

INSERT INTO user(code, name, password, type) VALUES('0', 'admin', 'pbkdf2:sha256:260000$gbasdekM8VdOaYao$42cdc17422cefc5fc260c67ad058c45ce176c85dd681b2392a783eaa619b977a', 'admin')
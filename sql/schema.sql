CREATE TABLE IF NOT EXISTS owners (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    owner_id INTEGER NOT NULL,
    weight_kg REAL NOT NULL CHECK (weight_kg >= 0),
    recommended_weight_kg REAL NOT NULL CHECK (recommended_weight_kg >= 0),
    FOREIGN KEY (owner_id) REFERENCES owners(id)
);

CREATE TABLE IF NOT EXISTS health_records (
    id INTEGER PRIMARY KEY,
    pet_id INTEGER NOT NULL,
    recorded_on TEXT NOT NULL,
    activity TEXT NOT NULL,
    appetite TEXT NOT NULL,
    symptoms TEXT NOT NULL,
    weight_kg REAL NOT NULL CHECK (weight_kg >= 0),
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);

CREATE INDEX IF NOT EXISTS idx_pets_owner_id ON pets(owner_id);
CREATE INDEX IF NOT EXISTS idx_health_records_pet_date
    ON health_records(pet_id, recorded_on DESC);

-- Named statements used by the Django views. Keep values parameterized with ?.

-- name: list_pets
SELECT pets.id, pets.name, pets.species, pets.owner_id,
       pets.weight_kg, pets.recommended_weight_kg,
       owners.name AS owner_name, owners.email AS owner_email
FROM pets
JOIN owners ON pets.owner_id = owners.id
ORDER BY pets.name;

-- name: pet_detail
SELECT pets.*, owners.name AS owner_name, owners.email AS owner_email
FROM pets
JOIN owners ON pets.owner_id = owners.id
WHERE pets.id = ?;

-- name: pet_records
SELECT id, pet_id, recorded_on, activity, appetite, symptoms, weight_kg
FROM health_records
WHERE pet_id = ?
ORDER BY recorded_on DESC, id DESC;

-- name: list_records
SELECT health_records.*, pets.name AS pet_name, pets.species,
       pets.owner_id, owners.name AS owner_name, owners.email AS owner_email
FROM health_records
JOIN pets ON health_records.pet_id = pets.id
JOIN owners ON pets.owner_id = owners.id
ORDER BY health_records.recorded_on DESC, health_records.id DESC;

-- name: record_detail
SELECT health_records.*, pets.name AS pet_name, pets.species,
       pets.owner_id, owners.name AS owner_name, owners.email AS owner_email
FROM health_records
JOIN pets ON health_records.pet_id = pets.id
JOIN owners ON pets.owner_id = owners.id
WHERE health_records.id = ?;

-- name: pets_by_species
SELECT pets.id, pets.name, pets.species, pets.weight_kg,
       pets.recommended_weight_kg, pets.owner_id,
       owners.name AS owner_name, owners.email AS owner_email
FROM pets
JOIN owners ON pets.owner_id = owners.id
WHERE pets.species LIKE ?
ORDER BY pets.name;

-- name: records_by_symptom
SELECT health_records.*, pets.name AS pet_name, pets.species, pets.owner_id,
       owners.name AS owner_name, owners.email AS owner_email
FROM health_records
JOIN pets ON health_records.pet_id = pets.id
JOIN owners ON pets.owner_id = owners.id
WHERE health_records.symptoms LIKE ?
ORDER BY health_records.recorded_on DESC;

-- name: records_in_date_range
SELECT health_records.id, health_records.pet_id, health_records.recorded_on,
       health_records.activity, health_records.appetite, health_records.symptoms,
       health_records.weight_kg, pets.name AS pet_name, pets.species,
       pets.owner_id, owners.name AS owner_name, owners.email AS owner_email
FROM health_records
JOIN pets ON health_records.pet_id = pets.id
JOIN owners ON pets.owner_id = owners.id
WHERE health_records.recorded_on BETWEEN ? AND ?
ORDER BY health_records.recorded_on DESC;

-- name: total_counts
SELECT (SELECT COUNT(*) FROM pets) AS pet_count,
       (SELECT COUNT(*) FROM health_records) AS record_count;

-- name: pet_statistics
SELECT pets.id, pets.name AS pet_name,
       COUNT(health_records.id) AS records_count,
       AVG(health_records.weight_kg) AS average_weight,
       MIN(health_records.weight_kg) AS minimum_weight,
       MAX(health_records.weight_kg) AS maximum_weight
FROM pets
LEFT JOIN health_records ON pets.id = health_records.pet_id
GROUP BY pets.id, pets.name
ORDER BY pets.name;

-- name: symptom_statistics
SELECT symptoms, COUNT(*) AS records_count
FROM health_records
WHERE symptoms <> ''
GROUP BY symptoms
HAVING COUNT(*) >= ?
ORDER BY records_count DESC, symptoms;

-- name: owner_pet_counts
SELECT owners.id, owners.name AS owner_name,
       COUNT(pets.id) AS pets_count
FROM owners
LEFT JOIN pets ON owners.id = pets.owner_id
GROUP BY owners.id, owners.name
ORDER BY pets_count DESC, owners.name;

INSERT INTO teams (id, name, image_url)
VALUES (:id, :name, :image_url)
ON CONFLICT(id) DO UPDATE SET name = :name, image_url = :image_url;
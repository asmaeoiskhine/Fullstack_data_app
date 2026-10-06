-- 1. Items disponibles à moins de 10 €/jour, tarif croissant
SELECT id, titre, tarif_jour
FROM items
WHERE disponible AND tarif_jour < 10
ORDER BY tarif_jour ASC;
-- Perceuse 5.00 ; Vélo de ville 8.50

-- 2. Titre contenant « velo », insensible à la casse
SELECT id, titre FROM items WHERE titre ILIKE '%velo%';
-- 0 ligne : « Vélo » contient un « é », qui n'est pas un « e ».
-- Version qui ignore les accents :
CREATE EXTENSION IF NOT EXISTS unaccent;
SELECT id, titre FROM items WHERE unaccent(titre) ILIKE '%velo%';
-- Vélo de ville

-- 3. Chaque item avec le nom de son propriétaire
SELECT i.id, i.titre, u.display_name AS proprietaire
FROM items i
JOIN users u ON u.id = i.owner_id
ORDER BY i.id;
-- 1 Vélo de ville Alice ; 2 Perceuse Alice ; 3 Tente 2 places Bob ; 4 Appareil photo Bob

-- 4. Nombre de réservations par item, y compris les items jamais réservés
SELECT i.id, i.titre, count(r.id) AS nb_reservations
FROM items i
LEFT JOIN reservations r ON r.item_id = i.id
GROUP BY i.id, i.titre
ORDER BY i.id;
-- 1 Vélo de ville 1 ; 2 Perceuse 0 ; 3 Tente 2 places 1 ; 4 Appareil photo 1

-- 5. Par utilisateur : nombre d'items et tarif moyen (au moins un item)
SELECT u.display_name, count(i.id) AS nb_items, round(avg(i.tarif_jour), 2) AS tarif_moyen
FROM users u
JOIN items i ON i.owner_id = u.id
GROUP BY u.id, u.display_name
ORDER BY u.id;
-- Alice 2 6.75 ; Bob 2 16.00  (Chloé n'a aucun item, elle n'apparaît pas)

-- 6. Réservations actives après le 1er septembre 2026, avec titre et emprunteur
SELECT r.id, i.titre, u.display_name AS emprunteur, r.date_debut
FROM reservations r
JOIN items i ON i.id = r.item_id
JOIN users u ON u.id = r.borrower_id
WHERE r.statut = 'active' AND r.date_debut > DATE '2026-09-01'
ORDER BY r.id;
-- 2 Tente 2 places Alice 2026-09-10 ; 3 Appareil photo Chloé 2026-09-15

-- 7. Les 2 items les plus chers, en sautant le premier
SELECT id, titre, tarif_jour
FROM items
ORDER BY tarif_jour DESC
LIMIT 2 OFFSET 1;
-- Tente 2 places 12.00 ; Vélo de ville 8.50

-- 8. Chiffre d'affaires potentiel de chaque réservation active
SELECT r.id, i.titre, i.tarif_jour * (r.date_fin - r.date_debut) AS ca_potentiel
FROM reservations r
JOIN items i ON i.id = r.item_id
WHERE r.statut = 'active'
ORDER BY r.id;
-- 2 Tente 2 places 24.00 ; 3 Appareil photo 100.00

-- Chaque INSERT marqué "DOIT ÉCHOUER" doit afficher une erreur avec la contrainte indiquée.

-- 1. Note hors plage -> ck_avis_note
INSERT INTO avis (reservation_id, note) VALUES (1, 6);          -- DOIT ÉCHOUER

-- 2. Deux avis pour la même réservation -> uq_avis_reservation
INSERT INTO avis (reservation_id, note) VALUES (1, 4);          -- OK (le premier avis)
INSERT INTO avis (reservation_id, note) VALUES (1, 5);          -- DOIT ÉCHOUER

-- 3. Avis sur une réservation inexistante -> fk_avis_reservation
INSERT INTO avis (reservation_id, note) VALUES (999, 3);        -- DOIT ÉCHOUER

-- 4. Deux tags de même libellé -> uq_tags_label
INSERT INTO tags (label) VALUES ('sport');                      -- OK
INSERT INTO tags (label) VALUES ('sport');                      -- DOIT ÉCHOUER

-- 4b. Libellé avec majuscule -> ck_tags_label_minuscules
INSERT INTO tags (label) VALUES ('Sport');                      -- DOIT ÉCHOUER

-- 5. Même tag deux fois sur le même objet -> pk_item_tags
INSERT INTO item_tags (item_id, tag_id)
  SELECT 1, id FROM tags WHERE label = 'sport';                 -- OK
INSERT INTO item_tags (item_id, tag_id)
  SELECT 1, id FROM tags WHERE label = 'sport';                 -- DOIT ÉCHOUER

-- 6. Réservation active qui chevauche une autre (Tente, 10-12 sept.) -> ex_reservations_no_overlap
INSERT INTO reservations (item_id, borrower_id, date_debut, date_fin, statut)
VALUES (3, 3, '2026-09-11', '2026-09-13', 'active');            -- DOIT ÉCHOUER

-- Nettoyage : on retire les lignes valides insérées par ce test
DELETE FROM item_tags;
DELETE FROM tags;
DELETE FROM avis;

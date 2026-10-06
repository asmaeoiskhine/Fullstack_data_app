-- Schéma v2 : avis, tags, index sur clés étrangères, non-chevauchement

CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Avis : un seul avis par réservation, note de 1 à 5
CREATE TABLE avis (
    id             INTEGER GENERATED ALWAYS AS IDENTITY,
    reservation_id INTEGER     NOT NULL,
    note           SMALLINT    NOT NULL,
    commentaire    TEXT,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT pk_avis PRIMARY KEY (id),
    CONSTRAINT fk_avis_reservation FOREIGN KEY (reservation_id)
        REFERENCES reservations (id) ON DELETE CASCADE,
    CONSTRAINT uq_avis_reservation UNIQUE (reservation_id),
    CONSTRAINT ck_avis_note CHECK (note BETWEEN 1 AND 5)
);

-- Tags : libellé unique et en minuscules
CREATE TABLE tags (
    id    INTEGER GENERATED ALWAYS AS IDENTITY,
    label VARCHAR(50) NOT NULL,
    CONSTRAINT pk_tags PRIMARY KEY (id),
    CONSTRAINT uq_tags_label UNIQUE (label),
    CONSTRAINT ck_tags_label_minuscules CHECK (label = lower(label))
);

-- Liaison objets <-> tags (relation plusieurs-à-plusieurs)
CREATE TABLE item_tags (
    item_id INTEGER NOT NULL,
    tag_id  INTEGER NOT NULL,
    CONSTRAINT pk_item_tags PRIMARY KEY (item_id, tag_id),
    CONSTRAINT fk_item_tags_item FOREIGN KEY (item_id)
        REFERENCES items (id) ON DELETE CASCADE,
    CONSTRAINT fk_item_tags_tag FOREIGN KEY (tag_id)
        REFERENCES tags (id) ON DELETE CASCADE
);

-- Index sur les clés étrangères (PostgreSQL n'en crée pas automatiquement)
CREATE INDEX idx_items_owner           ON items (owner_id);
CREATE INDEX idx_reservations_item     ON reservations (item_id);
CREATE INDEX idx_reservations_borrower ON reservations (borrower_id);
CREATE INDEX idx_item_tags_tag         ON item_tags (tag_id);
-- (avis.reservation_id est déjà indexé par la contrainte UNIQUE)

-- Pas deux réservations actives qui se chevauchent sur le même objet.
-- Intervalle [debut, fin) : une réservation peut commencer le jour où une autre finit.
ALTER TABLE reservations
    ADD CONSTRAINT ex_reservations_no_overlap
    EXCLUDE USING gist (
        item_id WITH =,
        daterange(date_debut, date_fin, '[)') WITH &&
    ) WHERE (statut = 'active');

-------------------------------------------------------------------------------
-- Grabungsdatenbank - Export von MS Access nach Sybase SQL
--
-- TABLE           : WT_Relationtyp
--
-- EXPORT DATE/TIME: 13.02.2015 12:03:58
-- SOURCE DATA BASE: B:\03_GDBs_Aktivit�tsNr\2510_Profen_HW-Block\Datenbank\Grabungsdatenbank\GDB.mde  (Created by Access V.4.0)
-- USER            : admin
-- EXPORTED BY     : exportSQLD 2.1 (on Access V.3.6)
-------------------------------------------------------------------------------

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     1, 
     '-', 
     'ist gleichzeitig mit', 
     '-', 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     2, 
     '<', 
     'fr�her (�lter) als', 
     '>', 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     3, 
     '=', 
     'ist gleich', 
     '=', 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     4, 
     '>', 
     'sp�ter (j�nger) als', 
     '<', 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     5, 
     'p', 
     'Teil von (part of)', 
     '0', 
     0 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     6, 
     '<', 
     'liegt unter', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     7, 
     '<', 
     'geschnitten von', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     8, 
     '<', 
     'verf�llt von', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     9, 
     '-', 
     'liegt in', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     10, 
     '>', 
     'zieht an bestehenden', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     11, 
     '>', 
     'schneidet', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     12, 
     '>', 
     'liegt �ber', 
     NULL, 
     1 )
go

INSERT INTO Relationtyp
     (RelationtyID, RelationCat, RelationFull, OpRelation, MAStrat)
VALUES (
     13, 
     '-', 
     'hat Kontakt mit', 
     NULL, 
     1 )
go


-------------------------------------------------------------------------------
-- Grabungsdatenbank - Export von MS Access nach Sybase SQL
--
-- TABLE           : T_Einstellungen
--
-- EXPORT DATE/TIME: 13.02.2015 12:02:53
-- SOURCE DATA BASE: B:\03_GDBs_AktivitätsNr\2510_Profen_HW-Block\Datenbank\Grabungsdatenbank\GDB.mde  (Created by Access V.4.0)
-- USER            : admin
-- EXPORTED BY     : exportSQLD 2.1 (on Access V.3.6)
-------------------------------------------------------------------------------

INSERT INTO T_Einstellungen
     (GrabungAuffindungID, EinstellungID, AktivitaetsNr, ArchivOrdner, DatenBE, MaxImgSize, SicherBE, DatSicherBE, SicherIntervall, GDB_FE_version)
VALUES (
     001, 1, 
     2510, 
     'B:\\03_GDBs_AktivitätsNr\\2510_Profen_HW-Block\\Fotodokumentation', 
     'B:\\03_GDBs_AktivitätsNr\\2510_Profen_HW-Block\\Datenbank\\Grabungsdatenbank\\DatenBE.mdb', 
     10240000, 
     'B:\\03_GDBs_AktivitätsNr\\2510_Profen_HW-Block\\Datenbank\\Grabungsdatenbank\\Sicherung\\DatenBE_150213.mdb', 
     '13-02-2015 00:00:00', 
     7, 
     '3.2.9' )
go


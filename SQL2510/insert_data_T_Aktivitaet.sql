-------------------------------------------------------------------------------
-- Grabungsdatenbank - Export von MS Access nach Sybase SQL
--
-- TABLE           : T_Aktivitaet
--
-- EXPORT DATE/TIME: 13.02.2015 12:02:28
-- SOURCE DATA BASE: B:\03_GDBs_AktivitätsNr\2510_Profen_HW-Block\Datenbank\Grabungsdatenbank\GDB.mde  (Created by Access V.4.0)
-- USER            : admin
-- EXPORTED BY     : exportSQLD 2.1 (on Access V.3.6)
-------------------------------------------------------------------------------

INSERT INTO T_Aktivitaet
     (GrabungAuffindungID, AktivitaetsNr, D_Nr, Aktivitaetsart, Anlass, Gebietsreferent, Koordinator, Bezeichnung, Gemeinde, Lage, Beginn, EndeGelaende, Ende, TK25, RW_110, HW_110, Investor, Bemerkung)
VALUES (
     001, 2510, 
     NULL, 
     10, 
     'Hochwasser', 
     'Friederich, Susanne, Dr.', 
     'Mehner, Andreas', 
     'Profen Blockbergungen HW', 
     0, 
     NULL, 
     '11-08-2014 00:00:00', 
     '30-06-2015 00:00:00', 
     NULL, 
     NULL, 
     0, 
     0, 
     NULL, 
     NULL )
go


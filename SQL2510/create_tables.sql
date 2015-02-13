-- Grabungsdatenbank - Export von MS Access nach Sybase SQL
--
-- EXPORT DATE/TIME: 13.02.2015 12:02:12
-- SOURCE DATA BASE: B:\03_GDBs_Aktivit�tsNr\2510_Profen_HW-Block\Datenbank\Grabungsdatenbank\GDB.mde  (Created by Access V.4.0)
-- USER            : admin
-- EXPORTED BY     : exportSQLD 2.1 (on Access V.3.6)
--
--  TABLE  (* means name changed)        DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  GDB_info                             N/A
--  RT_Befund_Bild                       N/A
--  T_Aktivitaet                         N/A
--  T_Bearbeiter                         N/A
--  T_Befundbeschreibung                 N/A
--  T_Beschreibung                       N/A
--  T_C14Daten                           N/A
--  T_Einstellungen                      Allgemeine Einstellungen
--  T_Flaeche                            N/A
--  T_Fotoliste                          N/A
--  T_Funde                              N/A
--  T_Fundzettel                         N/A
--  T_Koordinate                         N/A
--  T_MAStrat                            N/A
--  T_Planumbeschreibung                 N/A
--  T_Profilbeschreibung                 N/A
--  T_Relation                           N/A
--  tempFotosOhneFStDruck                N/A
--  ArtAuffindung                        N/A
--  Blicknach                            N/A
--  Filmformat                           N/A
--  Fundart                              N/A
--  Fundgegenstand                       N/A
--  FundstelleZustand                    N/A
--  Gemeinde                             N/A
--  KOMessung                            N/A
--  Labor                                N/A
--  Material                             N/A
--  Rang                                 N/A
--  RegBezirk                            N/A
--  Relationtyp                          N/A
--  Status                               N/A
--  TK25                                 N/A
--  Zeitstellung                         N/A
--  z_RT_Archaeologe_Bef                 N/A
--  z_RT_Archaeologe_Fotos               N/A
--  z_WT_Archaeologen                    N/A
--


-------------------------------------------------------------------------------
-- TABLE: GDB_info
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ID                                   N/A
--  GDB_version                          N/A
--  GDB_releaseDate                      N/A
--

CREATE TABLE GDB_info
     (
     GDB_infoID                      numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ID                              INT NULL,
     GDB_version                     NVARCHAR(255) NULL,
     GDB_releaseDate                 DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: RT_Befund_Bild
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ID                                   N/A
--  AktivitaetsNr                        Aktivit�tsnummer
--  FundstelleID                         N/A
--  Bef_Nr                               Befundnummer
--  Foto_Nr                              Bildkennung
--

CREATE TABLE RT_Befund_Bild
     (
     RT_Befund_BildID                numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ID                              INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     Foto_Nr                         NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Aktivitaet
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  AktivitaetsNr                        f�r <1000 entspricht sie der Grabungs-Nummer, wird vom LDA vergeben
--  D_Nr                                 Drittmittelnummern, z.B. D225, D226
--  Aktivitaetsart                       Art der Auffindung
--  Anlass                               frei w�hlbare(s) Schlagwort(e), z.B. Bauma�nahme
--  Gebietsreferent                      zust�ndige Gebietsreferent des LDA: Nachname, Vorname, Titel
--  Koordinator                          Koordinator(en): Nachname1, Vorname1, Titel1; Nachname2, Vorname2, Titel2
--  Bezeichnung                          Projektname
--  Gemeinde                             Gemeinde ausw�hlen
--  Lage                                 frei w�hlbare(s) Schlagwort(e), z.B. Altstadt, landwirtschaftliche Nutzfl�che, Aue, etc
--  Beginn                               Beginn der Ma�nahme
--  EndeGelaende                         Ende der Gel�ndearbeit
--  Ende                                 Ende der Ma�nahme
--  TK25                                 TK25 ausw�hlen, auch mehrere (2934, 2935)
--  RW_110                               Rechtswert im LS 110 ohne Nachkomma, Mittelpunktskoordinate
--  HW_110                               Hochwert im LS 110 ohne Nachkomma, Mittelpunktskoordinate
--  Investor                             Verursacher, Investor
--  Bemerkung                            gr��ere Speichermenge f�r freien Text
--

CREATE TABLE T_Aktivitaet
     (
     T_AktivitaetID                  numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     AktivitaetsNr                   INT NULL,
     D_Nr                            NVARCHAR(255) NULL,
     Aktivitaetsart                  INT NULL,
     Anlass                          NVARCHAR(255) NULL,
     Gebietsreferent                 NVARCHAR(255) NULL,
     Koordinator                     NVARCHAR(255) NULL,
     Bezeichnung                     NVARCHAR(255) NULL,
     Gemeinde                        INT NULL,
     Lage                            NVARCHAR(255) NULL,
     Beginn                          DATETIME NULL,
     EndeGelaende                    DATETIME NULL,
     Ende                            DATETIME NULL,
     TK25                            NVARCHAR(255) NULL,
     RW_110                          INT NULL,
     HW_110                          INT NULL,
     Investor                        NVARCHAR(255) NULL,
     Bemerkung                       TEXT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Bearbeiter
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  AktivitaetsNr                        Aktivit�ts-Nr
--  Bearb_Kurz                           Initalien eingeben, max. 4 Buchstaben
--  Nachname                             Nachname eingeben
--  Vorname                              Vorname eingeben
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--

CREATE TABLE T_Bearbeiter
     (
     T_BearbeiterID                  numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     AktivitaetsNr                   INT NULL,
     Bearb_Kurz                      NVARCHAR(255) NULL,
     Nachname                        NVARCHAR(255) NULL,
     Vorname                         NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Befundbeschreibung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  Bef_Nr                               Befundnummer (nur numerisch, ganzzahlig)
--  FundstelleID                         Fl�che ausw�hlen
--  AktivitaetsNr                        Aktivit�ts-Nr. wird vom LDA vergeben
--  Datum                                Datum (01.01.03 oder 1-1-3)
--  Schnitt                              Schnittnummer (m�glichst Ganzzahl)
--  Lage                                 Allgemeine Lagebeschreibung (im Schnitt, zu anderen Befunden, etc.) f�r die sp�tere Suche im Plan.
--  Siedlung                             Feld f�r die klassische Einteilung der Arch�ologie, auch additiv mit Siedlung, Grab, Hort u. Sonst. zu verwenden.
--  Grab                                 Feld f�r die klassische Einteilung der Arch�ologie, auch additiv mit Siedlung, Grab, Hort u. Sonst. zu verwenden.
--  Hort                                 Feld f�r die klassische Einteilung der Arch�ologie, auch additiv mit Siedlung, Grab, Hort u. Sonst. zu verwenden.
--  Sonst                                Feld f�r die klassische Einteilung der Arch�ologie, auch additiv mit Siedlung, Grab, Hort u. Sonst. zu verwenden.
--  FundartID                            Befundtyp (relational, nach M�glichkeit Vorgabe verwenden)
--  FundartTxt                           Befundtyp als Freitext f�r differenzierende Bezeichnung
--  ZeitstellungID                       Datierung des Befundes (relational, nach M�glichkeit Vorgabe verwenden)
--  ZeitSicher                           Die Datierung des Befundes ist sicher.
--  Bearbeiter                           Bearbeiter des Befundes (relational, Initialen bis 4 Buchstaben)
--  Profile                              Zugeh�rige Profile (z.B. 1 bis 4). Bitte angeben, wenn die Profile nicht beschrieben werden
--  Fundnummern                          Zugeh�rige Fundnummern. Bitte angeben, wenn keine Funderfassung erfolgt.
--  unter                                ab der Version 3.0 eine eigene Tabelle. Befund liegt unter bzw. wird geschnitten von:
--  gleichzeitig                         ab der Version 3.0 eine eigene Tabelle. Befund ist gleichzeitig mit:
--  ueber                                ab der Version 3.0 eine eigene Tabelle. Befund liegt �ber bzw. schneidet:
--  Bemerkung                            Bemerkungen zum Befund.
--  Erfassungsdatum                      Erfassungsdatum, automatischer Eintrag
--  Endkontrolle                         Endkontrolle erfolgt und Datensatz f�r die Archivierung freigegeben
--  Merker                               Feld zum Markieren des Datensatzes und �betragen in Abfrage A_markierte_Befunde
--

CREATE TABLE T_Befundbeschreibung
     (
     T_BefundbeschreibungID          numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     Bef_Nr                          INT NULL,
     FundstelleID                    INT NULL,
     AktivitaetsNr                   INT NULL,
     Datum                           DATETIME NULL,
     Schnitt                         NVARCHAR(255) NULL,
     Lage                            NVARCHAR(255) NULL,
     Siedlung                        BIT,
     Grab                            BIT,
     Hort                            BIT,
     Sonst                           BIT,
     FundartID                       INT NULL,
     FundartTxt                      NVARCHAR(255) NULL,
     ZeitstellungID                  INT NULL,
     ZeitSicher                      BIT,
     Bearbeiter                      NVARCHAR(255) NULL,
     Profile                         NVARCHAR(255) NULL,
     Fundnummern                     NVARCHAR(255) NULL,
     unter                           NVARCHAR(255) NULL,
     gleichzeitig                    NVARCHAR(255) NULL,
     ueber                           NVARCHAR(255) NULL,
     Bemerkung                       NVARCHAR(255) NULL,
     Erfassungsdatum                 DATETIME NULL,
     Endkontrolle                    BIT,
     Merker                          BIT
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Beschreibung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  BeschreibungID                       Indexfeld
--  AktivitaetsNr                        Aktivit�ts-Nr.Nr
--  FundstelleID                         Fl�chen-Nr
--  Bef_Nr                               Befundnummer
--  Datum                                Datum (1.1.3 oder 1-1-3)
--  Bearbeiter                           Bearbeiter (Initialien bis 4 Buchstaben)
--  Blatt_nr                             Blattnummer (Zahl)
--  Beschreibung                         Planumsbeschreibung
--

CREATE TABLE T_Beschreibung
     (
     T_BeschreibungID                numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     BeschreibungID                  INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     Datum                           DATETIME NULL,
     Bearbeiter                      NVARCHAR(255) NULL,
     Blatt_nr                        NVARCHAR(255) NULL,
     Beschreibung                    TEXT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_C14Daten
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  14C_ID                               N/A
--  AktivitaetsNr                        Aktivit�ts bzw. Grabungs-Nr
--  FundstelleID                         Fl�chen-Nr.
--  Bef_Nr                               Befund-Nummer der Probe
--  F_Nr                                 Fundnummer der Probe oder des ganzen Skelettes
--  Rang                                 Buchstabe der Probe (als Teil  des ganzen Skelettes unter a)
--  Probenname                           Probenname wird oft vom Labor vergeben, zus�tzlich zur Lab-Nr.
--  LAB                                  Labork�rzel (str 4, relational)
--  LAB_NR                               Labor-Nummer (str 12)
--  BP                                   unkalibriertes (!) BP-Datum des Labors (int)
--  STD                                  Standardabweichung (+/-) des Labordatums (int)
--  PRMAT_E                              Erg�nzungen zum Probenmaterial (str 255)
--  ANM                                  Anmerkungen aller Art zum Datum, dem Befund, der Probenqualit�t, etc (str 255)
--  VORBHLT                              Mit der Erfassung wird automatisch ein Publikationsvorbehalt von 1 Jahr gew�hrt (date)
--  ZITAT                                Nachname Jahr, Seitenzahl  (str 255)
--  RADON                                Datum an die Onlinedatenbank RADON �bermittelt (bool)
--  WAHL                                 Feld f�r die interne selektion von Datens�tzen (bool)
--  Eintrag                              automatisch gesetztes Datum des Eintrags (date)
--

CREATE TABLE T_C14Daten
     (
     T_C14DatenID                    numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     14C_ID                          INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     F_Nr                            INT NULL,
     Rang                            INT NULL,
     Probenname                      NVARCHAR(255) NULL,
     LAB                             NVARCHAR(255) NULL,
     LAB_NR                          NVARCHAR(255) NULL,
     BP                              INT NULL,
     STD                             INT NULL,
     PRMAT_E                         NVARCHAR(255) NULL,
     ANM                             NVARCHAR(255) NULL,
     VORBHLT                         DATETIME NULL,
     ZITAT                           NVARCHAR(255) NULL,
     RADON                           BIT,
     WAHL                            BIT,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Einstellungen
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  EinstellungID                        Ist immer nur "1", somit existiert immer nur max. 1 Datensatz
--  AktivitaetsNr                        Aktivitaets-Nr. der LDA
--  ArchivOrdner                         Archivordner f�r die Digitalbilder
--  DatenBE                              Pfad zum Backend, der Daten-Access-Datei
--  MaxImgSize                           Maximale gr��e der anzuzeigenden Bilddateien (Byte)
--  SicherBE                             Pfad und Name der vom Sytem angelegten Sicherungsdatei
--  DatSicherBE                          Datum der letzten vom System angelegten Sicherungsdatei
--  SicherIntervall                      Intervall der Datensicherung in Tagen
--  GDB_FE_version                       Version des Grabungsdatenbank-Frontends (GDB.mde)
--

CREATE TABLE T_Einstellungen
     (
     T_EinstellungenID               numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     EinstellungID                   INT NULL,
     AktivitaetsNr                   INT NULL,
     ArchivOrdner                    NVARCHAR(255) NULL,
     DatenBE                         NVARCHAR(255) NULL,
     MaxImgSize                      INT NULL,
     SicherBE                        NVARCHAR(255) NULL,
     DatSicherBE                     DATETIME NULL,
     SicherIntervall                 INT NULL,
     GDB_FE_version                  NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Flaeche
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  AktivitaetsNr                        Kennzahl der zugeh�rigen Aktivit�t (Projekt)
--  FundstelleID                         Nummer der Fl�che (arabisch), dient dem sortieren und der inneren Verwaltung
--  F_Name                               Fl�chen-Name, z.B. III oder III Ost (max. 12 Zeichen)
--  RegBezirkID                          Regierungszbezirk K�rzel (Halle), relational zu WT_RegBezirk
--  GNR                                  Gemeinde-Nummer aus der WT_Gemeinde. Wird �berwiegend zum Darstellen des Kreises verwendet.
--  GemeindeID                           GemeindeID (Halle)
--  TK25ID                               TK25 ID-Nummer (Halle), relational zu WT_TK25
--  RW_110                               Rechtswert im LS 110 ohne Nachkomma, Mittelpunktskoordinate
--  HW_110                               Hochwert im LS 110 ohne Nachkomma, Mittelpunktskoordinate
--  KOMessungID                          allgemeine Messgenauigkeit auf der Fl�che
--  Flurbezeichnung                      Flurname
--  FundstelleZustandID                  Zustand der Fundstelle ausw�hlen
--  Grabungsleiter                       Name(n) des(r) verantwortlichen Arch�ologen (Name1, Nachname1; Name2, Nachname2)
--  Grabungsbedingung                    Freitext f�r Anzahl der Mitarbeiter, Technikeinsatz, Rahmenbedingungen
--  Grabungsergebnis                     Freitext f�r Grabungsergebnisse
--  Geografie                            Freitext f�r allgemeine Beschreibung zur Topografie, Bodenkunde, Geologie
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--  ZustandVorBeginn                     Zustand der Fl�che vor Grabungsbeginn
--

CREATE TABLE T_Flaeche
     (
     T_FlaecheID                     numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     F_Name                          NVARCHAR(255) NULL,
     RegBezirkID                     INT NULL,
     GNR                             INT NULL,
     GemeindeID                      INT NULL,
     TK25ID                          INT NULL,
     RW_110                          INT NULL,
     HW_110                          INT NULL,
     KOMessungID                     INT NULL,
     Flurbezeichnung                 NVARCHAR(255) NULL,
     FundstelleZustandID             INT NULL,
     Grabungsleiter                  NVARCHAR(255) NULL,
     Grabungsbedingung               TEXT NULL,
     Grabungsergebnis                TEXT NULL,
     Geografie                       TEXT NULL,
     Eintrag                         DATETIME NULL,
     ZustandVorBeginn                TEXT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Fotoliste
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FotoID                               Index
--  Datum                                Datum der Aufnahme
--  Film_Nr                              Filmnummer (Zahl) eingeben
--  Bild_Nr                              Negativnummer (Zahl) eingeben
--  Bild_a                               ggf. Buchstabe "a" eingeben
--  Bef_Nr                               Befundnummer
--  AktivitaetsNr                        N/A
--  FundstelleID                         Flaeche
--  Schnitt                              Schnittnummer (1, 2, etc.)
--  Format_Code                          Filmmaterial (relational)
--  Planum                               Planum als Zahl
--  Profil                               Profil als Zahl
--  FundNr                               Fundnummer des dargestellten ObjektesFundfoto
--  Blickrichtung                        Blickrichtung des Fotografen (Wertevorgaben)
--  Bildinhalt                           Beschreibung Bildinhalt (Profil, Planum, �bersicht, Funde, Arbeitsfoto etc.)
--  Fehler                               fehler auf der Fototafel
--  chic                                 Sch�nes Bild (Vortrag, Publikation etc)
--  Pfad                                 N/A
--  Dateiname                            Dateiname aus Auslesevorgang und Nr. eingeben (z.B. 0012_001).
--  origDateiname                        urspr�nglicher Dateiname
--  Verbleib                             Verbleib des Bildes
--  Merker                               Feld zum Markieren des Datensatzes und �betragen in Abfrage A_markierte_Fotos
--  BAutor                               Bildautor / Fotograf
--  DS_Datum                             Bild erfasst am
--  istMessbild                          Bild ist wurde als Messbild verwendet
--  Fundfoto                             ist Fundfoto?
--  Dublette                             Pr�fung von doppelten Bildeintr�gen (s. Formular)
--  loeschen                             s. Formular Bilder einlesen (Bild wird nicht �bertragen)
--  Bildkennung                          interne Kennung zur Verkn�pfung mit Relationstabelle
--

CREATE TABLE T_Fotoliste
     (
     T_FotolisteID                   numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     FotoID                          INT NULL,
     Datum                           DATETIME NULL,
     Film_Nr                         INT NULL,
     Bild_Nr                         INT NULL,
     Bild_a                          NVARCHAR(255) NULL,
     Bef_Nr                          NVARCHAR(255) NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Schnitt                         NVARCHAR(255) NULL,
     Format_Code                     INT NULL,
     Planum                          NVARCHAR(255) NULL,
     Profil                          NVARCHAR(255) NULL,
     FundNr                          NVARCHAR(255) NULL,
     Blickrichtung                   NVARCHAR(255) NULL,
     Bildinhalt                      NVARCHAR(255) NULL,
     Fehler                          BIT,
     chic                            BIT,
     Pfad                            NVARCHAR(255) NULL,
     Dateiname                       NVARCHAR(255) NULL,
     origDateiname                   NVARCHAR(255) NULL,
     Verbleib                        NVARCHAR(255) NULL,
     Merker                          BIT,
     BAutor                          NVARCHAR(255) NULL,
     DS_Datum                        DATETIME NULL,
     istMessbild                     BIT,
     Fundfoto                        BIT,
     Dublette                        BIT,
     loeschen                        BIT,
     Bildkennung                     NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Funde
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FundeID                              Index
--  Fundzettel_Idx                       Fundzettel-Index kann �ber eine Abfrage aktualisiert werden
--  AktivitaetsNr                        N/A
--  FundstelleID                         Fl�chen-Nr.
--  Bef_Nr                               Befundnummer
--  F_Nr                                 Fundnummer
--  Rang                                 Ordnungszahl innerhalb der Fundeinheit (Fundzettel)
--  MaterialID                           Materialangabe aus der Liste ausw�hlen. Materialkomposite ggf. mit mehreren Eintr�gen beschreiben
--  Stueckzahl                           Anzahl (je Gruppe/Material): 1 Knochenkamm; 2 Glasperlen
--  Beschreibung                         Beschreibung. Oberbegriffe w�hlen und ggf. auch in Bemerkung erg�nzen
--  ZeitstellungID                       Datierung aus der Liste w�hlen. Erg�nzungen ggf. unter Bemerkung
--  Bemerkung                            Bemerkungen
--  Verbleib                             Verbleib der Funde, ggf. Entleiher+Datum
--  Zeichnung                            Fund(e) zeichnen?
--  Foto                                 Fund(e) fotografieren? (Doku)
--  Restaurieren                         Fund(e) restaurieren?
--  VE                                   Zahl f�r den Karton oder alternative Verpackungseinheit
--

CREATE TABLE T_Funde
     (
     T_FundeID                       numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     FundeID                         INT NULL,
     Fundzettel_Idx                  INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     F_Nr                            INT NULL,
     Rang                            INT NULL,
     MaterialID                      INT NULL,
     Stueckzahl                      INT NULL,
     Beschreibung                    NVARCHAR(255) NULL,
     ZeitstellungID                  INT NULL,
     Bemerkung                       NVARCHAR(255) NULL,
     Verbleib                        NVARCHAR(255) NULL,
     Zeichnung                       INT NULL,
     Foto                            INT NULL,
     Restaurieren                    INT NULL,
     VE                              INT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Fundzettel
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FundzettelID                         Index
--  Bef_Nr                               Befundnummer (Lesefunde: 0)
--  F_Nr                                 Fundnummer
--  FundstelleID                         Fl�che aus der Liste ausw�hlen
--  AktivitaetsNr                        N/A
--  Funddatum                            Datum (1.1.3, 1-1-3)
--  Unterschrift                         Bearbeiterk�rzel (relational)
--  Schnitt                              Schnittnummer ("1", "2-3", etc.)
--  Planum                               Angaben zum Planum, also "1" oder "1-2"
--  Profil                               Angaben zum Profil, also "1" oder "1-2"
--  Tiefe                                Angaben zur Tiefe, in der Regel cm unter Pl. 1 oder HN76
--  Lage                                 Angaben zur Lage, z.B. "Schicht 3"  oder "Lesefund s�dl. Abraum" etc.
--  HK_Jahr                              Jahr der HK-Nr
--  HK_Zahl                              Zahl der HK-Nr
--  Erfassungsdatum                      Erfassungsdatum, automatisch
--  Anzahl_Etiketten                     Anzahl der zu druckenden HKNr-Etiketten
--

CREATE TABLE T_Fundzettel
     (
     T_FundzettelID                  numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     FundzettelID                    INT NULL,
     Bef_Nr                          INT NULL,
     F_Nr                            INT NULL,
     FundstelleID                    INT NULL,
     AktivitaetsNr                   INT NULL,
     Funddatum                       DATETIME NULL,
     Unterschrift                    NVARCHAR(255) NULL,
     Schnitt                         NVARCHAR(255) NULL,
     Planum                          NVARCHAR(255) NULL,
     Profil                          NVARCHAR(255) NULL,
     Tiefe                           NVARCHAR(255) NULL,
     Lage                            NVARCHAR(255) NULL,
     HK_Jahr                         INT NULL,
     HK_Zahl                         INT NULL,
     Erfassungsdatum                 DATETIME NULL,
     Anzahl_Etiketten                INT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Koordinate
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  KoordinateID                         N/A
--  AktivitaetsNr                        Aktivit�ts-Nr
--  FundstelleID                         Fl�chen-Nummer
--  Bef_Nr                               Befundnummer auf die sich die Koordinate bezieht
--  F_Nr                                 Fundnummer eingeben, wenn es eine Fundkoordinate ist
--  Planum                               Planum eingeben
--  ProfilNagel                          Profiln�gel eines Profiles zum Befund
--  x_150                                RW im Lagestatus 150 (in der Regel vom Stra�enbau)
--  y_150                                HW im Lagestatus 150 (in der Regel vom Stra�enbau)
--  HN_76                                H�henwert in HN76
--  Plan_Nr                              Planblattnummer der abschlie�enden Papierdokumentation je Fl�che gez�hlt (z.B. Fl02_01)
--  x_110                                RW im Lagestatus 110 (Lagestatus des LDA LSA)
--  y_110                                HW im Lagestatus 110 (Lagestatus des LDA LSA)
--

CREATE TABLE T_Koordinate
     (
     T_KoordinateID                  numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     KoordinateID                    INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     F_Nr                            INT NULL,
     Planum                          REAL NULL,
     ProfilNagel                     INT NULL,
     x_150                           REAL NULL,
     y_150                           REAL NULL,
     HN_76                           REAL NULL,
     Plan_Nr                         NVARCHAR(255) NULL,
     x_110                           REAL NULL,
     y_110                           REAL NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_MAStrat
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  MAStratID                            automatischer Index
--  AktivitaetsNr                        Aktivit�ts-Nr der Grabung
--  FundstelleID                         FundstellenID der Grabung
--  Bef_Nr                               Befund-Nr der Grabung
--  RelationFull                         Relation nach MA-Befundblatt LDA-LSA
--  Befunde                              Befund wird geschnitten von folgenden Befunden:
--

CREATE TABLE T_MAStrat
     (
     T_MAStratID                     numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     MAStratID                       INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     RelationFull                    NVARCHAR(255) NULL,
     Befunde                         NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Planumbeschreibung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  PlanumID                             Indexfeld
--  AktivitaetsNr                        Aktivit�ts-Nr.Nr
--  FundstelleID                         Fl�chen-Nr
--  Bef_Nr                               Befundnummer
--  Planum                               Planumsnummer
--  AnBagger                             Planum angelegt mit dem Bagger.
--  AnMBagger                            Planum angelegt mit dem Minibagger.
--  AnSchaufel                           Planum angelegt mit der Schaufel.
--  AnKratzer                            Planum angelet mit dem Kratzer.
--  Datum                                Datum (1.1.3 oder 1-1-3)
--  Bearbeiter                           Bearbeiter (Initialien bis 4 Buchstaben)
--  Blatt_nr                             Blattnummer (Zahl)
--  Beschreibung                         Planumsbeschreibung
--

CREATE TABLE T_Planumbeschreibung
     (
     T_PlanumbeschreibungID          numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     PlanumID                        INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     Planum                          NVARCHAR(255) NULL,
     AnBagger                        BIT,
     AnMBagger                       BIT,
     AnSchaufel                      BIT,
     AnKratzer                       BIT,
     Datum                           DATETIME NULL,
     Bearbeiter                      NVARCHAR(255) NULL,
     Blatt_nr                        NVARCHAR(255) NULL,
     Beschreibung                    TEXT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Profilbeschreibung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ProfilID                             Index
--  AktivitaetsNr                        Ativit�ts-Nr.
--  FundstelleID                         Fl�chen-Nr.
--  Bef_Nr                               Befundnummer
--  ProfilNagel1                         erster Profilnagel des Profiles (nur Zahl)
--  ProfilNagel2                         zweiter Profilnagel des Profiles (nur Zahl)
--  Profil_Name                          Name des Profiles "1-2" sprich Profil Nagel 1 bis Nagel 2 oder "1" sprich Profil 1
--  AnNicht                              Profil nicht angelegt
--  AnUStrat                             Profil unstratifiziert angelegt
--  AnStrat                              Profil stratifiziert angelegt (M�chtigkeit s. Beschreibung o. Fundzettel).
--  AnSchicht                            Profil in nat�rlichen Schichten angelegt
--  AnBagger                             Anlage/Aushub des Profils mit einem Bagger
--  AnMBagger                            Anlage/Aushub des Profils mit einem Minibagger
--  AnSpaten                             Anlage/Aushub des Profils mit dem Spaten/Schaufel
--  AnKelle                              Anlage/Aushub des Profils mit Kelle/Kratzer durchgesehen
--  AnSieb                               Aushub gesiebt
--  Datum                                Datum (1.1.3 oder 1-1-3)
--  Bearbeiter                           Bearbeiter (Initalien bis 4 Buchstaben)
--  Blatt_Nr                             Blattnummer (Zahl)
--  Beschreibung                         Profilbeschreibung
--  AbNicht                              Profil nicht abgebaut
--  AbUStrat                             Profil unstratifiziert abgebaut
--  AbStrat                              Profil stratifiziert abgebaut
--  AbSchicht                            Profil in nat�rlichen Schichten abgebaut
--  AbBagger                             Abbau des Profils mit dem Bagger
--  AbMBagger                            Abbau des Profils mit dem Minibagger
--  AbSpaten                             Abbau den Profil mit dem Spaten
--  AbKelle                              Abbau/Aushub des Profils mit der Kelle/Kratzer durchgesehen
--  AbSieb                               Abbau/Aushub des Profils gesiebt
--

CREATE TABLE T_Profilbeschreibung
     (
     T_ProfilbeschreibungID          numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ProfilID                        INT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID                    INT NULL,
     Bef_Nr                          INT NULL,
     ProfilNagel1                    INT NULL,
     ProfilNagel2                    INT NULL,
     Profil_Name                     NVARCHAR(255) NULL,
     AnNicht                         BIT,
     AnUStrat                        BIT,
     AnStrat                         BIT,
     AnSchicht                       BIT,
     AnBagger                        BIT,
     AnMBagger                       BIT,
     AnSpaten                        BIT,
     AnKelle                         BIT,
     AnSieb                          BIT,
     Datum                           DATETIME NULL,
     Bearbeiter                      NVARCHAR(255) NULL,
     Blatt_Nr                        NVARCHAR(255) NULL,
     Beschreibung                    TEXT NULL,
     AbNicht                         BIT,
     AbUStrat                        BIT,
     AbStrat                         BIT,
     AbSchicht                       BIT,
     AbBagger                        BIT,
     AbMBagger                       BIT,
     AbSpaten                        BIT,
     AbKelle                         BIT,
     AbSieb                          BIT
     )
go


-------------------------------------------------------------------------------
-- TABLE: T_Relation
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  AktivitaetsNr                        Aktivit�ts-Nr.
--  FundstelleID1                        Fl�che vom 1.  Befund
--  Bef_Nr1                              Erste Befundnummer
--  Relation                             Beziehung zwischen den Befunden
--  FundstelleID2                        Fl�che vom 2. Befund
--  Bef_Nr2                              Zweite Befundnummer
--  Bemerkung                            Bemerkung
--

CREATE TABLE T_Relation
     (
     T_RelationID                    numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     AktivitaetsNr                   INT NULL,
     FundstelleID1                   INT NULL,
     Bef_Nr1                         INT NULL,
     Relation                        NVARCHAR(255) NULL,
     FundstelleID2                   INT NULL,
     Bef_Nr2                         INT NULL,
     Bemerkung                       NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: tempFotosOhneFStDruck
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  AktivitaetsNr                        N/A
--  Bezeichnung                          N/A
--  Format_Code                          N/A
--  Film_Nr                              N/A
--  Bild_Nr                              N/A
--  Bild_a                               N/A
--  Beschreibung                         N/A
--  Schnitt                              N/A
--  Bef_Nr                               N/A
--  Datei                                N/A
--  Bildkennung                          N/A
--

CREATE TABLE tempFotosOhneFStDruck
     (
     tempFotosOhneFStDruckID         numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     AktivitaetsNr                   INT NULL,
     Bezeichnung                     NVARCHAR(255) NULL,
     Format_Code                     INT NULL,
     Film_Nr                         INT NULL,
     Bild_Nr                         INT NULL,
     Bild_a                          NVARCHAR(255) NULL,
     Beschreibung                    NVARCHAR(255) NULL,
     Schnitt                         NVARCHAR(255) NULL,
     Bef_Nr                          NVARCHAR(255) NULL,
     Datei                           NVARCHAR(255) NULL,
     Bildkennung                     NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_ArtAuffindung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ArtAuffindungID                      N/A
--  ArtAuffindung                        N/A
--

CREATE TABLE ArtAuffindung
     (
     ArtAuffindungID                 INT NULL,
     ArtAuffindung                   NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Blicknach
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  BlickID                              N/A
--  Blicknach                            N/A
--  Blicklang                            N/A
--

CREATE TABLE Blicknach
     (
     WT_BlicknachID                  numeric(20,0) identity,
     BlickID                         INT NULL,
     Blicknach                       NVARCHAR(255) NULL,
     Blicklang                       NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Filmformat
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  Format_Code                          Zahlencode (Index)
--  Format_kurz                          K�rzel f�r Filmformat
--  Format_lang                          Filmformat
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--

CREATE TABLE Filmformat
     (
     WT_FilmformatID                 numeric(20,0) identity,
     Format_Code                     INT NULL,
     Format_kurz                     NVARCHAR(255) NULL,
     Format_lang                     NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Fundart
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FundartID                            N/A
--  Favorit                              N/A
--  Kategorie                            N/A
--  Fundart                              N/A
--  Fundart_kurz                         N/A
--

CREATE TABLE Fundart
     (
     FundartID                       REAL NULL,
     Favorit                         BIT,
     Kategorie                       NVARCHAR(255) NULL,
     Fundart                         NVARCHAR(255) NULL,
     Fundart_kurz                    NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Fundgegenstand
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FundgegenstandID                     N/A
--  Fundgegenstand                       N/A
--  Eintrag                              N/A
--

CREATE TABLE Fundgegenstand
     (
     FundgegenstandID                INT NULL,
     Fundgegenstand                  NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_FundstelleZustand
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  FundstelleZustandID                  N/A
--  FundstelleZustand                    N/A
--

CREATE TABLE FundstelleZustand
     (
     FundstelleZustandID             INT NULL,
     FundstelleZustand               NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Gemeinde
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  GemeindeID                           Interner Schl�ssel der GDB
--  GNR                                  Gemeinde-Nummer Stand 01.07.2007.
--  RS                                   Regional-Schl�ssel Stand 01.07.2007.
--  Gemeinde                             Gemeinde-Name Stand 01.07.2007.
--  VNR                                  Verwaltungsgemeinschaft-Nummer  Stand 01.07.2007.
--  VerwGemName                          Verwaltungsgemeinschaft-Name Stand 01.07.2007.
--  Kreis                                Kreis-Name Stand 01.07.2007.
--  Kreiskuerzel                         Kreisk�rzel
--

CREATE TABLE Gemeinde
     (
     GemeindeID                      INT NULL,
     GNR                             INT NULL,
     RS                              NVARCHAR(255) NULL,
     Gemeinde                        NVARCHAR(255) NULL,
     VNR                             INT NULL,
     VerwGemName                     NVARCHAR(255) NULL,
     Kreis                           NVARCHAR(255) NULL,
     Kreiskuerzel                    NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_KOMessung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  KOMessungID                          N/A
--  KOMessMethode                        N/A
--  KOMessFehler                         N/A
--

CREATE TABLE KOMessung
     (
     KOMessungID                     INT NULL,
     KOMessMethode                   NVARCHAR(255) NULL,
     KOMessFehler                    INT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Labor
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  Lab_Id                               N/A
--  LAB                                  Labork�rzel: Buchstaben der Labornummer vor dem "-" (str 4)
--  Typ                                  Kurze Bezeichnung des Verfahrens
--  LABOR                                Laborname mit Erl�uterung (str 51)
--  Land                                 Land mit Erl�uterung (str 18)
--  Eintrag                              automatisch gesetztes Datum des Einrags (date)
--

CREATE TABLE Labor
     (
     Lab_Id                          INT NULL,
     LAB                             NVARCHAR(255) NULL,
     Typ                             NVARCHAR(255) NULL,
     LABOR                           NVARCHAR(255) NULL,
     Land                            NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Material
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  MaterialID                           N/A
--  Material                             N/A
--  Mat_kurz                             N/A
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--

CREATE TABLE Material
     (
     MaterialID                      INT NULL,
     Material                        NVARCHAR(255) NULL,
     Mat_kurz                        NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Rang
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  Zaehler                              N/A
--  Rang                                 N/A
--

CREATE TABLE Rang
     (
     Zaehler                         INT NULL,
     Rang                            NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_RegBezirk
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  RegBezirkID                          N/A
--  RegBezirk                            N/A
--  RB_Kurz                              N/A
--  Eintrag                              N/A
--

CREATE TABLE RegBezirk
     (
     RegBezirkID                     INT NULL,
     RegBezirk                       NVARCHAR(255) NULL,
     RB_Kurz                         NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Relationtyp
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  RelationtyID                         N/A
--  RelationCat                          Symbol der m�glichen Relationen
--  RelationFull                         Beschreibung der Relation
--  OpRelation                           entgegengesetzte Relation (Oposition)
--  MAStrat                              MA-Stratigrafie im LDA LSA
--

CREATE TABLE Relationtyp
     (
     WT_RelationtypID                numeric(20,0) identity,
     RelationtyID                    INT NULL,
     RelationCat                     NVARCHAR(255) NULL,
     RelationFull                    NVARCHAR(255) NULL,
     OpRelation                      NVARCHAR(255) NULL,
     MAStrat                         BIT
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Status
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  StatusID                             N/A
--  Status                               N/A
--

CREATE TABLE Status
     (
     StatusID                        INT NULL,
     Status                          NVARCHAR(255) NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_TK25
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  TK25ID                               N/A
--  TK25                                 N/A
--  TK25_alt                             N/A
--  TK25_Name                            N/A
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--

CREATE TABLE TK25
     (
     TK25ID                          INT NULL,
     TK25                            NVARCHAR(255) NULL,
     TK25_alt                        NVARCHAR(255) NULL,
     TK25_Name                       NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: WT_Zeitstellung
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ZeitstellungID                       Zeitstellung Index (relational)
--  Absolut                              Absolute oder relative Datierung
--  Zeitstellung                         Zeitstellung
--  Zeitstellung_kurz                    Zeitstellung Abk�rzung
--  Eintrag                              Automatisch gesetztes Datum des Eintrages zur Kontrolle
--

CREATE TABLE Zeitstellung
     (
     ZeitstellungID                  INT NULL,
     Absolut                         BIT,
     Zeitstellung                    NVARCHAR(255) NULL,
     Zeitstellung_kurz               NVARCHAR(255) NULL,
     Eintrag                         DATETIME NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: z_RT_Archaeologe_Bef
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ID                                   N/A
--  ArchaeologID                         N/A
--  BefNrvon                             N/A
--  BefNrbis                             N/A
--

CREATE TABLE z_RT_Archaeologe_Bef
     (
     z_RT_Archaeologe_BefID          numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ID                              INT NULL,
     ArchaeologID                    INT NULL,
     BefNrvon                        INT NULL,
     BefNrbis                        INT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: z_RT_Archaeologe_Fotos
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ID                                   N/A
--  ArchaeologID                         N/A
--  FilmNrvon                            N/A
--  FilmNrbis                            N/A
--

CREATE TABLE z_RT_Archaeologe_Fotos
     (
     z_RT_Archaeologe_FotosID        numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ID                              INT NULL,
     ArchaeologID                    INT NULL,
     FilmNrvon                       INT NULL,
     FilmNrbis                       INT NULL
     )
go


-------------------------------------------------------------------------------
-- TABLE: z_WT_Archaeologen
--
--   FIELD (* means field name changed)  DESCRIPTION
--  -----------------------------------  ----------------------------------------
--  ID                                   N/A
--  Archaeologe                          N/A
--

CREATE TABLE z_WT_Archaeologen
     (
     z_WT_ArchaeologenID             numeric(20,0) identity,
     GrabungAuffindungID             INT NOT NULL,
     ID                              INT NULL,
     Archaeologe                     NVARCHAR(255) NULL
     )
go


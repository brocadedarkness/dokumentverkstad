# Användarguide

Den här guiden beskriver den funktionalitet som finns implementerad efter Iteration 5.

Dokumentverkstad är i detta läge en lokal webbapplikation för att registrera Documents, gå igenom nya Documents i Inbox, fånga noteringar som Knowledge Objects, arbeta med Projects och registrera PDF-filer från en konfigurerad Ingest Source.

## Starta Dokumentverkstad

Från projektets rot:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad run
```

Om inget kommando anges startar webbservern också:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad
```

Som standard körs webbgränssnittet på:

```text
http://127.0.0.1:8000/
```

Startsidan är Inbox.

## Konfiguration

Dokumentverkstad läser en TOML-fil.

Sökordningen är:

1. explicit config med `--config`,
2. miljövariabeln `DOKUMENTVERKSTAD_CONFIG`,
3. `dokumentverkstad.toml` i aktuell katalog,
4. inbyggda standardvärden.

Exempel:

```toml
archive_root = ".dokumentverkstad/archive"
runtime_root = ".dokumentverkstad/runtime"
ingest_source = ".dokumentverkstad/ingest"
host = "127.0.0.1"
port = 8000
```

Relativa sökvägar tolkas relativt config-filens katalog.

Om katalogerna inte finns skapas de normalt automatiskt första gången Dokumentverkstad används.

Om du vill använda andra kataloger ändrar du `archive_root`, `runtime_root` eller `ingest_source` i config-filen. Ange kataloger som programmet har rätt att skapa och skriva till.

## Archive Root

`archive_root` är den beständiga lagringen.

Om katalogen saknas skapas den automatiskt vid start.

Här sparas:

* Documents,
* original-PDF när sådan finns,
* extraherad dokumenttext,
* Knowledge Objects,
* Projects,
* Relations,
* Trash-status för Documents.

Archive är den auktoritativa datakällan. Runtime och index kan återskapas från Archive.

## Runtime Root

`runtime_root` är lokal och återskapbar arbetsdata.

Om katalogen saknas skapas den automatiskt vid start.

Efter Iteration 5 används runtime för:

* staging-kopia vid PDF-ingest,
* SQLite-index över Documents.

Runtime ska inte betraktas som beständig användardata.

## Ingest Source

`ingest_source` är en lokal katalog där PDF-filer kan placeras.

Om katalogen saknas skapas den automatiskt vid start eller när `process-ingest` körs.

Dropbox, iCloud eller liknande kan användas genom att deras klient synkar filer till denna lokala katalog. Dokumentverkstad använder ingen Dropbox- eller moln-API-integration.

## Manuell Document-registrering

Öppna:

```text
/documents
```

Ange en titel och skapa dokumentet.

Ett manuellt Document saknar digital originalfil men fungerar ändå som context för Capture och kan kopplas till Knowledge Objects.

Nya manuellt skapade Documents hamnar i Inbox med status `new`.

## PDF-import

Placera en PDF i den konfigurerade `ingest_source`.

Om Ingest Source-katalogen inte finns ännu kan du först starta Dokumentverkstad eller köra `process-ingest` en gång, så skapas katalogen.

Kör sedan:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad process-ingest
```

Systemet gör då en enkel ingest-pass:

* hittar PDF-filer i Ingest Source,
* kopierar varje PDF till lokal runtime för bearbetning,
* beräknar SHA-256-checksumma,
* hoppar över exakta dubbletter,
* skapar ett vanligt Document,
* sparar originalfilen i Archive,
* extraherar grundläggande metadata när möjligt,
* extraherar maskinläsbar text till Archive,
* lägger det nya Document i Inbox,
* bygger om Document-indexet.

Inga Knowledge Objects skapas automatiskt och ingen AI-analys körs.

Endast PDF med maskinläsbar text stöds. OCR finns inte.

## Inbox

Öppna:

```text
/
```

eller:

```text
/inbox
```

Inbox visar Documents som väntar på beslut.

Efter Iteration 5 kan Inbox visa:

* nya Documents,
* Documents markerade som senare.

För varje Document kan du:

* öppna Document-vyn,
* koppla dokumentet direkt till ett eller flera Projects,
* markera dokumentet som klart,
* markera dokumentet som senare,
* kasta dokumentet till Trash.

Inbox är inte en separat lagringsplats. Den visar Documents utifrån deras sparade status i Archive.

Om Inbox saknar objekt visas ett tomt tillstånd.

## Trash och Restore

Öppna:

```text
/trash
```

Documents som kastas från Inbox får status `trashed` och visas i Trash.

Från Trash kan ett Document återställas. Ett återställt Document får status `new` och visas i Inbox igen.

Trash är minimal i denna iteration. Inga permanenta raderingar görs automatiskt.

## Document-vy

Öppna ett Document från:

```text
/documents
```

Document-vyn visar:

* titel,
* om originalfil finns,
* länk till original-PDF när sådan finns,
* direkt kopplade Projects,
* Inbox-status,
* Capture med Document som context,
* Knowledge Objects kopplade till dokumentet.

Original-PDF öppnas via webbläsaren som en PDF-fil. Dokumentverkstad innehåller ingen egen PDF-läsare.

## Capture

Capture finns på `/capture` och i Document- och Project-vyer.

I Capture:

* `Enter` sparar aktuell notering,
* `Shift+Enter` infogar radbrytning,
* fältet töms efter sparande,
* fokus återgår till fältet.

En notering kan skapas utan Document, Project eller Relation.

När Capture öppnas från ett Document föreslås aktuellt Document som källa.

## Source Location

I Document-context kan en enkel källposition anges för en notering.

Exempel:

```text
s. 35
kapitel 4
ungefär i mitten
```

Källpositionen är fritext och normaliseras inte.

## Projects

Öppna:

```text
/projects
```

Där kan du:

* skapa Project,
* redigera namn och beskrivning,
* öppna Project-vy,
* använda Capture med Project som context,
* koppla Documents direkt till Project från Inbox,
* koppla befintliga Knowledge Objects till Project,
* skapa enkla relationer mellan Knowledge Objects.

Ett Knowledge Object kan tillhöra flera Projects.

Ett Document kan också kopplas direkt till flera Projects.

Project-vyn visar relevanta Documents både genom direkta Document-Project-kopplingar och genom de Knowledge Objects som ingår i projektet. Documents läggs inte i projektet som en mapp; kopplingen uttrycker att dokumentet är relevant arbetsmaterial.

## Rebuild Index

SQLite-indexet över Documents kan återskapas från Archive:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad rebuild-index
```

Indexet lagras i:

```text
runtime_root/sqlite/documents.sqlite3
```

Indexet är inte auktoritativt.

## Katalogstruktur

Exempel:

```text
.dokumentverkstad/
  archive/
    documents/
      doc_<id>/
        metadata.json
        original.pdf
        processing/
          text.txt
    knowledge/
      ko_<id>/
        object.json
    projects/
      project_<id>/
        metadata.json
    relations/
      rel_<id>/
        relation.json
    trash/
  runtime/
    ingest/
    sqlite/
      documents.sqlite3
  ingest/
    rapport.pdf
```

Manuella Documents har normalt bara `metadata.json`.

## Begränsningar

Följande finns inte efter Iteration 5:

* AI,
* AI-review,
* AI-kandidater,
* automatiska permanenta raderingar,
* OCR,
* EPUB-import,
* avancerad sökning,
* PDF-highlights,
* egen PDF-läsare,
* automatisk bakgrundsbevakning av Ingest Source.

PDF-ingest körs som ett explicit kommando. Det är ett enkelt registreringsflöde, inte en kontinuerlig tjänst.

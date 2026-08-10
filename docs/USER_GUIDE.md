# Användarguide

Den här guiden beskriver den funktionalitet som finns implementerad efter Iteration 6.

Dokumentverkstad är i detta läge en lokal webbapplikation för att registrera Documents, se väntande arbete i Inbox, fånga noteringar som Knowledge Objects, arbeta med Projects, registrera PDF-filer från en konfigurerad Ingest Source och köra valfri AI-analys efter uttryckligt godkännande.

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
ai_provider = "openai"
ai_model = "gpt-5.6-luna"
ai_output_language = "sv"
ai_currency = "USD"
ai_cost_limit = 0
secrets_path = ".dokumentverkstad/secrets.toml"
```

Relativa sökvägar tolkas relativt config-filens katalog.

Om katalogerna inte finns skapas de normalt automatiskt första gången Dokumentverkstad används.

Om du vill använda andra kataloger ändrar du `archive_root`, `runtime_root`, `ingest_source` eller `secrets_path` i config-filen. Ange kataloger som programmet har rätt att skapa och skriva till.

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
* AI-körningar och AI-kandidaters proveniens,
* Trash-status för Documents.

Archive är den auktoritativa datakällan. Runtime och index kan återskapas från Archive.

## Runtime Root

`runtime_root` är lokal och återskapbar arbetsdata.

Om katalogen saknas skapas den automatiskt vid start.

Efter Iteration 6 används runtime för:

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
* flyttar färdigbehandlade PDF-filer till `runtime_root/ingest/processed`,
* bygger om Document-indexet.

Inga Knowledge Objects skapas automatiskt och ingen AI-analys körs.

Endast PDF med maskinläsbar text stöds. OCR finns inte.

Om en PDF inte kan bearbetas ligger den kvar i Ingest Source så att felet kan undersökas och filen kan försökas igen senare.

## Inbox

Öppna:

```text
/
```

eller:

```text
/inbox
```

Inbox visar Documents och AI-kandidater som väntar på beslut.

Efter Iteration 6 kan Inbox visa:

* nya Documents,
* Documents markerade som senare,
* AI-genererade kandidater som väntar på review,
* AI-genererade kandidater som skjutits upp.

För varje Document kan du:

* öppna Document-vyn,
* koppla dokumentet direkt till ett eller flera Projects,
* markera dokumentet som klart,
* markera dokumentet som senare,
* kasta dokumentet till Trash.

Inbox är inte en separat lagringsplats. Den visar Documents utifrån deras sparade status i Archive.

För varje väntande AI-kandidat visar Inbox en egen post med kandidattyp, vilket Document kandidaten hör till, en kort identifiering och en länk för att granska kandidaten på Document-sidan.

AI-kandidater accepteras, redigeras, avvisas eller skjuts upp från Document-sidan, inte direkt från Inbox. När en AI-kandidat har behandlats försvinner dess Inbox-post automatiskt.

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
* möjlighet att förbereda AI-analys när extraherad text finns,
* tidigare AI-körningar,
* väntande AI-kandidater med review-formulär,
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

## AI

AI är valfritt. Dokumentverkstad fungerar för Capture, Documents, Projects, Inbox och PDF-ingest utan API-nyckel.

Första AI-providern är OpenAI. Provider och modell styrs av konfiguration:

```toml
ai_provider = "openai"
ai_model = "gpt-5.6-luna"
```

API-nyckeln söks i denna ordning:

1. miljövariabeln `OPENAI_API_KEY`,
2. lokal secrets-fil enligt `secrets_path`, normalt `.dokumentverkstad/secrets.toml`,
3. ingen konfigurerad AI-provider.

Exempel på secrets-fil:

```toml
[openai]
api_key = "..."
```

Secrets-filen ligger lokalt på maskinen, inte i Archive. Den ska inte versionshanteras och är ignorerad i Git.

Om ingen API-nyckel finns kan webbappen fortfarande startas. När du försöker använda AI visas ett begripligt meddelande om att nyckel saknas.

## Köra AI-analys

AI-analys startas från ett Document som har extraherad text, exempelvis ett PDF-dokument som registrerats med `process-ingest`.

Öppna Document-vyn och välj:

```text
Förbered AI-analys
```

Bekräftelsesidan visar:

* vilket Document som ska analyseras,
* provider,
* modell,
* capabilities,
* uppskattade input-token,
* planerade max output-token,
* uppskattad kostnad.

Uppskattningen görs lokalt med en konservativ teckenbaserad tokenuppskattning. Dokumenttext skickas inte till OpenAI för kostnadsestimatet.

AI-anropet körs först när du väljer:

```text
Starta AI-analys
```

Det som skickas till OpenAI är:

* dokumentets titel,
* den extraherade dokumenttexten från Archive,
* namn och ID för befintliga Projects,
* systemets promptversion och instruktion om strukturerat resultat.

Original-PDF skickas inte.

AI-resultatet sparas som kandidater, inte som etablerad kunskap. Kandidaterna visas i Inbox som väntande poster som länkar till dokumentet.

På Document-sidan visas väntande AI-kandidater grupperade i ordningen Summary, Claims, Insights, Questions och Project Suggestions. Där kan du acceptera, redigera och acceptera, skjuta upp eller avvisa varje kandidat. Vid avvisning kan du ange en frivillig avvisningsorsak.

När en AI-kandidat accepteras blir den ett accepterat Knowledge Object. AI:s originalförslag bevaras även om du redigerar formuleringen. Efter varje beslut återgår sidan till samma Document så att resten av AI-resultatet kan reviewas utan att lämna dokumentet.

Efter körningen sparas en AI-körning i Archive med:

* provider,
* modell,
* promptversion,
* capabilities,
* uppskattad tokenanvändning,
* uppskattad kostnad,
* faktisk tokenanvändning när API:t rapporterar den,
* faktisk beräknad kostnad,
* status,
* kandidat-ID:n.

Om AI-anropet misslyckas sparas ingen accepterad kunskap automatiskt. Dokumentet och tidigare Knowledge Objects påverkas inte.

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
    ai_runs/
      airun_<id>/
        run.json
    trash/
  runtime/
    ingest/
      processed/
    sqlite/
      documents.sqlite3
  secrets.toml
  ingest/
    rapport.pdf
```

Manuella Documents har normalt bara `metadata.json`.

## Begränsningar

Följande finns inte efter Iteration 6:

* automatiska permanenta raderingar,
* lokal AI,
* AI-chatt med dokument,
* RAG,
* embeddings,
* semantisk sökning,
* automatisk AI-router,
* AI-genererade projektsynteser,
* AI-genererade General Insights,
* OCR,
* EPUB-import,
* avancerad sökning,
* PDF-highlights,
* egen PDF-läsare,
* automatisk bakgrundsbevakning av Ingest Source.

PDF-ingest körs som ett explicit kommando. Det är ett enkelt registreringsflöde, inte en kontinuerlig tjänst.

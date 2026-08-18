# Användarguide

Den här guiden beskriver den funktionalitet som finns implementerad efter Iteration 8.4a.

Dokumentverkstad är i detta läge en lokal webbapplikation för att registrera Documents, korrigera Document-metadata, se väntande arbete i Inbox, fånga och redigera noteringar som Knowledge Objects, arbeta med Projects, registrera PDF-filer från en konfigurerad Ingest Source eller webb-upload, köra valfri AI-analys efter uttryckligt godkännande, korrigera AI-reviewbeslut och se enkel AI-/review-statistik.

## Första initiering

Från projektets rot:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad init
```

Detta skapar standardconfig, Archive, Runtime och Ingest Source om de saknas. Befintlig config skrivs inte över.

För att samtidigt skapa krypterad secrets-lagring och spara en OpenAI API key:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad init --with-openai
```

Du får då ange ett adminlösenord två gånger och därefter API-nyckeln. Både adminlösenord och API-nyckel läses utan terminal-echo.

## Starta Dokumentverkstad

Från projektets rot:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad start
```

`run` fungerar också och är samma startflöde. Om inget kommando anges startar webbservern också.

Som standard körs webbgränssnittet på:

```text
http://127.0.0.1:8000/
```

Standardservern lyssnar bara på `127.0.0.1`. Det är avsiktligt: lokal användning ska vara standard och Dokumentverkstad öppnar inte sig själv mot hela nätverket.

Startsidan är Inbox.

Om `.dokumentverkstad/secrets.enc` finns begär startflödet adminlösenord innan webbservern startar. Vid fel lösenord eller skadad secrets-fil startar inte tjänsten.

En installation utan krypterade secrets startar utan adminlösenord och kan användas utan AI.

## Privat fjärråtkomst med Tailscale Serve

Dokumentverkstad kan nås från egna enheter via Tailscale Serve utan att webbservern ändras från `127.0.0.1`.

Modellen är:

```text
Mobil/iPad/annan egen dator
    ↓
Tailscale tailnet
    ↓
Tailscale Serve
    ↓
127.0.0.1:8000
    ↓
Dokumentverkstad
```

Tailscale ska vara installerat och autentiserat på serverdatorn. Klientenheten måste också vara inloggad i samma tailnet eller tillåten av tailnetets policy.

Starta först Dokumentverkstad lokalt:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad start
```

Starta därefter Serve mot den lokala porten:

```powershell
tailscale serve 8000
```

Om du vill vara explicit om localhost-målet kan du i stället använda:

```powershell
tailscale serve localhost:8000
```

Kontrollera aktiv Serve-konfiguration:

```powershell
tailscale serve status
```

Statusutskriften visar vilken tailnet-adress eller MagicDNS-URL som ska öppnas på mobil, iPad eller annan dator. Öppna den adressen från en enhet som har åtkomst i tailnetet.

Stäng av/resetta Serve-konfigurationen:

```powershell
tailscale serve reset
```

Använd inte Tailscale Funnel för Dokumentverkstad i denna iteration. Tjänsten ska inte exponeras publikt mot internet.

Säkerhetsmodellen i 8.4a är nätverksbaserad: Tailscale/tailnetet avgör vem som kan nå webbgränssnittet. Det finns inget separat webb-login eller sessionsautentisering. Alla enheter och användare som har nätverksåtkomst till tjänsten kan använda webbgränssnittet. Adminlösenordet för krypterade secrets är bara en lokal upplåsning vid processstart och är inte ett webb-login. Om tjänsten senare delas med andra användare eller exponeras på annat sätt måste webbautentisering och behörigheter omprövas.

Kontrollera installationen:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad status
```

Status visar config-, Archive- och Runtime-sökvägar, om Archive är läsbart, om Runtime och SQLite-index finns, antal Documents, Knowledge Objects, Projects, AI-runs och Trash-objekt, samt credential-status utan att visa credential. Saknad OpenAI-nyckel är inte ett driftfel eftersom AI är valfritt.

Health kan vara:

* `ok`: inga kända driftproblem,
* `warning`: systemet kan användas men något bör åtgärdas, exempelvis saknad Runtime eller saknat index,
* `error`: ett grundläggande problem finns, exempelvis att Archive saknas eller inte kan läsas.

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
upload_max_bytes = 262144000
ai_provider = "openai"
ai_model = "gpt-5.6-luna"
ai_max_output_tokens = 6000
ai_output_language = "sv"
ai_currency = "USD"
ai_cost_limit = 0
encrypted_secrets_path = ".dokumentverkstad/secrets.enc"
secrets_path = ".dokumentverkstad/secrets.toml"
```

Relativa sökvägar tolkas relativt config-filens katalog.

Om katalogerna inte finns skapas de normalt automatiskt första gången Dokumentverkstad används.

Om du vill använda andra kataloger ändrar du `archive_root`, `runtime_root`, `ingest_source`, `encrypted_secrets_path` eller `secrets_path` i config-filen. Ange kataloger som programmet har rätt att skapa och skriva till.

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

Archive är den auktoritativa datakällan. Runtime och index kan återskapas från Archive. En vanlig backup innehåller Archive men inte Runtime, Ingest Source eller secrets.

## Runtime Root

`runtime_root` är lokal och återskapbar arbetsdata.

Om katalogen saknas skapas den automatiskt vid start.

Efter Iteration 8.2 används runtime för:

* staging-kopia vid PDF-ingest,
* säker staging för webb-uppladdade PDF-filer,
* färdigbehandlade ingest-filer i `runtime_root/ingest/processed`,
* SQLite-index över Documents,
* lokal diagnostiklogg i `runtime_root/logs/dokumentverkstad.log`.

Runtime ska inte betraktas som beständig användardata. Hela `runtime_root` kan tas bort och återskapas från Archive genom `rebuild-index`; pågående eller obehandlade filer ska ligga i Ingest Source eller Archive, inte i Runtime.

## Ingest Source

`ingest_source` är en lokal katalog där PDF-filer kan placeras.

Om katalogen saknas skapas den automatiskt vid start eller när `process-ingest` körs.

Dropbox, iCloud eller liknande kan användas genom att deras klient synkar filer till denna lokala katalog. Dokumentverkstad använder ingen Dropbox- eller moln-API-integration.

## Manuell Document-registrering

Öppna:

```text
/documents/new
```

Ange en titel och skapa dokumentet.

Du kan även ange upphov och utgivningsår direkt. Utgivningsår ska vara ett fyrsiffrigt år eller lämnas tomt.

Ett manuellt Document saknar digital originalfil men fungerar ändå som context för Capture och kan kopplas till Knowledge Objects.

Nya manuellt skapade Documents hamnar i Inbox med status `new`.

## Document-överblick

Sidan `/documents` visar registrerade Documents med titel, upphov och utgivningsår när dessa finns. Varje rad visar också om dokumentet har minst en slutförd AI-analys samt hur många egna användarskapade Captures som är kopplade till dokumentet.

Överblicken kan filtreras på:

* snabb sökning i titel, upphov och utgivningsår,
* AI-analyserade eller ej AI-analyserade Documents,
* Project-koppling.

Snabbsökningen söker bara i Document-metadata. Den söker inte i extraherad dokumenttext, Captures, Claims, Insights eller Questions.

Listan kan sorteras på titel, utgivningsår eller senast tillagd. Standardordningen är utgivningsår: dokument med årtal visas före dokument utan årtal och nyare årtal visas först.

Manuell Document-registrering finns kvar som en sekundär ingång via länken "Skapa Document manuellt".

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
* använder filnamn på formen `ÅÅÅÅ Titel.pdf` som fallback för titel och utgivningsår när PDF-metadata saknas eller inte är användbar,
* extraherar maskinläsbar text till Archive,
* lägger det nya Document i Inbox,
* flyttar färdigbehandlade PDF-filer till `runtime_root/ingest/processed`,
* bygger om Document-indexet.

Inga Knowledge Objects skapas automatiskt och ingen AI-analys körs.

Endast PDF med maskinläsbar text stöds. OCR finns inte.

Metadata prioriteras enkelt: användbar PDF-metadata används först, filnamnsmönstret används som fallback för titel och år, och manuell redigering räknas därefter som användarens korrigering. Originalfilens namn sparas alltid.

Om en PDF inte kan bearbetas ligger den kvar i Ingest Source så att felet kan undersökas och filen kan försökas igen senare.

## Webb-upload av PDF

Öppna:

```text
/upload
```

eller välj länken "Lägg till PDF" från Inbox.

Uploadflödet accepterar PDF-filer från desktop och mobil webbläsare. När en PDF laddas upp behandlas den som en vanlig ingest-PDF:

* filen tas emot i säker staging under Runtime,
* klientens filnamn saneras och får inte styra lokal sökväg,
* innehållet kontrolleras så att det ser ut som PDF, inte bara att filändelsen är `.pdf`,
* SHA-256-checksumma beräknas,
* exakta dubbletter stoppas,
* PDF-text och metadata extraheras,
* filnamn på formen `ÅÅÅÅ Titel.pdf` används som fallback för titel och år,
* originalfilen sparas i Archive,
* det nya dokumentet hamnar i Inbox,
* SQLite-indexet byggs om.

Webb-upload skapar alltså inte en separat typ av Document. En PDF är ett vanligt Document oavsett om den kom från Ingest Source eller från webbläsaren.

Standardgränsen för upload är:

```toml
upload_max_bytes = 262144000
```

Det motsvarar 250 MB och är valt för att rymma stora skannade eller bildrika PDF-filer utan att göra webbservern obegränsad. Värdet kan ändras i `dokumentverkstad.toml`.

Om samma PDF redan finns i Archive skapas inget nytt Document. Webbgränssnittet visar då att PDF-filen redan finns i Archive.

Andra filformat än PDF avvisas i 8.4a. EPUB, DOCX, OCR och liknande import ligger utanför denna iteration.

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
* Documents som har AI-genererade kandidater som väntar på review eller har skjutits upp.

För varje Document kan du:

* öppna Document-vyn,
* koppla dokumentet direkt till ett eller flera Projects,
* markera dokumentet som klart,
* markera dokumentet som senare,
* kasta dokumentet till Trash.

Inbox är inte en separat lagringsplats. Den visar Documents utifrån deras sparade status i Archive.

För AI-review visar Inbox en post per Document som har minst en väntande AI-kandidat. Posten visar Document-titel, antal väntande AI-kandidater och en länk för att granska dem på Document-sidan.

AI-kandidater accepteras, redigeras, avvisas eller skjuts upp från Document-sidan, inte direkt från Inbox. När en kandidat har behandlats uppdateras antalet i Inbox. När inga kandidater längre väntar för ett Document försvinner Documentets AI-review-post automatiskt.

Om Inbox saknar objekt visas ett tomt tillstånd.

## Trash och Restore

Öppna:

```text
/trash
```

Documents som kastas från Inbox får status `trashed` och visas i Trash. Trash-status lagras i Documentets `metadata.json` i Archive.

Från Trash kan ett Document återställas. Ett återställt Document får status `new` och visas i Inbox igen.

Restore skapar inte en ny kopia av dokumentet och påverkar inte Knowledge Object-historik eller befintliga relationer.

Permanent radering finns som ett uttryckligt val i Trash-vyn. Den kräver bekräftelse och är bara möjlig för Documents som redan ligger i Trash.

Permanent radering blockeras om Dokumentverkstad hittar kända Archive-referenser till dokumentet, exempelvis Knowledge Objects eller AI-runs. I så fall ligger dokumentet kvar i Trash tills referenserna kan hanteras säkert.

Ingen automatisk permanent radering görs.

## Document-vy

Öppna ett Document från:

```text
/documents
```

Document-vyn visar:

* titel,
* upphov och utgivningsår när de finns,
* om originalfil finns,
* länk till original-PDF när sådan finns,
* direkt kopplade Projects,
* möjlighet att förbereda AI-analys när extraherad text finns,
* tidigare AI-körningar,
* väntande AI-kandidater med review-formulär,
* Capture med Document som context,
* Knowledge Objects kopplade till dokumentet.

I Document-vyn finns också ett metadataformulär där titel, upphov och utgivningsår kan korrigeras utan manuell ändring av JSON-filer. Ändringen sparas i Archive och överlever omstart.

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

Befintliga Captures/Knowledge Objects kan redigeras från listorna där de visas. Det går att korrigera både innehåll och källposition. Den tidigare versionen sparas i objektets historik i Archive; UI:t visar normalt den senaste versionen.

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
ai_max_output_tokens = 6000
```

API-nyckeln söks i denna ordning:

1. miljövariabeln `OPENAI_API_KEY`,
2. upplåsta krypterade secrets enligt `encrypted_secrets_path`, normalt `.dokumentverkstad/secrets.enc`,
3. legacy `secrets.toml` enligt `secrets_path`,
4. ingen credential.

Miljövariabeln finns kvar för utveckling och kompatibilitet. Normal lokal drift bör använda krypterade secrets.

Skapa eller ersätt OpenAI API key senare:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad secrets set-openai
```

Ta bort OpenAI API key:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad secrets remove-openai
```

Initiera krypterade secrets utan API-nyckel:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad secrets init
```

Secrets-filen ligger lokalt på maskinen, inte i Archive. `.dokumentverkstad/secrets.enc` är ignorerad i Git. Den krypterade filen använder JSON-envelope med `version`, `kdf`, `kdf_parameters`, `salt`, `cipher`, `nonce` och `ciphertext`. Payloaden innehåller initialt provider-data som kan innehålla `providers.openai.api_key`.

Kryptering:

* KDF: `scrypt` med `n = 16384`, `r = 8`, `p = 1`, `length = 32`.
* Salt: 16 slumpmässiga bytes per filskrivning.
* AEAD: AES-256-GCM.
* Nonce: 12 slumpmässiga bytes per filskrivning.

Legacy `.dokumentverkstad/secrets.toml` kan fortfarande läsas om ingen miljövariabel eller upplåst encrypted secret finns. Den skrivs inte om eller raderas automatiskt. Migrera genom att köra `python -m dokumentverkstad secrets set-openai`, verifiera att AI fungerar, och ta sedan bort eller arkivera legacy-filen manuellt.

Om ingen API-nyckel finns kan webbappen fortfarande startas. När du försöker använda AI visas ett begripligt meddelande om att nyckel saknas.

## Glömt adminlösenord

Adminlösenordet kan inte återställas. Det skyddar endast secrets, inte Archive.

Om lösenordet glöms bort:

1. kassera `.dokumentverkstad/secrets.enc`,
2. återkalla gamla externa API-nycklar hos leverantören,
3. kör `python -m dokumentverkstad secrets init` eller `python -m dokumentverkstad init --with-openai`,
4. skapa och spara en ny API-nyckel,
5. fortsätt använda samma Archive.

Archive påverkas inte av att secrets-filen byts ut.

## Backup

Skapa en backup från projektets rot:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad backup
```

Backupfilen skapas som standard i aktuell katalog med ett namn på formen:

```text
dokumentverkstad-backup-2026-08-18T103000Z.zip
```

Du kan välja målkatalog:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad backup --output-dir C:\Backups
```

Backupen är ett vanligt ZIP-arkiv. Den innehåller:

* `backup-manifest.json` med backupformat, skapandetid, applikationsversion och objekträknare,
* `config/portable.json` med portabel icke-hemlig AI-konfiguration,
* `archive/` med Dokumentverkstads öppna Archive-struktur.

Backupen innehåller inte:

* `.dokumentverkstad/secrets.enc`,
* legacy `.dokumentverkstad/secrets.toml`,
* adminlösenord eller API-nycklar,
* Runtime eller SQLite-index,
* Ingest Source,
* staging- eller processed-ingest-filer.

Backup-kommandot skriver först till en temporär fil och byter namn när ZIP-filen har skapats och verifierats. En befintlig backupfil skrivs inte över; kommandot väljer ett unikt namn.

## Restore

Återställ en backup till en ny eller tom installation:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad restore dokumentverkstad-backup-2026-08-18T103000Z.zip
```

Restore validerar ZIP-filen, manifestet och alla sökvägar innan Archive skrivs. ZIP-medlemmar med `../`, absoluta paths, Windows-drive-prefix eller backslash-paths avvisas.

Restore skriver inte tyst över ett Archive som redan innehåller filer. Om du uttryckligen vill ersätta ett befintligt Archive:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad restore dokumentverkstad-backup-2026-08-18T103000Z.zip --force
```

Även med `--force` valideras backupen och packas upp till staging innan befintligt Archive ersätts.

Efter restore återskapas SQLite-indexet automatiskt från Archive. Secrets återställs inte; konfigurera dem separat med exempelvis:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad secrets set-openai
```

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
* planerade max output-token enligt `ai_max_output_tokens`,
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

AI-resultatet sparas som kandidater, inte som etablerad kunskap. Inbox visar en AI-review-post per Document som har väntande kandidater och länkar till dokumentet.

På Document-sidan visas väntande AI-kandidater grupperade i ordningen Summary, Claims, Insights, Questions och Project Suggestions.

Summary, Claims, Insights och Questions kan accepteras, redigeras och accepteras, skjutas upp eller avvisas. Vid avvisning kan du ange en frivillig avvisningsorsak.

Project Suggestions är annorlunda. De är förslag om att koppla dokumentet till ett befintligt Project, inte kunskap som ska bli ett Knowledge Object. För dem kan du välja att koppla dokumentet till projektet eller avvisa förslaget. Förslaget visas bara om det kan kopplas entydigt till ett befintligt Project. Om projektet är okänt, eller om dokumentet redan är kopplat till det föreslagna projektet, visas inte förslaget.

När Summary, Claim, Insight eller Question accepteras blir den ett accepterat Knowledge Object. AI:s originalförslag bevaras även om du redigerar formuleringen. Efter varje beslut återgår sidan till samma Document så att resten av AI-resultatet kan reviewas utan att lämna dokumentet.

Tidigare AI-reviewbeslut visas på Document-sidan och kan korrigeras. En accepterad kandidat kan markeras som avvisad och en avvisad kandidat kan markeras som accepterad igen. AI:s originalförslag ändras inte, och tidigare beslut sparas i Knowledge Object-historiken. Om ett accepterat objekt korrigeras till avvisat visas det inte längre som etablerad kunskap. Project Suggestions hanteras konsekvent genom att den föreslagna Document-Project-kopplingen tas bort om ett tidigare länkat förslag korrigeras till avvisat.

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

AI-anrop körs fortfarande synkront i webbrequesten i Iteration 7.1. Terminalen visar därför enkel diagnostik för AI-körningens start, provider-tid, slutförande eller fel, utan att logga dokumenttext eller API-nycklar.

## Administration

Öppna:

```text
/admin
```

Administrationsvyn är en enkel stödvy för AI- och review-statistik. Den är inte en ny primär arbetsyta.

Vyn visar:

* antal genomförda AI-körningar,
* total faktisk AI-kostnad,
* faktisk kostnad per modell,
* input- och output-tokenanvändning,
* användning per modell,
* användning per promptversion,
* användning per månad,
* antal AI-kandidater per typ,
* accepterade kandidater,
* redigerade och accepterade kandidater,
* avvisade kandidater,
* väntande och uppskjutna kandidater,
* behandlade Project Suggestions,
* avvisningsorsaker när sådana har sparats.

Statistiken beräknas från sparade AI-körningar och AI-kandidater i Archive. Runtime används inte som källa för statistiken och kan raderas utan att historiken går förlorad.

Dokumentverkstad ändrar inte promptar, modeller eller review-flöden automatiskt utifrån statistiken. Informationen är endast ett underlag för användarens egen förståelse.

Webbservern loggar långsamma requests med metod, path, status och tid. POST-body, query-parametrar, dokumentinnehåll och secrets loggas inte.

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

Om hela `runtime_root` har tagits bort skapar `rebuild-index` nödvändiga runtime-kataloger och bygger indexet på nytt från Archive.

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
  secrets.enc
  secrets.toml  (legacy, om den finns)
  ingest/
    rapport.pdf
```

Manuella Documents har normalt bara `metadata.json`.

## Begränsningar

Följande finns inte efter Iteration 8.4a:

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
* EPUB-/DOCX-upload,
* avancerad sökning,
* PDF-highlights,
* egen PDF-läsare,
* separat webb-login eller sessionsautentisering,
* PWA, native mobile-app eller Share Sheet-extension,
* automatisk bakgrundsbevakning av Ingest Source.

Katalogbaserad PDF-ingest körs som ett explicit kommando. Webb-upload är en manuell webbfunktion. Inget av flödena är en kontinuerlig bakgrundstjänst.

## Manuellt acceptanstest för fjärråtkomst

Det verkliga Tailscale-flödet behöver verifieras manuellt på dina enheter:

1. Starta Dokumentverkstad på serverdatorn med `python -m dokumentverkstad start`.
2. Starta Tailscale Serve med `tailscale serve 8000` eller `tailscale serve localhost:8000`.
3. Kontrollera adressen med `tailscale serve status`.
4. Anslut mobil, iPad eller annan dator till samma tailnet.
5. Öppna Serve-adressen från klientenheten.
6. Navigera i Documents och Inbox.
7. Ladda upp en verklig PDF via "Lägg till PDF".
8. Verifiera att den visas som ett normalt Document i Archive/Inbox.

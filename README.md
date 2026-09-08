# Dokumentverkstad

Dokumentverkstad är en personlig dokument- och kunskapsmiljö för kumulativt
kunskapsarbete.

Den bevarar dokument, egna noteringar och AI-stödda kunskapsförslag i ett
öppet arkiv där människans granskning är avgörande. Ambitionen är ett enda
auktoritativt Archive som kan köras på en egen server, medan datorer, telefoner
och surfplattor fungerar som klienter till samma kunskapsrum.

## Idé

Dokumentverkstad är inte en vanlig filsamling och inte en AI-chatt.

Ett Document är en bevarad källa. Kunskap uppstår som Knowledge Objects:
sammanfattningar, påståenden, insikter, frågor och egna noteringar. Dessa kan
knytas till dokument och projekt, bära proveniens och utvecklas över tid.

AI används som assistent för att föreslå kunskap, inte som auktoritet. AI-run,
modell, promptversion, kostnad och förslag sparas med proveniens, och förslag
blir etablerad kunskap först efter mänsklig granskning.

## Vad finns idag

Den nuvarande implementationen innehåller:

* server-renderat webbgränssnitt med Inkorg, Dokument, Projekt och Notering,
* PDF-ingest via konfigurerad ingest-katalog och webbuppladdning,
* gemensam ingest-semantik med checksumma, dublettkontroll, textutvinning,
  metadata och bevarad originalfil,
* dokumentbibliotek och dokumentvy med metadata, källtext, noteringar och
  AI-granskning,
* projekt som frivilliga sammanhang, inte mappar eller obligatoriska kategorier,
* fristående noteringar samt noteringar i dokument- och projektsammanhang,
* AI-analys som bakgrundsarbete med persistent AiRun-status och reviewflöde,
* accepterade, avvisade och uppskjutna AI-förslag där befintlig semantik stöder
  det,
* backup, restore, återskapande av index, statuskommando och driftloggning,
* separat web- och workerprocess för serverdrift.

Dokumentverkstad har ännu inte publik webbexponering, inloggning, HTTPS,
reverse proxy, DNS-konfiguration, OCR, EPUB, semantic search, embeddings eller
RAG.

## Kunskapsmodell

```text
Document
  -> källa, originalfil, metadata, extraherad text

Knowledge Object
  -> Sammanfattning
  -> Påstående
  -> Insikt
  -> Fråga
  -> Notering

Project
  -> frivilligt sammanhang för Documents och Knowledge Objects

AiRun
  -> AI-operation, modell/proveniens, kandidater för mänsklig granskning
```

Archive är den auktoritativa representationen av kunskapsrummet. Runtime är
härlett och kan återskapas från Archive.

## Arkitektur

```text
Browser
  |
  v
Web process
  |
  +-- Archive   beständig kunskap och originalmaterial
  +-- Runtime   index, loggar och temporär arbetsdata

Worker process
  |
  +-- ingest    processar nya PDF:er
  +-- AI jobs   kör planerade AI-analyser
```

Archive och Runtime kan placeras utanför git-repot via config eller environment
variables. Secrets ska hämtas från environment eller separat secrets-fil, inte
checkas in i repo.

## Kom igång lokalt

Installera i en virtuell Python-miljö:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m dokumentverkstad init
python -m dokumentverkstad start
```

På Linux/macOS används motsvarande aktivering:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m dokumentverkstad init
python -m dokumentverkstad start
```

Öppna sedan:

```text
http://127.0.0.1:8000/
```

`start` kör webbservern med inbäddad worker för enkel lokal användning.

För separat web och worker:

```sh
python -m dokumentverkstad run --no-worker
python -m dokumentverkstad worker
```

Vanliga administrativa kommandon:

```sh
python -m dokumentverkstad status
python -m dokumentverkstad backup
python -m dokumentverkstad rebuild-index
```

OpenAI-nyckel för lokal utveckling kan sättas med `OPENAI_API_KEY` eller via
Dokumentverkstads secrets-kommando:

```sh
python -m dokumentverkstad secrets set-openai
```

## Konfiguration

Konfigurationsfil kan anges med:

```sh
python -m dokumentverkstad --config /path/to/dokumentverkstad.toml start
```

eller:

```sh
export DOKUMENTVERKSTAD_CONFIG=/path/to/dokumentverkstad.toml
```

Centrala environment variables:

```text
DOKUMENTVERKSTAD_ARCHIVE_ROOT
DOKUMENTVERKSTAD_RUNTIME_ROOT
DOKUMENTVERKSTAD_INGEST_SOURCE
DOKUMENTVERKSTAD_HOST
DOKUMENTVERKSTAD_PORT
OPENAI_API_KEY
```

## Linux/VPS-status

Dokumentverkstad har verifierats manuellt på en liten Ubuntu-VPS med denna
layout:

```text
/opt/dokumentverkstad/
  git-repo
  .venv/
  dokumentverkstad.toml

/var/lib/dokumentverkstad/
  archive/
  runtime/
  ingest/
```

Web och worker kan köras som två separata systemd-tjänster:

```text
dokumentverkstad-web.service
dokumentverkstad-worker.service
```

Den verifierade serverkonfigurationen lyssnar endast på:

```text
127.0.0.1:8000
```

Externa klienter, domännamn, reverse proxy, HTTPS, autentisering och firewall
hör till kommande deploymentarbete. Exponera inte port 8000 direkt mot
internet.

Detaljer finns i [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Dokumentation

Projektets dokumentation finns i `docs/`.

Bra läsordning:

1. [docs/MANIFEST.md](docs/MANIFEST.md) - projektets riktning och varför det
   finns.
2. [docs/DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md) - övergripande
   designprinciper.
3. [docs/DOMAIN_MODEL.md](docs/DOMAIN_MODEL.md) - Document, Knowledge Object,
   Project och relationer.
4. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Archive, Runtime, ingest,
   AI och systemkomponenter.
5. [docs/WORKFLOWS.md](docs/WORKFLOWS.md) - viktiga arbetsflöden.
6. [docs/USER_GUIDE.md](docs/USER_GUIDE.md) - användardokumentation för
   faktisk funktionalitet.
7. [docs/UI.md](docs/UI.md) och [docs/DESIGN_SYSTEM.md](docs/DESIGN_SYSTEM.md)
   - gränssnitt och visuell identitet.
8. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - lokal drift, Linux/VPS och
   systemd.
9. [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) - aktuell
   utvecklingsplan.
10. [docs/BACKLOG.md](docs/BACKLOG.md) - medvetet uppskjutna idéer och
    framtida kandidater.

## Projektstatus

Dokumentverkstad är ett pågående personligt kunskapssystem. Kärnflödena för
lokal användning, serverförberedelse, systemd-drift, PDF-ingest, dokument,
projekt, noteringar och AI-granskning finns implementerade.

Nästa större område är fortsatt server-/deploymentarbete: privat åtkomst från
andra enheter, reverse proxy, HTTPS, autentisering, firewall och backupstrategi
för faktisk drift.

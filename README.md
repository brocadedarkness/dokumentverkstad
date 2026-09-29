# Dokumentverkstad

Dokumentverkstad är en personlig dokument- och kunskapsmiljö för kumulativt
kunskapsarbete.

Den bevarar dokument, egna noteringar och AI-stödda kunskapsförslag i ett
öppet arkiv där människans granskning är avgörande. Den verifierade v0.1.0
kör ett enda auktoritativt Archive på en egen server, medan datorer, telefoner
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
* dokumentbibliotek och dokumentvy med metadata, original-PDF, noteringar och
  AI-granskning,
* projekt som frivilliga sammanhang, inte mappar eller obligatoriska kategorier,
* fristående noteringar samt noteringar i dokument- och projektsammanhang,
* AI-analys som bakgrundsarbete med persistent AiRun-status och reviewflöde,
* accepterade, avvisade och uppskjutna AI-förslag där befintlig semantik stöder
  det,
* backup, restore, återskapande av index, statuskommando och driftloggning,
* separat web- och workerprocess för serverdrift.

Extern webbåtkomst via Caddy med HTTPS och Basic Auth är driftverifierad.
Applikationen har ingen egen användardatabas eller sessionsinloggning.
OCR, EPUB, kunskapssökning, offline-synk, externt kunskaps-API, semantisk
sökning, embeddings och RAG finns inte i v0.1.0.

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

I verifierad serverdrift körs web och worker som separata systemd-tjänster:

```text
dokumentverkstad-web.service
dokumentverkstad-worker.service
```

Den verifierade serverkonfigurationen lyssnar endast på:

```text
127.0.0.1:8000
```

Caddy ger extern HTTPS-åtkomst med Basic Auth. Tvåklientsflödet, AI med
stängd klient och automatisk återstart efter VPS-reboot är verifierade.
Port 8000 exponeras inte direkt mot internet.

Daglig off-server-backup via systemd och rclone är verifierad, inklusive
återläsning, SHA-256 och separat restore med indexrebuild och skrivtest.
Archive ingår i backupen; Runtime, ingestkön och secrets ingår inte.
Gallring är manuell i v0.1.0. Kör direkt `backup` endast när Archive inte
ändras; följ DEPLOYMENT.md för schemalagd backup och restore.

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
9. [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) - historiken
   fram till godkänd MVP-acceptans.
10. [docs/BACKLOG.md](docs/BACKLOG.md) - medvetet uppskjutna idéer och
    framtida kandidater.
11. [docs/ROADMAP.md](docs/ROADMAP.md) - planerad utveckling efter MVP mot v1.0.
12. [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) och [AGENTS.md](AGENTS.md) -
    utvecklingsarbete, installation och testkommandon.

## Projektstatus

**v0.1.0 / MVP COMPLETE**, godkänd 2026-09-29. Driftacceptans och det
rapporterade Linux-testresultatet 183/183 finns i DEPLOYMENT.md.
ROADMAP.md beskriver kommande arbete; dess v0.2.0-funktioner är inte
implementerade i v0.1.0.

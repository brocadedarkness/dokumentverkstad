# Arkitektur för Dokumentverkstad

## Syfte

Detta dokument beskriver hur Dokumentverkstads manifest, designprinciper och domänmodell översätts till en konkret systemarkitektur.

Arkitekturen ska stödja:

* lokal-first
* enkelhet
* lång livslängd
* öppna format
* portabilitet
* utbytbara AI-modeller
* mänsklig review före etablerad kunskap
* stöd för både digitala och fysiska dokument
* låg kognitiv kostnad för att fånga tankar

Arkitekturen beskriver systemets komponenter och deras ansvar. Den beskriver inte en specifik installation.

Dokumentverkstad ska vara plattformsoberoende. Operativsystemsspecifik funktionalitet ska isoleras till tunna adapterlager.

---

# Grundprincip

Dokumentverkstad skiljer tydligt mellan fyra typer av data.

## 1. Persistent Archive

Den beständiga användardatan.

Detta är den auktoritativa representationen av användarens kunskapsrum.

Den ska kunna flyttas mellan maskiner och överleva implementationer.

Archive Root betraktas som användardata och ska inte versionshanteras tillsammans med applikationens källkod.

---

## 2. Runtime

Tillfälliga data som endast behövs medan systemet arbetar.

Exempel:

* inbox
* jobb
* cache
* index
* loggar

Runtime ska kunna raderas utan att användarens kunskap går förlorad.

---

## 3. Konfiguration

Beskriver hur Dokumentverkstad arbetar.

Exempel:

* arkivets plats
* AI-provider
* modeller
* språk
* kostnadsgränser

Konfiguration är inte användardata.

---

## 4. Externa tjänster

Exempel:

* AI-tjänster
* synkronisering
* nätverk
* PDF-läsare

Dessa ska kunna bytas utan att Dokumentverkstads domänmodell förändras.

---

# Systemets huvudkomponenter

Dokumentverkstad består av följande huvudkomponenter.

* Ingest
* Archive
* Document Engine
* Knowledge Engine
* AI Layer
* Search Index
* Web UI

---

# Ingest

Ingest ansvarar för att ta emot nya dokument.

Alla inkommande dokument passerar genom samma ingest-flöde oavsett ursprung.

Möjliga Ingest Sources är exempelvis:

* lokal katalog
* Dropbox-katalog
* iCloud-katalog
* webbuppladdning
* framtida integrationer

Ingest Sources är utbytbara.

De producerar alltid samma interna resultat:

> Ett registrerat Document.

---

# Runtime

Runtime innehåller endast tillfälliga arbetsdata.

Exempel:

```text
runtime/

inbox/
jobs/
cache/
logs/
sqlite/
```

Runtime är lokal för den maskin som bearbetar dokument.

Den behöver inte synkroniseras.

Den ska kunna byggas upp på nytt.

---

# Persistent Archive

Arkivet innehåller all beständig information.

Exempel:

```text
archive/

documents/
knowledge/
projects/
trash/
```

Archive Root är konfigurerbar.

Det kan exempelvis ligga:

* lokalt
* i Dropbox
* på NAS
* i annan synkroniserad lagring

Dokumentverkstad ska inte vara beroende av en viss lagringslösning.

---

# Documents

Varje registrerat Document får en egen katalog.

Exempel:

```text
documents/

<document-id>/

metadata.json
processing/
```

Om en originalfil finns lagras även denna.

Exempel:

```text
original.pdf
```

Manuellt registrerade dokument behöver inte ha någon originalfil.

Originalfil kan läggas till senare.

---

# Knowledge

Knowledge Objects lagras beständigt i arkivet.

Målet är att de ska kunna läsas även utan Dokumentverkstad.

Historik ska bevaras.

Relationer ska kunna exporteras.

Formatet ska vara öppet och dokumenterat.

---

# Projects

Projekt lagras separat.

Projekt innehåller inte Knowledge Objects.

Projekt beskriver endast organisation och relationer.

General är inte ett Project.

General är hela kunskapsrummet.

---

# Trash

Raderade objekt flyttas först till Trash.

Efter en konfigurerbar tidsperiod kan permanent radering ske.

---

# Search Index

För snabb sökning används en lokal indexdatabas.

SQLite är den första implementationen.

Indexet är inte auktoritativt.

Det ska kunna byggas om från arkivet.

---

# Document Engine

Document Engine ansvarar för registrerade Documents.

Den hanterar:

* registrering
* metadata
* textutvinning
* struktur
* checksummor
* formatadaptrar

Den producerar aldrig Knowledge Objects direkt.

---

# Registrering av dokument

Det finns två sätt att registrera ett Document.

## Automatisk registrering

En fil tas emot genom Ingest.

Document Engine:

* verifierar filen
* skapar Document
* arkiverar originalet
* extraherar metadata
* extraherar text när möjligt

---

## Manuell registrering

Användaren registrerar ett dokument genom webbgränssnittet.

Minimikrav är normalt:

* titel

Övrig metadata är frivillig.

Originalfil kan läggas till senare.

Detta gör det möjligt att arbeta med exempelvis fysiska böcker.

---

# Formatadaptrar

Document Engine arbetar genom adaptrar.

Exempel:

```text
DocumentAdapter

PDFAdapter
EPUBAdapter
HTMLAdapter
```

Version 1 implementerar endast PDF.

Övriga delar av systemet arbetar mot Document, inte mot PDF.

---

# Source Location

Knowledge Objects kan hänvisa till olika delar av en källa.

Source Location beskriver denna koppling.

Precisionen kan exempelvis vara:

* dokument
* kapitel
* sida
* stycke
* textutdrag

Systemet ska stödja låg precision.

Hög precision får tillkomma senare.

---

# Knowledge Engine

Knowledge Engine ansvarar för:

* Knowledge Objects
* historik
* review
* relationer
* projektkopplingar
* source precision

Ett nytt Knowledge Object ska kunna skapas med minimal friktion.

Exempel:

```text
Ny notering

↓

Skriv

↓

Spara
```

Övrig struktur får växa fram senare.

---

# Relationer

Version 1 använder en avsiktligt enkel relationsmodell.

Kärnan behöver endast kunna uttrycka:

> A hör ihop med B.

Semantisk precision är frivillig.

Relationer kan utvecklas över tid.

---

# Review

AI-genererade objekt skapas som kandidater.

Review gör det möjligt att:

* acceptera
* redigera
* avvisa
* skjuta upp

Review förbättrar:

* formulering
* proveniens
* source precision
* projektkoppling
* eventuell semantisk typ

Review är en del av kunskapsbildningen.

---

# AI Layer

AI används genom capabilities.

Exempel:

* summarize
* extract_claims
* suggest_projects
* suggest_sources
* classify
* synthesize

Capability och provider är separerade.

Domänlogiken känner inte till vilken AI-modell som används.

---

# Bearbetningsnivåer

Arkitekturen stödjer tre nivåer.

## Nivå 1

Vanlig kod.

## Nivå 2

Lokal AI.

Ingår inte i första prototypen.

## Nivå 3

Moln-AI.

Första prototypen använder denna nivå.

---

# Konfiguration

Konfiguration lagras i en läsbar config-fil.

Hemligheter lagras separat.

API-nycklar får aldrig lagras i arkivet.

---

# Självobservation

Dokumentverkstad registrerar hur användaren arbetar.

Exempel:

* accepterade AI-förslag
* avvisade AI-förslag
* kostnader
* review-statistik

Systemet använder denna information för att föreslå förbättringar.

Det förändrar inte automatiskt sitt eget beteende.

---

# Webbgränssnitt

Webbgränssnittet ska vara serverrenderat.

Minimal JavaScript.

Kärnfunktioner ska fungera utan JavaScript.

Det ska fungera på:

* dator
* iPad
* telefon
* moderna e-ink-enheter

---

# Dokumentläsning

Dokumentverkstad ersätter inte specialiserade PDF- eller EPUB-läsare.

Originaldokument öppnas i extern läsare.

Dokumentverkstad ansvarar för kunskapsarbetet kring dokumentet.

---

# Portabilitet

Arkivet ska kunna flyttas till en ny maskin.

En ny installation ska kunna:

* peka ut Archive Root
* läsa konfiguration
* återskapa index
* fortsätta arbeta

Ingen lokal runtime-data ska krävas för återställning.

---

# Export

All beständig data ska kunna exporteras.

Målet är att användaren aldrig ska bli inlåst i Dokumentverkstad.

---

# Första prototypen

Version 1 innehåller inte:

* lokal AI
* EPUB
* OCR
* avancerad kunskapsgraf
* dokumentchatt
* multi-user
* publik molndrift

Arkitekturen ska däremot göra dessa möjliga senare.

---

# Arkitekturens kärna

Dokumentverkstad bygger på en liten kärna.

```text
Documents
    ↓
Knowledge Objects
    ↕
Relations
    ↕
Projects
```

Runt denna kärna finns:

* arkiv
* runtime
* AI
* index
* webbgränssnitt
* export

Dessa stödjer domänmodellen.

De definierar den inte.

---

# Avslutning

Arkitekturen ska göra Dokumentverkstad möjlig att förstå, underhålla och flytta mellan olika miljöer.

Systemets långsiktiga stabilitet ska bygga på den beständiga datan och den lilla domänmodellen, inte på en viss implementation eller teknikstack.

# UX_NOTES.md

# UX-observationer

Detta dokument samlar observationer från verklig användning av Dokumentverkstad.

Syftet är inte att beskriva önskad implementation, utan att dokumentera friktion, styrkor och frågor som uppstår när systemet används i praktiken.

En observation bör i första hand beskriva **vad som händer**, därefter **varför det känns problematiskt eller fungerar bra**, och först i tredje hand föreslå en möjlig lösning.

---

# 2026-08-10

## Ingest

### Observation

Importerade PDF-filer ligger kvar i `ingest_source` efter en lyckad import.

### Bedömning

`ingest_source` fungerar i praktiken som en inkorg. När ett dokument har registrerats och arkiverats känns det naturligt att det lämnar inkorgen.

### Möjlig riktning

Efter lyckad import bör dokumentet flyttas eller tas bort från `ingest_source` så att katalogen endast innehåller dokument som ännu inte har bearbetats.

---

## Inbox

### Dokumenttitlar

### Observation

Vissa dokument får obegripliga titlar från PDF-metadata, exempelvis:

* `hè3ì5'zÒI½ºcå?¸ÙºduJGòÓ`

Ett annat dokument fick titeln:

* `Microsoft Word - Ds 2012_13 BiblL för korr`

Övriga dokument verkar ha fått sina namn från filnamnet.

### Bedömning

Att använda dokumentets metadata är ofta bättre än att använda filnamnet, men metadata kan ibland vara ofullständig eller trasig.

När detta händer blir dokumentet svårt att identifiera.

### Möjlig riktning

Inbox bör kunna visa både dokumentets titel och originalfilens namn.

Det kan också vara motiverat att låta dokument med uppenbart trasig metadata hamna i ett särskilt arbetsflöde för manuell granskning.

---

### Status "Later"

### Observation

När ett dokument sätts till status `Later` ligger det fortfarande kvar i Inbox.

### Bedömning

Det är oklart vilken praktisk funktion statusen fyller.

Om dokumentet ändå ligger kvar i Inbox är skillnaden mellan `New` och `Later` liten.

### Fråga

Behövs statusen överhuvudtaget, eller bör den ersättas av ett framtida "snooze"-flöde där dokument tillfälligt döljs fram till ett visst datum?

---

### Inspiration till nya projekt

### Observation

Inbox fungerar inte bara som en arbetskö.

När många dokument kommer in samtidigt uppstår också idéer om nya projekt.

### Bedömning

Detta känns som en positiv bieffekt av arbetsflödet och kan vara något som Dokumentverkstad senare bör stödja.

---

## Capture

### Fristående Capture

### Observation

Det fungerar bra att kunna skapa Knowledge Objects utan att de från början är kopplade till något dokument eller projekt.

### Bedömning

Detta känns som ett viktigt arbetsflöde och bör bevaras.

---

### Organisering av fristående Knowledge Objects

### Observation

Det saknas idag ett naturligt sätt att senare koppla ett fristående Knowledge Object till ett Document eller ett Project.

### Bedömning

Arbetsflödet bör utgå från att tankar först fångas och därefter organiseras.

Det känns mindre naturligt att användaren först går till ett Project eller ett Document och därifrån försöker hitta tidigare fristående noteringar.

### Möjlig riktning

Systemet bör senare erbjuda ett enkelt arbetsflöde för att organisera tidigare fristående Knowledge Objects.

---

## Documents

### Document-listan

### Observation

Den övergripande listan över Documents fungerar bra för ett mindre antal dokument.

Det är enkelt att skapa manuella Documents.

### Fråga

När antalet dokument blir betydligt större behöver denna vy sannolikt utvecklas med bättre filtrering, sortering eller andra navigationsmöjligheter.

---

## Document-vyn

### Inbox-status

### Observation

Inbox-status visas tydligt även inne i ett enskilt Document.

### Bedömning

När dokumentet väl är öppnat känns denna information mindre viktig.

---

### Länk till aktuellt dokument

### Observation

Document-vyn visar en länk till "Aktuellt dokument", trots att användaren redan befinner sig på dokumentets sida.

### Bedömning

Länken tillför ingen information.

---

### Metadata

### Observation

Det finns idag ingen möjlighet att komplettera eller förbättra dokumentets metadata.

### Bedömning

Metadata bör kunna utvecklas över tid.

Exempelvis:

* titel,
* författare,
* bibliografiska uppgifter,
* annan referensinformation.

När sådan information finns i dokumentets metadata bör den kunna importeras, men användaren bör också kunna korrigera den manuellt.

---

## Projects

### Project-listan

### Observation

Listan över Projects fungerar bra.

Att skapa nya projekt känns enkelt och naturligt.

---

## Project-vyn

### Allmänt

### Observation

Project-vyn är den mest svårförståeliga delen av systemet i nuläget.

---

### Projektmetadata

### Observation

Projektets metadata visas högst upp.

### Bedömning

Det fungerar idag, men på sikt känns det mer naturligt att Capture eller relevanta Documents är projektets huvudsakliga arbetsyta.

Projektets metadata kan sannolikt döljas bakom en redigeringsfunktion.

---

### Koppla befintlig notering

### Observation

Det finns en funktion för att koppla befintliga Knowledge Objects till projektet.

### Bedömning

Funktionen behövs sannolikt, men arbetsflödet bör ses över tillsammans med hanteringen av fristående Knowledge Objects.

---

### Relationer mellan Knowledge Objects

### Observation

Det finns idag möjlighet att skapa explicita relationer mellan olika Knowledge Objects.

### Bedömning

Efter praktisk användning är det ännu oklart vilken nytta denna funktion faktiskt ger.

Det är möjligt att den visar sig värdefull senare, men i nuvarande arbetsflöde känns den inte central.

### Fråga

Behöver explicita relationer mellan Knowledge Objects finnas i användargränssnittet redan från början, eller bör de tills vidare betraktas som en avancerad funktion tills ett tydligare användningsfall har vuxit fram?

# 2026-08-11

## Capture

### Capture bör kunna användas utan att lämna läsningen

När jag läser exempelvis AI:s Summary eller ett dokument vill jag kunna skriva nya Captures utan att behöva scrolla bort från det jag läser.

Capture behöver därför kunna vara tillgänglig samtidigt som innehållet visas.

Detta är framför allt ett arbetsflödesproblem snarare än en layoutfråga.

---

## Document

### Utgivningsår är viktig metadata

Dokumentets utgivningsår behövs för att kunna bedöma:

* om slutsatser fortfarande är aktuella,
* i vilken historisk kontext dokumentet ska förstås.

Årtal bör därför betraktas som central metadata.

---

### Metadatahanteringen behöver utvecklas

Dokument bör innehålla mer metadata än idag.

Två typer av metadata behöver stödjas:

* metadata som kan extraheras automatiskt ur PDF-filen,
* metadata som användaren kan komplettera manuellt.

Exempel är:

* titel,
* upphov (författare eller organisation),
* utgivningsår,
* eventuellt andra bibliografiska uppgifter, t.ex. DOI och ISBN

---

### Metadata bör kunna extraheras från filnamn

Mitt nuvarande dokumentarkiv följer i hög grad mönstret:

```text
ÅÅÅÅ Titel.pdf
```

eller motsvarande.

Det borde därför vara möjligt att automatiskt extrahera åtminstone:

* utgivningsår,
* titel,

från filnamnet när PDF-metadata saknas eller är bristfällig.

---

### Document-listan behöver visa mer arbetsinformation

I listan över Documents vore det värdefullt att direkt kunna se exempelvis:

* om dokumentet har AI-analyserats,
* hur många Knowledge Objects/Captures som är kopplade till dokumentet.

Det gör det lättare att få en överblick över vilka dokument som redan bearbetats.

---

## AI-review

### Felaktiga review-beslut måste kunna rättas

Jag råkade acceptera en AI-Claim som egentligen borde ha avvisats.

Review behöver därför kunna ändras i efterhand.

Det gäller inte bara Accept/Reject utan hela review-historiken.

---

### AI-frågor kan stödja manuell läsning

De Questions som AI föreslår kan fungera som vägledning vid en snabb manuell genomläsning av dokumentet.

Det behöver dock vara tydligt att frågorna är AI:s frågor och inte nödvändigtvis besvaras av dokumentet.

---

### Hantering av stora AI-svar

När AI-analysen avbryts därför att max_output_tokens överskrids bör användaren kunna välja att fortsätta med en högre gräns.

Systemet bör då:

* göra en ny kostnadsuppskattning,
* visa denna,
* låta användaren ta ställning innan ett nytt anrop görs.

---

## Knowledge Objects

### Interna ID behöver inte exponeras

Knowledge Object-ID:n tillför inget i det dagliga arbetet.

Interna identifierare bör därför inte visas i användargränssnittet annat än i administrativa eller tekniska sammanhang.

---

## Framtida arkitektur

### Extern AI via MCP

Fördjupade AI-samtal bör sannolikt inte ske inne i Dokumentverkstad.

Istället kan Dokumentverkstad på sikt exponera ett säkert read-only-gränssnitt, exempelvis via MCP.

Det gör det möjligt för externa AI-klienter att:

* läsa Documents,
* läsa Knowledge Objects,
* söka i kunskapsrummet,
* resonera kring materialet,

utan att själva AI-konversationen behöver lagras i Dokumentverkstad.

Detta känns som en möjlig framtida Iteration 10: **Exponera kunskapsrummet**.

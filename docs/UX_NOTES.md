# UX_NOTES.md

# UX-observationer

Detta dokument samlar observationer från verklig användning av Dokumentverkstad.

Syftet är inte att beskriva önskad implementation, utan att dokumentera friktion, styrkor och frågor som uppstår när systemet används i praktiken.

En observation bör i första hand beskriva **vad som händer**, därefter **varför det känns problematiskt eller fungerar bra**, och först i tredje hand föreslå en möjlig lösning.

Observationerna utgör underlag för senare design- och implementationsbeslut. Att något finns dokumenterat här innebär inte i sig att det ska implementeras.

---

# 2026-08-10 – Första systematiska genomgången

## Ingest

### Importerade filer ligger kvar efter ingest

**Observation**

Importerade PDF-filer ligger kvar i `ingest_source` efter en lyckad import.

**Bedömning**

`ingest_source` fungerar i praktiken som en inkorg. När ett dokument har registrerats och arkiverats känns det naturligt att det lämnar inkorgen.

**Möjlig riktning**

Efter lyckad import bör dokumentet flyttas eller tas bort från `ingest_source` så att katalogen endast innehåller dokument som ännu inte har bearbetats.

---

## Inbox

### Dokumenttitlar kan vara svåra att identifiera

**Observation**

Vissa dokument får obegripliga titlar från PDF-metadata, exempelvis:

`hè3ì5'zÒI½ºcå?¸ÙºduJGòÓ`

Ett annat dokument fick titeln:

`Microsoft Word - Ds 2012_13 BiblL för korr`

Övriga dokument verkar i huvudsak ha fått sina namn från filnamnet.

**Bedömning**

Att använda dokumentets metadata är ofta bättre än att använda filnamnet, men metadata kan ibland vara ofullständig, missvisande eller trasig.

När detta händer blir dokumentet svårt att identifiera.

**Möjlig riktning**

Inbox bör kunna visa både dokumentets titel och originalfilens namn.

Det kan också vara motiverat att senare kunna identifiera dokument med uppenbart problematisk metadata för manuell granskning.

---

### Statusen Later har oklar funktion

**Observation**

När ett dokument sätts till status `Later` ligger det fortfarande kvar i Inbox.

**Bedömning**

Det är oklart vilken praktisk funktion statusen fyller.

Om dokumentet ändå ligger kvar i Inbox är skillnaden mellan `New` och `Later` liten.

**Fråga**

Behövs statusen överhuvudtaget, eller bör den på sikt få betydelsen att ett ärende skjuts upp och tillfälligt lämnar den aktiva Inboxen?

---

### Inbox kan ge inspiration till nya Projects

**Observation**

Inbox fungerar inte bara som en arbetskö.

När många dokument kommer in samtidigt uppstår också idéer om nya Projects.

**Bedömning**

Detta är en positiv bieffekt av arbetsflödet och kan vara något som Dokumentverkstad senare bör stödja, om ett naturligt användningsfall växer fram.

---

## Capture

### Fristående Capture fungerar väl

**Observation**

Det fungerar bra att kunna skapa Knowledge Objects utan att de från början är kopplade till något Document eller Project.

**Bedömning**

Detta känns som ett viktigt arbetsflöde och bör bevaras.

---

### Fristående Knowledge Objects behöver kunna organiseras i efterhand

**Observation**

Det saknas idag ett naturligt sätt att senare koppla ett fristående Knowledge Object till ett Document eller ett Project.

**Bedömning**

Arbetsflödet bör kunna utgå från att tankar först fångas och därefter organiseras.

Det känns mindre naturligt att användaren först går till ett Project eller ett Document och därifrån försöker hitta tidigare fristående noteringar.

**Möjlig riktning**

Systemet bör senare erbjuda ett enkelt arbetsflöde för att organisera tidigare fristående Knowledge Objects.

---

## Documents

### Document-listan fungerar i liten skala

**Observation**

Den övergripande listan över Documents fungerar bra för ett mindre antal dokument.

Det är också enkelt att skapa manuella Documents.

**Fråga**

När antalet dokument blir betydligt större behöver denna vy sannolikt utvecklas med bättre filtrering, sortering eller andra navigationsmöjligheter.

---

## Document-vyn

### Inbox-status är för framträdande

**Observation**

Inbox-status visas tydligt även inne i ett enskilt Document.

**Bedömning**

När dokumentet väl är öppnat känns denna information mindre viktig.

---

### Länk till aktuellt Document är redundant

**Observation**

Document-vyn visar en länk till "Aktuellt dokument", trots att användaren redan befinner sig på dokumentets sida.

**Bedömning**

Länken tillför ingen information.

---

### Dokumentmetadata behöver kunna utvecklas

**Observation**

Det finns idag ingen naturlig möjlighet att komplettera eller förbättra dokumentets metadata.

**Bedömning**

Metadata bör kunna utvecklas över tid.

Exempel är:

* titel,
* upphov,
* utgivningsår,
* bibliografiska uppgifter,
* annan referensinformation.

När sådan information finns i PDF-metadata bör den kunna importeras, men användaren bör också kunna korrigera och komplettera den manuellt.

---

## Projects

### Project-listan fungerar väl

**Observation**

Listan över Projects fungerar bra.

Att skapa nya Projects känns enkelt och naturligt.

---

## Project-vyn

### Project-vyn är svårast att förstå

**Observation**

Project-vyn är den mest svårförståeliga delen av systemet i nuläget.

---

### Projektmetadata behöver inte dominera arbetsytan

**Observation**

Projektets metadata visas högst upp.

**Bedömning**

Det fungerar idag, men på sikt känns det mer naturligt att Captures eller relevanta Documents utgör projektets huvudsakliga arbetsyta.

Projektets metadata kan sannolikt göras mindre framträdande och istället nås genom en redigeringsfunktion.

---

### Koppling av befintliga Knowledge Objects behöver ses i ett större arbetsflöde

**Observation**

Det finns en funktion för att koppla befintliga Knowledge Objects till ett Project.

**Bedömning**

Funktionen behövs sannolikt, men arbetsflödet bör ses över tillsammans med hanteringen av fristående Knowledge Objects.

---

### Nyttan med explicita relationer mellan Knowledge Objects är oklar

**Observation**

Det finns idag möjlighet att skapa explicita relationer mellan olika Knowledge Objects.

**Bedömning**

Efter praktisk användning är det ännu oklart vilken nytta denna funktion faktiskt ger.

Det är möjligt att den visar sig värdefull senare, men i nuvarande arbetsflöde känns den inte central.

**Fråga**

Behöver explicita relationer mellan Knowledge Objects finnas synligt i det normala användargränssnittet, eller bör de tills vidare betraktas som en avancerad funktion tills ett tydligare användningsfall har vuxit fram?

---

# 2026-08-11 – Första verkliga användningen

## Capture

### Capture bör kunna användas utan att lämna läsningen

**Observation**

När jag läser exempelvis AI:s Summary eller annat innehåll på ett Document vill jag kunna skriva nya Captures utan att behöva scrolla bort från det jag läser.

**Bedömning**

Capture behöver kunna vara tillgänglig samtidigt som det innehåll som bearbetas visas.

Detta är framför allt ett arbetsflödesproblem snarare än en rent visuell layoutfråga.

---

## Documents

### Utgivningsår är central metadata

**Observation**

Dokumentets utgivningsår behövs för att kunna bedöma:

* om slutsatser fortfarande är aktuella,
* i vilken historisk kontext dokumentet ska förstås.

**Bedömning**

Utgivningsår bör betraktas som central metadata för Documents.

---

### Metadatahanteringen behöver utvecklas

**Observation**

Documents behöver innehålla mer metadata än idag.

Två typer av metadata behöver kunna samverka:

* metadata som kan extraheras automatiskt ur PDF-filen,
* metadata som användaren kan komplettera eller korrigera manuellt.

Exempel är:

* titel,
* upphov, exempelvis författare eller organisation,
* utgivningsår,
* DOI,
* ISBN,
* andra relevanta bibliografiska uppgifter.

---

### Metadata kan ibland extraheras från filnamn

**Observation**

Mitt befintliga dokumentarkiv följer i hög grad mönstret:

```text
ÅÅÅÅ Titel.pdf
```

eller motsvarande.

**Bedömning**

Filnamnet innehåller därför i många fall mer tillförlitlig metadata än själva PDF-filen.

**Möjlig riktning**

Det bör vara möjligt att automatiskt extrahera åtminstone utgivningsår och titel från filnamnet när PDF-metadata saknas eller är bristfällig.

Detta är särskilt viktigt innan ett större befintligt dokumentarkiv importeras.

---

### Document-listan behöver visa bearbetningsinformation

**Observation**

I listan över Documents går det inte snabbt att avgöra vilka dokument som redan har bearbetats.

**Bedömning**

Det vore värdefullt att direkt kunna se åtminstone:

* om dokumentet har AI-analyserats,
* hur många Captures/Knowledge Objects som är kopplade till dokumentet.

Det gör det lättare att skilja mellan dokument som bara finns i arkivet och dokument som faktiskt har bearbetats.

---

## AI-review

### Felaktiga review-beslut måste kunna rättas

**Observation**

Jag råkade acceptera en AI-genererad Claim som egentligen borde ha avvisats.

**Bedömning**

Review-beslut behöver kunna ändras i efterhand.

Det gäller inte bara Accept/Reject utan review-historiken generellt.

En korrigering bör inte förstöra information om det tidigare beslutet.

---

### AI-frågor kan stödja manuell läsning

**Observation**

De Questions som AI föreslår kan fungera som vägledning vid en snabb manuell genomläsning av dokumentet.

**Bedömning**

Det behöver dock vara tydligt att frågorna är frågor som väckts genom AI-analysen och inte nödvändigtvis frågor som dokumentet självt besvarar.

---

### Avbruten AI-analys kan behöva kunna köras om med högre gräns

**Observation**

En AI-analys kan avbrytas därför att `max_output_tokens` överskrids.

**Bedömning**

Det är bra att det finns en gräns som förhindrar oväntat stora anrop, men ett överskridande behöver inte innebära att analysen bör överges.

**Möjlig riktning**

Systemet skulle i detta läge kunna:

* göra en ny kostnadsuppskattning med en högre output-gräns,
* visa uppskattningen,
* låta användaren välja om analysen ska köras igen med den högre gränsen.

---

## Knowledge Objects

### Interna ID behöver inte exponeras

**Observation**

Knowledge Object-ID:n tillför inget i det dagliga arbetet.

**Bedömning**

Interna identifierare bör inte visas i det normala användargränssnittet annat än där de behövs i administrativa eller tekniska sammanhang.

---

## Framtida arkitektur

### Extern AI via MCP

**Observation**

Fördjupade AI-samtal behöver sannolikt inte ske inne i Dokumentverkstad.

**Bedömning**

Det kan vara mer naturligt att Dokumentverkstad på sikt fungerar som ett strukturerat kunskapslager som externa AI-klienter kan läsa.

Själva AI-konversationen behöver då inte lagras i Dokumentverkstad.

**Möjlig riktning**

Dokumentverkstad skulle på sikt kunna exponera ett säkert, i första hand read-only, gränssnitt via exempelvis MCP.

Det skulle kunna ge externa AI-klienter möjlighet att:

* läsa Documents,
* läsa Knowledge Objects,
* söka i kunskapsrummet,
* läsa delar av Projects,
* resonera kring materialet.

En sådan server behöver exponeras med tydlig autentisering och begränsade behörigheter.

Detta kan vara en möjlig framtida **Iteration 10 – Exponera kunskapsrummet**.

---

# 2026-08-15 – Efter en veckas verklig användning

## Capture och Knowledge Objects

### Semantisk typ för egna Captures behöver övervägas

**Observation**

AI-genererade Knowledge Objects kan klassificeras som exempelvis Claim, Insight och Question, medan egna Captures inte behöver ha motsvarande semantiska typ.

**Bedömning**

Det är inte självklart att alla egna Captures behöver eller bör klassificeras.

Det finns däremot en tydlig nytta i att kunna formulera och identifiera egna **Questions**. Frågor kan fungera som öppna trådar för fortsatt läsning och tänkande.

**Fråga**

Kan semantisk typ göras till en frivillig egenskap hos egna Captures utan att Capture-flödet blir mer omständligt?

---

### Captures behöver fungera bättre som minnesanteckningar

**Observation**

Capture kopplat till Document fungerar väl under aktiv läsning.

När jag senare återvänder till ett Document är det däremot svårare att snabbt återfå vad jag själv tänkte när jag läste det.

**Bedömning**

Captures behöver presenteras på ett sätt som gör dem användbara även som minnesanteckningar om den tidigare läsningen.

Det bör vara lätt att snabbt återfå:

* vad jag själv reagerade på,
* vilka frågor jag formulerade,
* vilka delar av dokumentet jag bedömde som viktiga.

---

### Captures måste kunna korrigeras i efterhand

**Observation**

Jag gjorde en felaktig sidhänvisning i en Capture och upptäckte att det inte finns något naturligt sätt att korrigera den.

**Bedömning**

Knowledge Objects/Captures behöver kunna redigeras i efterhand genom gränssnittet.

Manuell redigering av JSON-filer ska inte behövas för normalt användararbete.

En sådan redigering bör följa systemets princip om historik: den tidigare versionen bör bevaras snarare än skrivas över utan spår.

---

## Documents

### Document-listan behöver visa bearbetningsstatus

**Observation**

Efter en veckas användning har behovet av mer arbetsinformation i den övergripande Documents-vyn blivit tydligare.

**Bedömning**

För varje Document vore det användbart att direkt kunna se åtminstone:

* om dokumentet har genomgått AI-analys,
* hur många Captures/Knowledge Objects som är kopplade till dokumentet.

Syftet är att snabbt kunna skilja mellan dokument som bara finns i arkivet och dokument som faktiskt har bearbetats.

---

### Documents kan behöva en övergripande kommentar

**Observation**

Det kan finnas behov av en fri kommentar eller anmärkning om ett Document, exempelvis:

> Utkast inför möte.

**Bedömning**

Detta är något annat än en Capture om dokumentets innehåll.

Kommentaren beskriver snarare dokumentets sammanhang, funktion eller status i ett arbetsflöde.

---

### Relationer mellan Documents behöver övervägas

**Observation**

I verkligt arbete förekommer olika Documents som hör nära samman.

Ett exempel är:

1. ett utkast till en rapport läses och kommenteras,
2. några månader senare publiceras slutrapporten,
3. båda dokumenten behöver kunna förstås tillsammans.

**Fråga**

Behöver detta modelleras genom:

* relationer mellan Documents,
* dokumentstatus eller dokumenttyp,
* gemensamt Project,
* eller någon kombination av dessa?

Ingen ny modell bör införas innan det finns tillräckliga verkliga användningsfall.

---

## Inbox

### Later kan eventuellt fungera som faktisk uppskjutning

**Observation**

Statusen `Later` har fortfarande begränsad funktionell betydelse.

**Möjlig riktning**

En möjlig modell vore att Later:

* sparar tidpunkten för uppskjutningen,
* tillfälligt tar bort objektet från den aktiva Inboxen,
* automatiskt visar objektet igen exempelvis nästa dag.

**Fråga**

Skulle detta faktiskt minska friktionen, eller skulle det bara göra Inboxens beteende mindre transparent?

Funktionen bör inte förändras innan användningsfallet blivit tydligare.

---

## Drift och responsivitet

### Systemet svarar ibland inte på interaktion

**Observation**

Vid vissa tillfällen verkar Dokumentverkstad inte reagera när jag utför en handling i gränssnittet.

Eftersom webbserver, Archive och klient för närvarande körs lokalt på samma dator är orsaken inte uppenbar.

**Bedömning**

Detta bör undersökas som ett prestanda- eller driftproblem snarare än behandlas som normal latens.

Det behöver framför allt fastställas:

* vilka handlingar som orsakar väntan,
* om servern arbetar under tiden,
* om disk-I/O eller indexering blockerar,
* om något synkront arbete blockerar HTTP-requesten,
* om användaren behöver tydligare återkoppling när en operation faktiskt pågår.

---

## Backup och portabilitet

### Reproducerbar backup och restore behövs sannolikt

**Observation**

Dokumentverkstad behöver kunna flyttas mellan installationer och återställas utan att användaren behöver förstå alla interna kataloger.

**Bedömning**

Det behövs sannolikt en enkel portabilitetsfunktion för backup och restore.

Syftet är inte att skapa ett separat proprietärt exportformat.

**Möjlig riktning**

Funktionen kan paketera den befintliga strukturen på ett säkert och reproducerbart sätt, exempelvis som ett tidsstämplat arkiv innehållande:

* Archive,
* nödvändig icke-hemlig konfiguration,
* information som behövs för att återskapa Runtime och index.

Secrets ska inte ingå i en vanlig backup/export.

En återställning på en ny installation ska kunna återskapa ett fungerande Dokumentverkstad från denna backup.

---

## Installation och första körning

### Initial konfiguration behöver ett eget flöde

**Observation**

En ny installation förutsätter idag att användaren själv känner till konfigurationsfiler, miljövariabler och andra tekniska förutsättningar.

**Bedömning**

Det är rimligt under utvecklingen men inte för en mogen installation av Dokumentverkstad.

**Möjlig riktning**

Vid första körningen skulle Dokumentverkstad kunna guida användaren genom relevant konfiguration.

Det kan exempelvis omfatta:

* placering av Archive och Runtime,
* API-provider och API-nyckel,
* initiering av krypterad secrets-lagring,
* nätverksåtkomst,
* eventuell användning av Tailscale.

Alla delar behöver inte vara obligatoriska.

Dokumentverkstad ska fortsatt kunna användas utan exempelvis extern AI eller fjärråtkomst.

---

## Erfarenhet från verklig användning

### Grundflödet fungerar

**Observation**

Den första användningen i ett verkligt arbetsflöde fungerade väl.

Dokumentverkstad användes för att läsa och göra Captures ur ett dokument inför ett kommande möte.

Grundflödet fungerade utan att verktyget behövde behandlas som ett testobjekt.

Capture kopplat till Document fungerade särskilt väl som stöd för aktiv läsning.

**Bedömning**

Detta bör betraktas som ett fungerande kärnflöde.

Framtida UX-förändringar bör förbättra arbetsflödet utan att göra den nu fungerande aktiva läsningen mer komplicerad.

# 2026-08-16

## Erfarenhet från utveckling av iteration 7.1

### Möjlig brist i relationen mellan dokument
Document.project_ids uttrycker just nu att relationen finns, men inte varför den finns. Så fort samma relation kan uppstå på flera sätt — manuellt, via AI-förslag, kanske senare via import eller annan automatik — räcker en ren mängd project_ids inte för att säkert kunna “ångra” en specifik händelse.

**Bedömning**

* Ingen automatisk unlink vid korrigering ses som säkert beteende tills proveniens finns.
* Frågan bör tas upp igen när relationer/proveniens ses över, troligen före eller under Iteration 9.

## Erfarenheter av användning efter iteration 7.1

### Behov av förändring i Inbox

Svårt att få överblick över inboxen när det ligger flera dokument där. Det tar tid att beta igenom många dokument.

**Bedömning**

* Önskvärt med en enkel siffra överst i inboxen av hur många dokument som ligger i kön.
* Överväg en möjlighet till massredigering, t.ex. att kunna markera flera dokument som klara och tillhörande olika projekt, sedan spara allt samtidigt.
* Om inte sidan behövde laddas om vid varje åtgärd skulle arbetet kunna gå klart snabbare. Asynkrona javascript/ajax kan vara en lösning.

### Behov av förändring i Documents-vyn

Större dokumentmängd förändrar kraven på Documents-vyn. Efter import av ett befintligt arkiv på cirka 230 PDF:er fungerar ingest och dubletthantering, men listvyn behöver utvärderas i verklig användning. Det är sannolikt att sortering, filtrering, sökning och bearbetningsstatus blir viktigare när dokumentmängden växer.

Likaså bör dokument som fortfarande ligger i inboxen och väntar på att sparas eller kastas inte visas i listvyn på Documents-sidan. Där bör bara dokument som godkänts i inboxen finnas med.

Det behövs ett sätt att från Documents-vyn knyta ett dokument till ett nytt projekt. Enda sättet idag är att göra en AI-review och knyta dokumentet till något av de projekt som föreslås, vilket är en märklig omväg.

**Bedömning**

Utvärderar behoven och väntar till iteration 9

### Behov av förändring i vyn för enskilda Documents

Länken till original-pdf öppnar pdf:en i samma fönster som man redan befinner sig i. Det tycker jag normalt är bra, men här blir det ett problem.

**Bedömning**

När man klickar på länken till originaldokument bör detta öppnas i en ny flik i webbläsaren.

### Prestandaproblem som effekt av större arkiv

Prestandan försämras när Archive växer. Efter import av cirka 230 Documents tar vissa lokala vyer omkring 1–2 sekunder att rendera. Slow-request-loggen visar exempelvis ~1 s för en Document-vy och ~2 s för Inbox. Detta tyder på att vyerna kan göra för omfattande genomläsningar av Archive vid varje request. 

**Bedömning**

Undersök om befintligt Runtime/SQLite-index bör utökas för listning, räknare och statusdata. Archive ska fortsatt vara auktoritativt och indexet helt återskapbart.

### Vidareutveckling av AI-körningar

Är det möjligt att även vid Ai-körningarna lägga en sidreferens? Det skulle underlätta det framtida arbetet.

### Lång väntetid vid AI-körningar

AI-körningar blockerar HTTP-requesten. Ett verkligt AI-anrop tog cirka 86 sekunder, varav nästan hela tiden låg hos AI-providern. 

**Bedömning**

AI-analys bör köras som ett bakgrundsjobb så att webbgränssnittet förblir responsivt under analysen.

### Gränssnittsinteraktionen vid AI-körningar

Efter genomförd AI-körning kommer man tillbaka till inboxen, och behöver om det är många dokument leta för att hitta körningen för att gå igenom dem.

**Bedömning**

Testa att istället låta användaren komma tillbaka till documents-sidan efter genomförd AI-körning. Vill inte användaren gå igenom körningen direkt, får den status "senare" och ligger då kvar i inboxen.
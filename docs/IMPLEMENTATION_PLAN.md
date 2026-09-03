# IMPLEMENTATION_PLAN.md

## Syfte

Implementationsplanen beskriver hur Dokumentverkstad utvecklas från idé till ett fungerande system.

Till skillnad från övriga projektdokument beskriver den inte *vad* Dokumentverkstad är, utan *hur den blir till*.

Planen är inte en detaljerad projektplan och inte heller en specifikation av alla funktioner. Den beskriver i vilken ordning systemet bör utvecklas för att ge största möjliga lärande med minsta möjliga komplexitet.

Implementationsplanen ska kunna förändras under projektets gång. Nya erfarenheter kan leda till att iterationer delas upp, slås samman eller får en annan ordning. Manifestet, designprinciperna och domänmodellen är däremot projektets långsiktiga referensramar och förändras endast när ny kunskap motiverar det.

---

# Utvecklingsfilosofi

Dokumentverkstad utvecklas genom **iterationer**, inte genom faser.

En iteration ska alltid resultera i ett sammanhängande arbetsflöde som kan användas i verkligt arbete. Målet är inte att färdigställa en teknisk komponent, utan att skapa ett system som användaren faktiskt kan arbeta i.

Utvecklingen ska därför följa samma grundprincip som Dokumentverkstad själv bygger på:

> Kunskap utvecklas genom användning, reflektion och omprövning.

Efter varje iteration ska systemet användas under en tid. Först därefter beslutas nästa iteration. Dokumentverkstad ska inte byggas efter en perfekt plan, utan växa fram genom erfarenhet.

---

# Arbetsflöden före komponenter

Den grundläggande utvecklingsenheten är inte en modul, en klass eller ett API.

Den grundläggande utvecklingsenheten är ett **arbetsflöde**.

Ett arbetsflöde börjar med ett verkligt behov hos användaren och slutar när detta behov kan utföras utan onödiga hinder.

Exempel:

> Jag läser en bok och vill snabbt skriva ned en tanke.

är ett arbetsflöde.

Däremot är

> Implementera en SQLite-tabell.

inte ett arbetsflöde.

Tekniska komponenter byggs endast när de behövs för att stödja ett arbetsflöde.

---

# Infrastruktur som möjliggörare

Infrastruktur är nödvändig, men är aldrig ett självändamål.

Arkiv, runtime, index, konfiguration och webbserver ska byggas så enkelt som möjligt och endast i den omfattning som krävs för nästa iteration.

Om ett val står mellan:

- mer generell infrastruktur,
- eller ett fungerande arbetsflöde,

ska arbetsflödet prioriteras.

Generalisering ska ske först när verklig användning visar att den behövs.

---

# Definition av en iteration

Varje iteration består av samma delar.

## Syfte

Vilket användarbeteende ska iterationen möjliggöra?

## Arbetsflöde

Vad ska användaren kunna göra när iterationen är klar?

## Infrastruktur

Vilken ny teknik måste byggas för att stödja arbetsflödet?

## Implementation

Vilka delar av systemet utvecklas?

## Tester

Hur verifierar vi att iterationen fungerar?

## Klart när

Vilka konkreta kriterier avgör att iterationen är färdig?

---

# Iteration 1 – Fånga en tanke

## Syfte

Den första iterationen etablerar Dokumentverkstads viktigaste arbetsyta.

Målet är inte att hantera PDF-filer eller AI, utan att användaren ska kunna fånga tankar och lita på att de finns kvar.

Om denna iteration fungerar finns redan kärnan i Dokumentverkstad.

## Arbetsflöde

Användaren öppnar Dokumentverkstad.

Ett tomt Capture-fält finns redan öppet.

Användaren skriver:

> "North påminner om Boyd."

Trycker **Spara**.

Textfältet töms.

Markören står kvar.

Användaren skriver nästa tanke.

Dagen därpå öppnas Dokumentverkstad igen.

Noteringarna finns kvar.

Detta är iterationens mål.

## Infrastruktur

För att stödja detta behövs endast:

- projektstruktur
- konfiguration
- Archive Root
- Runtime Root
- grundläggande webbserver
- öppna arkivformat

Ingen AI behövs.

Ingen PDF behövs.

Ingen Inbox behövs.

## Implementation

Iterationen implementerar:

- Knowledge Object
- skapande av Knowledge Objects
- historik
- skrivning till arkivet
- läsning från arkivet
- enkel Capture-vy
- enkel listning av senaste noteringar

Semantiska typer är frivilliga.

Projektkopplingar behövs inte ännu.

Relationer behövs inte ännu.

## Tester

Iterationen är godkänd när följande fungerar automatiskt:

- skapa ett Knowledge Object
- läsa tillbaka det
- ändra det
- historiken sparas
- applikationen kan startas om utan dataförlust

## Klart när

Iteration 1 är klar när följande scenario fungerar:

> Anders kan läsa en fysisk bok, öppna Dokumentverkstad, skriva fem anteckningar under läsningen, stänga datorn och hitta samma anteckningar nästa dag.

# Iteration 2 – Förstå ett dokument

## Syfte

Den andra iterationen introducerar Document som ett självständigt objekt.

Ett dokument behöver inte ha en digital fil. Det kan vara en fysisk bok, en rapport eller ett annat verk som användaren vill arbeta med.

Målet är att användaren ska kunna knyta sina tankar till en bestämd källa.

## Arbetsflöde

Användaren skapar ett nytt Document.

Exempel:

> Andens fenomenologi

eller

> Institutions, Institutional Change and Economic Performance

Användaren öppnar därefter Capture.

Nya noteringar kopplas automatiskt till det aktuella dokumentet.

När dokumentet öppnas senare visas alla noteringar som hör till det.

Användaren behöver aldrig fundera över var anteckningarna ligger.

## Infrastruktur

Denna iteration kräver:

- Document-objekt
- lagring av Documents
- koppling mellan Knowledge Objects och Documents
- enkel Document-vy

Ingen PDF-import behövs ännu.

Ingen AI behövs.

## Implementation

Iterationen implementerar:

- skapande av Documents
- redigering av Document-metadata
- Document-vy
- koppling mellan Capture och aktuellt Document
- listning av Documents

Originalfil är frivillig.

## Tester

Iterationen är godkänd när:

- Documents kan skapas
- Documents kan ändras
- Knowledge Objects kan kopplas till ett Document
- Capture använder aktuellt Document som standard
- tidigare anteckningar visas när ett Document öppnas

## Klart när

Iteration 2 är klar när följande scenario fungerar:

> Anders registrerar *Andens fenomenologi*, läser den fysiska boken under en vecka och skriver sina anteckningar i Dokumentverkstad. När boken öppnas igen visas samtliga anteckningar tillsammans.

# Iteration 3 – Bygg ett projekt

## Syfte

Den tredje iterationen introducerar Projects.

Projects gör det möjligt att orientera sig i ett kunskapsområde snarare än i ett enskilt dokument.

Målet är att användaren ska kunna samla tankar från flera dokument kring ett gemensamt problem.

## Arbetsflöde

Användaren skapar projektet:

> Rävfilosofi

Knowledge Objects från flera olika Documents kopplas till projektet.

När projektet öppnas visas den samlade kunskapen.

## Infrastruktur

Denna iteration kräver:

- Project-objekt
- koppling mellan Projects och Knowledge Objects
- Project-vy

## Implementation

Iterationen implementerar:

- skapa Project
- redigera Project
- koppla Knowledge Objects till flera Projects
- Project-vy
- enkel filtrering per Project

General implementeras fortfarande inte som ett Project.

## Tester

Iterationen är godkänd när:

- Projects kan skapas
- Knowledge Objects kan kopplas till flera Projects
- Project-vyn visar rätt innehåll
- Capture föreslår aktuellt Project

## Klart när

Iteration 3 är klar när följande scenario fungerar:

> Anders arbetar med projektet "Rävfilosofi". Anteckningar från Platon, Gibson, Boyd och North kan visas tillsammans trots att de kommer från olika dokument.

# Iteration 4 – Släpp in dokument

## Syfte

Den fjärde iterationen gör Dokumentverkstad användbar tillsammans med digitala dokument.

Användaren ska inte längre behöva registrera varje dokument manuellt.

## Arbetsflöde

Användaren placerar en PDF i Ingest Source.

Dokumentverkstad registrerar dokumentet automatiskt.

Dokumentet blir tillgängligt tillsammans med manuellt skapade Documents.

## Infrastruktur

Denna iteration kräver:

- Ingest Source
- PDF-import
- textextraktion
- checksumma
- dublettkontroll
- lokalt SQLite-index
- möjlighet att återskapa indexet från arkivet

## Implementation

Iterationen implementerar:

- PDF-ingest
- automatisk Document-registrering
- metadataextraktion
- lagring av originalfil
- länk till originalfil
- indexering av registrerade Documents
- rebuild-index

Ingen AI-analys sker ännu.

## Tester

Iterationen är godkänd när:

- PDF registreras automatiskt
- dubletter upptäcks
- originalfil sparas
- dokument kan öppnas från webbgränssnittet

## Klart när

Iteration 4 är klar när följande scenario fungerar:

> Anders sparar en rapport i en konfigurerad Ingest Source, exempelvis en Dropbox-synkad lokal mapp. Dokumentverkstad registrerar dokumentet och gör det tillgängligt tillsammans med tidigare dokument.

# Iteration 5 – Börja sortera

## Syfte

Den femte iterationen introducerar Inbox.

Nu börjar Dokumentverkstad aktivt hjälpa användaren att organisera sitt arbete.

Inbox är inte en lista över dokument.

Inbox är inte heller en egen kö.

Inbox är en arbetsyta som visar de beständiga objekt i kunskapsrummet som enligt sin sparade status behöver användarens uppmärksamhet.

## Arbetsflöde

Användaren öppnar Dokumentverkstad på telefonen.

Inbox visar exempelvis:

- nya dokument,
- dokument som ännu inte kopplats till Project,
- dokument vars behandling skjutits upp,
- andra objekt som väntar på ett användarbeslut.

Användaren går igenom objekten ett i taget.

Varje beslut leder direkt vidare till nästa objekt.

## Infrastruktur

Denna iteration kräver:

- Inbox-vy
- beständig status för triage
- beständig status för review
- minimal Trash
- Restore
- enkel arbetsmodell för objekt som väntar på beslut

Inbox får cacheas i Runtime, men dess innehåll ska alltid kunna återskapas från Archive.

Runtime får därför aldrig vara den auktoritativa lagringsplatsen för Inbox.

## Implementation

Iterationen implementerar:

- Inbox-vy
- beslut: senare
- beslut: kasta
- beslut: koppla till Project
- beslut: klar
- minimal Trash
- Restore

Inbox ska kunna visa olika typer av objekt.

I denna iteration används den främst för Documents, men modellen ska vara generell nog att senare även kunna hantera AI-kandidater utan att Inbox behöver byggas om.

Inbox blir systemets startsida på telefon.

## Tester

Iterationen är godkänd när:

- nya dokument visas i Inbox
- ett beslut uppdaterar objektets beständiga status
- nästa objekt visas direkt
- objekt som kastas återfinns i Trash
- objekt kan återställas från Trash
- Inbox kan återskapas efter att Runtime raderats
- Inbox fungerar väl även på telefon

## Klart när

Iteration 5 är klar när följande scenario fungerar:

> Anders sitter på tåget och går igenom dagens nya dokument på telefonen. Han kopplar några till projekt, skjuter upp några till senare och kastar ett dokument av misstag. När han upptäcker misstaget återställer han dokumentet från Trash och fortsätter sedan där han slutade.

# Iteration 6 – Ta hjälp av AI

## Syfte

Den sjätte iterationen introducerar AI som en rådgivare.

AI producerar aldrig etablerad kunskap.

Den producerar endast kandidater som användaren kan acceptera, redigera eller avvisa.

Målet är att AI ska minska användarens arbete utan att minska användarens kontroll.

## Arbetsflöde

Användaren öppnar ett nytt dokument.

Systemet visar:

- vald AI-provider,
- vald modell,
- uppskattad tokenförbrukning,
- uppskattad kostnad.

Användaren väljer att starta analysen.

AI producerar:

- Summary
- Candidate Insights
- Candidate Claims
- Candidate Questions
- föreslagna Projects

Samtliga kandidater visas i Inbox för review.

Användaren kan:

- acceptera,
- redigera och acceptera,
- avvisa,
- skjuta upp.

## Infrastruktur

Denna iteration kräver:

- AI-provider
- provider-interface
- promptsystem
- kostnadsberäkning
- review-flöde

## Implementation

Iterationen implementerar:

- AI-provider
- mock-provider
- kostnadsdialog
- AI-kandidater
- proveniens
- review

Vid varje AI-körning ska systemet dessutom spara den metadata som krävs för framtida självobservation.

Minst:

- provider
- modell
- promptversion
- faktisk tokenförbrukning
- faktisk kostnad
- confidence när sådan finns
- review-beslut
- eventuell avvisningsorsak

Ingen AI får skapa etablerade Knowledge Objects utan användarens uttryckliga godkännande.

## Tester

Iterationen är godkänd när:

- AI aldrig körs utan användarens godkännande
- kostnad visas innan körningen startar
- faktisk kostnad sparas
- proveniens sparas
- kandidater alltid kräver review
- metadata för framtida självobservation sparas tillsammans med varje AI-körning

## Klart när

Iteration 6 är klar när följande scenario fungerar:

> Anders lägger in en rapport, väljer att använda moln-AI och får några minuter senare ett antal kandidater. Han accepterar några, redigerar några och avvisar resten. Samtliga beslut och all AI-proveniens sparas automatiskt.

# Iteration 7 – Lär av användningen

## Syfte

Den sjunde iterationen gör den insamlade erfarenheten synlig.

Dokumentverkstad ska inte automatiskt förändra sitt beteende.

Den ska hjälpa användaren att förstå hur systemet används och hur AI bidrar till arbetet.

## Arbetsflöde

Efter en tids användning öppnar användaren administrationsvyn.

Där visas exempelvis:

- hur många AI-körningar som genomförts,
- total kostnad,
- kostnad per modell,
- hur många kandidater som accepterats,
- hur många som redigerats,
- hur många som avvisats,
- vilka typer av kandidater som oftast ändras.

Systemet presenterar informationen.

Det fattar inga egna beslut.

## Infrastruktur

Denna iteration kräver:

- statistikmodul
- rapportering
- sammanställning av tidigare insamlad metadata

Ingen ny datainsamling introduceras.

Iterationen bygger helt på den metadata som redan samlats in i tidigare iterationer.

## Implementation

Iterationen implementerar:

- administrationsvy
- AI-statistik
- kostnadsöversikt
- sammanställning av review-resultat
- enkel visualisering av användningshistorik

Systemet ska kunna sammanställa historiken utan att förändra den.

## Tester

Iterationen är godkänd när:

- kostnader kan summeras
- AI-användning kan följas över tid
- review-statistik visas korrekt
- sammanställningar kan återskapas från den sparade metadata som redan finns i Archive

## Klart när

Iteration 7 är klar när följande scenario fungerar:

> Efter några månaders användning öppnar Anders Dokumentverkstad och ser hur mycket AI som använts, vad den kostat och vilka typer av AI-förslag som oftast accepterats, redigerats eller avvisats. Informationen hjälper honom att förstå sitt eget arbetssätt, men Dokumentverkstad förändrar inte sitt beteende automatiskt.

# Iteration 7.1 – Stabilisering efter verklig användning

## Syfte

Efter de första iterationerna har Dokumentverkstad använts i verkliga arbetsflöden under en period.

Grundflödet fungerar väl, men användningen har identifierat ett mindre antal brister i kärnfunktionaliteten som bör åtgärdas innan systemet går vidare till drift, portabilitet och UX-konsolidering.

Iteration 7.1 ska inte introducera nya större arbetsflöden.

Den ska stabilisera sådant som redan finns och åtgärda problem som annars riskerar att påverka fortsatt användning eller framtida import av ett större dokumentarkiv.

Utgångspunkten är observationerna i `UX_NOTES.md`.

## Fokusområden

Iterationen omfattar:

- förbättrad metadatahantering för Documents,
- möjlighet att korrigera Captures i efterhand,
- möjlighet att korrigera tidigare AI-review-beslut,
- undersökning och diagnostik av tillfällen då webbgränssnittet inte svarar.

## Document-metadata

Documents behöver kunna innehålla åtminstone:

- titel,
- upphov, exempelvis författare eller organisation,
- utgivningsår.

Metadata ska kunna komma från flera källor:

1. PDF-metadata,
2. originalfilens namn,
3. manuell redigering.

När filnamnet följer mönstret:

`ÅÅÅÅ Titel.pdf`

ska systemet kunna använda detta som underlag för utgivningsår och titel när motsvarande PDF-metadata saknas eller bedöms som oanvändbar.

Originalfilens namn ska alltid bevaras.

Metadata ska kunna korrigeras och kompletteras manuellt efter ingest.

Arkivformatet ska kunna utökas utan att befintliga Documents blir ogiltiga.

Mer avancerad bibliografisk metadata, externa metadatauppslag och automatisk metadataförbättring ligger utanför iterationen.

## Redigering av Captures

Befintliga användarskapade Captures ska kunna korrigeras genom användargränssnittet.

Det gäller både innehåll och tillhörande uppgifter, exempelvis sidhänvisning.

Redigering får inte kräva manuell ändring av JSON-filer.

Systemets princip om kumulativ historik ska bevaras.

En ändring ska därför inte innebära att den tidigare versionen försvinner utan spår.

Iterationen behöver inte införa ett generellt versionshanteringsgränssnitt.

## Korrigering av AI-review

Ett tidigare review-beslut för en AI-genererad kandidat ska kunna korrigeras.

Exempel:

- ett accepterat Claim kan i efterhand markeras som avvisat,
- ett tidigare avvisat objekt kan återställas eller accepteras om datamodellen medger detta.

Tidigare review-historik ska bevaras.

Korrigeringen ska inte innebära att AI:s ursprungliga kandidat förändras.

## Responsivitet och diagnostik

Det har vid verklig användning förekommit tillfällen då webbgränssnittet inte verkar svara på en användarhandling.

Eftersom systemet för närvarande körs lokalt ska detta inte betraktas som normal nätverkslatens.

Iterationen ska identifiera om långsamma eller blockerande operationer förekommer i det normala webbflödet.

Det ska gå att avgöra:

- vilken operation som pågår,
- om servern fortfarande arbetar,
- om disk-I/O, indexering eller annan synkron bearbetning blockerar requesten,
- om användargränssnittet behöver ge återkoppling medan en operation pågår.

Målet är i första hand att hitta och åtgärda faktiska blockeringsproblem.

Större prestandaoptimering ligger utanför iterationen.

## Avgränsning

Iteration 7.1 ska inte implementera:

- ny Project-modell,
- nya relationstyper mellan Documents,
- klassificering av användarens Captures som Claim, Insight eller Question,
- förändrad semantik för `Later`,
- större redesign av Inbox, Document eller Project,
- mobilanpassning,
- fjärråtkomst,
- MCP-server,
- avancerad bibliografisk metadatahämtning,
- generell sök- eller filtreringsfunktionalitet.

Dessa frågor ligger kvar som observationer i `UX_NOTES.md` eller hanteras i senare iterationer.

## Tester

Iterationen är godkänd när:

- befintliga Documents fortfarande kan läsas efter utökningen av metadata,
- nya Documents kan innehålla titel, upphov och utgivningsår,
- metadata från filnamn kan identifieras för det definierade filnamnsmönstret,
- metadata kan korrigeras manuellt,
- en Capture kan redigeras utan manuell ändring av Archive-filer,
- tidigare Capture-data inte förloras vid redigering,
- ett felaktigt AI-review-beslut kan korrigeras,
- AI:s ursprungliga kandidat bevaras,
- kända blockerande operationer i webbflödet antingen har åtgärdats eller kan diagnostiseras,
- hela den befintliga testsviten fortfarande passerar.

## Klart när

Iteration 7.1 är klar när följande scenario fungerar:

> Anders importerar ett dokument vars filnamn innehåller utgivningsår och titel. Dokumentverkstad registrerar användbar metadata som Anders senare kan korrigera eller komplettera. Under läsningen upptäcker han att en tidigare Capture innehåller en felaktig sidhänvisning och rättar den genom gränssnittet utan att den tidigare historiken förloras. Han kan också korrigera ett tidigare felaktigt AI-review-beslut. Det normala webbflödet innehåller inga kända oförklarliga blockeringar.

# Iteration 7.2 – Dokumentöverblick

## Syfte

Efter import av ett större befintligt dokumentarkiv har Documents-vyn blivit en central del av det dagliga arbetsflödet.

Dokumentverkstad används inte längre bara för att registrera och bearbeta enstaka nya dokument, utan också för att orientera sig bland ett växande antal tidigare importerade Documents och hitta tillbaka till relevant material.

Iteration 7.2 ska göra Documents-vyn användbar som överblick och navigationsyta även när arkivet innehåller hundratals dokument.

Iterationen ska samtidigt säkerställa att listningen förblir snabb när Archive växer.

Detta är inte en generell redesign av Dokumentverkstad och inte en implementation av fulltextsökning.

## Arbetsflöde

Användaren öppnar Documents-vyn för att hitta ett dokument.

Det ska gå att:

- snabbt filtrera listan genom att börja skriva delar av titel eller upphov,
- sortera dokument efter relevanta egenskaper,
- filtrera på bearbetningsstatus,
- filtrera på Project,
- direkt i listan se central metadata och hur mycket dokumentet har bearbetats.

Exempel:

Om användaren skriver:

`digital`

ska listan kunna begränsas till dokument med titlar som:

- `Digitala böcker ...`
- `Digital välfärdsutveckling ...`

utan att någon sökning görs i dokumentens fulltext.

Filter och sortering ska kunna kombineras där det är naturligt.

## Snabbfilter

Documents-vyn ska innehålla ett enkelt snabbfilter.

Snabbfiltret ska:

- vara case-insensitive,
- matcha delsträngar,
- minst kunna matcha titel och upphov,
- kunna användas utan att användaren behöver formulera en särskild sökfråga.

Det är önskvärt att listan filtreras medan användaren skriver, om detta kan implementeras enkelt och robust.

Snabbfiltret är ett filter över Document-metadata.

Det ska inte söka i:

- extraherad dokumenttext,
- Captures,
- Claims,
- Insights,
- Questions.

Fulltextsökning och semantisk sökning ligger utanför denna iteration.

## Sortering

Documents ska kunna sorteras efter åtminstone:

- titel,
- utgivningsår,
- senast tillagt.

Sorteringsordningen ska vara tydlig och reproducerbar.

En rimlig standardordning ska väljas utifrån det befintliga arbetsflödet.

## Filtrering

Documents-vyn ska kunna filtreras på åtminstone:

- AI-analyserad / inte AI-analyserad,
- Project.

Överväg om det går att uttrycka en enkel bearbetningsstatus utifrån redan befintliga data, exempelvis:

- inga Captures och ingen AI-analys,
- AI-analyserad,
- egna Captures finns.

Inför inte en ny permanent Document Status-modell enbart för detta.

Om en användbar status kan härledas från befintliga data ska den betraktas som presentationsdata.

## Information i listan

Varje Document i listan ska visa tillräckligt med information för att användaren ska kunna identifiera och orientera sig kring dokumentet utan att först öppna det.

Visa åtminstone:

- titel,
- utgivningsår när det finns,
- upphov när det finns,
- om AI-analys har genomförts,
- antal användarskapade Captures/Knowledge Objects kopplade till dokumentet.

Interna ID:n ska inte visas i den normala listvyn.

Presentationens exakta visuella utformning behöver inte slutdesignas i denna iteration.

## Prestanda

Efter att Archive vuxit till hundratals Documents har vissa lokala GET-requests tagit omkring 1–2 sekunder.

Documents-vyn ska inte behöva göra omfattande genomläsningar av Archive för varje request om informationen kan hämtas effektivare från Runtime/index.

Undersök vilka data som idag läses eller beräknas vid rendering av Documents-vyn.

Använd eller utöka det befintliga återskapbara Runtime-indexet där detta ger en tydlig prestandavinst.

Archive ska fortsatt vara systemets auktoritativa datakälla.

Runtime/index får endast innehålla information som kan återskapas från Archive.

Ingen information får existera enbart i indexet.

Det ska fortsatt gå att radera Runtime/index och återskapa det från Archive.

## Infrastruktur

Iterationen kan kräva:

- utökning av befintligt Runtime/SQLite-index,
- indexering av Document-metadata,
- härledda räknare eller statusuppgifter för listvyn,
- effektiva frågor för filtrering och sortering.

Inför inte en separat sökmotor eller extern söktjänst.

## Avgränsning

Iteration 7.2 ska inte implementera:

- fulltextsökning i PDF-text,
- sökning i Captures eller andra Knowledge Objects,
- semantisk sökning,
- embeddings,
- RAG,
- ny permanent Document Status-modell,
- nya relationstyper mellan Documents,
- större redesign av Documents-vyn,
- generell visuell redesign,
- mobilanpassning,
- MCP,
- Iteration 8-funktionalitet,
- Iteration 9:s övergripande UX-konsolidering.

Dessa frågor hanteras separat.

## Tester

Iterationen är godkänd när:

- snabbfiltret hittar Documents genom delsträngar i titel,
- snabbfiltret är case-insensitive,
- upphov kan användas för filtrering,
- sortering på titel fungerar,
- sortering på utgivningsår fungerar,
- sortering på senast tillagt fungerar,
- AI-analyserade och icke AI-analyserade Documents kan skiljas åt,
- Documents kan filtreras på Project,
- antal Captures visas korrekt,
- befintliga Documents utan fullständig metadata fortfarande visas korrekt,
- listdata kan återskapas från Archive efter att Runtime/index raderats,
- listningen inte kräver onödiga fullständiga genomläsningar av Archive,
- hela den befintliga testsviten fortfarande passerar.

## Klart när

Iteration 7.2 är klar när följande scenario fungerar:

> Anders öppnar Documents-vyn i ett arkiv med hundratals Documents. Han börjar skriva `digital` och listan begränsas snabbt till dokument vars metadata matchar texten. Han kan kombinera detta med att exempelvis visa dokument inom ett visst Project eller dokument som ännu inte AI-analyserats. I listan ser han titel, år, upphov, AI-status och hur många egna Captures som finns kring varje dokument. Han kan sortera resultatet och öppna rätt dokument utan att först behöva gå igenom en lång osorterad lista. Documents-vyn förblir snabb även när Archive växer.

# Iteration 8 – Låt Dokumentverkstad bli vardag

## Syfte

Iteration 8 handlar om att göra Dokumentverkstad till ett robust och portabelt vardagsverktyg.

Systemets grundläggande arbetsflöden fungerar nu i verklig användning. Documents kan importeras, bearbetas med AI, läsas och kompletteras med egna Captures. Archive innehåller verkligt material och ska betraktas som långlivad användardata.

Fokus flyttas därför från ny kärnfunktionalitet till:

- säker och enkel drift,
- säker hantering av secrets,
- backup och återställning,
- portabilitet mellan datorer,
- reproducerbar Runtime,
- kontrollerad åtkomst från andra egna enheter,
- enkel installation och första konfiguration.

Efter denna iteration ska användaren inte behöva förstå eller manuellt hantera Dokumentverkstads interna filstruktur för normal drift.

---

## Grundprincip

Archive är systemets auktoritativa och långlivade datalager.

Runtime, index och andra härledda data ska kunna raderas och återskapas från Archive.

Secrets ska hanteras separat från Archive och ska inte ingå i vanliga backups eller exporter.

Iteration 8 får inte införa nya beroenden mellan Archive och en viss dator, installation eller nätverksmiljö.

---

## 1. Installation och initiering

En ny installation ska kunna initieras genom ett tydligt arbetsflöde.

Det ska inte krävas att användaren manuellt skapar interna kataloger eller redigerar interna konfigurationsfiler för att få en grundinstallation att fungera.

Ett CLI-baserat initieringsflöde är tillräckligt.

Exempel:

```text
dokumentverkstad init
```

Initieringen ska kunna:

- skapa nödvändig katalogstruktur,
- skapa eller konfigurera grundläggande icke-hemlig konfiguration,
- initiera Runtime,
- initiera secrets-hantering,
- kontrollera att installationen är användbar.

Extern AI och fjärråtkomst ska fortsatt vara valfria funktioner.

Dokumentverkstad ska kunna användas utan dem.

---

## 2. Secrets och säker start

API-nycklar och andra secrets ska inte behöva lagras i klartext i vanlig konfiguration.

Dokumentverkstad ska erbjuda lokal krypterad lagring av secrets.

Användaren ska kunna skydda denna lagring med ett separat adminlösenord eller motsvarande lokal autentisering.

Ett normalt startflöde kan exempelvis vara:

1. användaren startar Dokumentverkstad,
2. Dokumentverkstad begär lösenord för att låsa upp secrets,
3. secrets görs tillgängliga för den körande processen,
4. tjänsten startar.

Lösenordet självt ska inte lagras i klartext.

Secrets ska inte:

- skrivas till loggar,
- visas i webbgränssnittet,
- lagras i Archive,
- inkluderas i vanlig backup/export,
- committas till Git.

Exakt kryptografisk implementation ska väljas utifrån etablerade bibliotek och vedertagna metoder.

Egen kryptografi ska inte implementeras.

---

## 3. Drift och CLI

Normala driftoperationer ska kunna utföras genom tydliga kommandon.

Överväg stöd för exempelvis:

```text
dokumentverkstad start
dokumentverkstad stop
dokumentverkstad status
dokumentverkstad backup
dokumentverkstad restore
dokumentverkstad rebuild-index
```

Den exakta CLI-strukturen får anpassas till befintlig implementation.

Målet är att användaren inte ska behöva känna till interna Python-moduler eller filoperationer för normal drift.

Systemet ska ge begripliga felmeddelanden när något saknas eller inte kan startas.

---

## 4. Backup och portabilitet

Dokumentverkstad ska kunna skapa en reproducerbar backup av användarens långlivade data.

Exempel:

```text
dokumentverkstad backup
```

kan skapa något i stil med:

```text
dokumentverkstad-backup-2026-08-18.zip
```

Backupen ska minst innehålla:

- Archive,
- nödvändig icke-hemlig konfiguration,
- information som krävs för att förstå backupformat och version.

Backupen ska inte behöva innehålla Runtime eller index om dessa kan återskapas.

Secrets ska som standard inte ingå.

Backupformatet ska så långt möjligt bestå av den befintliga öppna filstrukturen snarare än ett nytt proprietärt exportformat.

---

## 5. Restore

En backup ska kunna återställas till en ny eller tom installation.

Exempel:

```text
dokumentverkstad restore dokumentverkstad-backup-2026-08-18.zip
```

Efter restore ska Dokumentverkstad kunna:

1. återställa Archive,
2. återställa relevant icke-hemlig konfiguration,
3. bygga upp Runtime/index på nytt,
4. verifiera att arkivet är läsbart.

Secrets ska vid behov konfigureras separat på den nya installationen.

Restore ska inte tyst skriva över ett befintligt Archive utan tydlig kontroll eller uttryckligt användarbeslut.

---

## 6. Reproducerbar Runtime

Det ska vara möjligt att radera hela Runtime och därefter återskapa den från Archive.

Detta gäller bland annat:

- index,
- härledda räknare,
- sök- och listdata som redan används av systemet,
- annan cache eller runtime-state som inte är auktoritativ.

Ett kommando som:

```text
dokumentverkstad rebuild-index
```

ska kunna användas för detta.

Ingen användarskapad information får gå förlorad när Runtime raderas.

Detta ska testas mot ett realistiskt Archive med Documents, Knowledge Objects, Projects och AI-runs.

---

## 7. Trash och återställning

Befintliga principer för Trash ska färdigställas för vardagsanvändning.

Användaren ska kunna:

- ta bort objekt utan omedelbar permanent förlust,
- se vad som finns i Trash,
- återställa objekt,
- permanent radera objekt enligt systemets definierade regler.

Historik och referenser ska hanteras på ett förutsägbart sätt.

Normal användning ska inte kräva manuell redigering av Archive-filer.

---

## 8. Fjärråtkomst från egna enheter

Dokumentverkstad ska kunna nås från en annan egen enhet på ett kontrollerat sätt.

Det primära användningsfallet är åtkomst från exempelvis mobiltelefon, iPad eller annan egen dator.

Tailscale är en möjlig och önskvärd driftlösning, men Dokumentverkstad ska inte göras arkitektoniskt beroende av Tailscale.

Systemet ska kunna konfigureras för att lyssna på en adress som gör sådan åtkomst möjlig.

Det ska dokumenteras tydligt:

- vilken nätverksyta tjänsten exponeras på,
- vilka säkerhetskonsekvenser detta har,
- hur lokal-only drift skiljer sig från fjärråtkomst.

Dokumentverkstad ska inte exponeras öppet mot internet som en bieffekt av denna iteration.

---

## 9. Mobil ingest

När Dokumentverkstad nås från en mobil enhet ska det finnas ett enkelt sätt att lägga ett dokument i systemets ingest-flöde.

Målet är att användaren exempelvis ska kunna:

1. få eller hitta en PDF på telefonen,
2. öppna Dokumentverkstad,
3. välja filen,
4. lägga den i Inbox/ingest,
5. låta det befintliga ingest-flödet ta över.

Mobil ingest ska använda samma grundläggande Document- och Archive-semantik som annan ingest.

Skapa inte ett separat mobilt arkiv eller parallellt importflöde.

Den visuella mobilupplevelsen behöver inte slutdesignas i denna iteration.

---

## 10. Responsivitet och långvariga operationer

Iteration 7.1 identifierade att AI-anrop fortfarande körs synkront i HTTP-requesten.

Verkliga AI-anrop kan ta omkring en minut eller mer.

Undersök om långvariga AI-operationer bör flyttas från den synkrona requesten till ett enkelt bakgrundsjobb.

Målet är att:

- webbservern fortsatt ska kunna svara under ett AI-anrop,
- användaren ska kunna se att analys pågår,
- resultatet ska sparas enligt befintlig AI-run-semantik,
- fel och avbrutna körningar ska kunna diagnostiseras.

Inför inte en distribuerad jobbkösarkitektur om en betydligt enklare lokal lösning räcker.

Om befintlig serverarkitektur redan hanterar parallella requests tillräckligt väl ska detta verifieras innan ny infrastruktur införs.

---

## 11. Diagnostik

Den diagnostik som infördes i Iteration 7.1 ska utvecklas till stöd för vardagsdrift.

Det ska vara möjligt att förstå:

- om tjänsten kör,
- om Archive är tillgängligt,
- om Runtime/index fungerar,
- om AI-provider är konfigurerad,
- om en långvarig operation pågår eller har misslyckats.

Loggar får inte innehålla:

- API-nycklar,
- lösenord,
- dokumentinnehåll,
- andra secrets.

Diagnostik ska i första hand hjälpa till att identifiera fel, inte samla generell användartelemetri.

---

## Tester

Iteration 8 är godkänd när minst följande kan verifieras.

### Installation

- en tom installation kan initieras utan manuell redigering av interna filer,
- nödvändiga kataloger och konfiguration skapas korrekt.

### Secrets

- secrets kan lagras utan klartext i vanlig konfiguration,
- korrekt lösenord kan låsa upp secrets,
- felaktigt lösenord ger ett säkert och begripligt fel,
- secrets förekommer inte i loggar eller vanlig backup.

### Backup och restore

- ett befintligt Archive kan säkerhetskopieras,
- backupen kan återställas till en tom installation,
- Documents, Projects, Knowledge Objects och AI-historik bevaras,
- Runtime/index kan återskapas efter restore,
- secrets behöver inte följa med backupen.

### Runtime

- Runtime kan raderas fullständigt,
- Runtime/index kan återskapas från Archive,
- ingen användardata går förlorad.

### Trash

- borttagna objekt kan återställas enligt definierad Trash-semantik.

### Fjärråtkomst

- tjänsten kan nås från en annan egen enhet när detta uttryckligen konfigurerats,
- lokal-only drift fungerar fortsatt.

### Mobil ingest

- en PDF som laddas upp via webbgränssnittet går genom det befintliga ingest-flödet och blir ett normalt Document.

### Responsivitet

- långvariga AI-anrop gör inte tjänsten oanvändbar för andra normala operationer,
- AI-run-status och felhantering bevaras.

Hela den befintliga testsviten ska fortsatt passera.

---

## Avgränsning

Iteration 8 ska inte implementera:

- generell visuell redesign,
- slutlig mobil design,
- fulltextsökning,
- semantisk sökning,
- embeddings eller RAG,
- ny ämnes- eller taggmodell,
- förändrad Project-semantik,
- nya Document-relationer,
- MCP-server,
- extern AI-åtkomst till kunskapsrummet,
- automatisk AI-optimering.

Dessa frågor hör till senare iterationer.

---

## Implementationsordning

Iteration 8 implementeras stegvis snarare än som ett enda förändringspaket.

Under verklig användning har iterationen delats upp i mindre delar för att hålla förändringarna granskningsbara och för att undvika att flera arkitekturbeslut införs samtidigt.

### 8.1 – Initiering, CLI och secrets

Omfattar:

* initieringsflöde,
* grundläggande driftkommandon,
* krypterad secrets-lagring,
* säker start,
* status för installation och AI-konfiguration.

**Status: genomförd.**

### 8.2 – Backup, restore och reproducerbar Runtime

Omfattar:

* backup,
* restore,
* portabilitet,
* rebuild-index,
* verifiering av Archive som auktoritativ källa,
* verifiering att Runtime kan raderas utan informationsförlust.

Backup ska endast innehålla långlivad information och nödvändig portabel konfiguration. Secrets och Runtime ska inte ingå.

**Status: genomförd och verifierad mot ett verkligt Archive.**

### 8.3 – Trash, drift och diagnostik

Omfattar:

* Trash-hantering för Documents,
* Restore från Trash,
* säker permanent radering där detta är möjligt,
* driftstatus,
* diagnostik,
* loggning,
* kontroll av Archive, Runtime och index.

**Status: genomförd.**

### 8.4a – Fjärråtkomst och webb-ingest

Omfattar:

* möjlighet att nå Dokumentverkstad från en annan egen enhet,
* dokumenterad användning tillsammans med Tailscale,
* PDF-uppladdning genom webbgränssnittet,
* gemensamt ingest-flöde för lokal och webbaserad uppladdning,
* säker staging av uppladdade filer,
* samma checksumme-, dublett- och Archive-semantik oavsett ingest-väg.

Dokumentverkstad ska inte göras arkitektoniskt beroende av Tailscale.

Webbservern ska fortsatt kunna köras lokalt och behöver inte i denna deliteration exponeras öppet mot internet.

**Status: implementerad. Verifiering från andra egna enheter återstår som praktiskt driftstest.**

### 8.4b – Långvariga AI-operationer

AI-analyser kan ta omkring en minut eller mer och ska därför inte göra det normala webbgränssnittet oanvändbart medan analysen pågår.

Denna deliteration ska undersöka och vid behov införa ett enkelt bakgrundsflöde för AI-analyser.

Målet är att:

* användaren kan starta en AI-analys och därefter fortsätta använda Dokumentverkstad,
* ett Document tydligt kan visa att AI-analys pågår,
* en färdig analys kan öppnas för review utan att användaren behöver leta efter den,
* befintlig AI-run-semantik och proveniens bevaras,
* fel och avbrutna körningar kan diagnostiseras,
* serveromstart och andra relevanta felsituationer får ett definierat beteende.

Inför inte en distribuerad jobbkösarkitektur om en enklare lösning räcker.

Den exakta interaktionen ska samordnas med Iteration 9 så att bakgrundsjobb passar in i Dokumentverkstads konsoliderade gränssnitt.

**Status: återstår.**

---

## Klart när

Iteration 8 är klar när följande scenario fungerar:

> Anders använder Dokumentverkstad som ett långlivat vardagsverktyg med ett verkligt dokumentarkiv. Tjänsten kan startas utan manuell hantering av secrets, nås kontrollerat från andra egna enheter och ta emot nya PDF:er därifrån. Han kan skapa en backup av hela sitt kunskapsarkiv och återställa den på en ny installation. Runtime kan raderas och återskapas från Archive utan dataförlust. Långvariga AI-operationer hindrar inte fortsatt arbete och när något går fel finns tillräcklig diagnostik för att förstå problemet utan att känsliga uppgifter exponeras.

Efter Iteration 8 ska Dokumentverkstad inte bara fungera som program.

Den ska gå att förvalta som ett personligt, långlivat kunskapsarkiv.

# Iteration 9 – Konsolidera arbetsytan

## Syfte

Dokumentverkstad används nu i verkligt arbete med ett Archive som innehåller hundratals Documents och ett växande antal Knowledge Objects.

Grundflödet fungerar.

Iteration 9 ska därför inte introducera en ny domänmodell eller större ny kärnfunktionalitet. Den ska göra de befintliga funktionerna till ett sammanhängande arbetsverktyg.

Utgångspunkten är:

* observationerna i `UX_NOTES.md`,
* erfarenheter från verklig daglig användning,
* de framtagna designskisserna,
* de arbetsflöden som redan visat sig fungera.

Iteration 9 är både en UX-iteration och en visuell designiteration.

Visuell förändring ska dock alltid stödja informationsarkitektur och arbetsflöde. Funktion ska styra form.

## Grundprincip

> Användaren ska arbeta med dokument, kunskap och egna tankar – inte med Dokumentverkstads interna modell.

Gränssnittet ska därför prioritera:

1. innehållet användaren arbetar med,
2. den handling som är naturlig i det aktuella sammanhanget,
3. orientering och navigation,
4. teknisk eller administrativ information först när den behövs.

Interna ID:n, implementationstekniska begrepp och sällan använda funktioner ska inte dominera normala arbetsytor.

## Arbetsflöden

Iteration 9 ska framför allt konsolidera följande arbetsflöden.

### Fånga en tanke

Capture ska fortsätta vara ett lågfriktionsflöde.

Det ska vara möjligt att:

* snabbt skapa en fristående Capture,
* skapa en Capture i ett Document,
* skapa en Capture i ett Project där detta är naturligt,
* skriva en Capture samtidigt som användaren läser annat innehåll,
* återvända till tidigare Captures som minnesanteckningar.

Capture ska inte kräva att användaren först klassificerar eller organiserar tanken.

Principen:

> Capture first, organize later.

ska bevaras.

### Arbeta med ett Document

Document-vyn ska fungera som den naturliga arbetsytan kring ett dokument.

Användaren ska snabbt kunna förstå:

* vilket dokument detta är,
* dess centrala metadata,
* vad användaren själv tidigare har tänkt om dokumentet,
* vilken AI-analys som finns,
* vilka Projects dokumentet hör till,
* vilka relevanta handlingar som går att utföra.

Egna Captures ska vara lätta att återfinna och tydligt skiljas från AI-genererat material.

Capture ska vara tillgängligt utan att användaren behöver lämna det innehåll som läses.

Original-PDF ska kunna öppnas utan att Dokumentverkstads arbetsyta försvinner, exempelvis i en ny webbläsarflik.

Metadataredigering ska vara tillgänglig men behöver inte dominera arbetsytan.

### Orientera sig bland Documents

Documents-vyn är en navigationsyta för ett växande Archive.

Den funktionalitet som etablerades i Iteration 7.2 ska bevaras:

* snabbfilter,
* sortering,
* Project-filter,
* AI-status,
* antal Captures,
* central metadata.

Utgivningsår ska vara naturlig standardordning så länge verklig användning inte visar något annat.

Manuellt skapande av Document utan ingest är ett specialfall och ska inte dominera denna vy.

Den visuella utformningen ska göra det lätt att skanna stora mängder dokument utan att informationsmängden blir tung.

### Arbeta med Inbox

Inbox är en arbetsyta för sådant som behöver ett användarbeslut.

Den ska inte upplevas som ett alternativt dokumentarkiv.

När flera objekt väntar ska användaren snabbt kunna förstå:

* hur mycket som återstår,
* vilken typ av beslut som behöver fattas,
* vad som redan har behandlats,
* vart användaren går efter ett beslut.

Onödiga omladdningar och navigationssteg ska minimeras.

Undersök om flera enkla beslut kan genomföras effektivare utan att varje objekt måste behandlas genom ett fullständigt separat sidflöde.

Inför inte massredigering enbart för att funktionen är möjlig. Den ska införas endast om den tydligt minskar den friktion som observerats vid större Inboxar.

AI-review ska ge en naturlig väg tillbaka till det Document som analyserats.

### Arbeta med Projects

Projects ska behandlas som användarcentrerade sammanhang.

Ett Project beskriver i första hand:

> varför något är relevant för användarens arbete,

inte nödvändigtvis:

> vad ett dokument objektivt handlar om.

Iteration 9 ska därför inte försöka göra Projects till en fullständig ämnesklassifikation.

Documents får sakna Project.

Project-vyn ska i första hand visa det material användaren arbetar med:

* relevanta Documents,
* Captures och andra Knowledge Objects,
* aktuella arbetsmöjligheter.

Project-metadata ska finnas men behöver inte dominera arbetsytan.

Explicita relationer mellan Knowledge Objects ska inte ges en central plats i gränssnittet innan verklig användning visar att de behövs.

## Navigation

Dokumentverkstad ska få en tydlig och konsekvent informationsarkitektur.

Det ska vara lätt att röra sig mellan åtminstone:

* Inbox,
* Documents,
* Projects,
* fristående Capture,
* aktuellt Document,
* aktuellt Project.

Navigationen ska fungera på både desktop och mindre skärmar.

Användaren ska inte behöva förstå URL-struktur eller använda webbläsarens bakåtknapp som huvudsaklig navigationsmodell.

När en handling leder till ett nytt tillstånd ska nästa naturliga steg vara tydligt.

## AI i gränssnittet

AI ska fortsatt vara rådgivare, inte auktoritet.

Gränssnittet ska tydligt skilja mellan:

* användarskapat innehåll,
* accepterat AI-genererat innehåll,
* AI-kandidater som väntar på review,
* AI-analys som pågår,
* misslyckad eller avbruten AI-analys.

AI Questions ska presenteras som frågor som AI-analysen väcker, inte som frågor dokumentet nödvändigtvis besvarar.

Om Iteration 8.4b inför bakgrundskörning ska dess status och återkoppling integreras i samma visuella språk.

## Visuellt designsystem

Iteration 9 ska etablera ett konsekvent visuellt designsystem för Dokumentverkstad.

Utgångspunkten är de designskisser som tagits fram före iterationen.

Den övergripande riktningen är ett möte mellan:

* modernistiskt arkiv,
* bibliotek och dokumentation,
* återhållsam retrofuturism,
* geometriska och lätt ockulta referenser.

Det visuella uttrycket får vara särpräglat men ska aldrig göra informationen svårare att läsa.

### Färg

Grundpaletten utgår från:

* **ivory** – huvudsaklig ljus yta,
* **ebony** – text, struktur och mörka ytor,
* **cinnabar** – accent, handling och orientering.

Färg ska användas funktionellt och sparsamt.

Gradients ska inte användas.

### Typografi

Typografin ska skapa:

* tydlig hierarki,
* god läsbarhet,
* tydlig skillnad mellan dokumentinnehåll, metadata och systeminformation.

Långa texter, Summaries och Captures ska prioriteras som läsinnehåll.

Små tekniska etiketter och metadata kan använda ett mer arkivmässigt eller maskinellt uttryck.

### Identitet

Diskreta systemetiketter kan exempelvis använda former som:

`DOC 0241`

`YR 2025`

`AI COMPLETE`

så länge de bygger på information som faktiskt hjälper användaren.

Geometriska symboler och andra identitetsskapande element får användas för navigation, orientering och visuell karaktär, men inte som dekoration som konkurrerar med innehållet.

## Responsiv design

Iteration 9 ska omfatta både desktop och mobil användning.

Mobilvyn ska inte bara vara desktop-layouten hoptryckt till en smal skärm.

Prioriteringen på mindre skärmar ska utgå från verkliga mobila arbetsflöden, framför allt:

* Inbox,
* Capture,
* uppladdning av Document,
* snabb kontroll av ett Document,
* enklare AI-review,
* navigation.

Desktop ska ge bättre utrymme för parallell läsning och Capture där detta minskar friktion.

E-ink kan beaktas genom god kontrast, typografi och begränsat beroende av färg, men särskild e-ink-funktionalitet ska inte byggas utan ett konkret behov.

## Interaktion

Iteration 9 får införa enklare klientbaserad interaktion där detta tydligt förbättrar arbetsflödet.

Det kan exempelvis gälla:

* uppdatering av Inbox utan full sidomladdning,
* tydlig återkoppling efter en handling,
* status för pågående AI-jobb,
* snabbare Capture,
* enklare filtrering.

Javascript ska användas som ett verktyg för minskad friktion, inte som anledning att bygga om applikationen till en komplex klientapplikation.

Server-rendering får fortsatt vara grundmodell där den fungerar väl.

Tangentbordsgenvägar, swipe och drag-and-drop ska endast införas där ett verkligt arbetsflöde motiverar dem.

## Avgränsning

Iteration 9 ska inte implementera:

* ny generell Project-modell,
* ämnesklassifikation eller generell taggmodell,
* semantisk sökning,
* embeddings,
* RAG,
* generell fulltextsökning,
* MCP-server,
* OCR,
* EPUB eller andra nya dokumentformat,
* lokal AI-modell,
* multimodal dokumentanalys,
* automatisk bibliografisk metadatahämtning,
* generell modell för Document-versioner eller Document-relationer,
* ny generell Knowledge Object-ontologi.

Sådana behov ska dokumenteras i `UX_NOTES.md` eller backloggen och tas upp i senare iterationer.

## Implementation

Iteration 9 bör genomföras i mindre, visuellt och funktionellt sammanhängande deliterationer.

En möjlig ordning är:

### 9.1 – Designgrund och navigation

* gemensamt visuellt designsystem,
* typografi,
* färg,
* spacing,
* grundkomponenter,
* huvudnavigation,
* desktop- och mobilstruktur.

### 9.2 – Documents och Document

* Documents-lista,
* Document-arbetsyta,
* Capture under läsning,
* presentation av egna Captures,
* AI-material,
* metadata,
* originaldokument.

### 9.3 – Inbox och AI-review

* Inbox-överblick,
* effektivare triage,
* review-flöde,
* återkoppling,
* integration med bakgrundsjobb.

### 9.4 – Projects och Capture

* Project-vy,
* fristående Capture,
* organisering av befintliga Knowledge Objects där befintlig domänmodell medger detta,
* konsekvent navigation mellan sammanhang.

Deliterationerna får ändras efter att designarbetet konkretiserats.

## Tester

Iteration 9 är godkänd när:

* befintliga kärnflöden fortsatt fungerar,
* inga Archive-format behöver förändras enbart på grund av designen,
* Capture kan göras utan onödiga navigationssteg,
* Documents kan orienteras och filtreras effektivt,
* ett Document tydligt presenterar metadata, egna Captures och AI-material,
* Inbox ger tydlig överblick och återkoppling,
* Projects fungerar som användarcentrerade sammanhang utan att klassifikation framtvingas,
* navigationen fungerar konsekvent på desktop och mobil,
* centrala arbetsflöden fungerar utan Javascript där sådan graceful degradation är rimlig,
* hela den befintliga automatiska testsviten fortsatt passerar.

## Klart när

Iteration 9 är klar när följande scenario fungerar:

> Anders öppnar Dokumentverkstad för att arbeta, inte för att administrera systemet. Han hittar snabbt rätt dokument, ser vad han tidigare tänkt om det och kan skriva en ny Capture medan han läser. Ett nytt dokument kan tas om hand genom Inbox och AI-review utan onödiga omladdningar eller orienteringsproblem. Projects hjälper honom att återvända till material utifrån varför det är relevant för hans arbete. Samma kunskapsrum fungerar naturligt från dator, iPad och telefon. Gränssnittet har en tydlig egen identitet men drar inte uppmärksamheten från dokumenten och tänkandet.

# Iteration 10 – Ett kunskapsrum, flera klienter

## Syfte

Hittills har Dokumentverkstad huvudsakligen körts på samma dator som användaren arbetar vid.

Iteration 10 ska verifiera en annan driftmodell:

> Dokumentverkstad har ett enda auktoritativt Archive på en server. Användarens datorer, telefoner och surfplattor är klienter till samma kunskapsrum.

Målet är inte att göra Dokumentverkstad till en publik molntjänst eller ett fleranvändarsystem.

Målet är att göra den befintliga personliga applikationen oberoende av vilken klient användaren råkar arbeta från.

## Grundprincip

Det ska finnas **ett kanoniskt Archive**.

Flera aktiva Dokumentverkstad-installationer med separata Archive som behöver synkroniseras ska undvikas.

Serverns lagringsplats kan förändras över tid utan att Archive-formatet behöver förändras.

Det kan exempelvis vara:

* en hyrd virtuell Linux-server,
* en framtida egen hemmaserver,
* en Mac mini,
* annan maskin med lämplig persistent lagring.

Driftmiljön är utbytbar.

Archive är beständigt.

## Första referensmiljö

En liten hyrd Linux-VPS kan användas som första verkliga referensmiljö.

Syftet är att prova servermodellen utan att först behöva köpa särskild hårdvara.

VPS-lösningen ska inte innebära att Dokumentverkstad görs beroende av en viss molnleverantör.

Applikationen ska fortsatt använda vanliga filer, SQLite där Runtime behöver det och den befintliga Archive-strukturen.

PaaS-lösningar som kräver att Archive flyttas till proprietär databas eller objektlagring ska inte införas enbart för deploymentens skull.

## Arbetsflöde

Användaren ska kunna:

1. öppna Dokumentverkstad i en vanlig webbläsare,
2. autentisera sig,
3. använda samma Archive oavsett klient,
4. ladda upp nya Documents,
5. göra Captures,
6. starta och reviewa AI-analyser,
7. stänga klienten utan att någon lokal Archive-synkronisering behövs.

## Persistent lagring

Archive ska ligga på persistent lagring.

Serverns temporära filsystem eller container-state får inte vara den enda lagringsplatsen för långlivad information.

Runtime ska fortsatt vara härledd och reproducerbar.

Samma invariant gäller:

> Archive är auktoritativt. Runtime är härlett och kan återskapas.

## HTTPS och autentisering

En internetåtkomlig Dokumentverkstad måste skyddas med:

* HTTPS,
* autentisering,
* begränsad åtkomst,
* säker secrets-hantering.

Att känna till serverns URL får inte i sig ge tillgång till Archive.

Den exakta lösningen ska väljas när iterationen genomförs.

Möjliga arkitekturer kan exempelvis använda en autentiserande reverse proxy eller extern access-gateway framför Dokumentverkstad.

Dokumentverkstad ska inte exponeras direkt mot internet utan ett definierat autentiseringslager.

Arbetsplatsens säkerhetspolicy och nätverksbegränsningar ska respekteras. Iterationen ska inte försöka kringgå administrativt införda begränsningar.

## Drift

Servern ska kunna:

* starta automatiskt efter omstart,
* köras utan ett öppet terminalfönster,
* rapportera begriplig status,
* skriva diagnostiska loggar,
* återhämta sig från normala omstarter,
* uppdateras på ett kontrollerat sätt.

Normal användning ska inte kräva SSH eller serveradministration.

Administrativa operationer får däremot fortsatt vara CLI-baserade.

## Backup

Central drift gör backup viktigare, inte mindre viktig.

Det ska finnas en definierad strategi för regelbundna backups till en annan lagringsplats än den aktiva serverdisken.

Backupen ska bygga vidare på det format och restore-flöde som etablerades i Iteration 8.

Automatisk backup kan införas om det kan göras enkelt och robust.

En ny backup ska verifieras innan äldre backups tas bort.

Behållning av flera generationer ska föredras framför att endast behålla den senaste kopian.

## Portabilitet och återställning

Det ska vara möjligt att:

1. skapa backup på server A,
2. skapa en ny installation på server B,
3. återställa backupen,
4. återskapa Runtime,
5. fortsätta använda samma kunskapsrum.

En hyrd VPS ska därför kunna ersättas av exempelvis en framtida hemmaserver utan datamigrering till ett nytt proprietärt format.

## Avgränsning

Iteration 10 ska inte implementera:

* flera användare,
* samarbetsfunktioner,
* synkronisering mellan flera Archive,
* Kubernetes eller distribuerad drift,
* distribuerad databas,
* proprietär molnlagring enbart för deployment,
* publik delning av Documents,
* MCP,
* extern AI-åtkomst till Archive.

## Tester

Iteration 10 är godkänd när:

* Dokumentverkstad kan installeras på den valda servermiljön,
* ett verkligt Archive kan återställas där,
* Archive ligger på persistent lagring,
* tjänsten överlever serveromstart,
* tjänsten nås genom HTTPS,
* obehörig åtkomst stoppas,
* Dokumentverkstad fungerar från minst två olika klientenheter,
* PDF-uppladdning fungerar från fjärrklient,
* Capture fungerar från fjärrklient,
* AI-flödet fungerar från fjärrklient,
* backup kan skapas på servern,
* backupen kan återställas till en separat installation,
* Runtime fortsatt kan återskapas från Archive,
* hela den befintliga testsviten fortsatt passerar.

## Klart när

Iteration 10 är klar när följande scenario fungerar:

> Anders öppnar Dokumentverkstad från en vanlig webbläsare på en dator, en iPad eller en telefon och arbetar alltid mot samma kunskapsrum. Archive finns på en server och behöver inte synkroniseras mellan klienterna. Nya dokument, Captures och AI-resultat blir omedelbart del av samma Archive. Servern kan startas om utan handpåläggning och kunskapsrummet kan säkerhetskopieras och återställas på en annan maskin utan att dess struktur förändras.

# Senare iterationer

Efter Iteration 10 är Dokumentverkstads grundläggande MVP etablerad:

* kunskap kan fångas,
* Documents kan arkiveras och bearbetas,
* Projects kan ge användarcentrerade sammanhang,
* AI kan bidra med granskade kandidater,
* Archive är portabelt och reproducerbart,
* gränssnittet är konsoliderat för verklig användning,
* ett enda kunskapsrum kan användas från flera klienter.

Fortsatt utveckling ska därefter styras av verklig användning och backloggen.

Möjliga senare områden omfattar bland annat:

* read-only MCP och extern AI-åtkomst till kunskapsrummet,
* fulltextsökning i Documents och Knowledge Objects,
* OCR för bildbaserade PDF:er,
* fler dokumentformat, i första hand EPUB,
* lokal AI,
* multimodal dokumentanalys,
* bibliografisk metadatahämtning,
* Document-relationer och versioner,
* vidareutvecklad proveniens för relationer,
* frivilliga semantiska typer för egna Captures,
* vidareutveckling av Later/Snooze,
* arkivintegritet och digitalt bevarande,
* BagIt-kompatibla preservation packages,
* periodiska fixity-kontroller,
* utvärdering mot relevanta principer från etablerade Trusted Digital Repository-modeller.

Ingen av dessa punkter är genom sin placering här beslutad för implementation.

De ska prioriteras först när verklig användning visar vilket problem som är viktigast att lösa.

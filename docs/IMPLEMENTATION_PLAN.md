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

# Iteration 8 – Låt Dokumentverkstad bli vardag

## Syfte

Den sista iterationen handlar inte om en ny funktion.

Den handlar om att systemet ska kunna användas varje dag utan att användaren behöver tänka på infrastrukturen.

## Arbetsflöde

Dokumentverkstad körs kontinuerligt.

Nya dokument registreras.

Inbox fylls.

Capture används.

Projects utvecklas.

Systemet blir en naturlig del av användarens arbete.

## Infrastruktur

Denna iteration omfattar:

- drift
- CLI
- backup
- index rebuild
- återställning
- felsökning

## Implementation

Iterationen implementerar:

- CLI
- driftkommandon
- Trash
- restore
- index rebuild
- backup-rutiner

## Tester

Iterationen är godkänd när:

- systemet kan köras under längre tid
- data aldrig förloras
- hela systemet kan återställas från arkivet

## Klart när

Iteration 8 är klar när följande scenario fungerar:

> Anders använder Dokumentverkstad som sitt dagliga arbetsverktyg. Han tänker sällan på hur systemet fungerar, utan använder det på samma självklara sätt som en programmerare använder sitt IDE.
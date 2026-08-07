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

## Implementation

Iterationen implementerar:

- PDF-ingest
- automatisk Document-registrering
- metadataextraktion
- lagring av originalfil
- länk till originalfil

Ingen AI-analys sker ännu.

## Tester

Iterationen är godkänd när:

- PDF registreras automatiskt
- dubletter upptäcks
- originalfil sparas
- dokument kan öppnas från webbgränssnittet

## Klart när

Iteration 4 är klar när följande scenario fungerar:

> Anders sparar en rapport i Dropbox. Några sekunder senare finns den registrerad i Dokumentverkstad och kan användas precis som ett manuellt registrerat dokument.

# Iteration 5 – Börja sortera

## Syfte

Den femte iterationen introducerar Inbox.

Nu börjar Dokumentverkstad aktivt hjälpa användaren att organisera sitt arbete.

Inbox är inte en lista över dokument.

Inbox är en lista över beslut som väntar.

## Arbetsflöde

Användaren öppnar Dokumentverkstad på telefonen.

Inbox visar:

- nya dokument,
- dokument utan Project,
- dokument som väntar på AI-analys,
- andra objekt som behöver användarens uppmärksamhet.

Användaren går igenom inkorgen ett objekt i taget.

Varje beslut leder direkt vidare till nästa.

## Infrastruktur

Denna iteration kräver:

- Inbox
- status för "väntar på review"
- enkel arbetskö

## Implementation

Iterationen implementerar:

- Inbox-vy
- beslut: senare
- beslut: kasta
- beslut: koppla till Project
- beslut: klar

Inbox blir systemets startsida på telefon.

## Tester

Iterationen är godkänd när:

- nya dokument hamnar i Inbox
- ett beslut tar bort objektet från Inbox
- nästa objekt visas direkt
- Inbox fungerar väl även på telefon

## Klart när

Iteration 5 är klar när följande scenario fungerar:

> Anders sitter på tåget och går igenom dagens nya dokument på telefonen. På några minuter har han sorterat allt utan att behöva öppna några avancerade vyer.

# Iteration 6 – Ta hjälp av AI

## Syfte

Den sjätte iterationen introducerar AI som en rådgivare.

AI producerar aldrig etablerad kunskap.

Den producerar endast kandidater.

## Arbetsflöde

Användaren öppnar ett nytt dokument.

Systemet visar:

- uppskattad kostnad,
- vald modell,
- uppskattad tokenförbrukning.

Användaren väljer att starta analysen.

AI producerar:

- Summary
- Candidate Insights
- Candidate Claims
- Candidate Questions
- föreslagna Projects

Allt placeras i Inbox för review.

## Infrastruktur

Denna iteration kräver:

- AI-provider
- provider-interface
- kostnadsberäkning
- promptsystem

## Implementation

Iterationen implementerar:

- AI-provider
- mock-provider
- kostnadsdialog
- AI-kandidater
- proveniens
- review

Ingen AI får skapa etablerade Knowledge Objects.

## Tester

Iterationen är godkänd när:

- AI aldrig körs utan godkännande
- kostnad visas före körning
- faktisk kostnad sparas
- kandidater alltid kräver review

## Klart när

Iteration 6 är klar när följande scenario fungerar:

> Anders lägger in en rapport, väljer att använda moln-AI och får några minuter senare ett antal kandidater som kan accepteras, redigeras eller avvisas.

# Iteration 7 – Lär av användningen

## Syfte

Den sjunde iterationen introducerar systemets självobservation.

Dokumentverkstad ska kunna lära sig hur användaren arbetar utan att automatiskt förändra sitt beteende.

## Arbetsflöde

När användaren arbetar registrerar systemet:

- accepterade AI-förslag,
- redigerade förslag,
- avvisade förslag,
- kostnader,
- modeller,
- svarstider.

Ingen automatisk optimering sker ännu.

Systemet samlar endast erfarenheter.

## Infrastruktur

Denna iteration kräver:

- loggning
- statistik
- analysdata

## Implementation

Iterationen implementerar:

- lagring av review-data
- lagring av AI-statistik
- lagring av kostnader
- enkel administrationsvy

## Tester

Iterationen är godkänd när:

- review-data sparas
- kostnader kan summeras
- AI-användning kan följas över tid

## Klart när

Iteration 7 är klar när följande scenario fungerar:

> Anders kan efter några månaders användning se hur mycket AI som använts, vad den kostat och vilka typer av förslag som oftast accepterats.

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
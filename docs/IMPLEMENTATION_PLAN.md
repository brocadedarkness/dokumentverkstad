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

Iteration 8 handlar inte om ny kärnfunktionalitet.

Den handlar om att Dokumentverkstad ska kunna användas varje dag utan att användaren behöver tänka på infrastrukturen, samtidigt som tjänsten och dess hemligheter skyddas på ett begripligt sätt.

Dokumentverkstad ska vara stabil, återställningsbar och säker nog för kontinuerlig personlig användning.

## Arbetsflöde

Dokumentverkstad startas.

Innan webbservern blir tillgänglig måste användaren ange ett adminlösenord.

Adminlösenordet används för att låsa upp tjänsten och dekryptera lokalt lagrade secrets, exempelvis API-nycklar.

När tjänsten är upplåst:

* Dokumentverkstad körs kontinuerligt,
* nya dokument kan tas emot,
* Inbox fylls,
* Capture används,
* Projects utvecklas,
* AI kan användas när credentials finns tillgängliga.

Systemet blir en naturlig del av användarens arbete.

## Infrastruktur

Denna iteration omfattar:

* kontinuerlig drift,
* tjänstestart och avstängning,
* adminautentisering vid start,
* krypterad lokal secrets-lagring,
* bakgrundsbevakning av Ingest Source,
* backup,
* återställning,
* administrativa driftverktyg,
* övervakning och felsökning.

## Adminlösenord och upplåsning

Dokumentverkstad ska inte starta sin webbserver förrän ett korrekt adminlösenord har angetts.

Adminlösenordet ska:

* aldrig lagras i klartext,
* inte skrivas till logg,
* inte sparas i Archive,
* inte versionshanteras.

Lösenordet används för att härleda en krypteringsnyckel som i sin tur används för att dekryptera lokala secrets.

Fel lösenord ska inte starta tjänsten.

Efter lyckad upplåsning hålls nödvändiga secrets endast i minnet under den aktuella körningen.

När processen avslutas ska den dekrypterade informationen inte finnas kvar på disk.

## Krypterad secrets-lagring

API-nycklar och andra hemligheter ska kunna lagras krypterat lokalt.

Exempel:

```text
.dokumentverkstad/
    secrets.enc
```

Secrets-filen:

* ligger utanför Archive,
* versionshanteras aldrig,
* får säkerhetskopieras endast om backupen hanteras som känslig information,
* ska kunna ersättas utan att Archive eller övrig användardata påverkas.

Använd en etablerad och välgranskad kryptografisk lösning.

Bygg inte egen kryptografi.

Lösenordsbaserad key derivation och authenticated encryption ska användas.

## Återställning av credentials

Om adminlösenordet glöms bort ska Dokumentverkstads Archive fortfarande vara intakt.

Det ska vara möjligt att:

* kassera den krypterade secrets-filen,
* återkalla externa API-nycklar,
* skapa nya credentials,
* initiera secrets-lagringen på nytt.

Förlust av adminlösenord ska alltså inte innebära förlust av dokument, Knowledge Objects eller Projects.

## Kontinuerlig drift

När Dokumentverkstad är upplåst ska den kunna köras under längre tid utan manuell hantering.

Iteration 8 ska stödja:

* stabil webbserverdrift,
* automatisk hantering av nödvändiga lokala kataloger,
* bakgrundsbevakning av Ingest Source,
* tydlig felrapportering,
* kontrollerad avstängning.

Automatisk tjänstestart efter omboot utan mänsklig upplåsning ingår inte i denna iteration.

Om detta senare behövs ska OS-baserad secrets-hantering, exempelvis Windows Credential Manager eller macOS Keychain, utvärderas separat.

## Backup och återställning

Iteration 8 ska etablera fungerande rutiner för backup och återställning.

Archive är den auktoritativa datakällan.

Det ska vara möjligt att:

* säkerhetskopiera Archive,
* återställa Archive till en ny installation,
* återuppbygga Runtime och index,
* fortsätta använda systemet efter återställning.

Secrets ska hanteras separat från Archive.

## Implementation

Iteration 8 implementerar eller härdar:

* startkommando för tjänsten,
* adminlösenord vid start,
* krypterad secrets-fil,
* initiering och byte av credentials,
* bakgrundsbevakning av Ingest Source,
* administrativa driftkommandon,
* backup-rutiner,
* återställning av hela systemet,
* robust index rebuild,
* tydlig felsökning och loggning.

Funktioner som redan finns, exempelvis Trash, Restore och index rebuild, ska inte implementeras på nytt utan göras robusta och administrerbara för daglig drift.

## Tester

Iterationen är godkänd när:

* tjänsten inte startar utan korrekt adminlösenord,
* fel adminlösenord inte låser upp secrets,
* secrets aldrig sparas i klartext,
* secrets inte exponeras i loggar eller UI,
* tjänsten kan köras utan dataförlust under längre tid,
* Ingest Source kan bevakas i bakgrunden,
* Archive kan säkerhetskopieras och återställas,
* Runtime och index kan återskapas från återställt Archive,
* förlust av secrets-filen inte påverkar Archive,
* systemet kan återinitiera credentials utan att användardata förändras.

## Klart när

Iteration 8 är klar när följande scenario fungerar:

> Anders startar Dokumentverkstad, anger sitt adminlösenord och tjänsten låses upp. Därefter kan systemet köras under dagen utan att han behöver tänka på drift, index eller secrets. Om datorn går sönder kan Archive återställas på en ny installation, Runtime byggas upp igen och nya credentials konfigureras utan att kunskapsrummet går förlorat.

# Iteration 9 – Konsolidering

## Mål

Iteration 9 syftar inte till att införa ny kärnfunktionalitet.

Målet är istället att konsolidera Dokumentverkstad till ett sammanhängande, snabbt och intuitivt arbetsverktyg.

Efter denna iteration ska hela arbetsflödet upplevas som naturligt även vid daglig användning.

## Fokusområden

Iterationen omfattar framför allt:

* förbättrad informationsarkitektur,
* förbättrad navigering,
* effektivare arbetsflöden,
* förbättrad layout och typografi,
* konsekvent interaktion mellan systemets olika vyer.

## Utgångspunkt

Utgångspunkten är verklig användning.

Förändringar ska i första hand bygga på observationer från UX_NOTES.md och praktisk användning av systemet, inte på spekulativ design.

## Exempel på förbättringar

Exempel på förbättringar som kan ingå:

* förbättrad Inbox,
* effektivare Capture,
* bättre Document-vy,
* bättre Project-vy,
* tangentbordsgenvägar,
* swipe-gester,
* drag-and-drop där det förenklar arbetsflödet,
* förbättrad mobilanpassning,
* förbättrad e-ink-användning,
* tydligare typografi,
* bättre spacing,
* färger och visuell hierarki,
* snabbare navigering mellan relaterade objekt,
* bättre återkoppling efter användarhandlingar.

Listan är inte uttömmande.

Iterationen ska styras av faktisk användning.

## Designprincip

Varje förändring ska minska friktion i ett verkligt arbetsflöde.

Ingen förändring ska införas enbart därför att den ser modern eller estetiskt tilltalande ut.

## Leverans

När Iteration 9 är färdig ska Dokumentverkstad upplevas som ett sammanhängande arbetsverktyg snarare än en samling funktioner.

Systemets användbarhet ska förbättras utan att förändra dess grundläggande domänmodell eller arbetsprocess.

## Klart när

Iteration 9 är klar när följande scenario fungerar:

> Anders arbetar en hel dag i Dokumentverkstad utan att tänka på gränssnittet. Han fokuserar på sina dokument och sitt tänkande, medan systemet känns snabbt, naturligt och konsekvent i varje arbetsmoment.
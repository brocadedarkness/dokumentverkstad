# MVP-specifikation för Dokumentverkstad

## Syfte

Detta dokument definierar den första körbara versionen av Dokumentverkstad.

Målet är inte att implementera hela visionen.

Målet är att skapa den minsta version som gör det möjligt att använda Dokumentverkstad i verkligt arbete och därmed lära sig vilka delar som fungerar, vilka som skaver och vad som behöver utvecklas vidare.

MVP:n ska vara liten, begriplig och möjlig att förändra.

---

# MVP:ns kärna

Den första versionen ska göra det möjligt att:

1. registrera dokument,
2. fånga egna noteringar,
3. köra enkel AI-analys efter uttryckligt godkännande,
4. reviewa AI-genererade kandidater,
5. koppla kunskap till projekt,
6. lista och filtrera dokument och Knowledge Objects,
7. arbeta från dator, iPad och telefon,
8. bevara all beständig data i öppna format.

---

# 1. Documents

MVP:n ska stödja två sätt att registrera Documents.

## Digital registrering

En PDF placeras i en konfigurerad Ingest Source.

Systemet:

* upptäcker PDF-filen,
* kopierar den till lokal runtime,
* beräknar checksumma,
* kontrollerar exakt dublett,
* skapar Document-ID,
* arkiverar originalfilen,
* extraherar text,
* extraherar grundläggande metadata när möjligt,
* gör dokumentet tillgängligt i webbgränssnittet.

Endast PDF med maskinläsbar text behöver stödjas.

OCR ingår inte.

## Manuell registrering

Användaren ska kunna välja:

> Nytt dokument

och registrera ett Document utan digital fil.

Minimikrav:

* titel

Valfria fält:

* författare,
* år,
* dokumenttyp,
* språk,
* upplaga,
* egen kommentar.

En digital originalfil behöver inte kunna kopplas till ett manuellt Document i första MVP:n, men domänmodellen och datalagringen ska inte förhindra att funktionen läggs till senare.

---

# 2. Persistent Archive

Beständig användardata ska lagras utanför runtime.

Archive Root ska vara konfigurerbar.

MVP:n ska lagra minst:

* Documents,
* original-PDF-filer,
* metadata,
* extraherad text,
* Knowledge Objects,
* Projects,
* historik,
* Trash.

Arkivet ska använda öppna och dokumenterade format.

SQLite får inte vara den enda lagringsplatsen för beständig information.

---

# 3. Runtime

Runtime ska vara lokal och återuppbyggbar.

Den får innehålla:

* Inbox,
* jobs,
* cache,
* SQLite-index,
* loggar.

Runtime behöver inte synkroniseras mellan maskiner.

---

# 4. Capture

Capture ska vara en av MVP:ns huvudsakliga arbetsytor.

Den ska vara persistent och stödja kontinuerlig inmatning.

Användaren ska kunna:

1. skriva en notering,
2. spara,
3. omedelbart skriva nästa.

Efter sparande ska:

* textfältet tömmas,
* fokus återgå till textfältet,
* den sparade noteringen synas bland senaste noteringar.

Det ska inte krävas:

* semantisk typ,
* Project,
* Document,
* källa,
* metadata.

## Kontext

Om Capture öppnas från ett Document ska det aktuella Document föreslås som källa.

Om Capture öppnas från ett Project ska Project föreslås som koppling.

Användaren ska kunna ta bort dessa kopplingar.

## Syntax

MVP:n behöver endast stödja vanlig text eller enkel Markdown.

`@`-referenser och `#`-projektreferenser behöver inte implementeras ännu.

---

# 5. Knowledge Objects

Alla manuella noteringar och accepterade AI-förslag ska lagras som Knowledge Objects.

MVP:n behöver stödja:

* innehåll,
* ID,
* skapare,
* skapandetid,
* senaste ändring,
* historik,
* eventuell Document-koppling,
* eventuell Project-koppling,
* review-status,
* eventuell semantisk typ.

Semantisk typ får vara:

* okänd,
* Summary,
* Claim,
* Insight,
* Question.

Användaren behöver inte välja typ vid skapande.

---

# 6. Source Precision

MVP:n ska stödja enkel Source Precision.

En Knowledge Object-källa ska minst kunna anges som:

* inget Document,
* Document,
* Document + sidnummer,
* Document + fritextnotering.

Exempel:

> s. 35

eller:

> kapitel 4, ungefär i mitten

Systemet ska inte kräva normaliserade stycken eller koordinater.

---

# 7. Projects

MVP:n ska kunna:

* skapa Project,
* byta namn,
* visa Project,
* koppla Knowledge Objects till Project,
* koppla ett Knowledge Object till flera Projects.

Project-vyn ska minst visa:

* namn,
* beskrivning,
* kopplade Knowledge Objects,
* relevanta Documents.

General implementeras inte som objekt eller Project.

---

# 8. Relationer

MVP:n ska endast stödja en generell relation:

> hör ihop med

Användaren ska kunna koppla:

* Knowledge Object till Knowledge Object,
* Knowledge Object till Document,
* Knowledge Object till Project.

Ingen avancerad relationssemantik behöver implementeras.

Fritextkommentar till relationen är valfri.

---

# 9. Inbox

Inbox ska vara MVP:ns primära triage-yta.

På telefon är Inbox standardsidan.

Inbox ska minst kunna visa:

* nya Documents som ännu inte reviewats,
* AI-genererade kandidater som väntar på review.

För nya Documents ska användaren kunna:

* öppna dokumentöversikten,
* koppla till ett eller flera Projects,
* lämna utan Project,
* skjuta upp,
* kasta.

För AI-kandidater ska användaren kunna:

* acceptera,
* redigera och acceptera,
* avvisa,
* skjuta upp.

---

# 10. AI-analys

MVP:n använder endast moln-AI.

AI-lagret ska ändå vara provider-abstraherat.

Första implementationen använder en enda provider.

MVP:n ska stödja följande capabilities:

* kort sammanfattning,
* candidate insights,
* candidate claims,
* frågor att ta vidare,
* projektförslag.

Alla AI-genererade Knowledge Objects skapas som kandidater.

---

# 11. Sekretess

Nya Documents ska som standard ha:

> Endast lokal behandling

Moln-AI får inte användas förrän användaren uttryckligen tillåter det.

MVP:n behöver endast två tillstånd:

* lokal behandling tillåten,
* moln-AI tillåten.

---

# 12. Kostnadsgodkännande

Innan ett moln-AI-anrop ska användaren se:

* vilka capabilities som ska köras,
* vald provider,
* vald modell,
* uppskattade input-token,
* uppskattade output-token,
* uppskattat kostnadsintervall.

Användaren ska uttryckligen starta körningen.

Efter körningen ska systemet visa:

* faktisk input-token,
* faktisk output-token,
* faktisk kostnad,
* provider,
* modell,
* tidpunkt.

---

# 13. Review

Review ska bevara AI:s ursprungliga förslag.

Vid redigering ska systemet lagra:

* originalförslag,
* användarens accepterade version,
* tidpunkt,
* proveniens.

Vid avvisning ska användaren frivilligt kunna ange:

* irrelevant,
* trivial,
* felaktig,
* överdriven,
* redan känd,
* annat.

Denna feedback lagras för framtida självobservation.

---

# 14. Självobservation

MVP:n behöver inte generera förbättringsförslag.

Den ska däremot samla den data som senare behövs.

Minst:

* accepterat oförändrat,
* redigerat och accepterat,
* avvisat,
* avvisningsorsak,
* provider,
* modell,
* promptversion,
* confidence,
* kostnad.

---

# 15. Document-vy

Document-vyn ska minst visa:

* titel,
* grundmetadata,
* sekretessstatus,
* Projects,
* kort sammanfattning när sådan finns,
* kopplade Knowledge Objects,
* AI-kandidater,
* länk till originalfil när sådan finns.

Det ska gå att öppna Capture från Document-vyn med Document som aktivt context.

---

# 16. Project-vy

Project-vyn ska minst visa:

* namn,
* beskrivning,
* kopplade Knowledge Objects,
* relevanta Documents.

Det ska gå att öppna Capture med Project som aktivt context.

AI-genererad projektsyntes ingår inte i MVP:n.

---

# 17. Listning och filtrering

MVP:n ska innehålla enkla listvyer för:

## Documents

Filtrering minst efter:

* Project,
* har AI-analys / saknar AI-analys,
* har originalfil / saknar originalfil.

## Knowledge Objects

Filtrering minst efter:

* Project,
* Document,
* skapare,
* review-status,
* semantisk typ.

Full avancerad sökning behöver inte vara färdig.

---

# 18. Search

MVP:n får innehålla enkel fritextsökning.

Den är inte prioriterad framför listning och filtrering.

Sökning behöver endast täcka:

* Document metadata,
* Knowledge Object-innehåll,
* Project-namn.

Semantisk sökning ingår inte.

---

# 19. Trash

Documents, Knowledge Objects och Projects ska kunna kastas.

De flyttas till Trash.

De ska vara återställningsbara i 30 dagar.

Permanent automatisk radering efter 30 dagar får implementeras i MVP:n men är inte kritisk för den första körbara versionen.

---

# 20. Webbgränssnitt

UI:t ska vara serverrenderat.

MVP:n ska använda:

* HTML,
* CSS,
* minimal JavaScript.

Alla centrala flöden ska fungera utan JavaScript.

JavaScript får användas för bekvämlighet, exempelvis för att hålla Capture snabbt.

---

# 21. Responsivitet

MVP:n ska vara användbar på:

* desktop,
* iPad,
* telefon.

E-ink-kompatibilitet ska beaktas i designen, men behöver inte testas uttömmande innan första körbara versionen.

## Telefon

Prioriterar:

* Inbox,
* Capture,
* enkel Document-vy.

## iPad

Ska kunna använda alla centrala MVP-funktioner.

---

# 22. Extern dokumentläsning

MVP:n ska inte innehålla en egen PDF-läsare.

Original-PDF ska kunna öppnas via read-only URL från webbgränssnittet.

---

# 23. Index

MVP:n använder SQLite som lokalt index.

Ett administrativt kommando ska kunna återskapa indexet från arkivet.

Exempel:

```text id="5zav7x"
dokumentverkstad rebuild-index
```

---

# 24. CLI

MVP:n ska minst stödja:

```text id="x398av"
dokumentverkstad run
dokumentverkstad process-inbox
dokumentverkstad rebuild-index
dokumentverkstad status
```

CLI är främst till för drift, test och felsökning.

---

# 25. Konfiguration

MVP:n ska använda en läsbar config-fil.

Minst följande ska vara konfigurerbart:

* Archive Root,
* Runtime Root,
* Ingest Source,
* AI-provider,
* AI-modell,
* språk för AI-output,
* valuta,
* kostnadsgräns.

Hemligheter ska lagras separat.

---

# 26. Ingest

MVP:n behöver endast en fungerande Ingest Source:

* konfigurerad lokal katalog.

Om användarens deployment använder Dropbox ska Dropbox-klienten eller ett separat enkelt synkflöde göra filen tillgänglig där.

Dokumentverkstad behöver inte ha en Dropbox-specifik API-integration i MVP:n.

---

# 27. Felhantering

MVP:n ska prioritera datasäkerhet.

Ett fel i:

* textextraktion,
* AI-anrop,
* indexering,
* review

får inte leda till att originalfil eller tidigare Knowledge Objects förloras.

Misslyckade AI-körningar ska kunna göras om.

---

# 28. Testkrav

MVP:n ska ha automatiska tester för minst:

* Document-registrering,
* dublettkontroll,
* Knowledge Object-skapande,
* versionshistorik,
* Project-koppling,
* Trash och restore,
* index rebuild,
* AI-provider-interface med mock-provider.

Tester ska verifiera beteenden snarare än interna implementationer.

---

# 29. Explicit utanför MVP

Följande ska inte implementeras i MVP:n:

* EPUB
* OCR
* lokal AI
* semantisk sökning
* avancerad relationssemantik
* knowledge graph-visualisering
* chatt med dokument
* AI-genererade General Insights
* AI-genererade projektsynteser
* automatisk AI-router mellan lokal och moln
* automatisk förbättring av prompts
* automatisk source matching
* import av PDF-highlights
* `@`-referenser och `#`-syntax i Capture
* multi-user
* avancerad autentisering
* publik internetdrift
* native iOS/iPadOS-app
* egen PDF-läsare

Dessa funktioner får endast införas senare efter att MVP:n har använts och verkliga behov har observerats.

---

# 30. MVP:n är klar när

MVP:n betraktas som användbar när följande scenario fungerar från början till slut:

1. En PDF placeras i Ingest Source.
2. Dokumentverkstad registrerar och arkiverar den.
3. Användaren öppnar Inbox från iPad eller telefon.
4. Dokumentet kan kopplas till ett Project.
5. Användaren tillåter moln-AI.
6. Dokumentverkstad visar uppskattad kostnad.
7. Användaren startar analysen.
8. AI skapar sammanfattning och kandidater.
9. Den faktiska kostnaden visas.
10. Användaren accepterar, redigerar eller avvisar kandidater.
11. Accepterade Knowledge Objects visas i Document- och Project-vyerna.
12. Användaren kan skriva egna noteringar i Capture.
13. Dessa kan kopplas till Document och Project utan klassificeringstvång.
14. Tjänsten kan stängas av.
15. Den kan startas igen utan att någon beständig information gått förlorad.
16. SQLite-indexet kan raderas och byggas upp på nytt från arkivet.

Om detta fungerar har Dokumentverkstad nått sin första verkligt användbara version.

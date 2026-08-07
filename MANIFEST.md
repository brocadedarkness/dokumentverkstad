# Manifest för Dokumentverkstad

## Inledning

Dokumentverkstad är ett system för kumulativ kunskapsbildning.

Det är inte i första hand ett verktyg för att sammanfatta dokument, och inte heller ett arkiv i traditionell mening. Det är en arbetsmiljö där dokument, analyser, egna anteckningar, frågor, påståenden och insikter kan föras samman, granskas, omprövas och utvecklas över tid.

Dokumentverkstad utgår från att kunskap inte är ett stillastående lager av fakta.

Kunskap är en historia av omprövningar och översättningar.

Ett dokument översätts till påståenden. Påståenden översätts till insikter. Insikter sätts i relation till projekt, tidigare läsning och nya frågor. Varje ny förståelse förändrar hur det tidigare materialet kan läsas.

Dokumentverkstad är därför inte en pipeline från dokument till svar.

Det är en cykel:

> Dokument → bearbetning → insikt → omprövning → ny fråga → nytt dokument

Systemets uppgift är att stödja denna cykel utan att låtsas att den någonsin blir slutgiltig. Systemet ska kunna tillhandahålla snabba sammanfattningar och AI-genererade insikter, som sedan kan omprövas eller utvecklas kontinuerligt.

---

## 1. En verkstad, inte ett orakel

Dokumentverkstad ska vara en plats för arbete.

Den ska inte framstå som allvetande, personlig eller magisk. Den ska inte tala med auktoritet där den bara erbjuder ett förslag. Den ska inte dölja osäkerhet bakom ett säkert tonfall.

Systemet ska därför presentera:

* vad dokumentet säger,
* vad AI föreslår,
* vad användaren själv har formulerat,
* vilka slutsatser som är preliminära,
* vad som fortfarande är öppet.

AI är ett verktyg i verkstaden. Det är inte verkstaden själv.

Dokumentverkstad ska inte fatta epistemiska beslut åt användaren. Den ska hjälpa användaren att fatta dem.

Kunskap utvecklas genom stabilisering, omprövning och översättning. Dokumentverkstad utgår från det konkreta och låter struktur, relationer och abstraktioner växa fram genom kunskapsarbetet.

---

## 2. Kunskap byggs genom granskning

AI-genererade sammanfattningar, påståenden, projektförslag och insikter ska alltid behandlas som kandidater.

De får inte automatiskt bli en del av den etablerade kunskapsbasen.

Varje AI-genererat objekt ska kunna:

* accepteras,
* redigeras,
* avvisas,
* skjutas upp.

När användaren redigerar ett AI-förslag ska både originalförslaget och den redigerade versionen bevaras.

Ett accepterat objekt betyder inte nödvändigtvis att objektet är sant. Det betyder att det är värt att bevara, återvända till eller arbeta vidare med.

Dokumentverkstad ska därmed skilja mellan:

* kandidat,
* accepterad,
* reviderad,
* ifrågasatt,
* ersatt,
* avvisad.

Kunskap ska kunna utvecklas utan att tidigare steg raderas.

---

## 3. Originalet är beständigt

Originaldokumentet är den primära källan.

Det ska bevaras oförändrat och aldrig skrivas över av Dokumentverkstad.

Sammanfattningar, påståenden, analyser, metadata och insikter är derivat. De kan förändras, återskapas eller förbättras. Originalet ska förbli stabilt.

Varje härlett objekt ska så långt möjligt kunna spåras tillbaka till:

* dokument,
* sida,
* textutdrag,
* tidpunkt,
* metod,
* modell,
* promptversion.

Dokumentverkstad ska alltid göra det möjligt att återvända från en tolkning till dess källa.

---

## 4. Proveniens är en del av kunskapen

Det räcker inte att veta vad som står i systemet. Det måste också gå att se varifrån det kommer.

Varje kunskapsobjekt ska därför kunna ange om det härrör från:

* dokumentet,
* AI,
* användaren,
* användaren efter redigering av ett AI-förslag,
* flera källor tillsammans.

Proveniens ska inte gömmas undan som teknisk metadata. Den ska vara synlig där den behövs för förståelsen.

Det ska vara möjligt att skilja mellan:

> Dokumentet hävdar detta.

> AI tolkar dokumentet så här.

> Användaren drar denna slutsats.

De tre utsagorna får inte blandas samman.

---

## 5. Confidence ska vara begripligt

Dokumentverkstad ska visa osäkerhet, men inte reducera all osäkerhet till en enda siffra.

Systemet bör skilja mellan exempelvis:

* hur säkert det är att dokumentet faktiskt säger något,
* hur säker en tolkning är,
* hur starkt stöd dokumentet ger ett påstående,
* hur säker en föreslagen koppling till annat material är.

Ett dokument kan tydligt formulera ett påstående som samtidigt har svagt stöd. Hög säkerhet i extraktionen betyder inte hög evidensstyrka.

Confidence ska därför användas som hjälp för bedömning, inte som ersättning för bedömning.

---

## 6. Dokument genererar kunskapsobjekt

Dokumentverkstad ska inte endast lagra dokument.

Dokument ska kunna ge upphov till olika typer av kunskapsobjekt:

* metadata,
* sammanfattningar,
* claims,
* insights,
* begrepp,
* citat,
* frågor,
* invändningar,
* observationer,
* open threads,
* projektförslag,
* relationer till andra dokument.

Ett claim är ett påstående som dokumentet gör eller stöder.

En insight är en tolkning, syntes eller möjlig slutsats som kan bygga på ett eller flera claims.

En open thread är en fråga, spänning eller möjlig fortsättning som ännu inte är löst.

Dessa objekt ska kunna knytas till varandra utan att behöva dupliceras.

---

## 7. Projekt organiserar arbetet

Dokument, claims, insights, frågor och andra kunskapsobjekt ska kunna knytas till ett eller flera projekt.

Projekt är inte mappar i traditionell mening. De är sammanhang.

Ett dokument kan vara relevant för flera projekt samtidigt. En insight kan uppstå i ett projekt och senare visa sig vara viktig i ett annat.

AI får föreslå möjliga projekt, men användaren avgör.

Samtliga dokument, även de som inte hör hemma i något särskilt projekt, ska även placeras i General.

General är inte en restkategori. Det är en övergripande kunskapsbas för alla dokument som finns i systemet.

Systemet ska på sikt kunna identifiera återkommande teman i General och föreslå möjliga nya projekt, men aldrig skapa dem automatiskt.

Projekt ska kunna:

* skapas,
* pausas,
* arkiveras,
* byta namn,
* slås samman,
* delas upp.

Kunskapsobjekten ska bestå även när projekten förändras.

---

## 8. General ska vara en källa till nya riktningar

General ska sammanföra insikter som går över projektgränser.

Den ska kunna synliggöra:

* återkommande teman,
* starkt understödda claims,
* motsägelser,
* insikter som förekommer i flera projekt,
* frågor med bred relevans,
* möjliga framtida projekt.

General ska inte försöka reducera allt till en enda sammanhängande världsbild.

Den ska bevara skillnader, spänningar och alternativa tolkningar.

---

## 9. Historik är inte skräp

Dokumentverkstad ska bevara utvecklingen av en tanke.

När en insight förändras ska tidigare versioner finnas kvar.

Historiken ska visa:

* vad som ändrades,
* när det ändrades,
* vem eller vad som initierade ändringen,
* vilka källor som låg bakom,
* varför den nya versionen accepterades.

Systemet ska inte dölja att tidigare förståelser varit otillräckliga.

Omprövningen är inte ett misslyckande som ska raderas. Den är en del av kunskapen.

---

## 10. Användarens egna anteckningar är centrala

Dokumentverkstad får inte bli en maskin för AI läsning av användarens dokument.

Användaren ska enkelt kunna lägga till:

* observationer,
* insights,
* frågor,
* invändningar,
* citat,
* att-göra-punkter,
* kopplingar till andra dokument eller projekt.

Dessa objekt ska ha samma status som andra kunskapsobjekt och tydlig proveniens.

Systemet ska på sikt kunna ta emot anteckningar, markeringar och kommentarer från externa PDF-läsare och andra verktyg.

Den mänskliga läsningen är inte ett tillägg till systemet. Den är dess centrum.

---

## 11. Tre nivåer av bearbetning

Dokumentverkstad ska alltid försöka använda den enklaste metod som är tillräckligt bra.

### Nivå 1: vanlig kod

Vanlig programvara ska användas för sådant som inte kräver AI:

* checksummor,
* filhantering,
* metadata,
* indexering,
* textextraktion,
* språkidentifiering,
* sökning,
* relationshantering,
* versionshistorik.

### Nivå 2: lokal AI

Lokala modeller ska på sikt kunna användas för återkommande och relativt avgränsade uppgifter:

* sammanfattningar,
* claim extraction,
* ämnesord,
* projektförslag,
* begreppsidentifiering,
* första candidate insights.

Den lokala modellen är systemets billiga och uthålliga medarbetare.

### Nivå 3: moln-AI

Molnmodeller ska användas när deras högre kvalitet motiverar kostnaden och den externa behandlingen av materialet:

* komplex syntes,
* jämförelser mellan många dokument,
* svåra tolkningar,
* tvärgående general insights,
* särskilt kvalificerade analyser.

Molnmodellen är en dyr konsult, inte ett standardverktyg för allt.

---

## 12. Systemet ska vara modellagnostiskt

Dokumentverkstad ska känna till förmågor, inte enskilda modeller.

Systemet ska kunna efterfråga exempelvis:

* sammanfattning,
* claim extraction,
* projektförslag,
* begreppsidentifiering,
* komplex syntes.

Konfigurationen avgör vilken leverantör eller modell som utför uppgiften.

AI-lagret ska vara utbytbart.

Det ska vara möjligt att byta mellan:

* lokal modell,
* OpenAI,
* annan molnleverantör,
* framtida open source-lösning.

Dokument, kunskapsobjekt och historik får aldrig vara beroende av en särskild AI-leverantör.

---

## 13. Kostnad ska vara synlig

AI-användning kostar resurser och pengar.

Innan en molnbaserad AI-körning ska Dokumentverkstad visa:

* vilka arbetsmoment som ska utföras,
* vilken modell som används,
* uppskattad tokenmängd,
* uppskattat kostnadsintervall.

Körningen ska kräva uttryckligt godkännande.

Efteråt ska systemet visa:

* faktisk tokenanvändning,
* faktisk kostnad,
* kostnad per arbetsmoment,
* eventuell skillnad mot uppskattningen.

AI-arbete som redan är utfört ska inte automatiskt göras om.

Omkörning ska vara ett medvetet val och skapa en ny version.

---

## 14. Sekretess ska vara konservativ som standard

Dokumentverkstad ska inte skicka dokument till en molntjänst utan ett uttryckligt beslut.

Standardinställningen ska vara:

> Endast lokal behandling.

Lokal behandling får omfatta:

* arkivering,
* checksummor,
* metadata,
* textextraktion,
* indexering,
* lokal sökning.

Molnbaserad AI-analys ska kräva att användaren tillåter den för dokumentet.

Systemet ska kunna skilja mellan exempelvis:

* privat material,
* arbetsmaterial som får skickas till moln-AI,
* arbetsmaterial som endast får behandlas lokalt,
* material som inte ska arkiveras i systemet.

Sekretessbeslut ska vara synliga och möjliga att ändra.

---

## 15. Irreversibla handlingar ska undvikas

Dokumentverkstad ska vara försiktigt när något kan gå förlorat.

Systemet ska därför:

* inte radera dokument permanent direkt,
* inte skriva över original,
* inte ersätta gamla insights tyst,
* inte ändra regler automatiskt,
* inte flytta objekt mellan projekt utan godkännande,
* inte skicka material till molnet utan uttryckligt beslut.

Dokument som kastas ska först flyttas till en återställningsbar papperskorg.

De kan raderas permanent efter 30 dagar.

Systemet ska göra det tydligt när en handling är reversibel och när den inte är det.

---

## 16. Systemet får observera sig självt

Dokumentverkstad får registrera hur dess egna förslag används.

Det kan exempelvis följa:

* vilka candidate insights som accepteras,
* vilka som redigeras,
* vilka som avvisas,
* varför de avvisas,
* vilka projektförslag som används,
* hur ofta sammanfattningar kortas eller förlängs,
* hur olika modeller presterar,
* kostnad i relation till kvalitet.

Syftet är inte att analysera användaren som person.

Syftet är att förbättra systemets egna förslag och arbetsflöden.

Dokumentverkstad får föreslå ändringar av exempelvis:

* confidence-trösklar,
* sammanfattningslängd,
* modellval,
* promptversioner.

Systemet får inte genomföra sådana ändringar automatiskt.

Användaren godkänner alltid när en observation ska omvandlas till en ny regel.

---

## 17. Öppna format och fri rörlighet

Dokumentverkstad äger aldrig användarens dokument eller kunskap.

Allt ska kunna exporteras i öppna, begripliga format.

Det gäller:

* originaldokument,
* metadata,
* claims,
* insights,
* frågor,
* open threads,
* projekt,
* relationer,
* historik,
* egna anteckningar.

Systemet bör stödja format som:

* Markdown,
* JSON,
* CSV,
* öppna bibliografiska format.

Ett projekt ska kunna exporteras som en vanlig mappstruktur som fortfarande är begriplig utan Dokumentverkstad.

Den lokala databasen ska vara ett återuppbyggbart index, inte den enda plats där kunskapen finns.

Arkivet ska kunna flyttas till en ny maskin och fortsätta fungera.

---

## 18. Gränssnittet ska presentera arbetet, inte produkten

Webbgränssnittet behöver inte presentera Dokumentverkstad som varumärke.

Användaren vet redan vilket system som är öppet.

Gränssnittet ska därför börja i arbetet:

* Inkorg,
* Projekt,
* Insights,
* Open Threads,
* Sök.

Det ska inte finnas någon onödig dashboard, välkomsttext eller självpresentation.

Systemet ska vara tyst, tydligt och återhållsamt.

Det ska visa vad som kräver ett beslut och sedan träda tillbaka.

---

## 19. Gränssnittet ska vara enkelt och beständigt

Dokumentverkstads webbgränssnitt ska byggas med enkel, robust och långlivad webbteknik.

Alla centrala funktioner ska fungera med serverrenderad HTML och CSS.

JavaScript får användas för frivilliga bekvämlighetsfunktioner, men systemet får inte vara beroende av en tung klientapplikation.

Gränssnittet ska följa principen om progressiv förbättring.

Det ska vara användbart på:

* dator,
* iPad,
* telefon,
* moderna e-ink-enheter.

Det ska därför undvika:

* animationer,
* hover-beroenden,
* drag-and-drop som enda metod,
* låg kontrast,
* färg som enda informationsbärare,
* oändlig scroll,
* onödiga realtidsuppdateringar.

Gränssnittet är en arbetsyta, inte en demonstration av frontendteknik.

---

## 20. Telefonen är till för triage

Telefonvyn ska i första hand stödja den första granskningen.

På telefonen ska det vara enkelt att:

* bevaka inkorgen,
* läsa en kort sammanfattning,
* se candidate insights,
* acceptera, redigera eller avvisa enkla förslag,
* lägga ett dokument i ett eller flera projekt,
* lägga det i General,
* kasta det till papperskorgen,
* skriva en kort egen anteckning,
* öppna originaldokumentet.

Mer avancerad redigering och relationsbyggande kan i första hand vara anpassad för iPad och dator.

---

## 21. Inkorgen är en granskningskö

När ett dokument har tagits emot och bearbetats ska det hamna i en inkorg för review.

Där ska användaren kunna fatta några få tydliga beslut:

* ska dokumentet sparas,
* vilka projekt hör det till,
* ska det ligga i General,
* vilka candidate insights är värda att bevara,
* vilka claims är viktiga,
* finns det en egen anteckning eller fråga att lägga till.

En normal review ska kunna genomföras snabbt.

Systemet ska inte tvinga användaren att förstå eller hantera all intern data som skapats.

Inkorgen är en beslutsyta, inte en rapport om systemets egen aktivitet.

---

## 22. Dokumentverkstad ska förbli begripligt

Systemet ska kunna förklaras utan hänvisning till magi, agenter eller abstrakt intelligens.

Det ska gå att beskriva vad som händer:

* ett dokument tas emot,
* originalet bevaras,
* text extraheras,
* kandidater skapas,
* användaren granskar,
* kunskapsobjekt accepteras,
* relationer byggs,
* historiken bevaras.

Den tekniska komplexiteten får inte göra den epistemiska processen ogenomskinlig.

Användaren ska kunna förstå:

* vad systemet gjort,
* varför det gjort det,
* vad det kostat,
* vilken modell som använts,
* vad som fortfarande är osäkert,
* hur ett beslut kan återställas.

---

## Avslutning

Dokumentverkstad ska inte göra tänkandet automatiskt.

Den ska göra det möjligt att tänka kumulativt.

Den ska hjälpa användaren att återvända till tidigare material, se hur förståelsen har förändrats, upptäcka nya relationer och bevara frågor som ännu inte fått svar.

Dess mål är inte att producera den slutgiltiga sammanfattningen.

Dess mål är att hålla kunskapen i rörelse utan att förlora dess historia.

Dokumentverkstad är en plats där dokument blir till material för vidare arbete.

En plats där AI kan föreslå, men inte avgöra.

En plats där insikter kan accepteras utan att förstenas.

En plats där varje omprövning blir ännu en översättning.

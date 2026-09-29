# Dokumentverkstad – Roadmap

## Syfte

Denna roadmap beskriver utvecklingen av Dokumentverkstad efter den verifierade
MVP-releasen v0.1.0 och mot v1.0.

Roadmapen beskriver produktens mål och prioriterade utvecklingsområden.
Den avslutade `IMPLEMENTATION_PLAN.md` dokumenterar arbetet fram till MVP:n
och betraktas därefter som historisk.

Roadmapen är inte en fullständig backlog. Enskilda förbättringar och tekniska
skulder kan finnas i `BACKLOG.md` och `UX_NOTES.md` utan att ingå i en
planerad release.

## Utgångspunkt: v0.1.0

v0.1.0 är Dokumentverkstads verifierade MVP.

MVP:n etablerar bland annat:

- ett beständigt Archive med Runtime som återskapningsbart lager,
- ingest och lagring av PDF-dokument,
- automatisk textextraktion,
- dokument, projekt, noteringar och Knowledge Objects,
- AI-analys i separat worker,
- review av AI-genererade Knowledge Objects,
- webbåtkomst från flera klienter,
- drift på VPS bakom HTTPS och autentisering,
- verifierad off-server-backup och restore.

MVP:n visar att den grundläggande produktidén och arkitekturen fungerar.
Vägen mot v1.0 handlar därför inte om att ersätta MVP:n, utan om att göra
Dokumentverkstad till ett långsiktigt och naturligt vardagsverktyg.

## Målbild för v1.0

Dokumentverkstad v1.0 är ett beständigt personligt dokument- och
kunskapslager.

Dokument ska kunna föras in friktionsfritt från de enheter som används,
bevaras oberoende av läsverktyg och externa tjänster, analyseras för snabb
orientering och tillsammans med egna anteckningar bilda en strukturerad
kunskapsmängd som också kan användas av externa AI-system.

Dokumentverkstad är inte i första hand en dokumentläsare. Den är den
beständiga infrastrukturen runt dokumenten och arbetet med dem.

### 1. Friktionsfri ingest

Det ska vara snabbt och naturligt att föra in material från de enheter som
används i vardagen, exempelvis dator, iPad och telefon.

Att spara något i Dokumentverkstad ska kunna vara en del av det normala
arbetsflödet och inte kräva att användaren först administrerar ett särskilt
ingestflöde.

Målbilden föreskriver inte en viss teknisk lösning för detta.

### 2. Beständigt dokumentarkiv och interoperabilitet

Dokumentverkstad ska vara den beständiga plats där dokumenten finns samlade.

Det ingestade originalet bevaras oförändrat. Dokumenten ska samtidigt enkelt
kunna öppnas och användas i andra program och tjänster.

Dokumentverkstad ska inte förutsätta att läsning eller annan bearbetning sker
i Dokumentverkstads eget gränssnitt.

Hantering av alternativa representationer, reviderade utgåvor och
återimporterade externt modifierade filer är en separat designfråga och är
inte ett krav för v1.0.

### 3. Lässtöd och anteckningar

Dokument ska enkelt kunna öppnas i en lämplig extern läsmiljö samtidigt som
Dokumentverkstad erbjuder ett snabbt och nära tillgängligt gränssnitt för
dokumentkopplade anteckningar.

Ett typiskt arbetsflöde kan vara att läsa ett dokument i ett separat fönster
eller en separat app och växla mellan läsningen och Dokumentverkstad.

Anteckningar ska kunna göras utan nätanslutning och senare synkroniseras.
Detta är ett produktkrav; roadmapen föreskriver ännu inte om lösningen ska
vara exempelvis PWA, native-klient eller något annat.

### 4. AI-orientering

AI-analyser ska ge snabb orientering i enskilda dokument.

Summary, Claim, Insight och Question utgör den nuvarande grunden för detta.
AI-resultat ska vara tydligt skilda från mänskliga anteckningar. AI-förslag
lagras beständigt med proveniens, men blir accepterad kunskap först efter
mänsklig granskning.

Dokumentverkstad ska inte vara beroende av en viss AI-modell eller leverantör
för sin grundläggande datamodell.

### 5. Kunskapslager och återfinning

Dokument, egna anteckningar och granskade Knowledge Objects ska tillsammans
bilda en användbar och växande kunskapsmängd.

Innehållet ska kunna organiseras och avgränsas, bland annat genom projekt,
och återfinnas även när arkivet omfattar tusentals dokument och många tusen
Knowledge Objects.

Roadmapen förutsätter inte att detta kräver embeddings, semantisk sökning
eller någon annan viss sökteknik.

### 6. Extern maskin- och AI-åtkomst

Valda delar av kunskapslagret ska kunna göras tillgängliga för externa
system, inklusive AI.

Dokumentverkstad behöver därför inte själv utvecklas till en generell
"chat with your documents"-produkt. Dess roll kan i stället vara att
tillhandahålla den beständiga och strukturerade kunskap som externa verktyg
arbetar med.

v1.0 bör stödja kontrollerad read-only-åtkomst till levande, avgränsade
kunskapsmängder. Exakt protokoll och integrationsmodell bestäms senare.

Det ska vara möjligt att uttryckligen styra vad som ingår i ett sådant urval,
exempelvis projekt, dokumentmetadata, egna Notes och accepterade Knowledge
Objects. Ogranskade AI-förslag, originalfiler och intern historik ska inte
exponeras implicit.

## Tvärgående krav för v1.0

v1.0 innebär inte bara att ovanstående funktioner existerar. Dokumentverkstad
ska vara tillräckligt robust för att kunna användas som ett långsiktigt
personligt arkiv och vardagsverktyg.

Det innebär bland annat:

- Archive förblir source of truth och Runtime ska kunna återskapas.
- Beständiga data ska använda begripliga och portabla format.
- Skrivningar till Archive ska vara robusta mot avbrott och samtidighet.
- Backup och restore ska vara tillförlitliga och verifierbara.
- Normal drift ska inte kräva regelbunden SSH-administration.
- Arkivet ska kunna flyttas och återställas utan beroende av en viss VPS,
  klient eller extern tjänst.
- Byte av AI-leverantör ska inte kräva byte av kunskapsmodell.
- Sökning och återfinning ska förbli korrekt och praktiskt användbar när
  arkivet växer.
- Säkerhetsmodellen ska vara rimlig för den ökade maskin- och klientåtkomst
  som införs på vägen mot v1.0.

## Principer för vägen mot v1.0

Utvecklingen efter MVP:n ska ske i mindre, verifierbara releaser.

Versionsnummer mellan v0.1.0 och v1.0 representerar sammanhängande
produktförbättringar, inte förutbestämda faser. Det finns därför inget krav
på att vägen måste bestå av v0.2, v0.3 ... v0.9 eller att releaserna ska vara
lika stora.

Varje release ska:

- ha ett begränsat och begripligt mål,
- föra produkten konkret närmare v1.0,
- ha verifierbara acceptanskriterier,
- inte i onödan låsa senare arkitekturval,
- lämna Archive i ett dokumenterat och migrerbart tillstånd.

Detaljerad implementation planeras när en release väljs, inte i denna
övergripande roadmap.

## Utvecklingsområden mot v1.0

Gap-analysen efter v0.1.0 visar inte något behov av att ersätta den
grundläggande Archive/Runtime-arkitekturen. Vägen mot v1.0 handlar i stället
om att utveckla ett antal förmågor ovanpå denna grund.

Områdena nedan är inte framtida releaser och står inte i en strikt
implementationsordning. Det finns däremot beroenden mellan dem. Framför allt
behöver beständiga skrivningar och identitet vara tillräckligt robusta innan
flera klienter tillåts synkronisera ändringar mot samma Archive.

### Dataintegritet och skrivmodell

v0.1.0 har ett beständigt och portabelt Archive, men vanliga
Archive-skrivningar saknar ännu de garantier som behövs när systemet får fler
skrivvägar och mer självständig klientåtkomst.

Utvecklingen mot v1.0 behöver därför omfatta:

- atomiska skrivningar av beständiga Archive-data,
- skydd mot förlorade uppdateringar vid samtidiga read-modify-write-flöden,
- en tydlig modell för revisioner eller motsvarande ändringsidentitet,
- idempotenta skrivoperationer där samma operation kan behöva skickas igen,
- en definierad modell för konflikter när två klienter ändrar samma objekt,
- en modell för radering som fungerar även vid framtida synkronisering.

Detta innebär inte att Dokumentverkstad behöver bli ett generellt
distribuerat databassystem. Synkmodellen ska utformas för det faktiska
användningsfallet: ett personligt arkiv med ett begränsat antal klienter.

Det första steget är att göra dagens serverbaserade skrivningar robustare.
En fullständig konflikt- och synkmodell behövs först när klienter ska kunna
göra självständiga ändringar offline.

### Återfinning och skalning

v0.1.0 har indexering, sökning, projekt och filtrering, men dagens lösningar
är inte tillräckliga som slutlig modell för ett betydligt större
kunskapslager.

Särskilt behöver den nuvarande hanteringen där Knowledge Objects i vissa
flöden begränsas innan filtrering ersättas. Ett större arkiv får inte ge
ofullständiga resultat därför att äldre relevanta objekt faller utanför en
intern resultatgräns.

Mot v1.0 behöver Dokumentverkstad kunna:

- återfinna innehåll utan hårda bortfall när mängden Knowledge Objects växer,
- utöka dagens sökning i dokumentmetadata med sökning i egna Notes och
  Knowledge Objects; sökning i extraherad dokumenttext är en separat
  utvidgning och ingår inte i v0.2.0,
- kombinera fritextsökning med avgränsning efter exempelvis projekt,
  dokument och objekttyp,
- hantera minst storleksordningen tusentals dokument och tiotusentals
  Knowledge Objects utan att korrekthet eller praktisk användbarhet går
  förlorad.

Semantisk sökning, embeddings eller andra mer avancerade söktekniker kan
senare utvärderas utifrån verkliga behov. De är inte i sig krav för v1.0.
Korrekt och begriplig återfinning prioriteras före mer avancerad ranking.

### Ingest och interoperabilitet

v0.1.0 kan ta emot dokument via webbuppladdning och har en separat
ingestkälla, men ingest är ännu inte en tillräckligt naturlig del av
användarens arbetsflöde från alla relevanta enheter.

Mot v1.0 behöver det bli enkelt att föra dokument till Dokumentverkstad från
dator, iPad och telefon utan att först administrera systemet.

Den befintliga ingestmekanismen kan fungera som integrationspunkt, men
produktkravet är oberoende av om den framtida transporten sker via
filsynkronisering, delningsfunktion, webb, klientintegration eller någon
annan mekanism.

Interoperabilitet gäller också i motsatt riktning. Ett dokument som bevaras
i Dokumentverkstad ska enkelt kunna öppnas i en extern läsare eller annat
verktyg. Dokumentverkstad behöver inte själv återimplementera
formatspecifika läsmiljöer.

Det ingestade originalet förblir oförändrat. Eventuell framtida hantering av
alternativa representationer, reviderade utgåvor eller återimporterade
modifierade filer behandlas som en separat designfråga.

### Offline och flera klienter

Det primära offlinebehovet för v1.0 är avgränsat: användaren ska kunna arbeta
med dokumentkopplade egna Notes när nätanslutning saknas och senare
synkronisera ändringarna.

Målet är inte att göra hela Dokumentverkstad, dess Runtime eller
AI-funktioner tillgängliga offline.

Ett framtida offlineflöde behöver bland annat kunna:

- göra relevanta dokument eller länkar till lokalt tillgängliga dokument
  användbara under läsningen,
- visa befintliga dokumentkopplade Notes,
- skapa och redigera Notes utan serverkontakt,
- köa ändringar lokalt,
- synkronisera dem när anslutningen återkommer,
- upptäcka och hantera verkliga skrivkonflikter utan tyst dataförlust.

Dagens UUID-baserade identiteter ger en användbar grund, men offline-synk
förutsätter att skrivmodellen först kompletteras med tillräcklig
revisions-, konflikt- och raderingssemantik.

Valet mellan exempelvis webb/PWA och en separat klient är ett senare
implementationsbeslut och ska grundas i vilket alternativ som bäst stödjer
detta begränsade arbetsflöde.

### Kunskapsurval och extern åtkomst

v0.1.0 har strukturerade Documents, Notes, Projects och Knowledge Objects,
men saknar ett stabilt externt kontrakt för att exponera en avgränsad
kunskapsmängd.

Innan ett protokoll eller en AI-integration väljs behöver Dokumentverkstad
definiera vad ett kunskapsurval är.

Ett urval ska kunna uttrycka exempelvis:

- ett eller flera projekt,
- dokument och relevant dokumentmetadata,
- egna Notes,
- accepterade Knowledge Objects,
- vid uttryckligt behov extraherad dokumenttext.

Ogranskade AI-förslag, intern körhistorik, secrets och originalfiler ska inte
ingå implicit.

Ett första steg kan vara ett deterministiskt read-only-urval eller en export.
För v1.0 är målbilden att externa system även ska kunna få kontrollerad
read-only-åtkomst till levande, avgränsade kunskapsmängder.

Protokoll och transport — exempelvis ett vanligt API, MCP eller framtida
alternativ — ska väljas efter att innehållskontrakt, säkerhetsgränser och
användningsfall är definierade.

### Drift och hardening

Driftsäkerhet är inte ett separat produktspår utan ett tvärgående arbete
under hela vägen mot v1.0.

v0.1.0 har verifierad deployment, backup, readback och restore, men vissa
driftmoment kräver fortfarande manuell uppföljning.

På vägen mot v1.0 bör bland annat följande successivt hanteras:

- automatisk gallring av äldre backupgenerationer med skydd för den senaste
  verifierade generationen,
- tydligare upptäckt av misslyckade eller uteblivna backupkörningar,
- uppföljning och vid behov optimering av backupens minnesanvändning,
- minskad mängd återkommande SSH-administration,
- dokumenterade och reproducerbara uppgraderings- och migreringsvägar,
- fortsatt verifiering av restore när datamodellen utvecklas.

Hardening ska prioriteras utifrån faktisk risk. En observation eller teknisk
skuld behöver inte blockera en release om systemets dataintegritet och
acceptanskriterier fortfarande är uppfyllda.

## Beroenden mellan utvecklingsområden

Några beroenden är särskilt viktiga för planeringen:

1. **Dataintegritet före offline-synk.**
   Atomiska skrivningar och en tillräcklig revisionsmodell behöver finnas
   innan flera klienter får synkronisera självständiga ändringar.

2. **Korrekt återfinning före avancerad sökning.**
   Hårda resultatbortfall och ofullständig filtrering ska lösas innan
   semantisk sökning eller mer avancerad ranking prioriteras.

3. **Kunskapskontrakt före AI-protokoll.**
   Dokumentverkstad ska först definiera vad ett externt kunskapsurval
   innehåller och vilka säkerhetsgränser som gäller. Först därefter väljs
   API-, MCP- eller annan integrationsmodell.

4. **Arbetsflöde före klientteknik.**
   Mobil ingest och offlineanteckningar ska beskrivas utifrån vad användaren
   behöver göra. PWA, native-app, filsynkronisering eller andra tekniker är
   implementationer, inte mål.

5. **Portabilitet genom hela utvecklingen.**
   Nya funktioner får inte göra Runtime till source of truth eller göra
   Archive beroende av en viss klient, VPS, AI-leverantör eller extern
   tjänst.

## v0.2.0 – Robust kunskapsgrund

### Mål

v0.2.0 stärker den befintliga MVP:n som grund för fortsatt utveckling mot
v1.0.

Releasen fokuserar på två egenskaper som flera senare förmågor är beroende
av:

1. beständiga Archive-skrivningar ska vara robusta mot avbrott och skydda
   mot oavsiktlig förlust av samtidiga uppdateringar,
2. återfinning ska vara korrekt och omfatta den växande kunskapsmängden,
   inte bara dokumenten.

Releasen ska dessutom åtgärda ett mindre antal avgränsade drift- och
UX-problem som identifierades under verklig användning av v0.1.0.

v0.2.0 inför inte offline-synk, nya dokumentformat eller extern AI-åtkomst.
Den gör den befintliga grunden bättre rustad för sådana senare steg.

### 1. Robustare Archive-skrivningar

Sparning av enskilda Archive-poster ska publicera en komplett fil. Ett
processavbrott får inte lämna en befintlig målfil partiellt ersatt.
Garantin omfattar inte transaktioner över flera filer. Tillfälliga
skrivfiler ska inte behandlas som arkivdata eller ingå i backup. Mekanismens
garantier och begränsningar vid maskin- eller strömavbrott ska dokumenteras
separat från garantin vid processavbrott.

Identifierade läs–ändra–skriv-operationer från web, worker och stödda
CLI-flöden ska serialiseras lokalt på servern så att samtidiga operationer inte skriver
tillbaka inaktuella objekt och tappar oberoende ändringar. Hela operationen,
inte enbart filskrivningen, ska omfattas.

Skydd mot inaktuella redigeringsformulär ingår också. Om samma objekt har
ändrats sedan formuläret laddades ska en konflikt upptäckas och tyst
överskrivning förhindras. Konflikten ska visas tydligt och den inskickade
redigeringen så långt rimligt bevaras för fortsatt arbete. Eventuella
begränsningar ska beskrivas. Automatisk merge ingår inte.

v0.2.0 ska införa den minsta samtidighetsmekanism som behövs för dagens
serverbaserade modell. Dess gränser inför framtida offline-synk ska
dokumenteras, men inget distribuerat synkroniseringsprotokoll ska införas.

Releasen behöver däremot inte definiera den fullständiga framtida modellen
för:

- offline-konflikter,
- synkronisering mellan självständiga klienter,
- tombstones eller distribuerad raderingssemantik,
- generell versionshistorik för Documents eller andra objekt.

### 2. Korrekt återfinning i kunskapslagret

Den nuvarande begränsningen där Knowledge Objects i vissa flöden begränsas
innan filtrering ska tas bort eller ersättas med en lösning som inte ger
ofullständiga resultat när arkivet växer.

v0.2.0 ska utvidga dagens sökning i dokumentmetadata med fritextsökning i
aktuellt innehåll i egna noteringar och accepterade Knowledge Objects.
Historik, ogranskade AI-förslag och dokumenttext ingår inte i denna sökning.

Resultat ska kunna filtreras på Knowledge Objectets egna projektkopplingar
och dokumenterade befintliga typkategorier. Dokumentets projektkopplingar
ärvs inte av sökfiltret. Egna noteringar är redan Knowledge Objects i
datamodellen; sökningen inför ingen ny objekttyp. Fritextmatchning och
sorteringsordning ska vara definierade och testbara.

Målet är korrekt och begriplig återfinning. v0.2.0 behöver inte införa:

- embeddings,
- vektordatabas,
- semantisk sökning,
- AI-genererad ranking,
- generell frågesvarsfunktion över arkivet.

Deterministiska tester ska verifiera fullständiga urval med fler än 10 000
Knowledge Objects, inklusive äldre relevanta objekt. Prestanda ska mätas
på en dokumenterad representativ datamängd. Ingen hård söksvarstid sätts
för v0.2.0, och releasen innebär inte en generell prestandagaranti för alla
v1.0-scenarier.

### 3. AI-jobbstatus

Den befintliga bakgrundskörningen av AI ska bli tydligare för användaren.

När ett dokument har ett planerat eller pågående AI-jobb ska detta framgå
tydligt i relevant gränssnitt. Användaren ska inte behöva starta samma
analys igen därför att det är oklart om ett jobb redan pågår.

Status ska vara korrekt vid sidladdning; automatisk liveuppdatering eller
polling eller websocket krävs inte i v0.2.0. Aktiva jobb ska inte döljas av felstatus från
andra körningar.

Backend ska atomiskt säkerställa högst ett `planned`/`running`-jobb per
Document för dagens samlade dokumentanalys. Denna analystyp omfattar
Summary, Claim, Insight, Question och projektförslag i samma körning.
Upprepad start hänvisar till befintligt jobb, även vid samtidiga anrop;
enbart skydd i gränssnittet räcker inte. Ny analys efter avslut eller fel
är tillåten. Befintliga dubletter från v0.1.0 ska hanteras dokumenterat
utan tyst radering.

Detta förändrar inte den grundläggande AI-modellen eller reviewflödet och
kräver ingen ny generell jobbarkitektur.

### 4. Automatisk backupretention

Den manuella gallringen av off-server-backuper i v0.1.0 ska ersättas med en
enkel automatiserad retention: verifierade generationer behålls i minst
30 dygn från `verified_at` i UTC.

Gallringen ska vara fail-safe:

- den senaste verifierade backupgenerationen får inte raderas,
- gallring sker endast efter en ny verifierad backup; en misslyckad backup
  utlöser ingen gallring,
- endast igenkända verifierade generationer som passerat åldersgränsen
  får väljas för gallring; ej verifierade och okända generationer lämnas kvar,
- osäkert underlag, exempelvis listningsfel eller ogiltiga markörer,
  medför utebliven gallring,
- retentionsfel rapporteras separat från backupens verifieringsresultat
  och får inte göra en verifierad backup ogiltig,
- beteendet ska vara testbart utan åtkomst till den verkliga
  off-server-lagringen.

Retention hör till deploymentlagret och ska kunna använda den konfigurerade
externa lagringen utan Dropbox-specifik applikationslogik. Den exakta
retentionstekniken är en implementationsfråga.

### Acceptanskriterier

v0.2.0 kan accepteras när följande är verifierat:

- [ ] Enskilda Archive-poster använder en dokumenterad atomisk skrivmekanism;
      tester med simulerade processavbrott visar att befintlig målfil inte
      lämnas partiellt ersatt.
- [ ] Tillfälliga skrivfiler behandlas inte som arkivdata och ingår inte i
      backup. Garantier vid maskin-/strömavbrott dokumenteras separat;
      transaktioner över flera filer ingår inte.
- [ ] Identifierade läs–ändra–skriv-operationer från web, worker och stödda
      CLI-flöden skyddas som hela operationer mot förlust av oberoende
      samtidiga ändringar genom serverlokal serialisering. Tester täcker
      samtidiga operationer mellan både trådar och processer.
- [ ] Inaktuella redigeringsformulär ger en tydlig konflikt utan tyst
      överskrivning, verifierat med två formulär för samma objekt där det
      ena sparas först. Inskickad redigering bevaras så långt rimligt för
      fortsatt arbete och begränsningar dokumenteras; automatisk merge ingår inte.
- [ ] Den införda samtidighetsmekanismen är dokumenterad med avseende på
      framtida offline-synk och inför inget distribuerat synkroniseringsprotokoll
      i v0.2.0.
- [ ] Knowledge Objects faller inte bort ur filtrerade resultat på grund av
      att en global resultatgräns appliceras före filtrering.
- [ ] Fritextsökning återfinner aktuellt innehåll i egna noteringar och
      accepterade Knowledge Objects. Historik, ogranskade AI-förslag och
      dokumenttext ingår inte.
- [ ] Sökresultat kan avgränsas efter KO:ts egna projektkopplingar och
      dokumenterade befintliga typkategorier. Matchning och sortering är
      definierade och testade, även i kombination med projekt-/typfilter.
      Tester visar att Documentets projektkopplingar inte ärvs av sökfiltret.
- [ ] Deterministiska tester visar korrekt återfinning med fler än 10 000
      Knowledge Objects, inklusive äldre relevanta objekt.
- [ ] Prestanda är mätt på en dokumenterad representativ datamängd, utan
      krav på en hård söksvarstid i v0.2.0.
- [ ] Planerade och pågående AI-jobb visas tydligt och korrekt vid
      sidladdning, även när fel från andra körningar finns. Polling krävs inte.
- [ ] Samtidiga startanrop ger högst ett aktivt `planned`/`running`-jobb per
      Document för dagens samlade analys; upprepad start hänvisar till
      befintligt jobb. Ny analys efter avslut/fel fungerar och befintliga
      dubletter från v0.1.0 hanteras dokumenterat utan tyst radering.
- [ ] Retention behåller verifierade generationer i minst 30 dygn från
      `verified_at` i UTC och skyddar alltid senaste verifierade generationen,
      även om denna är äldre än 30 dygn. Tester täcker åldersgränsen.
- [ ] Tester utan verklig off-server-lagring visar att misslyckad backup
      eller osäkert gallringsunderlag inte utlöser gallring och att okända
      eller ej verifierade generationer lämnas kvar. Gallring sker endast
      efter en ny verifierad backup; retentionsfel rapporteras separat
      utan att ogiltigförklara backupen.
- [ ] Backup och restore fungerar efter förändringarna med samma
      dataintegritetskrav som för v0.1.0.
- [ ] Befintliga Archive-data från v0.1.0 kan användas eller migreras
      dokumenterat utan dataförlust.
- [ ] Hela testsuiten passerar i Linux-målmiljön.
- [ ] De centrala användarflödena från v0.1.0 fungerar fortfarande efter
      uppgradering.

### Utanför v0.2.0

Följande ingår uttryckligen inte i v0.2.0. Listan omfattar både senare
utvecklingsområden och möjliga förbättringar som inte är krav för v1.0:

- offline Notes och synkronisering,
- fullständig revisions- och konfliktmodell för offlineklienter,
- automatisk merge och transaktioner över flera Archive-filer,
- sökning i dokumenttext, historik eller ogranskade AI-förslag,
- automatisk liveuppdatering/polling av AI-status,
- mobil share-funktion eller annan ny ingesttransport,
- EPUB eller andra nya dokumentformat,
- alternativa representationer eller dokumentversioner,
- semantisk sökning och embeddings,
- externt API eller MCP för kunskapslagret,
- generell AI-interaktion med hela arkivet,
- egen PDF- eller EPUB-läsare.

Dessa områden ska inte implementeras som bieffekt av arbetet med v0.2.0.

### Efter v0.2.0

Nästa release bestäms först efter att v0.2.0 har använts och verifierats.

Roadmapen förutsätter därför inte redan nu att nästa version är v0.3.0 eller
vilket utvecklingsområde den i så fall ska omfatta. Erfarenheter från den
faktiska användningen av v0.2.0 vägs tillsammans med målbilden för v1.0 när
nästa release väljs.

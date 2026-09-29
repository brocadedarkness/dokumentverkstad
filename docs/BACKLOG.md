Backloggen samlar idéer, möjliga framtida funktioner och identifierade behov som uttryckligen inte ingår i nuvarande implementation. En post i backloggen är inte ett beslut om att funktionen ska implementeras. När ett behov blivit tillräckligt tydligt flyttas det vid behov till implementationsplanen.

Planerade delar för v0.2.0 markeras uttryckligen nedan och avgränsas i
[ROADMAP.md](ROADMAP.md), som anger den normativa releaseavgränsningen och
acceptanskriterierna. Uttryckliga avgränsningar nedan anger vad som inte
ingår i v0.2.0. Övriga öppna punkter är framtida idéer utan beslutad release
eller utfästelse om implementation. MVP:s implementationsplan är historisk.

---

# MCP

Read-only MCP-server som låter externa AI-klienter läsa Documents, metadata, Captures/Knowledge Objects och söka i kunskapsrummet. Djupare AI-konversationer sker utanför Dokumentverkstad och behöver inte lagras där.

# Fulltextsökning och kunskapssökning

Nuvarande snabbsökning filtrerar bara titel/upphov/år.

**Planerat för v0.2.0:** ta bort resultatbortfall där en global KO-gräns
appliceras före filtrering. Lägg till fritextsökning i aktuellt innehåll i
egna noteringar och accepterade Knowledge Objects, med filter på KO:ts egna
projektkopplingar och befintliga typkategorier. Verifiera korrekthet
deterministiskt med fler än 10 000 KO, inklusive äldre relevanta objekt,
och mät prestanda på en dokumenterad representativ datamängd utan hårt
svarstidskrav.

Sökning i dokumenttext, historik och ogranskade AI-förslag, liksom semantisk
sökning och embeddings, ligger utanför v0.2.0.

# Robustare Archive-skrivningar

**Planerat för v0.2.0:** atomisk publicering av enskilda Archive-poster och
serverlokal serialisering av hela läs–ändra–skriv-operationer från web,
worker och stödda CLI-flöden. Om samma objekt ändrats sedan formuläret
laddades ska en konflikt upptäckas; tyst överskrivning förhindras och
inskickad redigering bevaras så långt rimligt för fortsatt arbete.
Tillfälliga skrivfiler ska inte bli arkivdata eller följa med i backup.

Automatisk merge, generell versionshistorik eller revisions-/synkmodell,
offlinekonflikter och transaktioner över flera filer ingår inte. Se roadmapen för de avgränsade
garantierna vid processavbrott respektive maskin-/strömavbrott.

# Fler dokumentformat
Framför allt EPUB, men också frågan om andra format som DOCX etc. 

# Extern webbtillgång utan Tailscale-klient

Levererat i Iteration 10 och godkänt i 10.5: ett enda privat Archive nås via
vanlig HTTPS med Caddy och HTTP Basic Auth. Verklig driftverifiering finns
i [DEPLOYMENT.md](DEPLOYMENT.md).

# Automatiserad backup

Grundbehovet är levererat och verifierat i Iteration 10.4/10.5: systemd-timer,
befintligt ZIP-format, rclone till Dropbox och verifierad återläsning/restore.
Första automatiska timerkörningen godkändes 2026-09-29. MVP-driften behåller
verifierade generationer i en månad med manuell gallring. Automatisk gallring
är planerad för v0.2.0 enligt den separata posten nedan.

# Tydligare AI-jobbstatus i Document-vyn

Vid verklig fjärranvändning syntes det inte tillräckligt tydligt i
Document-vyn att en AI-analys var `planned` eller `running`. Status finns
redan i implementationen men återkopplingen behöver bli tydligare.

**Planerat för v0.2.0:** korrekt och tydlig status vid sidladdning, åtskild
från review-status, samt en backendgaranti om högst ett aktivt
`planned`/`running`-jobb per Document för dagens samlade dokumentanalys.
Upprepad start hänvisar till befintligt jobb även vid samtidiga anrop;
ny analys efter avslut eller fel är tillåten. Befintliga dubletter hanteras
dokumenterat utan tyst radering.

Automatisk liveuppdatering (polling/websocket) och en ny generell
jobbarkitektur ingår inte i v0.2.0.
Punkten förblir utanför den redan godkända MVP-acceptansen.

# AI max-token override och bättre kostnadsuppskattning

När en analys väntas överskrida gränsen: beräkna uppskattad kostnad och låt användaren uttryckligen godkänna en högre gräns.

# Bibliografisk enrichment

Bättre metadata än vad PDF/filnamn ger; externa källor kan senare användas för att komplettera titel, upphov, år, DOI, ISBN etc.

# Dokumentrelationer/versioner

Utkast → slutrapport, tidigare → senare version osv. Vi beslutade uttryckligen att inte skapa en modell innan verkliga användningsfall blivit tydligare.

# Document status/type

Närliggande ovanstående: utkast, slutversion etc. Även detta avsiktligt uppskjutet.

# Captures som semantiska objekt

Ska egna Captures kunna märkas Claim, Insight, Question? Framför allt såg du tydlig nytta med egna Questions, men vi ville inte belasta Capture-flödet.

# Captures som minnesanteckningar

När man återvänder till ett dokument bör ens tidigare läsning kunna rekonstrueras snabbt: vad reagerade jag på, vad var viktigt, vilka frågor hade jag?

# Projects behöver mogna

Project betyder ibland i praktiken arbetsprojekt och ibland något mer som ämne/klassifikation, om än alltid utifrån relevans för mig, inte någon inneboende dokumentklassifikation. I MVP beslutades att inte tvinga alla Documents in i Projects. Senare behöver vi se vad modellen egentligen vill bli när användningsfallen ackumulerats.

# Later/Snooze

Möjlighet att skjuta undan något ur Inbox och få tillbaka det exempelvis nästa dag. Fortfarande oklart om det hjälper eller bara gör Inbox mindre transparent.

# AI-frågor som lässtöd

AI-genererade Questions skulle kunna användas som vägledning vid snabb manuell läsning, men det måste framgå att dokumentet inte nödvändigtvis besvarar dem.

# Archival integrity / TDR alignment

Utvärdera Dokumentverkstads Archive och backupmodell mot etablerade principer för långsiktigt digitalt bevarande, särskilt BagIt (RFC 8493), CoreTrustSeal och relevanta delar av ISO 16363. Överväg BagIt-kompatibla preservation packages, periodisk fixity checking, dokumenterad preservation policy och verifierbara restore-tester. Målet är inte formell certifiering utan att tekniska designbeslut där det är rimligt ska vara förenliga med etablerad digital preservation practice.

# Runtime lifecycle / cleanup

Definiera livscykel och automatisk städning för härledda och temporära Runtime-data. Runtime ska kunna raderas i sin helhet utan informationsförlust och återskapas från Archive. Processade ingest-kopior och staging-filer ska inte bevaras längre än de behövs för säker bearbetning eller diagnostik. Index och andra cachedata får behållas av prestandaskäl men ska alltid vara reproducerbara.

# OCR för bildbaserade PDF:er

Upptäck Documents där vanlig PDF-textutvinning ger ingen eller otillräcklig text. Använd lokalt OCR-stöd via PyMuPDF/Tesseract för relevanta sidor. Originalfilen ska aldrig förändras. OCR-text ska lagras som härledd processing-data med proveniens, språk och engine/version. OCR ska inte köras när vanlig textutvinning redan ger användbar text.

* OCR pipeline: lokal Tesseract-baserad OCR för bild-PDF och bildsidor, med proveniens och reproducerbar textutvinning.
* Multimodal document analysis: lokal visuell modell för bildbaserade eller visuellt komplexa sidor; används som analyslager, inte som ersättning för arkiverad OCR-text.

# Separera AI-orkestrering från webblagret

Background workern är en separat process men återanvänder AI-orkestrering genom `CaptureApp` i `web.py`. Det innebär att gränsen mellan webblagret och den gemensamma applikationslogiken inte är helt ren: kod som behövs av workern ligger i en modul vars primära ansvar är webbapplikationen.

Detta är inte nödvändigtvis ett funktionellt problem i nuläget och bör inte refaktoreras enbart av arkitektoniska skäl. Vid framtida arbete som berör `CaptureApp`, AI-orkestreringen eller workerarkitekturen bör det dock övervägas om den gemensamma logiken kan flyttas till en neutral applikations- eller servicemodul som både webben och workern använder.

Målet skulle vara att behålla webben och workern som separata klienter av gemensam applikationslogik, snarare än att workern är beroende av webblagret.

# Automatisk backupgallring

**Planerat för v0.2.0:** automatisk retention i deploymentlagret som behåller
verifierade generationer i minst 30 dygn från `verified_at` i UTC och alltid
skyddar den senaste verifierade generationen. Gallring sker endast efter en
ny verifierad backup. Misslyckad backup eller osäkert underlag medför ingen
gallring; okända och ej verifierade generationer lämnas kvar. Retentionsfel
rapporteras separat utan att göra backupen ogiltig. Beteendet ska testas
utan verklig extern lagring och utan Dropbox-specifik applikationslogik.

MVP använder fortfarande manuell gallring. Automatiken är planerad, inte
implementerad, och ändrar inte den avslutade MVP-acceptansen.

# Minnesanvändning vid backupverifiering

Verifierade backupkörningar har nått cirka 4,2–5,6 GB peak memory på en VPS
med 8 GB RAM. Backup fungerar i nuläget, men minnesanvändningen bör följas
upp och vid behov optimeras post-MVP. Detta är teknisk skuld, inte en
MVP-blocker. Se även [UX_NOTES.md](UX_NOTES.md).

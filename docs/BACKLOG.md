Backloggen samlar idéer, möjliga framtida funktioner och identifierade behov som uttryckligen inte ingår i nuvarande implementation. En post i backloggen är inte ett beslut om att funktionen ska implementeras. När ett behov blivit tillräckligt tydligt flyttas det vid behov till implementationsplanen.

---

# MCP – ”Exponera kunskapsrummet”

Read-only MCP-server som låter externa AI-klienter läsa Documents, metadata, Captures/Knowledge Objects och söka i kunskapsrummet. Djupare AI-konversationer sker utanför Dokumentverkstad och behöver inte lagras där.

# Fulltextsökning och kunskapssökning

Nuvarande snabbsökning filtrerar bara titel/upphov/år. Senare: indexering och sökning i dokumenttext, Captures, Claims, Insights och Questions.

# Fler dokumentformat
Framför allt EPUB, men också frågan om andra format som DOCX etc. Du har redan filer i arkivet som inte kunde importeras eftersom de inte är PDF.

# Extern webbtillgång utan Tailscale-klient

Ett enda privat Archive som kan nås från exempelvis jobbdatorn via vanlig HTTPS. Cloudflare Tunnel + Access är ett tänkbart framtida alternativ. Viktig princip: inte flera synkroniserade Dokumentverkstad-arkiv.

# Automatiserad backup

Nattliga backups till konfigurerbar katalog, exempelvis en Dropbox-synkad katalog. Retention först kanske fem senaste; senare eventuellt daily/weekly/monthly-generationer.

# Bakgrundsjobb för AI

AI-anrop ligger fortfarande synkront i HTTP-requesten och kan ta 80+ sekunder. Kör analys som jobb i bakgrunden med status/progress i UI.

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

# Första-körningsflödet kan utvecklas vidare

8.1 löste mycket av konfigurationen, men ett riktigt installations-/onboardingflöde kan senare hantera exempelvis Archive-placering, AI-provider, nätverksåtkomst etc.

# Archival integrity / TDR alignment

Utvärdera Dokumentverkstads Archive och backupmodell mot etablerade principer för långsiktigt digitalt bevarande, särskilt BagIt (RFC 8493), CoreTrustSeal och relevanta delar av ISO 16363. Överväg BagIt-kompatibla preservation packages, periodisk fixity checking, dokumenterad preservation policy och verifierbara restore-tester. Målet är inte formell certifiering utan att tekniska designbeslut där det är rimligt ska vara förenliga med etablerad digital preservation practice.
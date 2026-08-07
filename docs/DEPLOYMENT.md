# Deployment för Dokumentverkstad

## Syfte

Detta dokument beskriver den aktuella produktionsmiljön för Dokumentverkstad.

Till skillnad från arkitekturen är deployment-specifikationen avsedd att kunna förändras över tid när hårdvara, operativsystem eller externa tjänster byts ut.

---

# Mål

Den första produktionsmiljön ska:

* kunna köras kontinuerligt i hemmet,
* vara enkel att administrera,
* ge privat fjärråtkomst,
* minimera driftskostnader,
* kunna återställas på en ny maskin.

---

# Utvecklingsmiljö

Syfte: utveckling och test.

Miljö:

* Windows
* VS Code
* Python
* Lokal runtime
* Lokal Archive Root (kan senare flyttas till Dropbox)
* OpenAI API
* Ingen permanent bakgrundstjänst

Den här miljön används tills en dedikerad server finns.

Målet är att utvecklingsmiljön och huvudservern ska använda samma kodbas. Skillnaden mellan miljöerna ska i första hand bestå av konfiguration och driftsätt.

---

# Huvudserver

* Planerad miljö:
* Mac mini
* macOS
* Dokumentverkstad som bakgrundstjänst
* Tailscale
* Dropbox (eller annan synkroniserad lagring)
* iPad och telefon som klienter
* Time Machine

Servern ansvarar för:

* bearbetning av dokument,
* AI-anrop,
* indexering,
* webbgränssnitt,
* arkivhantering.

---

# Klienter

Planerade klienter:

* iPad (primär)
* iPhone
* stationär eller bärbar dator vid behov

Klienterna använder endast webbgränssnittet.

Ingen lokal installation av Dokumentverkstad krävs.

---

# Arkiv

Persistent Archive lagras i en synkroniserad katalog.

Första implementationen använder Dropbox.

Arkivet innehåller:

* Documents
* Knowledge Objects
* Projects
* Trash

Arkivet ska kunna flyttas till annan lagring utan förändringar i systemets kärna.

---

# Runtime

Runtime lagras lokalt på servern.

Den omfattar bland annat:

* inbox
* jobs
* cache
* SQLite-index
* loggar

Runtime betraktas som återuppbyggbar.

---

# Ingest

Första implementationen använder en Dropbox-mapp som Ingest Source.

Dokument som läggs där registreras automatiskt av Dokumentverkstad.

Systemet är dock inte beroende av Dropbox och ska kunna använda andra Ingest Sources i framtiden.

---

# AI

Första implementationen använder OpenAI som AI-provider.

Endast moln-AI används.

Arkitekturen förbereds för lokal AI i framtiden.

---

# Nätverk

Privat fjärråtkomst sker genom Tailscale.

Ingen publik exponering av Dokumentverkstad krävs.

Alla klienter ansluter via Tailscale till den lokala servern.

---

# Säkerhet

API-nycklar lagras lokalt på servern.

De ingår inte i arkivet.

Kommunikation sker över Tailscale eller lokalt nätverk.

---

# Backup

Dropbox används som synkronisering, inte som backup.

Servern bör kompletteras med regelbunden backup, exempelvis Time Machine.

Arkivet är den viktigaste tillgången och ska kunna återställas oberoende av serverns runtime-data.

---

# Framtida utveckling

Deploymentmiljön kan senare förändras, exempelvis genom:

* lokal AI,
* annan synkronisering än Dropbox,
* annan serverplattform,
* NAS,
* fler klienter.

Sådana förändringar ska normalt endast kräva uppdateringar av detta dokument.

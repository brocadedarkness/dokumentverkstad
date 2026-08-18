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

Archive Root ska normalt ligga utanför Git-repositoryt.

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

Aktuell implementation skriver lokal diagnostik till `runtime_root/logs/dokumentverkstad.log` med enkel rotation. Loggen används för warnings, errors, långsamma requests och driftåtgärder som ingest, backup, restore och index rebuild. Den ska inte innehålla API-nycklar, adminlösenord, POST-body, Capture-innehåll eller dokumenttext.

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

Aktuell 8.4a-modell är:

```text
Tailnet client
    ↓
Tailscale Serve
    ↓
localhost Dokumentverkstad
```

Dokumentverkstad ska som standard fortsätta lyssna på `127.0.0.1`, normalt `http://127.0.0.1:8000/`. Tailscale Serve är en rekommenderad extern driftlösning som proxyar tailnet-trafik till den lokala porten. Det är inte en del av Dokumentverkstads domänarkitektur och Dokumentverkstad hanterar inte Tailscale-installation, inloggning, API, credentials eller tailnet policies.

Rekommenderad Serve-konfiguration är att först starta Dokumentverkstad lokalt och sedan köra:

```powershell
tailscale serve 8000
```

Alternativt, explicit:

```powershell
tailscale serve localhost:8000
```

Driftstatus kontrolleras med:

```powershell
tailscale serve status
```

Serve-konfigurationen tas bort med:

```powershell
tailscale serve reset
```

Tailscale Funnel ska inte användas för Dokumentverkstad i denna deployment-modell. Tjänsten ska vara nåbar via ett kontrollerat tailnet, inte publikt på internet.

---

# Säkerhet

API-nycklar lagras lokalt på servern.

De ingår inte i arkivet.

Kommunikation sker över Tailscale eller lokalt via `127.0.0.1`.

I 8.4a finns inget separat webb-login eller sessionsautentisering. Tailnet-åtkomst är åtkomstskyddet för webbgränssnittet. Alla enheter och användare som har nätverksåtkomst till Dokumentverkstad kan använda webbgränssnittet.

Adminlösenordet för krypterade secrets används bara för lokal upplåsning vid processstart och är inte ett webb-login.

Webb-upload av PDF använder säker staging i Runtime, sanerar klientens filnamn, avvisar osäkra sökvägar och kontrollerar PDF-innehåll innan filen registreras i Archive. Standardgränsen för upload är 250 MB (`upload_max_bytes = 262144000`) och kan ändras i config.

---

# Backup

Dropbox används som synkronisering, inte som backup.

Servern bör kompletteras med regelbunden backup, exempelvis Time Machine.

Arkivet är den viktigaste tillgången och ska kunna återställas oberoende av serverns runtime-data.

Dokumentverkstads inbyggda backup är en portabel ZIP-förpackning av Archive och ett litet manifest. Den innehåller inte Runtime, SQLite-index, Ingest Source eller secrets.

Restore ska göras till en ny eller tom installation, eller med ett uttryckligt `--force`-val efter att backupfilen har validerats. Efter restore byggs Runtime/index upp igen från Archive.

Backupen återställer inte absoluta sökvägar, host, port eller andra maskinspecifika driftval från den gamla datorn. Den nya installationens lokala konfiguration avgör var Archive, Runtime och secrets ligger.

---

# Framtida utveckling

Deploymentmiljön kan senare förändras, exempelvis genom:

* lokal AI,
* annan synkronisering än Dropbox,
* annan serverplattform,
* NAS,
* fler klienter.

Sådana förändringar ska normalt endast kräva uppdateringar av detta dokument.

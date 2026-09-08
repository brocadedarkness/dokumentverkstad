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

# Linux/VPS-readiness

Syfte: första förberedelse för drift på en liten Linux-VPS.

Detta är inte en komplett serverdeployment. Ingen VPS, DNS, HTTPS,
reverse proxy, systemd-unit, Docker eller autentisering definieras här.

Rekommenderad separation mellan kod och persistent data:

```text
/opt/dokumentverkstad/
  applikationskod
  virtuell Python-miljö

/var/lib/dokumentverkstad/
  archive/
  runtime/
  ingest/
  secrets.enc        # valfri krypterad secrets-fil
```

Exempel på konfiguration:

```toml
archive_root = "/var/lib/dokumentverkstad/archive"
runtime_root = "/var/lib/dokumentverkstad/runtime"
ingest_source = "/var/lib/dokumentverkstad/ingest"
host = "127.0.0.1"
port = 8000
encrypted_secrets_path = "/var/lib/dokumentverkstad/secrets.enc"
```

Samma värden kan anges med environment variables, vilket är praktiskt när
processer startas av ett externt service-lager:

```sh
export DOKUMENTVERKSTAD_CONFIG=/opt/dokumentverkstad/dokumentverkstad.toml
export DOKUMENTVERKSTAD_ARCHIVE_ROOT=/var/lib/dokumentverkstad/archive
export DOKUMENTVERKSTAD_RUNTIME_ROOT=/var/lib/dokumentverkstad/runtime
export DOKUMENTVERKSTAD_INGEST_SOURCE=/var/lib/dokumentverkstad/ingest
export DOKUMENTVERKSTAD_HOST=127.0.0.1
export DOKUMENTVERKSTAD_PORT=8000
export DOKUMENTVERKSTAD_ENCRYPTED_SECRETS_PATH=/var/lib/dokumentverkstad/secrets.enc
```

För serverdrift bör `OPENAI_API_KEY` i första hand komma från environment om
AI används:

```sh
export OPENAI_API_KEY=...
```

Det gör att API-nyckeln inte behöver ligga i repo eller Archive. Krypterade
secrets kan fortfarande användas när processen startas interaktivt, men en
unattended serverprocess bör inte kräva manuell upplåsning efter varje restart.

Förbered katalogerna:

```sh
sudo mkdir -p /opt/dokumentverkstad /var/lib/dokumentverkstad
sudo chown -R dokumentverkstad:dokumentverkstad /var/lib/dokumentverkstad
```

När koden är installerad och Python-miljön aktiverad kan web och worker köras
som två separata långlivade processer:

```sh
python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml run --no-worker
```

```sh
python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml worker
```

`run --no-worker` startar endast webbservern. `worker` processar ingest och
planerade AI-körningar. Båda processerna använder samma Archive, Runtime och
ingest source via config/environment.

För enkel lokal kontroll:

```sh
python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml status
```

Loggning sker till:

```text
/var/lib/dokumentverkstad/runtime/logs/dokumentverkstad.log
```

Loggen ligger i Runtime och är diagnostisk. Den ska inte användas som
auktoritativ datakälla.

---

# systemd på verifierad Linux-VPS

Syfte: köra Dokumentverkstad som två separata långlivade tjänster på den
verifierade VPS-layouten.

Verifierad layout:

```text
/opt/dokumentverkstad/
  git-repo
  .venv/
  dokumentverkstad.toml

/var/lib/dokumentverkstad/
  archive/
  runtime/
  ingest/
```

Verifierad config:

```toml
archive_root = "/var/lib/dokumentverkstad/archive"
runtime_root = "/var/lib/dokumentverkstad/runtime"
ingest_source = "/var/lib/dokumentverkstad/ingest"
host = "127.0.0.1"
port = 8000
```

Dokumentverkstad ska fortsatt bara lyssna på `127.0.0.1:8000`. Exponera inte
port 8000 direkt mot internet.

## Unit-filer

Unit-filerna finns i repot:

```text
deploy/systemd/dokumentverkstad-web.service
deploy/systemd/dokumentverkstad-worker.service
```

Installera dem på servern:

```sh
sudo cp /opt/dokumentverkstad/deploy/systemd/dokumentverkstad-web.service /etc/systemd/system/
sudo cp /opt/dokumentverkstad/deploy/systemd/dokumentverkstad-worker.service /etc/systemd/system/
```

Webbtjänsten kör:

```text
/opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml run --no-worker
```

Workertjänsten kör:

```text
/opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml worker
```

Båda tjänsterna körs som användaren och gruppen `dokumentverkstad`, använder
`WorkingDirectory=/opt/dokumentverkstad`, restartar vid oväntad krasch och
skriver stdout/stderr till journald.

## Environment och secrets

Secrets ska inte hårdkodas i unit-filer och ska inte checkas in.

Skapa en environment-fil om AI används eller om driftvärden behöver sättas via
environment:

```sh
sudo install -d -o root -g dokumentverkstad -m 750 /etc/dokumentverkstad
sudo cp /opt/dokumentverkstad/deploy/systemd/dokumentverkstad.env.example /etc/dokumentverkstad/dokumentverkstad.env
sudo chown root:dokumentverkstad /etc/dokumentverkstad/dokumentverkstad.env
sudo chmod 640 /etc/dokumentverkstad/dokumentverkstad.env
sudo editor /etc/dokumentverkstad/dokumentverkstad.env
```

Exempel:

```sh
OPENAI_API_KEY=...
```

Filen läses av båda tjänsterna med:

```text
EnvironmentFile=-/etc/dokumentverkstad/dokumentverkstad.env
```

Minustecknet gör filen valfri. Om ingen AI används kan den saknas.

## Rättigheter

Verifiera att systemanvändaren finns:

```sh
id dokumentverkstad
```

Sätt ägare och rättigheter för persistent data:

```sh
sudo chown -R dokumentverkstad:dokumentverkstad /var/lib/dokumentverkstad
sudo find /var/lib/dokumentverkstad -type d -exec chmod 750 {} \;
sudo find /var/lib/dokumentverkstad -type f -exec chmod 640 {} \;
```

Applikationskoden och configen behöver vara läsbar för
`dokumentverkstad`-användaren. Den virtuella miljön behöver vara körbar:

```sh
sudo chown -R root:dokumentverkstad /opt/dokumentverkstad
sudo find /opt/dokumentverkstad -type d -exec chmod 750 {} \;
sudo find /opt/dokumentverkstad -type f -exec chmod 640 {} \;
sudo chmod -R g+rx /opt/dokumentverkstad/.venv/bin
```

Om deploymenten görs genom `git pull` som en annan administrativ användare kan
ägare/rättigheter på `/opt/dokumentverkstad` behöva anpassas till den faktiska
serverrutinen. Ge inte web/worker skrivåtkomst till koden om det inte behövs.

## Starta tjänsterna

Läs om systemd-konfigurationen:

```sh
sudo systemctl daemon-reload
```

Aktivera autostart och starta båda tjänsterna:

```sh
sudo systemctl enable --now dokumentverkstad-web.service
sudo systemctl enable --now dokumentverkstad-worker.service
```

Kontrollera status:

```sh
systemctl status dokumentverkstad-web.service
systemctl status dokumentverkstad-worker.service
```

Kontrollera loggar:

```sh
journalctl -u dokumentverkstad-web.service -n 100 --no-pager
journalctl -u dokumentverkstad-worker.service -n 100 --no-pager
```

Följ loggar live:

```sh
journalctl -u dokumentverkstad-web.service -f
journalctl -u dokumentverkstad-worker.service -f
```

Applikationens runtime-logg finns också kvar:

```text
/var/lib/dokumentverkstad/runtime/logs/dokumentverkstad.log
```

## Verifiering

Verifiera webben lokalt på servern:

```sh
curl -I http://127.0.0.1:8000/
curl http://127.0.0.1:8000/ | head
```

Verifiera appstatus:

```sh
/opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad --config /opt/dokumentverkstad/dokumentverkstad.toml status
```

Verifiera efter reboot:

```sh
sudo reboot
```

Efter att servern är uppe igen:

```sh
systemctl is-active dokumentverkstad-web.service
systemctl is-active dokumentverkstad-worker.service
curl -I http://127.0.0.1:8000/
```

## Restart och stop

Restart:

```sh
sudo systemctl restart dokumentverkstad-web.service
sudo systemctl restart dokumentverkstad-worker.service
```

Stop:

```sh
sudo systemctl stop dokumentverkstad-web.service
sudo systemctl stop dokumentverkstad-worker.service
```

## Enkel deploy efter git pull

Exempel efter att ny kod hämtats till `/opt/dokumentverkstad`:

```sh
cd /opt/dokumentverkstad
git pull
.venv/bin/python -m compileall src/dokumentverkstad
.venv/bin/python -m unittest discover -s tests
sudo cp deploy/systemd/dokumentverkstad-web.service /etc/systemd/system/
sudo cp deploy/systemd/dokumentverkstad-worker.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl restart dokumentverkstad-web.service
sudo systemctl restart dokumentverkstad-worker.service
curl -I http://127.0.0.1:8000/
```

Om Python-beroenden har ändrats:

```sh
cd /opt/dokumentverkstad
.venv/bin/python -m pip install -e .
```

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

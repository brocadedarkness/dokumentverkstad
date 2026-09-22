# Deployment för Dokumentverkstad

## Syfte

Detta dokument beskriver den aktuella produktionsmiljön för Dokumentverkstad.

Till skillnad från arkitekturen är deployment-specifikationen avsedd att kunna förändras över tid när hårdvara, operativsystem eller externa tjänster byts ut.

## Verifierat nuläge inför 10.4

Enligt verklig driftverifiering körs nu det kanoniska Archive på Linux-VPS,
migrerat med Dokumentverkstads backup/restore och återskapat Runtime/index.
`https://verkstad.asdr.se` fungerar med Caddy, publikt TLS-certifikat och
Basic Auth. Webben lyssnar endast på `127.0.0.1:8000`; web och worker kör
som separata systemd-tjänster med autostart aktiverad. Extern mobil klient
har verifierats för läsning, skrivning och AI-jobb som slutförts av workern
mot OpenAI. API-nyckeln finns i skyddad EnvironmentFile, inte i Git.

Restore som root gav root-ägda Archive-filer och PermissionError vid
review/save. Ägarskapet korrigerades manuellt. Rutinen i 10.4 nedan kör
restore som serviceanvändaren och verifierar även skrivning.

10.3-avsnitten nedan är installations- och återinstallationsreferens; de
innebär inte att den redan fungerande installationen ska göras om. Off-server
backup är förberedd i repo men inte aktiverad eller fjärrverifierad genom
detta arbete. Samlad reboot-/tvåklientsacceptans återstår i 10.5.

---

# Mål

Den första produktionsmiljön ska:

* kunna köras kontinuerligt på Linux/VPS,
* vara enkel att administrera,
* ge autentiserad fjärråtkomst via HTTPS,
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

Den här miljön används fortsatt för lokal utveckling parallellt med servern.

Målet är att utvecklingsmiljön och huvudservern ska använda samma kodbas. Skillnaden mellan miljöerna ska i första hand bestå av konfiguration och driftsätt.

---

# Linux/VPS-readiness

Syfte: första förberedelse för drift på en liten Linux-VPS.

Denna grund från 10.1 kompletteras av systemd-avsnittet och Caddy-rutinen
från 10.3 nedan. Extern aktivering är genomförd enligt nuläget ovan.

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
curl -sS -D - -o /dev/null http://127.0.0.1:8000/
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
curl -sS -D - -o /dev/null http://127.0.0.1:8000/
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
curl -sS -D - -o /dev/null http://127.0.0.1:8000/
```

Om Python-beroenden har ändrats:

```sh
cd /opt/dokumentverkstad
.venv/bin/python -m pip install -e .
```

---

# Huvudserver

Aktuell referensmodell är Linux/VPS med systemd och persistent lagring under
`/var/lib/dokumentverkstad`. Installationskommandona för Caddy nedan använder
Debian/Ubuntu med apt. Kontrollera serverns distribution före installation.
En framtida hemmaserver kan använda samma Archive och deploymentprinciper.
Tailscale kan fortsatt användas för privat administration.

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

Ett kanoniskt Archive lagras på serverns persistenta disk. Klienterna använder
samma Archive via webben och ska inte hålla egna synkroniserade arkivkopior.

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

Serverns Ingest Source är en lokal kö på persistent lagring. En synktjänst
kan leverera filer dit men krävs inte för webbuppladdning.

Dokument som läggs där registreras automatiskt av Dokumentverkstad.

Systemet är dock inte beroende av Dropbox och ska kunna använda andra Ingest Sources i framtiden.

---

# AI

Första implementationen använder OpenAI som AI-provider.

Endast moln-AI används.

Arkitekturen förbereds för lokal AI i framtiden.

---

# Nätverk och säkerhet

Målmodellen från 10.3.1 är Caddy + HTTPS + Basic Auth. Ingen extern
aktivering ingår i förberedelsen. Tailscale och fungerande SSH-administration
bevaras. Tailscale Serve kan finnas kvar som privat diagnostikväg under
befintliga tailnet-regler, men är inte MVP:ns primära användarautentisering.
Ingen publik Funnel eller annan väg direkt till appen ska införas.

`	ext
browser -> HTTPS :443 -> Caddy -> Basic Auth -> HTTP 127.0.0.1:8000 -> web
                                                                     |
                                                              Archive/Runtime
                                                                     |
                                                               separat worker
`

Caddy är enda publika webbentrypoint. HTTP :80 används för omdirigering till
HTTPS och certifikatvalidering, aldrig för att använda appen eller skicka
credentials. Workern lyssnar inte på någon nätverksport.

API-nycklar ligger utanför Archive och Git. Iteration 8:s lokala krypterade
secrets använder scrypt och AES-256-GCM; adminlösenordet låser upp secrets
lokalt och är inget webb-login. För unattended systemd används befintlig
OpenAI-environment-fil. Observera att web-start fortfarande frågar efter
upplåsning om en krypterad secrets-fil finns på konfigurerad sökväg, även om
OPENAI_API_KEY finns. Peka därför serverconfig på en oanvänd secrets.enc-sökväg
vid environment-drift; radera inte en befintlig secrets-fil. Caddys
credentials lagras separat enligt nästa avsnitt.

# Backup

Dropbox används som synkronisering, inte som backup.

Servern ska aktivera regelbunden backup till annan lagring än den aktiva
serverdisken enligt 10.4 nedan.

Arkivet är den viktigaste tillgången och ska kunna återställas oberoende av serverns runtime-data.

Dokumentverkstads inbyggda backup är en portabel ZIP-förpackning av Archive och ett litet manifest. Den innehåller inte Runtime, SQLite-index, Ingest Source eller secrets.

Restore ska göras till en ny eller tom installation, eller med ett uttryckligt `--force`-val efter att backupfilen har validerats. Efter restore byggs Runtime/index upp igen från Archive.

Backupen återställer inte absoluta sökvägar, host, port eller andra maskinspecifika driftval från den gamla datorn. Den nya installationens lokala konfiguration avgör var Archive, Runtime och secrets ligger.

# 10.4 – Off-server backup och restore

## Ansvar och avgränsning

I repo finns `deploy/backup/offserver_backup.py`, backup-service/timer,
`backup.env.example`, en separat restore-service och CLI `verify-backup`.
Applikationens befintliga ZIP-format (version 1) används oförändrat.
Archive är auktoritativt; Runtime/SQLite, ingest-kön, OpenAI-credentials,
Caddy-credentials och rclone-konfiguration ingår inte. Portabel AI-konfiguration
ingår, men inte serverns absoluta sökvägar eller nätverksinställningar.

Administratören måste välja en lagringsplats som överlever förlust av hela
VPS-disken, skapa åtkomst och konfigurera en namngiven rclone-remote.
Ingen specifik leverantör krävs. En remote som i praktiken pekar tillbaka
till samma VPS-disk uppfyller inte kravet; det kan skriptet inte avgöra.
Välj skyddad transport och begränsad åtkomst till en dedikerad backupkatalog.
ZIP-filen är inte krypterad. Om lagringsplatsen kräver klientkryptering kan
transportlagrets rclone crypt användas; förvara då även dess nycklar separat
från VPS och Archive så att restore är möjlig efter total serverförlust.

## Körning, verifiering och generationer

Timern kör dagligen omkring 03:30 i serverns tidszon, med upp till 15 minuters
slumpfördröjning. `Persistent=true` tar igen en missad körning efter boot.
Lokal kopiering begränsas till 15 minuter, varefter felvägen tinar upp
tjänsterna. Justera gränsen först efter mätning på verkligt Archive.
Systemd kör inte samma service parallellt med sig själv; kör inte skriptets
faser manuellt eller en annan backupskrivare samtidigt.

1. Preflight kontrollerar konfiguration, separata datakataloger, rclone och
   frånvaro av symlänkar i Archive. Secrets måste ligga utanför Archive.
2. Web och worker fryses tillfälligt med systemd/cgroup v2. Befintligt `create_backup` skapar och CRC-/manifest-
   verifierar en lokal ZIP under `/var/lib/dokumentverkstad/backups/<generation>/`.
3. Web och worker tinas upp innan nätöverföringen. `ExecStopPost` begär
   upptining även om backupsteget misslyckas eller timeout inträffar.
4. ZIP kopieras till `<remote>/<unik-generation>/<backupfil>.zip` med
   `rclone copyto --immutable`; ingen `sync`, `delete` eller extern gallring körs.
5. Hela ZIP-filen laddas ned igen. SHA-256 måste överensstämma med den lokala
   filen. Därefter görs riktig provrestore i en tillfällig separat katalog:
   ZIP/manifest/sökvägar, läsbara domänposter, manifestets objektantal och
   SQLite-rebuild kontrolleras.
6. Först därefter laddas `verified.json` upp till samma generation. Lokal
   `last-success.json` uppdateras och just den lyckade lokala ZIP-generationen
   tas bort. Äldre externa generationer rörs aldrig.

En ZIP utan verifieringsmarkering är en ofullständig/ej verifierad generation.
Kontrollera alltid nedladdad backup igen vid restore; markeringen är ett
kvitto på en tidigare kontroll, inte en digital signatur eller garanti mot
senare ändring. Varje generation är självständig; inga inkrementella kedjor.

Backupen är inte en transaktionell snapshot medan tjänsterna skriver.
Frysningen hindrar ytterligare skrivningar under kopieringen utan att döda
en pågående skrivning i produktions-Archive. Använd inte direkt `backup`
mot ett aktivt Archive för schemalagd serverbackup. Undvik manuella
CLI-skrivningar och service-/configändringar under fönstret. Systemd kan
automatiskt tina upp en unit om ett annat administrationsjobb körs mot den.

Frysning kan fånga en ofärdig post; ogiltig JSON eller felaktiga objektantal
underkänns av backup/provrestore och generationen får ingen verifieringsmarkering.
Det finns ingen generell transaktionsgaranti över flera Archive-filer.
Välj ett lugnt tidsfönster utan aktiva skrivningar eller AI-jobb och granska
felstatus. Requests och externa AI-anrop kan hinna få timeout under pausen;
ingen process dödas av backupen. Ingen ny jobbscheduler eller låsarkitektur
införs. Caddy fortsätter skydda tjänsten men klienter kan tillfälligt få vänta
eller få proxy-timeout. Om pausen blir lång är annan snapshotteknik ett
separat driftsbeslut, inte en ny Archive-modell.

Servicen förutsätter systemd 246+ med unified cgroup v2 och normalt aktiva
web/worker. Saknat stöd ska ge fel, aldrig falla tillbaka till live-kopiering.
**Stoppa timern och invänta/stoppa pågående backup-service före underhåll**;
kontrollera att båda app-tjänsterna är upptinade innan arbetet fortsätter.

Alla externa generationer behålls i MVP. Administratören måste följa utrymme
och bestämma manuell retention, exempelvis minst sju senaste verifierade
generationer. Gallra endast explicit valda äldre generationer efter att en
ny generation och dess restore har verifierats; ingen automatisk
lagringslivscykel hos leverantören får radera dem i förtid. Vid transportfel
ligger lokal ZIP kvar för diagnos och eventuell manuell återföring. Nästa
timerkörning skapar en ny generation och återför inte automatiskt gamla
misslyckade försök. Kontrollera även lokalt diskutrymme; provrestore kräver
plats för ZIP, nedladdad ZIP, staging och återställt Archive med index.

## Förbered servern (manuellt, ingen aktivering från repoarbetet)

Följande förutsätter den dokumenterade Debian/Ubuntu-layouten, installerad
app i `/opt/dokumentverkstad/.venv` och användaren `dokumentverkstad`.

```sh
sudo apt install rclone
rclone version
systemctl --version
test -f /sys/fs/cgroup/cgroup.controllers
sudo install -d -o root -g dokumentverkstad -m 750 /etc/dokumentverkstad
sudo install -d -o dokumentverkstad -g dokumentverkstad -m 700 /var/lib/dokumentverkstad/backups
sudo install -d -o dokumentverkstad -g dokumentverkstad -m 700 /etc/dokumentverkstad/rclone
if ! sudo test -e /etc/dokumentverkstad/rclone/rclone.conf; then
  sudo install -o dokumentverkstad -g dokumentverkstad -m 600 /dev/null /etc/dokumentverkstad/rclone/rclone.conf
fi
sudo -u dokumentverkstad rclone --config /etc/dokumentverkstad/rclone/rclone.conf config
if ! sudo test -e /etc/dokumentverkstad/backup.env; then
  sudo install -o root -g dokumentverkstad -m 640 /opt/dokumentverkstad/deploy/systemd/backup.env.example /etc/dokumentverkstad/backup.env
fi
sudo editor /etc/dokumentverkstad/backup.env
```

Skapa inte om en befintlig `rclone.conf` med `/dev/null`; det tömmer filen.
Vid befintlig konfiguration: granska och använd den, eller välj en separat ny
fil. Konfigurationsdialogen och eventuell initial extern auktorisering görs
av administratören. Rclone-filen och dess privata underkatalog ägs av
serviceanvändaren så att tokenförnyelse kan sparas via temporär fil och rename.
Den överordnade `/etc/dokumentverkstad` ägs av root. Använd inte
credentials i kommandorader, repo eller loggar. Unattended åtkomst måste fungera
utan lösenordsprompt. Säkerhetskopiera återställningscredentials separat.

Sätt i `backup.env`, med det namn och den katalog du själv valt:

```text
DOKUMENTVERKSTAD_BACKUP_REMOTE=offserver:dokumentverkstad
RCLONE_CONFIG=/etc/dokumentverkstad/rclone/rclone.conf
```

`offserver` är ett exempel på eget remote-namn, inte en förvald tjänst.
Rclone och dess konfiguration är deploymentberoenden, inte Python- eller
Archive-beroenden. Backupservicen läser samma `dokumentverkstad.env` som web
och worker så att lagringsöverskrivningar överensstämmer. Den behöver ingen
AI-nyckel för backup och skickar inte environment till ZIP-filen. Håll alla
secrets utanför Archive, även om filnamnet inte heter `secrets.*`.

Kontrollera remote utan att skapa eller radera backupfiler:

```sh
sudo -u dokumentverkstad rclone --config /etc/dokumentverkstad/rclone/rclone.conf lsf offserver:dokumentverkstad --max-depth 1
sudo install -o root -g root -m 644 /opt/dokumentverkstad/deploy/systemd/dokumentverkstad-backup.service /etc/systemd/system/
sudo install -o root -g root -m 644 /opt/dokumentverkstad/deploy/systemd/dokumentverkstad-backup.timer /etc/systemd/system/
sudo install -o root -g root -m 644 /opt/dokumentverkstad/deploy/systemd/dokumentverkstad-restore@.service /etc/systemd/system/
sudo systemd-analyze verify /etc/systemd/system/dokumentverkstad-backup.service /etc/systemd/system/dokumentverkstad-backup.timer /etc/systemd/system/dokumentverkstad-restore@.service
sudo systemctl daemon-reload
```

Granska paths, servicekonto, rclone-version, cgroup v2 och serverns tidszon. Koden och
unit-filerna måste vara administratörskontrollerade; endast systemctl-stegen
kör med utökade rättigheter (`+`), själva backup/transport kör som
`dokumentverkstad` med umask 0077. En annan installation kan anpassa
deploymentartefakternas paths utan ändring av Archive-formatet.

I ett valt underhållsfönster, när konfiguration och extern destination är klara:

```sh
sudo systemctl start dokumentverkstad-backup.service
systemctl status dokumentverkstad-backup.service --no-pager
journalctl -u dokumentverkstad-backup.service -n 100 --no-pager
systemctl is-active dokumentverkstad-web.service dokumentverkstad-worker.service
systemctl show dokumentverkstad-web.service dokumentverkstad-worker.service -p FreezerState
sudo cat /var/lib/dokumentverkstad/backups/last-success.json
```

Kräv lyckad återläsning/provrestore och `backup verified` före aktivering av timern:

```sh
sudo systemctl enable --now dokumentverkstad-backup.timer
systemctl list-timers dokumentverkstad-backup.timer --all
```

Normal backupdrift kräver därefter ingen SSH eller öppen klient. SSH/annan
administrationsväg används bara vid installation, felsökning och restore.

## Status och fel

```sh
systemctl show dokumentverkstad-backup.service -p Result -p ExecMainStatus
systemctl status dokumentverkstad-backup.timer --no-pager
journalctl -u dokumentverkstad-backup.service --since yesterday --no-pager
df -h /var/lib/dokumentverkstad
```

En avslutad oneshot är normalt `inactive (dead)`; kontrollera resultat och
journal, inte bara `is-active`. `last-success.json` visar senaste fullständigt
verifierade generation och tid. Gammalt kvitto betyder inte att dagens körning
lyckats. Loggen visar snapshot, upload, readback, restore check och marker upload.
Rclone-fel ger exitkod och fas; providerutdata undertrycks för att inte läcka
credentials eller privata adresser. Kontrollera konfiguration, nätåtkomst,
behörigheter och kvot i en skyddad administrativ session, utan debugdumpning.
Automatisk larmleverans ingår inte; granska journal och kvittots ålder regelbundet.

Efter körning ska `FreezerState=running` gälla för båda app-tjänsterna.
Vid fel i upptiningen, kör:

```sh
sudo systemctl thaw dokumentverkstad-web.service dokumentverkstad-worker.service
```

Kontrollera sedan journalen. Vid faktisk serverreboot startar de aktiverade
app-tjänsterna normalt på nytt; frysningen är inte beständig.

## Restore från off-server till separat installation

Detta är en provåterställning utan produktionsskrivning. Använd en separat
maskin om målet är att verifiera återställning efter total VPS-förlust. Samma
rutin kan först övas i nedanstående isolerade katalog på befintlig server.
Installera samma appversion/beroenden, serviceanvändare och restore-unit där.
Återskapa transportcredentials från den separat bevarade kopian.

Välj en verklig generation och backupfil från remote-listningen; ersätt
`GENERATION` och `BACKUPFIL.zip` nedan. Använd ett nytt instansnamn/katalog
om `acceptance` redan innehåller data. Inget `--force` behövs.

```sh
sudo install -d -o root -g dokumentverkstad -m 750 /var/lib/dokumentverkstad-restore
sudo install -d -o dokumentverkstad -g dokumentverkstad -m 750 /var/lib/dokumentverkstad-restore/acceptance
sudo -u dokumentverkstad rclone --config /etc/dokumentverkstad/rclone/rclone.conf copyto offserver:dokumentverkstad/GENERATION/BACKUPFIL.zip /var/lib/dokumentverkstad-restore/acceptance/backup.zip --immutable
sudo -u dokumentverkstad rclone --config /etc/dokumentverkstad/rclone/rclone.conf copyto offserver:dokumentverkstad/GENERATION/verified.json /var/lib/dokumentverkstad-restore/acceptance/verified.json --immutable
sudo -u dokumentverkstad sha256sum /var/lib/dokumentverkstad-restore/acceptance/backup.zip
sudo -u dokumentverkstad cat /var/lib/dokumentverkstad-restore/acceptance/verified.json
sudo -u dokumentverkstad /opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad verify-backup /var/lib/dokumentverkstad-restore/acceptance/backup.zip
sudo editor /var/lib/dokumentverkstad-restore/acceptance/dokumentverkstad.toml
```

**Avbryt om SHA-256 inte exakt motsvarar `sha256` i kvittot eller
`verify-backup` misslyckas.** Detta CLI-kommando kontrollerar ZIP-CRC, manifest
och sökvägar utan att läsa installationsconfig eller skriva Archive/Runtime.
Det ersätter inte nästa stegs verkliga restore och funktionella kontroll.

Skriv följande isolerade TOML, inte produktionsconfigens paths:

```toml
archive_root = "/var/lib/dokumentverkstad-restore/acceptance/archive"
runtime_root = "/var/lib/dokumentverkstad-restore/acceptance/runtime"
ingest_source = "/var/lib/dokumentverkstad-restore/acceptance/ingest"
secrets_path = "/var/lib/dokumentverkstad-restore/acceptance/secrets.toml"
encrypted_secrets_path = "/var/lib/dokumentverkstad-restore/acceptance/secrets.enc"
host = "127.0.0.1"
port = 8001
```

```sh
sudo chown root:dokumentverkstad /var/lib/dokumentverkstad-restore/acceptance/dokumentverkstad.toml
sudo chmod 640 /var/lib/dokumentverkstad-restore/acceptance/dokumentverkstad.toml
sudo systemctl start dokumentverkstad-restore@acceptance.service
systemctl status dokumentverkstad-restore@acceptance.service --no-pager
journalctl -u dokumentverkstad-restore@acceptance.service -n 100 --no-pager
sudo -u dokumentverkstad /opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad --config /var/lib/dokumentverkstad-restore/acceptance/dokumentverkstad.toml rebuild-index
sudo -u dokumentverkstad /opt/dokumentverkstad/.venv/bin/python -m dokumentverkstad --config /var/lib/dokumentverkstad-restore/acceptance/dokumentverkstad.toml status
sudo find /var/lib/dokumentverkstad-restore/acceptance/archive /var/lib/dokumentverkstad-restore/acceptance/runtime ! -user dokumentverkstad -print
```

Restore bygger redan index; det explicita `rebuild-index` visar att Runtime
kan återskapas igen. Sista kommandot ska inte lista felägda filer. Kontrollera
också att administrativa shellmiljön inte har `DOKUMENTVERKSTAD_*`-överskrivningar
som pekar tillbaka på produktion när CLI körs. Restore-uniten läser avsiktligt
inte produktions-EnvironmentFile och tillåter skrivning endast under sin instans.

Starta vid behov provwebben lokalt med `run --no-worker` som serviceanvändaren
och provconfigen. Använd skyddad administrationsåtkomst till loopback:8001;
exponera inte testinstallationen publikt och ändra inte fungerande Caddy.
Kontrollera dokument/PDF, noteringar, historik och AI-resultat. **Skapa och
redigera en testnotering i provinstallationen som samma serviceanvändare**,
och verifiera att produktions-Archive är oförändrat. Starta inte provworkern
eller nya AI-jobb under en ren återställningskontroll.

## Ownership: orsak, förebyggande och reparation

ZIP-formatet lagrar inte en portabel serviceidentitet. Restore extraherar och
kopierar filer som den användare som kör processen. `sudo ... restore` som
root gav därför root-ägda filer i verklig drift. Läsbarhet eller fungerande
index är inte bevis på att review/save kan skriva.

Restore-uniten ovan löser detta genom `User=dokumentverkstad` och
`Group=dokumentverkstad`, utan automatisk chown eller ändrat Archive-format.
Även direkt CLI-restore ska köras med `sudo -u dokumentverkstad` till kataloger
som kontot får skriva i. Kör rebuild som samma användare. För ny produktions-
installation: skapa datakatalogerna med rätt ägare före restore och starta
web/worker först efter kontroll av både läsning och skrivning.

Om en tidigare root-restore måste repareras: stoppa backup-timern, stoppa
eventuell backupkörning, därefter web och worker. Kontrollera först att configen
verkligen använder nedanstående data och att inga oväntade symlänkar/mounts
pekar på annan data. Kör sedan endast mot den verifierade dataroten:

```sh
sudo systemctl stop dokumentverkstad-backup.timer dokumentverkstad-backup.service
sudo systemctl stop dokumentverkstad-web.service dokumentverkstad-worker.service
sudo chown -R dokumentverkstad:dokumentverkstad /var/lib/dokumentverkstad
sudo find /var/lib/dokumentverkstad -type d -exec chmod 750 {} \;
sudo find /var/lib/dokumentverkstad -type f -exec chmod 640 {} \;
sudo systemctl start dokumentverkstad-web.service dokumentverkstad-worker.service
```

Kör bara backup-stop-kommandot om dessa units är installerade. Skyddade filer
under `/etc/dokumentverkstad` och Caddy ändras inte. Verifiera review/save innan
timern startas igen med `sudo systemctl start dokumentverkstad-backup.timer`.
Ingen generell root-chown-logik läggs i applikationen.

## Lokal kontra verklig verifiering

Lokalt testas ZIP-format, tomt Archive, valideringsfel, oförändrat mål vid
felaktig restore, transportfel, skadad återläsning, flera generationer och
restore/rebuild med skrivbar notering. Transporten ersätts i enhetstesterna
med en lokal testdubbel; det bevisar inte nätverk eller extern lagring.
POSIX-testet för ägare körs bara på POSIX. Kör hela sviten:

```sh
python -m unittest discover -s tests
```

Verifierat lokalt 2026-09-22 på Windows/Python 3.13: hela sviten kördes med
183 tester, 182 godkända och ett POSIX-ownership-test överhoppat. En separat
integration med rclone 1.75.1 mot en lokal alias-remote skapade och verifierade
två generationer med återläsning och provrestore. Ingen extern lagring eller
credential användes. Linux/systemd finns inte i denna lokala testmiljö.

På Linux måste dessutom units valideras, rättigheter och frysning/upptining
testas, rclone köras mot den valda lagringen och minst en schemalagd generation
återställas på separat installation. Testa även otillgänglig remote i en
separat provkonfiguration: misslyckad körning ska synas i journalen, äldre
backups vara orörda och web/worker ha tinats upp. Dokumentera datum, revision,
generation och resultat. Aktiveringen och 10.5 är inte godkända enbart genom
lokala tester.

Transport- och servicebeteendet bygger på officiella referenser:
[rclone copyto](https://rclone.org/commands/rclone_copyto/),
[rclone crypt](https://rclone.org/crypt/) och
[systemd.service](https://www.freedesktop.org/software/systemd/man/latest/systemd.service.html),
samt [systemctl freeze/thaw](https://www.freedesktop.org/software/systemd/man/latest/systemctl.html).

# 10.5 – MVP acceptance och driftverifiering

Använd den fullständiga checklistan i IMPLEMENTATION_PLAN.md. Den omfattar
reboot av Caddy/web/worker, HTTPS/auth inklusive obehöriga försök, minst två
klienter, dokument/PDF, notering, fjärrupload med automatisk ingest, AI med
stängd klient, review/save, schemalagd backup, verifierad off-server-generation,
separat restore, rebuild, ownership och hela testsviten.

Registrera faktisk körning och resultat, inte bara att kommandon finns.
10.5 inför inga nya features. Först efter godkänd checklista kan planen få
slutstatus **MVP COMPLETE**.

---

# 10.3.1 – förberedelse för HTTPS och autentisering

Repoartefakter:

- `deploy/caddy/Caddyfile`: målkonfiguration med domänen `verkstad.example.com`.
- `deploy/caddy/dokumentverkstad.auth.example`: endast ogiltiga placeholders.
- Befintliga `deploy/systemd/dokumentverkstad-{web,worker}.service` återanvänds.

Ingen av mallarna ska startas på VPS i 10.3.1. Ingen domän, DNS, firewall,
verklig credential eller publikt certifikat ska skapas i denna deliteration.
Lokal utveckling fortsätter med samma `run`/`start` och valfri inbyggd worker.

## Bindning och proxygräns

`AppConfig` och `load_config` har redan standardvärdena `127.0.0.1:8000`.
`web.main` skickar dem till `ThreadingHTTPServer`. `host`/`port` i TOML kan
åsidosättas av `DOKUMENTVERKSTAD_HOST`/`DOKUMENTVERKSTAD_PORT`; environment
har företräde. Produktionsconfig ska ha `host = "127.0.0.1"`, `port = 8000`.
Kontrollera även den befintliga systemd-environment-filen så att den inte
åsidosätter adressen med `0.0.0.0` eller en publik adress. Om porten ändras
måste även Caddyfilens `reverse_proxy`-target ändras. Appen behöver ingen
publik port och Caddy behöver ingen åtkomst till Archive eller OpenAI-nyckeln.

Caddyfilens `basic_auth bcrypt` saknar route-matcher och gäller därför alla
requests innan `reverse_proxy`: Documents, Inbox, Projects, Capture,
AI-review, upload, PDF-original, statiska resurser och `/admin`. Inga
undantag införs. Den obligatoriska importen använder ett exakt filnamn,
inte wildcard: saknad credential-fil ger konfigurationsfel. Platshållarhashen
är ogiltig och ska inte kunna användas för deployment. Caddy tar bort
`Authorization` innan requesten går vidare till appen.

Appens redirects använder relativa `Location`-värden och länkar/formulär
bygger inte absoluta URL:er från Host eller scheme. Inga forwarding headers
läses av appen, och dess requestdiagnostik loggar inte klient-IP. Caddys
normala X-Forwarded-hantering räcker; inga `trusted_proxies` anges eftersom
Caddy möter internet direkt. Appen får inte börja lita på klientskickade
headers. Den lokala hosten är trust boundary; andra lokala processer med
åtkomst till port 8000 kan nå appen utan Basic Auth.

## Upload och bakgrundsarbete

Appens oförändrade gräns är `upload_max_bytes = 262144000` (250 MiB),
kontrollerad mot Content-Length för hela multipart-requesten inklusive
overhead. Caddyfilen sätter ingen `request_body max_size` eller extra
requestbuffring; proxyn inför ingen lägre storleksgräns. Vanlig browser-upload
med Content-Length går till appens befintliga staging och ingest-kö.
Appen stöder inte generellt chunked request-body utan Content-Length; detta
är en befintlig begränsning, inte ett nytt streaming-upload-API.

`POST /documents/<id>/ai/run` sparar planerat arbete och svarar med redirect.
`POST /upload` lägger PDF i ingest-kön. Den separata workern gör import och
AI-anrop; Caddy får inga särskilda långa AI-timeouts. Överföring av en stor
PDF kan naturligtvis ta tid, men väntar inte på AI-resultat.

## Lokal verifiering utan aktivering

Kör hela appsviten med `python -m unittest discover -s tests`. Ingen
applikationskod ändras i 10.3.1, så inga nya Python-tester av Caddy behövs.
Om Caddy finns lokalt: kopiera de två mallarna till en tillfällig katalog
utanför versionshanteringen, döp auth-kopian till `dokumentverkstad.auth`
och använd enbart en tillfällig testidentitet och interaktivt genererad hash.
Kör `caddy validate --config <katalog>/Caddyfile --adapter caddyfile`.
Validering startar inte webbservern eller begär publika certifikat. Kör inte
`caddy run`, `start` eller `reload` för placeholderdomänen. Publicera inte
`caddy adapt`-utdata: importerade credentials finns i den expanderade configen.

Verifierat i 10.3.1 på Windows: hela befintliga sviten passerade, 172 tester
med `python -m unittest discover -s tests`. Caddy v2.11.4 godkände målfilen
med en tillfällig testhash via `caddy validate`; saknad auth-fil och
platshållarhash avvisades. Den adapterade konfigurationen kontrollerades för
auth före proxy utan route-undantag, loopback-target och borttagen Authorization.
Testhashen raderades. Ingen Caddy-server startades och inget publikt certifikat
begärdes. Verklig TLS, Linux-filrättigheter och browser-upload genom en körande
proxy återstår att verifiera i 10.3.2.

# 10.3.2 – verklig extern aktivering (manuell körplan)

Alla serverkommandon i detta avsnitt är instruktioner för 10.3.2, inte steg
som ska köras i förberedelseiterationen.

## Installera Caddy på Debian/Ubuntu

Använd Caddys officiella stable-paket och dess `caddy.service` (Caddy 2.8+
för direktivnamnet `basic_auth`). Ingen egen duplicerad Caddy-unit behövs.
På en ny server kan installation göras enligt nedan. Maskeringen hindrar
paketets automatiska start innan config och auth är klara. Om Caddy redan
används på servern: granska befintliga sites och service först; ersätt eller
stoppa inte andra tjänster med denna nyinstallationsrutin.

```sh
sudo systemctl mask caddy.service
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl gnupg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
caddy version
```

## Installera config och sätt verklig domän/credential

```sh
sudo install -o root -g caddy -m 644 /opt/dokumentverkstad/deploy/caddy/Caddyfile /etc/caddy/Caddyfile
sudo install -o root -g caddy -m 640 /opt/dokumentverkstad/deploy/caddy/dokumentverkstad.auth.example /etc/caddy/dokumentverkstad.auth
sudo editor /etc/caddy/Caddyfile
```

Byt endast `verkstad.example.com` på site-raden till vald verklig FQDN,
utan `http://`, sökväg eller wildcard. Detta är deployment-konfiguration.
Behåll auth-blocket och target `127.0.0.1:8000`.

Generera hashen i administratörens interaktiva terminal:

```sh
caddy hash-password --algorithm bcrypt
sudo editor /etc/caddy/dokumentverkstad.auth
sudo chown root:caddy /etc/caddy/dokumentverkstad.auth
sudo chmod 640 /etc/caddy/dokumentverkstad.auth
```

Caddy frågar efter lösenord utan eko. Använd inte `--plaintext`, shell-echo,
shellhistorik eller inspelad terminal för lösenordet. Kommandots stdout är
hashen; kopiera den direkt till auth-filen utan att publicera den. Sätt en
enda aktiv rad med `VERKLIGT_USERNAME GENERERAD_HASH`. Välj ett enkelt username
utan whitespace, kolon eller Caddy-syntax (exempelvis bokstäver, siffror,
bindestreck och understreck). Hashen kopieras oförändrad med sina dollartecken;
filen är Caddy-syntax och ska inte köras eller source:as som shellscript.
Använd en editor som håller eventuella swap-/backupfiler lika skyddade.

Auth-filen ligger bredvid Caddyfile och läses genom relativ `import`.
Den ska vara läsbar för Caddy, men inte för Dokumentverkstads servicekonto
eller övriga användare. `/etc/caddy` måste vara traverserbar för gruppen caddy.
Plaintext-lösenordet lagras inte där. Auth-filen är ändå känslig och ingår
inte i Archive eller appbackupen. Vid lösenordsbyte: generera ny hash, uppdatera
filen, validera och reloada Caddy.

Repo innehåller bara mallar. Exakta lokala kopior
`deploy/caddy/dokumentverkstad.auth`, `deploy/caddy/Caddyfile.local` och
`deploy/systemd/dokumentverkstad.env` ignoreras i Git. Lägg inga serverkopior,
certifikat eller privata nycklar i andra repokataloger. TLS-state lagras av
Caddy under serviceanvändarens hem `/var/lib/caddy`, utanför repo och appdata.
Caddys autosparade config kan också innehålla hash: skydda hela Caddys
state/config, och publicera inte configdumpar eller admin-API-svar.

## Validering, start och löpande drift

Validera som samma användare som tjänsten, så även läsrättigheter kontrolleras:

```sh
sudo -u caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
```

Kräv lyckad validering innan start/reload. När verklig DNS och firewall är
kontrollerade enligt nedan:

```sh
sudo systemctl unmask caddy.service
sudo systemctl enable --now caddy.service
systemctl status caddy.service
```

Senare config-ändring eller credential-rotation:

```sh
sudo -u caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
sudo systemctl reload caddy.service
```

Kör reload bara om föregående kommando lyckas. Vid behov av processomstart:
`sudo systemctl restart caddy.service`. Status/loggar:

```sh
systemctl is-active caddy.service dokumentverkstad-web.service dokumentverkstad-worker.service
journalctl -u caddy.service -n 100 --no-pager
journalctl -u caddy.service -f
journalctl -u dokumentverkstad-web.service -n 100 --no-pager
journalctl -u dokumentverkstad-worker.service -n 100 --no-pager
```

Tre oberoende systemd-services startas vid boot. Dokumentverkstad startar
inte Caddy. Caddy behöver inte starta om när web/worker uppdateras; om webben
är nere ger proxyn normalt 502 efter lyckad auth. Om bara workern är nere
kan webben svara medan jobb väntar. Ingen ny servicekoppling krävs.

Ingen accesslog aktiveras i mallen; journald ger Caddys drift-/TLS-diagnostik.
Appens befintliga runtime-logg ger requestfel och jobbdiagnostik, utan headers
eller POST-body. Aktivera inte debug/configdumpning för att felsöka credentials.

## DNS, TLS och HTTP

Sätt A till rätt publik IPv4. Sätt AAAA endast om serverns IPv6 verkligen
fungerar med samma firewall och Caddy; en felaktig AAAA kan bryta både klienter
och certifikatvalidering. Kontrollera med `dig +short A <domän>` och
`dig +short AAAA <domän>` från ett externt nät.

När Caddy startas med verkligt domännamn, korrekt DNS och nåbara portar
skaffar och förnyar den normalt betrodda publika certifikat automatiskt.
Port 80 omdirigerar till HTTPS; ACME-validering hanteras av Caddy utan route
till Dokumentverkstad. Ingen manuell TLS-kod, certifikatfil i Git,
`tls internal` eller eget förnyelsescript behövs. Använd aldrig credentials
vid test mot `http://`; börja autentiserade tester direkt på `https://`.

## Firewall och administration

Slutläge för publik webbtrafik: 80/tcp och 443/tcp till Caddy. Port 8000
ska endast lyssna på IPv4-loopback. Caddys admin-API (normalt localhost:2019)
ska förbli lokalt och aldrig proxyas eller öppnas publikt. 443/udp för HTTP/3
är valfritt och behövs inte för MVP; TCP räcker. Workern har ingen lyssningsport
men behöver utgående trafik för AI. Caddy behöver utgående DNS/HTTPS för ACME.

Granska befintlig host-firewall och eventuell provider-firewall i 10.3.2.
Bevara SSH-regler, faktisk SSH-port, Tailscale-regler och fungerande privat
administration. Behåll en befintlig adminsession och verifiera en andra innan
regeländringar. Kör inte generell firewall-reset eller `ufw enable` på chans.

Om servern redan använder aktiv UFW är följande en plan, efter separat kontroll
av administrationsvägen (på andra system används deras befintliga brandvägg):

```sh
sudo ufw status verbose
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status numbered
sudo ss -ltnp
```

Granska och ta bort eventuell tidigare publik allow-regel för 8000 enligt
dess verkliga regelnamn/nummer; kontrollera både IPv4 och IPv6. Lägg inte till
en generell deny som kan krocka med administrationsregler. Kontrollera externt
att port 8000 och 2019 inte kan nås. Ingen firewalländring görs i 10.3.1.

## Diagnostik och acceptans från verklig klient

| Lager | Kontroll | Förväntat resultat |
| --- | --- | --- |
| DNS | `dig +short A <domän>` / `AAAA` | Endast fungerande serveradresser |
| TLS/Caddy | `curl -v https://<domän>/ -o /dev/null` utan credentials | Giltigt certifikat, inga `-k`-undantag |
| HTTP | `curl -sS -D - -o /dev/null http://<domän>/` utan credentials | Redirect till samma host över HTTPS, inget appinnehåll eller auth-prompt |
| Auth | `curl -sS -D - -o /dev/null https://<domän>/inbox` | 401 och WWW-Authenticate |
| Auth + proxy | `curl --user '<username>' -sS -D - -o /dev/null https://<domän>/inbox` | Interaktiv lösenordsfråga, sedan 200 |
| Lokal web | `curl -sS -D - -o /dev/null http://127.0.0.1:8000/` på servern | 200 även utan Basic Auth på lokal trust boundary |
| Worker | systemd-status, workerjournal och appens CLI `status` | Aktiv worker och jobb som lämnar planned/running |

Använd GET enligt tabellen: appen implementerar inte HEAD, så `curl -I` mot
appen kan ge 501 och är inte en tillförlitlig hälsokontroll.

Upprepa oautentiserade GET och POST mot `/`, `/documents`, `/inbox`,
`/projects`, `/capture`, `/upload`, `/admin`, en verklig PDF-/static-URL och
en verklig `/documents/<id>/ai/run`: allt ska ge 401 före appen. Fel lösenord
ska också ge 401. Testa giltiga credentials endast över HTTPS utan verbose
curl-utdata. Testa från minst två klienter utan Tailscale: skapa Capture,
följ redirects (HTTPS-host ska bevaras), öppna PDF, ladda upp vanlig och stor
tillåten PDF och kontrollera att för stor request ger appens 413. Starta AI,
stäng klienten och verifiera senare färdigt resultat. Kontrollera efter reboot
att alla tre tjänster går utan terminal och att auth fortfarande krävs.

## Källor för Caddy-konfigurationen

- [Installation och officiella paket](https://caddyserver.com/docs/install#debian-ubuntu-raspbian)
- [Basic Auth och hashformat](https://caddyserver.com/docs/caddyfile/directives/basic_auth)
- [CLI: hash-password och validate](https://caddyserver.com/docs/command-line)
- [Obligatorisk import](https://caddyserver.com/docs/caddyfile/directives/import)
- [Reverse proxy och forwarding headers](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
- [Request body-gränser](https://caddyserver.com/docs/caddyfile/directives/request_body)
- [Automatic HTTPS](https://caddyserver.com/docs/automatic-https)
- [Caddy som systemd-service och lagring](https://caddyserver.com/docs/running)

## Ordnad checklista för 10.3.2

1. Välj domän, granska serverdistribution, befintliga lyssnare och bevara SSH/Tailscale.
2. Sätt och verifiera A samt eventuell fungerande AAAA.
3. Installera Caddy med automatisk start tillfälligt blockerad enligt nyinstallationsrutinen.
4. Installera Caddyfile, byt placeholderdomänen och kontrollera appens loopback-binding.
5. Sätt verkligt username och interaktivt genererad hash i skyddad serverfil.
6. Validera som caddy-användaren; åtgärda alla fel före start.
7. Granska host/provider-firewall, bevara administration och tillåt publik 80/443 TCP.
8. Aktivera Caddy och verifiera verkligt certifikat samt HTTP-till-HTTPS-redirect.
9. Verifiera 401 för alla routes utan/fel auth och stängd extern 8000/2019.
10. Testa Capture, upload, PDF och asynkron AI från minst två verkliga klienter; kontrollera drift efter reboot.

# Framtida utveckling

Deploymentmiljön kan senare förändras, exempelvis genom:

* lokal AI,
* annan synkronisering än Dropbox,
* annan serverplattform,
* NAS,
* fler klienter.

Sådana förändringar ska normalt endast kräva uppdateringar av detta dokument.

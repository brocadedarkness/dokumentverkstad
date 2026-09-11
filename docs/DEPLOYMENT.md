# Deployment för Dokumentverkstad

## Syfte

Detta dokument beskriver den aktuella produktionsmiljön för Dokumentverkstad.

Till skillnad från arkitekturen är deployment-specifikationen avsedd att kunna förändras över tid när hårdvara, operativsystem eller externa tjänster byts ut.

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

Denna grund från 10.1 kompletteras av systemd-avsnittet och förberedelserna
för Caddy i 10.3.1 nedan. Extern aktivering sker först i 10.3.2.

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

Servern ska kompletteras med regelbunden backup till annan lagring än den aktiva serverdisken.

Arkivet är den viktigaste tillgången och ska kunna återställas oberoende av serverns runtime-data.

Dokumentverkstads inbyggda backup är en portabel ZIP-förpackning av Archive och ett litet manifest. Den innehåller inte Runtime, SQLite-index, Ingest Source eller secrets.

Restore ska göras till en ny eller tom installation, eller med ett uttryckligt `--force`-val efter att backupfilen har validerats. Efter restore byggs Runtime/index upp igen från Archive.

Backupen återställer inte absoluta sökvägar, host, port eller andra maskinspecifika driftval från den gamla datorn. Den nya installationens lokala konfiguration avgör var Archive, Runtime och secrets ligger.

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

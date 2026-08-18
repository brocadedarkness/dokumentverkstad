# Dokumentverkstad

Dokumentverkstad är en lokal-first arbetsyta för kumulativt kunskapsarbete.

## Användning

Aktuell användardokumentation finns i:

* [docs/USER_GUIDE.md](docs/USER_GUIDE.md)

Guiden beskriver den funktionalitet som faktiskt finns implementerad.

Kort startflöde:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad init
python -m dokumentverkstad start
```

Backup, restore och index-återskapande:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad backup
python -m dokumentverkstad restore dokumentverkstad-backup-2026-08-18T103000Z.zip
python -m dokumentverkstad rebuild-index
```

Driftstatus och lokal diagnostik:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad status
```

Webbservern och CLI skriver diagnostik till `runtime_root/logs/dokumentverkstad.log`. Loggen ligger i Runtime och kan raderas utan dataförlust.

Webbgränssnittet startar lokalt på `http://127.0.0.1:8000/`. För privat åtkomst från egna enheter rekommenderas Tailscale Serve mot samma localhost-port, till exempel `tailscale serve 8000`; använd inte offentlig Funnel-exponering.

PDF-filer kan importeras antingen från den konfigurerade Ingest Source eller via webbflödet "Lägg till PDF". Båda vägarna använder samma ingest-semantik med checksumma, dublettkontroll, PDF-text/metadata, Archive-lagring, Inbox-status och indexuppdatering.

För krypterad lokal lagring av OpenAI API key:

```powershell
$env:PYTHONPATH = "src"
python -m dokumentverkstad init --with-openai
```

Krypterade secrets lagras separat från Archive i `.dokumentverkstad/secrets.enc`.
De ingår inte i vanlig backup och behöver konfigureras separat efter restore.

## Projektdokumentation

Projektets auktoritativa dokumentation finns i `docs/`.

Nya utvecklare och AI-agenter bör läsa dokumenten i följande ordning:

1. [MANIFEST.md](docs/MANIFEST.md)
2. [DESIGN_PRINCIPLES.md](docs/DESIGN_PRINCIPLES.md)
3. [DOMAIN_MODEL.md](docs/DOMAIN_MODEL.md)
4. [ARCHITECTURE.md](docs/ARCHITECTURE.md)
5. [DEPLOYMENT.md](docs/DEPLOYMENT.md)
6. [WORKFLOWS.md](docs/WORKFLOWS.md)
7. [UI.md](docs/UI.md)
8. [MVP.md](docs/MVP.md)
9. [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)

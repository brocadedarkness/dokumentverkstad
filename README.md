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

# Arbetsflöden för Dokumentverkstad

## Syfte

Detta dokument beskriver hur användaren arbetar med Dokumentverkstad.

Arbetsflödena utgår från användarens mål och beslut. De beskriver inte implementationens interna kodstruktur.

Varje arbetsflöde ska ange:

* utgångsläge,
* utlösande handling,
* systemets arbete,
* användarens beslut,
* beständigt resultat,
* möjliga avvikelser eller fel.

Arbetsflödena ska användas för att pröva att domänmodell, arkitektur och användargränssnitt stödjer verkligt arbete.

---

# Workflow 1: Registrera ett digitalt dokument

## Utgångsläge

Användaren har en digital fil som ska in i Dokumentverkstad.

I första versionen är filen en PDF.

## Utlösande handling

Användaren placerar filen i en konfigurerad Ingest Source.

## Systemets arbete

Dokumentverkstad:

1. upptäcker filen,
2. väntar tills den är färdigsynkroniserad,
3. kopierar den till lokal staging,
4. beräknar checksumma,
5. kontrollerar om filen redan är registrerad,
6. skapar ett Document-ID,
7. arkiverar originalfilen,
8. extraherar teknisk och tillgänglig bibliografisk metadata,
9. extraherar text om möjligt,
10. registrerar dokumentet i indexet.

## Användarens beslut

Ingen AI-bearbetning startas automatiskt.

Dokumentet visas som registrerat och väntar på vidare arbete.

Användaren kan:

* komplettera metadata,
* tillåta eller neka moln-AI,
* lägga dokumentet i ett eller flera projekt,
* skapa egna noteringar,
* starta AI-analys,
* kasta dokumentet.

## Beständigt resultat

* Document registrerat
* originalfil arkiverad
* metadata sparad
* extraherad text sparad när sådan finns
* index uppdaterat

---

# Workflow 2: Registrera en fysisk bok

## Utgångsläge

Användaren läser ett dokument som inte finns digitalt i Dokumentverkstad.

Exempel: en fysisk bok.

## Utlösande handling

Användaren väljer:

> Nytt dokument

## Användarens arbete

Användaren anger så lite metadata som behövs för att känna igen källan.

Normalt räcker:

* titel

Valfritt:

* författare
* år
* upplaga
* språk
* kommentar

## Systemets arbete

Dokumentverkstad:

1. skapar ett Document-ID,
2. sparar metadata,
3. markerar att ingen originalfil finns,
4. gör dokumentet tillgängligt för Knowledge Objects och Projects.

## Beständigt resultat

Ett Document finns i kunskapsrummet utan digital originalfil.

En digital fil kan kopplas till dokumentet senare.

---

# Workflow 3: Fånga en tanke under läsning

## Utgångsläge

Användaren läser ett dokument eller tänker vidare på ett tidigare problem.

## Utlösande handling

Användaren väljer:

> Ny notering

## Användarens arbete

Användaren skriver fri text.

Exempel:

> Påminner om North.

eller:

> Institutioner reducerar osäkerhet, se s. 35.

eller:

> Är detta North eller Gibson?

Användaren behöver inte klassificera noteringen.

Koppling till ett Document är frivillig.

Källposition är frivillig.

## Systemets arbete

Dokumentverkstad:

1. skapar ett Knowledge Object,
2. sparar skapare och tidpunkt,
3. sparar eventuell Document-koppling,
4. sparar eventuell Source Location,
5. lämnar semantisk typ oklassificerad om användaren inte anger annat.

## Beständigt resultat

Tanken är bevarad med minsta möjliga friktion.

Struktur och precision kan förbättras senare.

---

# Workflow 4: Köra AI-analys av ett dokument

## Utgångsläge

Ett Document är registrerat och har maskinläsbar text.

Moln-AI är inte tillåten som standard.

## Utlösande handling

Användaren väljer:

> Analysera

## Systemets arbete före körning

Dokumentverkstad:

1. kontrollerar dokumentets behandlingstillstånd,
2. visar vilka capabilities som ska användas,
3. visar vald AI-provider och modell,
4. uppskattar input- och output-token,
5. beräknar uppskattad kostnad.

Exempel på capabilities:

* kort sammanfattning,
* claims,
* candidate insights,
* frågor att ta vidare,
* projektförslag.

## Användarens beslut

Användaren kan:

* godkänna molnbehandling,
* välja bort arbetsmoment,
* starta analysen,
* avbryta.

## Systemets arbete efter godkännande

AI-resultaten sparas som kandidater med:

* provider,
* modell,
* promptversion,
* tidpunkt,
* tokenanvändning,
* kostnad,
* confidence,
* källkopplingar när sådana finns.

## Beständigt resultat

AI-genererade Knowledge Objects och andra förslag läggs i review-kön.

Efter körningen visas faktisk kostnad.

---

# Workflow 5: Reviewa AI-genererade Knowledge Objects

## Utgångsläge

AI har producerat kandidater.

## Användarens arbete

För varje kandidat kan användaren:

* acceptera,
* redigera och acceptera,
* avvisa,
* skjuta upp.

Vid avvisning kan användaren frivilligt ange anledning:

* irrelevant,
* trivial,
* felaktig,
* överdriven,
* redan känd,
* annat.

## Systemets arbete

Dokumentverkstad bevarar:

* AI:s originalförslag,
* användarens eventuella redigering,
* review-beslut,
* tidpunkt,
* avvisningsorsak,
* proveniens.

## Beständigt resultat

Accepterade Knowledge Objects blir del av kunskapsrummet.

Avvisade kandidater bevaras endast i den omfattning som behövs för historik och självobservation.

---

# Workflow 6: Koppla kunskap till projekt och andra objekt

## Utgångsläge

Ett Knowledge Object finns i kunskapsrummet.

## Utlösande handling

Användaren väljer att skapa en koppling.

## Användarens arbete

Användaren kan exempelvis:

* lägga Knowledge Object i ett Project,
* koppla det till ett Document,
* koppla det till ett annat Knowledge Object,
* ange att två objekt "hör ihop".

Användaren behöver inte ange exakt semantisk relation.

## Systemets arbete

Dokumentverkstad skapar och sparar relationen med:

* objekt A,
* objekt B,
* skapare,
* tidpunkt,
* eventuell fritext,
* eventuell confidence.

## Beständigt resultat

Kunskapsrummet blir rikare utan att objekten dupliceras.

---

# Workflow 7: Kasta och återställa

## Utgångsläge

Användaren bedömer att ett Document, Knowledge Object eller Project inte längre behövs.

## Utlösande handling

Användaren väljer:

> Kasta

## Systemets arbete

Objektet flyttas till Trash.

Det raderas inte permanent.

Systemet registrerar:

* tidpunkt,
* ursprunglig plats,
* planerat datum för permanent radering.

## Användarens möjligheter

Under 30 dagar kan användaren:

* återställa objektet,
* radera det permanent tidigare.

Efter 30 dagar kan Dokumentverkstad radera objektet permanent enligt konfiguration.

## Beständigt resultat

Irreversibel radering sker aldrig direkt genom ett vanligt användarbeslut.

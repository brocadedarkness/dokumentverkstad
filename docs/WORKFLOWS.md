# Arbetsflöden för Dokumentverkstad

## Syfte

Detta dokument beskriver arbetsflöden med kodstöd i v0.1.0. Rapporterad driftverifiering finns i DEPLOYMENT.md; framtida produktmål finns i ROADMAP.md.

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

Användaren laddar upp PDF via webbgränssnittet eller placerar en färdig fil i konfigurerad Ingest Source.

## Systemets arbete

Dokumentverkstad:

1. köar webbuppladdningen eller upptäcker en PDF i ingestkatalogen,
2. låter workern hämta filen för bearbetning,
3. kopierar den till lokal staging,
4. beräknar checksumma,
5. kontrollerar om filen redan är registrerad,
6. skapar ett Document-ID,
7. arkiverar originalfilen,
8. extraherar teknisk och tillgänglig bibliografisk metadata,
9. extraherar text om möjligt,
10. registrerar dokumentet i indexet.

Ingest väntar inte på att en externt kopierad fil är färdigskriven.
Överföringen måste därför publicera färdiga PDF:er i kön. Uploadsvaret
bekräftar endast köning. Dubbletter skapar inget nytt Document.
Bearbetningsfel flyttar filen till `ingest_source/failed` med felinformation;
workern fortsätter med andra filer. OCR ingår inte.

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

Webbformuläret erbjuder titel, upphov och år. Datamodellen har även fält
för upplaga, språk och kommentar, men de exponeras inte i detta formulär.

## Systemets arbete

Dokumentverkstad:

1. skapar ett Document-ID,
2. sparar metadata,
3. markerar att ingen originalfil finns,
4. gör dokumentet tillgängligt för Knowledge Objects och Projects.

## Beständigt resultat

Ett Document finns i kunskapsrummet utan digital originalfil.

Att senare koppla en digital originalfil till ett befintligt manuellt Document saknar användarflöde i v0.1.0.

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
5. sparar noteringen med semantisk typ `unknown`; UI:t erbjuder ingen typklassificering.

## Beständigt resultat

Tanken är bevarad med minsta möjliga friktion.

Innehåll och källposition kan redigeras med bevarad historik. Sparande kräver serverkontakt; offline och konfliktskydd finns inte i v0.1.0.

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

1. kontrollerar att extraherad text finns och kan användas,
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

* godkänna molnbehandling och köa den samlade analysen,
* lämna bekräftelsesidan utan att starta.

Enskilda capabilities kan inte väljas bort i v0.1.0. Ett redan köat jobb
har inget avbrytflöde i UI:t.

## Systemets arbete efter godkännande

Workern kör det planerade jobbet även om klienten stängs. AI-resultaten sparas som kandidater med:

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

Efter körningen visas kostnad beräknad från rapporterade token och kodens pristabell, inte en leverantörsfaktura. Ladda om dokumentvyn för status och resultat. Misslyckade jobb sparas som `failed`; avbrutna `running`-jobb markeras som misslyckade vid workerstart. Dubbla startanrop spärras inte i v0.1.0.

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

Även avvisade kandidater bevaras i Archive med originalförslag och historik; ingen automatisk gallring görs. Projektförslag har ett separat flöde för att koppla dokumentet till ett befintligt projekt eller avvisa, inte samma acceptansflöde som övriga kandidater.

---

# Workflow 6: Koppla kunskap till projekt och andra objekt

## Utgångsläge

Ett Knowledge Object finns i kunskapsrummet.

## Utlösande handling

Användaren väljer att skapa en koppling.

## Användarens arbete

Användaren kan exempelvis:

* lägga Knowledge Object i ett Project,
* skapa en notering med Document-koppling från dokumentvyn,
* koppla det till ett annat Knowledge Object,
* ange att två objekt "hör ihop".

Användaren behöver inte ange exakt semantisk relation.

## Systemets arbete

Dokumentverkstad skapar och sparar relationen med:

* objekt A,
* objekt B,
* relationstypen "hör ihop med",
* tidpunkt,
* eventuell kommentar.

Detta gäller relationer mellan KO. Projektkopplingar sparas i objektets
`project_ids`. Befintliga noteringar kan inte fritt kopplas om till andra
Documents via redigeringsformuläret.

## Beständigt resultat

Kunskapsrummet blir rikare utan att objekten dupliceras.

---

# Workflow 7: Kasta och återställa

## Utgångsläge och handling

Användaren väljer Kasta för ett Document i Inbox. Borttagning av Knowledge
Objects och Projects finns inte i v0.1.0.

## Systemets arbete

Document får status `trashed` i sin metadata och visas i Trash. Originalfil
och övrig data flyttas inte till en separat fysisk papperskorg.

## Användarens möjligheter

Från Trash kan användaren återställa dokumentet till status `new` och Inbox.
Identiteten behålls. Permanent radering kräver uttrycklig bekräftelse och
blockeras om det finns kopplade Knowledge Objects eller AI runs.

Ingen 30-dagarstimer eller automatisk permanent radering finns. Dokument
ligger kvar tills de återställs eller kan raderas manuellt. Det finns inget
separat flöde för att bara ta bort originalfilen.

## Beständigt resultat

Återställning bevarar befintligt dokument och dess kopplingar. Tillåten
permanent radering tar bort dokumentkatalogen.

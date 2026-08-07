# UI för Dokumentverkstad

## Syfte

Detta dokument beskriver hur användaren arbetar i Dokumentverkstads webbgränssnitt.

Gränssnittet ska organiseras efter användarens arbete, inte efter systemets interna objektmodell.

UI:t ska stödja fyra huvudsakliga arbetslägen:

* Capture
* Inbox
* Document
* Project

Övriga funktioner, som sök, historik, export och inställningar, är stödjande och behöver inte vara egna huvudvyer.

---

# Grundläggande UI-principer

## Arbete före presentation

Gränssnittet ska visa det användaren behöver arbeta med.

Dokumentverkstad behöver inte presentera sitt namn, sitt varumärke eller sin egen aktivitet i onödan.

Systemet ska träda tillbaka.

---

## Persistenta arbetslägen

Vanliga arbetslägen ska kunna ligga öppna medan användaren arbetar.

Användaren ska inte behöva öppna nya dialogrutor eller fönster för varje handling.

Om användaren arbetar i Capture ska Capture förbli aktivt efter att en notering sparats.

Om användaren arbetar i Inbox ska nästa objekt vara omedelbart tillgängligt efter ett beslut.

---

## Minimera kognitiv kostnad

Det ska vara enklare att fånga en tanke än att klassificera den.

Metadata, semantisk typ, källprecision och relationer ska kunna förbättras senare.

Gränssnittet ska aldrig kräva mer precision än användaren har.

---

## Visa beslut, inte all information

Information ska visas när den hjälper användaren att fatta ett beslut.

Detaljer som proveniens, historik och AI-metadata ska alltid vara tillgängliga men behöver inte dominera huvudvyn.

---

## Progressiv komplexitet

En enkel handling ska vara enkel.

Avancerade funktioner ska framträda först när användaren behöver dem.

---

# Huvudnavigation

Dokumentverkstad har fyra primära arbetsytor:

```text
Capture
Inbox
Document
Project
```

De motsvarar fyra typer av arbete:

```text
Capture
→ fånga

Inbox
→ sortera och fatta beslut

Document
→ fördjupa förståelsen av en källa

Project
→ syntetisera och orientera sig i ett kunskapsområde
```

Sökning är global och tillgänglig från alla arbetsytor, men är inte i första versionen en egen huvudyta.

---

# Capture

## Syfte

Capture används för att fånga tankar med minsta möjliga friktion.

Capture är ett arbetsläge, inte en dialogruta.

## Grundvy

Capture ska i sin enklaste form bestå av:

* ett permanent textfält,
* tydlig spara-funktion,
* lista över de senaste noteringarna,
* aktuellt sammanhang när sådant finns.

Exempel:

```text
Capture

[ skriv här...                         ]

Spara

Senaste noteringar
• Påminner om North
• Är detta Gibson eller Hegel?
• s. 143 verkar motsäga s. 112
```

Efter att en notering sparats:

* textfältet töms,
* fokus återgår till textfältet,
* användaren kan omedelbart skriva nästa notering.

Ingen omladdning eller ny dialog krävs.

---

## Capture-context

Capture kan arbeta i ett sammanhang.

Exempel:

```text
Aktuellt dokument:
Andens fenomenologi

Aktuellt projekt:
Rävfilosofi
```

Nya noteringar kan automatiskt föreslås kopplas till detta sammanhang.

Användaren ska enkelt kunna ändra eller ta bort kopplingen.

---

## Markdownliknande syntax

Capture ska kunna utvecklas mot ett enkelt markdownliknande arbetssätt.

Version 1 behöver endast stödja vanlig text eller enkel Markdown.

Senare kan specialsyntax införas, exempelvis:

```text
@North
@Andens fenomenologi
```

för referenser till Documents eller Knowledge Objects, och:

```text
#Rävfilosofi
```

för projektkopplingar.

Syntaxen ska vara ett genvägssystem, inte ett krav.

Allt ska fortfarande kunna göras utan specialsyntax.

---

## Kortkommandon

På dator och iPad med tangentbord ska Capture kunna stödja enkla kortkommandon.

Exempel:

```text
Cmd/Ctrl + Enter
→ spara notering
```

Kortkommandon ska komplettera, inte ersätta, synliga kontroller.

---

## Capture ska vara optimerat för snabbt tangentbordsarbete.

Enter sparar den aktuella noteringen.

Shift+Enter infogar en ny rad.

---

# Inbox

## Syfte

Inbox visar arbete som väntar på användarens uppmärksamhet.

Inbox är inte en lista över dokument.

Den är en beslutsyta.

På telefon är Inbox standardsidan.

---

## Inbox kan innehålla

Exempel:

* nytt Document
* AI-genererad Summary
* Candidate Insight
* projektförslag
* saknad metadata
* saknat sekretessbeslut
* Knowledge Object som väntar på review

Version 1 behöver inte implementera alla dessa typer.

---

## Inbox-kort

Varje objekt ska visa endast det som behövs för nästa beslut.

Exempel för ett Document:

```text
Titel

Kort sammanfattning

Possible projects
□ Bibliotekspolitik
□ Institutioner
□ General

Candidate insights
3

[Review]
[Later]
[Discard]
```

---

## Normal Inbox-review

En vanlig review ska kunna genomföras snabbt.

Användaren ska kunna:

* läsa kort sammanfattning,
* välja ett eller flera Projects,
* lämna objektet i General,
* godkänna eller avvisa AI-förslag,
* skjuta upp,
* kasta.

Användaren ska inte behöva öppna detaljer om de inte behövs.

---

## Inbox på telefon

Telefonversionen prioriterar:

* kort sammanfattning,
* projektkoppling,
* accept/reject,
* later,
* discard.

Avancerad redigering och historik behöver inte vara lika lättillgänglig.

Efter ett beslut ska nästa Inbox-objekt visas direkt.

Inbox ska kännas mer som triage än dokumentadministration.

---

# Document

## Syfte

Document-vyn svarar på frågan:

> Vad har denna källa gett mig?

Document-vyn ersätter inte en PDF- eller EPUB-läsare.

Originalet öppnas separat.

---

## Översikt

Överst visas:

* titel,
* författare när känd,
* år när känt,
* språk,
* eventuell originalfil,
* Projects,
* sekretessstatus,
* möjlighet att öppna originalet.

Metadata ska inte ta över vyn.

---

## Huvudinnehåll

Document-vyn ska kunna visa:

### Kort sammanfattning

En snabb orientering i dokumentets innehåll.

### Knowledge Objects

Noteringar, insights, claims och questions som är kopplade till dokumentet.

De ska inte behöva separeras hårt efter semantisk typ.

### Candidate Objects

AI-genererade objekt som fortfarande väntar på review.

### Open Threads

Frågor eller problem som är kopplade till dokumentet.

### Relationer

Andra Documents eller Knowledge Objects som hör ihop med detta dokument.

### Historik

Tillgänglig vid behov.

---

## Notering från Document-vyn

Document-vyn ska ha enkel tillgång till Capture med det aktuella dokumentet som aktivt context.

Användaren ska kunna skriva:

```text
Detta liknar North.
```

och spara utan att lämna Document-arbetet.

---

# Project

## Syfte

Project-vyn svarar på frågan:

> Vad vet jag om detta problem eller område?

Ett Project är ett perspektiv på kunskapsrummet, inte en mapp.

---

## Project-vyn kan visa

* projektets korta beskrivning,
* senaste Knowledge Objects,
* centrala Knowledge Objects,
* Documents som är relevanta,
* Open Threads,
* relationer,
* förändringar sedan föregående besök,
* projektsammanfattning när sådan finns.

---

## Project som arbetscontext

Ett Project kan vara aktivt.

När ett Project är aktivt kan:

* nya Capture-noteringar föreslås höra dit,
* Inbox filtreras till relevanta objekt,
* Document-vyer visa projektets relevanta Knowledge Objects först.

Användaren ska kunna arbeta "i" ett Project utan att projektet blir en hård behållare.

---

## Syntes

Senare versioner kan erbjuda AI-genererade projektsynteser.

Sådana synteser ska vara Knowledge Objects och granskas på samma sätt som annan AI-genererad kunskap.

---

# General

General är inte en egen primär arbetsyta.

General är hela kunskapsrummet.

Om användaren behöver en övergripande vy kan den skapas genom filtrering och listning över hela kunskapsrummet.

Systemet ska undvika att skapa en separat "General"-behållare som konkurrerar med Projects.

---

# Listningar och filtrering

I första versionen är listning och filtrering viktigare än avancerad sökning.

Documents, Knowledge Objects och Projects ska kunna listas och filtreras.

Exempel på Document-filter:

* Project
* författare
* år
* språk
* dokumenttyp
* har AI-analys
* saknar AI-analys
* saknar metadata

Exempel på Knowledge-filter:

* Project
* skapare
* semantisk typ
* review-status
* kopplat Document
* datum

Filter ska kunna kombineras utan att användaren behöver formulera avancerade sökfrågor.

---

# Sökning

Global sökning ska finnas men behöver inte vara avancerad i första versionen.

Den ska kunna söka i:

* Document metadata,
* extraherad dokumenttext,
* Knowledge Objects,
* Project-namn och beskrivningar.

Sökning ska senare kunna utvecklas mot semantisk sökning utan att UI:t behöver byggas om.

---

# Proveniens och AI-identitet

UI:t ska tydligt kunna visa vem eller vad som skapat ett Knowledge Object.

Exempel:

```text
Anders
AI – OpenAI / modell X
Anders, redigerad från AI-förslag
```

Denna information ska vara synlig vid behov men behöver inte dominera varje kort eller listning.

AI-genererade kandidater ska alltid vara tydligt identifierbara som kandidater.

---

# Confidence och Source Precision

Confidence och Source Precision ska presenteras tydligt men enkelt.

Systemet ska undvika falsk exakthet.

Exempel:

```text
Confidence: hög
Källa: dokument
```

eller:

```text
Confidence: medel
Källa: s. 35–36
```

Mer detaljerad information kan visas vid begäran.

---

# E-ink

UI:t ska vara användbart i e-ink-webbläsare.

Det innebär bland annat:

* hög kontrast,
* inga nödvändiga animationer,
* ingen funktionalitet beroende av hover,
* inga viktiga färgkodningar utan textetikett,
* begränsade dynamiska omladdningar,
* tydliga knappar och länkar.

---

# Responsivitet

Samma grundläggande UI ska fungera på dator, iPad och telefon.

Arbetsytorna anpassas efter skärmstorlek snarare än att implementeras som separata appar.

## Telefon

Prioriterar:

* Inbox
* Capture
* snabb Document-översikt

## iPad

Prioriterar:

* Capture
* Inbox
* Document
* Project

Kan använda mer yta för parallell information.

## Desktop

Kan visa fler paneler samtidigt och ge enklare tillgång till:

* historik,
* avancerad filtrering,
* export,
* administration.

---

# Vad UI:t inte ska göra

Version 1 ska undvika:

* dashboards,
* knowledge graph-visualisering som huvudgränssnitt,
* tung drag-and-drop,
* omfattande modaler,
* animationer,
* chatt som primär interaktion,
* automatisk pop-up-hjälp,
* onödig AI-personifiering.

---

# Avslutning

Dokumentverkstads UI ska fungera som en arbetsmiljö för läsning och tänkande.

De viktigaste arbetsytorna är:

```text
Capture
Inbox
Document
Project
```

Capture fångar tanken.

Inbox hjälper användaren att fatta beslut.

Document fördjupar förståelsen av en källa.

Project hjälper användaren att orientera sig i och syntetisera ett kunskapsområde.

Gränssnittet ska minimera avbrott och låta användaren fortsätta arbeta med så liten friktion som möjligt.

# Domänmodell för Dokumentverkstad

## Syfte

Detta dokument beskriver de grundläggande begrepp som existerar i Dokumentverkstad och relationerna mellan dem.

Domänmodellen är oberoende av implementation. Den beskriver inte databastabeller, API:er eller programmeringsspråk, utan den begreppsvärld som systemet modellerar.

När implementationen förändras ska domänmodellen i huvudsak kunna förbli densamma.

---

# Grundläggande ontologi

Dokumentverkstad bygger på en enkel ontologisk uppdelning mellan tre typer av objekt.

## Externa objekt

Externa objekt existerar utanför Dokumentverkstad och produceras inte av systemet.

Den första och viktigaste typen är:

* **Document**

Dokumentverkstad bevarar dokument, analyserar dem och använder dem som källor, men producerar dem aldrig.

---

## Interna objekt

Interna objekt produceras genom användarens arbete, AI:s bearbetning eller samspelet mellan dem.

Den grundläggande typen är:

* **Knowledge Object**

Knowledge Objects utgör Dokumentverkstads interna kunskapsbas.

---

## Relationella strukturer

Den tredje kategorin består av strukturer som organiserar kunskapsrummet.

Den viktigaste typen är:

* **Project**

Projekt producerar inte kunskap.

De organiserar och avgränsar delar av kunskapsrummet för ett visst syfte.

---

# Kunskap uppstår genom interaktion

Dokument innehåller inte färdiga kunskapsobjekt.

Kunskapsobjekt uppstår genom interaktionen mellan en källa och en aktör.

Aktören kan vara:

* en människa,
* en AI,
* eller ett samspel mellan båda.

Samma dokument kan därför ge upphov till olika Knowledge Objects vid olika tidpunkter.

Kunskap betraktas inte som något som extraheras ur dokument utan som något som stabiliseras genom bearbetning.

---

# Document

## Definition

Ett **Document** är en identifierbar extern källa till kunskap som registreras och bevaras i Dokumentverkstad.

Ett Document kan motsvara exempelvis en digital fil, en fysisk bok, en tryckt artikel eller annat avgränsat källmaterial.

Ett Document kan, men behöver inte, ha en kopplad originalfil.

Dokument kan registreras på två sätt:

* automatiskt genom att en fil tas emot av Dokumentverkstad,
* manuellt genom att användaren anger grundläggande metadata.

En originalfil kan läggas till senare till ett manuellt registrerat Document. Metadata och källkopplingar kan på motsvarande sätt kompletteras och förbättras över tid.

Dokumentverkstad producerar eller förändrar aldrig själva källmaterialet.

## Ansvar

Document ansvarar för:

* den kopplade originalfilen, när en sådan finns,
* dess identitet,
* dess metadata,
* att fungera som källa.

Document ansvarar inte för:

* sammanfattningar,
* claims,
* insights,
* frågor,
* användarens förståelse.

## Livscykel

Ett Document:

* registreras automatiskt eller manuellt,
* kan få en originalfil vid registreringen eller senare,
* arkiveras,
* analyseras,
* kan knytas till Knowledge Objects,
* kan återställas från papperskorgen,
* kan raderas.

Själva dokumentets innehåll förändras inte av Dokumentverkstad.

## Relationer

Ett Document kan:

* fungera som källa för ett eller flera Knowledge Objects,
* relateras till andra dokument,
* förekomma i flera projekt genom sina relationer till Knowledge Objects.

---

# Knowledge Object

## Definition

Ett **Knowledge Object** är en beständig representation av en stabiliserad tanke.

Knowledge Objects utgör Dokumentverkstads interna kunskapsbas.

De produceras av användaren, AI eller genom samspel mellan båda.

Knowledge Objects kan bygga på en eller flera källor men kan också uppstå utan en direkt dokumentkälla.

## Ansvar

Knowledge Objects ansvarar för att representera och bevara kunskap som vuxit fram genom arbetet i Dokumentverkstad.

De kan:

* omprövas,
* utvecklas,
* relateras till andra Knowledge Objects,
* tillhöra flera projekt,
* få nya källor över tid.

## Livscykel

Knowledge Objects föds ofta som enkla noteringar.

Deras semantiska typ behöver inte vara bestämd när de skapas.

De kan därefter utvecklas genom:

* redigering,
* AI-förslag,
* nya relationer,
* förbättrad källkoppling,
* ökad source precision,
* omklassificering.

Kunskap betraktas därför som något som mognar snarare än något som klassificeras färdigt från början.

## Semantisk typ

Ett Knowledge Object kan ha en semantisk typ.

Exempel är:

* Summary
* Claim
* Insight
* Question

Den semantiska typen beskriver hur objektet bäst förstås vid en given tidpunkt.

Den är inte en del av objektets identitet och kan förändras över tid.

Systemet kan föreslå en semantisk typ, men användaren behöver inte ta ställning till den när objektet skapas.

## Relationer

Knowledge Objects kan relateras till:

* Documents,
* andra Knowledge Objects,
* Projects.

---

# Project

## Definition

Ett **Project** är ett perspektiv på Dokumentverkstads kunskapsrum.

Projekt producerar inte kunskap.

De organiserar och avgränsar delar av kunskapsrummet för ett visst syfte.

Det finns inget särskilt objekt för "General". General utgör hela kunskapsrummet, medan projekt är utsnitt av detta.

## Ansvar

Projekt ansvarar för:

* organisation,
* fokus,
* sammanhang.

Projekt ansvarar inte för innehållet.

## Livscykel

Projekt kan:

* skapas,
* byta namn,
* arkiveras,
* återaktiveras,
* slås samman,
* tas bort.

Knowledge Objects består även om projekt förändras.

## Relationer

Knowledge Objects kan tillhöra:

* inget projekt,
* ett projekt,
* flera projekt.

---

# Relation

## Definition

En **Relation** beskriver att två objekt i Dokumentverkstad hör ihop.

Relationer ansvarar för sammanhang, inte för innehåll.

Version 1 använder en medvetet enkel relationsmodell.

Systemet behöver inte från början förstå exakt hur två objekt hänger ihop.

Det räcker att de gör det.

Semantisk precision kan tillföras senare om den visar sig användbar.

## Ansvar

Relationer:

* kopplar samman objekt,
* gör kunskapsrummet navigerbart,
* kan utvecklas och förtydligas över tid.

---

# Gemensamma egenskaper

## Proveniens

Alla Knowledge Objects och Relationer ska bära information om sin proveniens.

Proveniens beskriver hur ett objekt kom till.

Den omfattar bland annat:

* skapare,
* skapandetid,
* AI-modell och version (om relevant),
* historik över senare bearbetningar.

Proveniens beskriver ursprung, inte sanningshalt.

---

## Historik

Kunskap skrivs inte över.

Den utvecklas.

Knowledge Objects och Relationer ska därför kunna bevara tidigare versioner.

Historiken utgör en del av kunskapen.

Det ska alltid vara möjligt att förstå hur ett objekt har förändrats över tid.

---

## Source Precision

När ett Knowledge Object bygger på en källa kan kopplingen beskrivas med olika grad av precision.

Precisionen kan förbättras över tid.

Exempel på ökande precision är:

* okänd källa,
* dokument,
* kapitel eller avsnitt,
* sida,
* stycke,
* specifikt textutdrag.

Systemet ska aldrig kräva högre precision än vad användaren eller AI faktiskt känner till.

---

## Review

Nya Knowledge Objects betraktas som arbetsmaterial tills de har granskats.

Review syftar inte till att avgöra om ett objekt är sant.

Review syftar till att:

* förbättra formuleringen,
* stärka proveniensen,
* förbättra source precision,
* föreslå relationer,
* föreslå semantisk typ,
* eller avvisa objekt som inte längre bedöms vara värdefulla.

Review är en del av kunskapsbildningen, inte en kvalitetskontroll.

---

# Begrepp som inte modelleras

Följande begrepp förekommer i Dokumentverkstads beskrivning men modelleras inte som egna domänobjekt i version 1:

* Annotation
* Note
* General
* Source
* Work
* Manifestation

De betraktas istället som:

* arbetsmoment,
* perspektiv,
* roller,
* eller egenskaper hos andra objekt.

---

# Sammanfattning

Dokumentverkstad bygger på fyra centrala begrepp:

* **Document** – den externa källan.
* **Knowledge Object** – den interna, beständiga representationen av en stabiliserad tanke.
* **Relation** – sambandet mellan objekt.
* **Project** – ett perspektiv på kunskapsrummet.

Övriga begrepp i systemet är egenskaper, arbetsflöden eller processer kring dessa fyra grundobjekt.

Domänmodellen ska hållas så liten som möjligt. Nya objekt ska endast införas när de beskriver ett verkligt begrepp i användarens arbete och inte kan uttryckas enklare genom befintliga objekt eller relationer.

# Dokumentverkstad – Design System

## 1. Syfte och status

Detta dokument beskriver Dokumentverkstads visuella språk, grundläggande interaktionsprinciper och återkommande mönster för gränssnittet.

Designsystemets syfte är att göra Dokumentverkstad till ett sammanhängande arbetsinstrument. Nya vyer och funktioner ska inte behöva uppfinna ett eget visuellt språk, och befintliga vyer ska successivt kunna föras in i samma system.

Dokumentet är normerande för gränssnittets design, men är inte en pixel-specifikation. Exakta mått, brytpunkter och tekniska lösningar får utvecklas under implementation och verklig användning så länge de följer principerna här.

Designsystemet är ett levande dokument. Det får förändras när verklig användning visar att en regel skapar friktion eller när nya behov kräver att systemet utvecklas.

### 1.1 Förhållande till andra dokument

`IMPLEMENTATION_PLAN.md` beskriver ****vad som ska byggas och i vilken ordning****.

`DESIGN_SYSTEM.md` beskriver **hur gränssnittet ska organisera, uttrycka och presentera det som byggs**.

Designskisserna i `docs/design/` är visuella referenser som konkretiserar designsystemets riktning.

Designskisserna är inte bindande wireframes eller specifikationer av domänmodellen. De innehåller idéer och funktioner från olika stadier i

Dokumentverkstads utveckling och ska därför inte implementeras bokstavligt.

När källorna står i konflikt gäller följande:

1. den aktuella domänmodellen avgör vilka begrepp och relationer som finns,
2. implementationsplanen avgör vilken funktionalitet som ska implementeras,
3. designsystemet avgör hur denna funktionalitet ska organiseras och uttryckas,
4. designskisserna används som visuell referens.

Ett element ska alltså inte införas enbart därför att det förekommer i en designskiss.

### 1.2 Design och funktion

Design är inte ett dekorativt lager ovanpå Dokumentverkstad.

Informationsarkitektur, navigation, typografi, layout, färg, återkoppling och interaktion är delar av hur systemet fungerar.

En designförändring ska därför i första hand:

- minska friktion,
- förbättra orientering,
- göra information lättare att förstå eller överblicka,
- tydliggöra möjliga handlingar,
- eller göra längre arbete i systemet lugnare och mer behagligt.

Estetisk konsekvens har ett värde i sig, men får inte användas som skäl för att göra ett arbetsflöde sämre.

---

## 2. Designidentitet

Dokumentverkstad är ett personligt kunskapsarkiv och ett arbetsinstrument.

Det ska inte i första hand kännas som en konventionell webbapplikation, administrationspanel eller SaaS-produkt. Det ska kännas som en plats där dokument, kunskap och egna tankar samlas, granskas och bearbetas över lång tid.

Det visuella språket förenar:

- modernistisk informationsdesign,
- bibliotek och arkiv,
- dokumentation och katalogsystem,
- återhållsam retrofuturism,
- geometrisk och diskret ockult symbolik.

Resultatet får vara särpräglat.

Dokumentverkstad behöver inte efterlikna ett generiskt produktgränssnitt för att uppfattas som modernt eller användbart. Dess identitet är en del av upplevelsen av ett personligt och långlivat kunskapsrum.

Samtidigt ska identiteten vara återhållsam. Dokumenten och kunskapen är viktigare än gränssnittet omkring dem.

### 2.1 Ett alternativt informationssystem

En användbar visuell föreställning är ett informationssystem ur en alternativ modernistisk tradition: precist, systematiskt och rationellt, men med en symbolvärld och kulturell identitet som inte har reducerats till neutral företagsdesign.

Det får finnas något lätt främmande i Dokumentverkstad.

Maskinella beteckningar, geometriska tecken, arkivmässig typografi och ovanliga historiska referenser får bidra till denna känsla.

De ska dock användas med precision.

Det främmande får aldrig göra systemet svårbegripligt.

### 2.2 Arkiv, inte arkivpastisch

Dokumentverkstad får hämta visuella associationer från bibliotek, arkivförteckningar, katalogkort, teknisk dokumentation och äldre informationssystem.

Det ska däremot inte försöka se gammalt ut.

Undvik exempelvis:

- artificiellt åldrat papper,
- pergamentestetik,
- simulerade tryckfel,
- dekorativa sigill,
- överdriven skrivmaskinsnostalgi,
- historiserande ornament utan funktion.

Ivory, typografi och arkivmässiga etiketter ska skapa en materiell känsla utan att gränssnittet imiterar ett historiskt föremål.

### 2.3 Ockultism genom struktur

Den ockulta dimensionen ska framför allt finnas i systemets geometri, symbolik och identitet.

Cirkel, triangel, romb, kvadrat, stjärna och andra enkla geometriska former kan bilda ett återkommande visuellt alfabet. Dokumentverkstads symbol och devis kan ge systemet ytterligare identitet.

Detta ska vara en underström, inte ett tema.

Undvik ockulta illustrationer eller ornament som inte fyller någon funktion.

Gränssnittet ska aldrig likna ett rollspel, ett tarotprogram eller en esoterisk webbplats.

### 2.4 Språk och identitet

Det huvudsakliga användarspråket ska vara tydligt och funktionellt.

Ett annat språkligt eller historiskt register får användas mycket sparsamt som identitetsbärande inskription eller devis, exempelvis den kyrkslaviska undertiteln i designreferenserna.

Sådana element behöver inte förklara systemets funktion. Deras roll är identitet, ungefär som en inskription på en byggnad eller ett exlibris.

Kontroller, instruktioner, felmeddelanden och annan information som användaren måste förstå för att kunna arbeta ska däremot inte göras gåtfulla av estetiska skäl.

---

## 3. Designprinciper

### 3.1 Innehållet är huvudpersonen

Dokumentverkstad finns för det som finns i kunskapsrummet:

- Documents,
- Captures,
- Knowledge Objects,
- Projects,
- metadata och relationer som hjälper användaren att förstå dem.

Gränssnittet ska rama in detta innehåll snarare än konkurrera med det.

När användaren läser ett Document eller en Capture ska den visuella uppmärksamheten i första hand ligga på innehållet.

Systemstatus, navigation och metadata ska vara lätta att hitta utan att ständigt kräva uppmärksamhet.

### 3.2 Arbetsyta före dashboard

Dokumentverkstad är en plats där användaren gör saker:

- hittar,
- läser,
- granskar,
- tänker,
- fångar,
- organiserar,
- återvänder.

Det är inte i första hand en dashboard över Dokumentverkstad själv.

Statistik, systemstatus och administrativa uppgifter ska därför inte dominera normala arbetsytor. Information som `235 dokument` kan hjälpa orienteringen; information som endast beskriver systemet ska visas först när den fyller en funktion.

En vy ska i första hand hjälpa användaren vidare i det arbete som förde honom dit.

### 3.3 Linjer före lådor

Struktur ska i första hand skapas genom:

- typografisk hierarki,
- alignment,
- whitespace,
- kolumner,
- tunna linjer,
- återkommande rytm.

Undvik att göra varje informationsenhet till ett eget kort.

En lista över Documents ska i första hand uppfattas som en sammanhängande förteckning, inte som en samling fristående widgets.

Paneler, ramar och bakgrunder får användas när de uttrycker en verklig strukturell skillnad, men inte som standardlösning för gruppering.

### 3.4 Tätt men lugnt

Dokumentverkstad är informationsrikt och får vara informationsrikt.

Målet är inte maximal mängd tomrum eller minsta möjliga mängd information på skärmen. Målet är hög informationsdensitet utan visuell stress.

Det kräver:

- konsekvent alignment,
- tydlig hierarki,
- återkommande spacing,
- begränsad färganvändning,
- tillräckligt radavstånd,
- tydlig skillnad mellan primär och sekundär information.

En desktopvy får visa mycket samtidigt om användaren snabbt kan förstå vad som är viktigt.

Luft ska användas för struktur, inte som dekoration.

### 3.5 Färg är signal

Färgpaletten ska vara liten.

Ivory bildar rummet.

Ebony bär huvuddelen av informationen och strukturen.

Cinnabar är signal.

Cinnabar ska därför inte användas för att "göra sidan mer färgglad". När den förekommer ska användaren kunna lära sig att färgen betyder något: exempelvis aktivt tillstånd, status, identitet, orientering eller en viktig handling.

Om allt är accentuerat är ingenting accentuerat.

### 3.6 Geometri är språk

Geometriska former är en del av Dokumentverkstads visuella grammatik.

När en symbol används för att representera en viss typ eller funktion ska betydelsen vara stabil inom gränssnittet.

Symboler får användas för att:

- skapa igenkänning,
- skilja typer eller tillstånd,
- stödja navigation,
- förstärka hierarki.

De får inte användas som godtycklig dekoration.

Textetiketter ska användas när en symbol ensam inte ger tillräcklig begriplighet.

### 3.7 Systemet får ha personlighet

Dokumentverkstad är ett personligt system och behöver inte se ut som om det vore designat för den största möjliga anonyma användargruppen.

Logotypen, den begränsade paletten, geometrin, arkivreferenserna, maskinella etiketter och den sparsamma historiska devisen får tillsammans skapa en stark egen identitet.

Den identiteten ska inte automatiskt tas bort därför att en mer generisk lösning är vanligare i moderna webbapplikationer.

Det finns inget egenvärde i neutralitet.

### 3.8 Funktion före pastisch

Personligheten får aldrig bli ett hinder.

Läsbarhet, tillgänglighet, begriplighet och effektiv interaktion har företräde framför stilistisk renlärighet.

En kontroll ska kännas som en kontroll.

Ett fel ska gå att förstå.

Ett aktivt tillstånd ska gå att urskilja.

Lång text ska vara behaglig att läsa.

På små skärmar ska funktioner prioriteras efter användning, inte efter hur symmetriskt en desktopdesign kan skalas ned.

### 3.9 Progressiv komplexitet

Dokumentverkstad får innehålla avancerade funktioner utan att visa hela sin komplexitet hela tiden.

Vanliga handlingar ska ligga nära till hands.

Mer sällan använda funktioner kan finnas ett steg längre bort.

Metadata, tekniska detaljer, historik och avancerade relationer ska kunna upptäckas när de behövs utan att varje arbetsyta belastas av dem permanent.

Detta är särskilt viktigt eftersom kunskapsrummet förväntas bli mer komplext över tid.

### 3.10 Capture first, organize later

Designen ska stödja Dokumentverkstads princip:

> Capture first, organize later.

Det ska vara lättare att fånga en tanke än att klassificera den.

Gränssnittet får inte kräva Project, typ, relation eller annan organisering innan en Capture kan sparas, om inte sådan information faktiskt är nödvändig.

Organisation kan erbjudas i sammanhang där den hjälper, men ska inte skapa friktion i själva fångstögonblicket.

### 3.11 Visuell kontinuitet över tid

Dokumentverkstad är avsett att vara ett långlivat system.

Designsystemet ska därför undvika att vara alltför beroende av kortlivade gränssnittstrender.

Nya komponenter ska i första hand härledas ur systemets etablerade språk: typografi, linjer, geometri, färg och rumslig struktur.

Målet är inte att gränssnittet aldrig ska förändras, utan att det ska kunna utvecklas utan att förlora sin identitet.

## 4. Visuella referenser

De visuella referenserna för designsystemet finns i `docs/design/`.

Följande filer ingår:

- `design-overview.png`
- `documents.png`
- `inbox-mobile.png`

### 4.1 Kanonisk referens

`design-overview.png` är den huvudsakliga visuella referensen.

Den visar tillsammans:

- Dokumentverkstads övergripande identitet,
- desktoplayout,
- huvudnavigation,
- kontextuell sidokolumn,
- Documents-vy,
- Document-vy,
- Projects-vy,
- filterpanel,
- mobil Documents/Inbox-liknande arbetsyta,
- mobil Document-vy.

Den ska i första hand användas för att förstå relationerna mellan typografi, färg, linjer, geometri, informationsdensitet och layout.

`documents.png` är en detaljreferens för desktop. Den gör framför allt Documents- och Document-vyernas typografi, spacing, kolumnstruktur och informationshierarki lättare att studera.

`inbox-mobile.png` är detaljreferens för mobil design och för den senare utvecklingen av Dokumentverkstads identitet, inklusive den historiska devisen.

### 4.2 Referenserna visar ett designspråk

Referenserna ska inte behandlas som skärmbilder av en färdig produkt.

De visar ett designspråk.

Det innebär att följande egenskaper är viktigare att bevara än exakta pixelmått:

- relationen mellan ivory, ebony och cinnabar,
- den starka typografiska hierarkin,
- användningen av tunna linjer istället för kort,
- den höga men ordnade informationsdensiteten,
- geometriska symboler,
- arkivmässiga och maskinella etiketter,
- den tydliga skillnaden mellan kontext och arbetsyta,
- den återhållsamma användningen av accentfärg,
- känslan av ett sammanhängande informationssystem.

En ny vy behöver inte likna någon av referensbilderna till sin exakta komposition. Den ska däremot kunna uppfattas som en del av samma system.

### 4.3 Referenserna är inte domänspecifikationer

Innehållet i designreferenserna speglar olika stadier i Dokumentverkstads utveckling.

Förekomsten av ett objekt, begrepp eller navigationsalternativ i en bild innebär därför inte att det ska implementeras.

Exempelvis får designreferenserna inte i sig användas som grund för att införa:

- globala huvudvyer för Claims, Insights eller Questions,
- taggar,
- nya dokumenttyper,
- nya metadatafält,
- systemräknare,
- aktivitetsflöden,
- nya relationstyper,
- funktioner som inte finns i den aktuella domänmodellen eller
  implementationsplanen.

På motsvarande sätt ska en befintlig funktion inte tas bort därför att den saknas i en designreferens.

Designen ska appliceras på den aktuella produkten, inte återskapa den produkt som råkade föreställas när skissen gjordes.

### 4.4 Referenserna är inte pixel-specifikationer

Exakta värden i bilderna är inte normerande.

Det gäller exempelvis:

- kolumnbredder,
- fontstorlekar,
- marginaler,
- radavstånd,
- ikonstorlekar,
- brytpunkter,
- antal synliga rader,
- höjd på header och navigation.

Sådana värden ska bestämmas under implementation utifrån designsystemets principer och sedan bedömas i en verklig webbläsare.

Det visuella resultatet ska jämföras med referenserna, men en avvikelse är riktig om den förbättrar läsbarhet, responsivitet, tillgänglighet eller arbetsflöde utan att förlora designspråket.

### 4.5 Referenserna får utvecklas

Nya designreferenser kan läggas till när nya typer av arbetsytor behöver utforskas.

En ny referens ska inte automatiskt bli normerande för hela systemet.

Om en ny skiss innebär en förändring av designspråket ska förändringen först formuleras i detta dokument.

`DESIGN_SYSTEM.md` är därmed den långlivade designkällan.

Bilderna är exempel på hur systemet kan ta form.

---

## 5. Färg

Dokumentverkstads färgsystem ska vara litet, stabilt och funktionellt.

Grundpaletten består av tre roller:

- ****ivory**** – rum och bakgrund,
- ****ebony**** – information och struktur,
- ****cinnabar**** – identitet och signal.

Färgpaletten ska inte utökas för att skapa visuell variation.

Nya färger ska endast införas när det finns ett återkommande semantiskt behov

som inte kan uttryckas tydligt genom den befintliga paletten, typografi, geometri eller andra visuella tillstånd.

### 5.1 Ivory – rummet

Ivory är Dokumentverkstads huvudsakliga bakgrund.

Den ska vara varm men återhållsam: tydligt skild från ren skärmvit utan att uppfattas som beige dekoration eller simulerat gammalt papper.

Ivory används för:

- sidbakgrund,
- huvudsakliga arbetsytor,
- sidokolumner,
- formulärytor där ingen annan strukturell skillnad behöver markeras.

Olika delar av gränssnittet ska i första hand skiljas genom linjer, spacing och typografi snarare än genom flera olika bakgrundsfärger.

Ett begränsat antal mycket närliggande ivory-toner får användas när det krävs för exempelvis overlay, hover eller annan subtil separation, men de ska uppfattas som variationer inom samma rum.

Ren vit ska inte vara systemets normala bakgrund.

### 5.2 Ebony – informationen

Ebony är den huvudsakliga informationsfärgen.

Den används för:

- brödtext,
- rubriker,
- metadata,
- symboler,
- linjer,
- formulärkontroller,
- huvuddelen av navigationen.

Ebony behöver inte tekniskt vara absolut svart.

En mycket mörk, lätt mjukare ton kan ge bättre relation till ivory och minska den hårdhet som uppstår med ren svart mot ren vit.

Kontrasten ska samtidigt vara tillräckligt hög för långvarig läsning och god tillgänglighet.

Sekundär information ska i första hand skiljas från primär information genom storlek, vikt, position och typografi. Lägre kontrast får användas sparsamt men ska inte göra metadata svårläst.

### 5.3 Cinnabar – signalen

Cinnabar är Dokumentverkstads accentfärg.

Den har två närbesläktade roller:

1. ****identitet****, och
2. ****signal****.

Som identitetsfärg kan cinnabar förekomma i exempelvis:

- logotypen,
- devisen,
- utvalda systemetiketter,
- sparsamma geometriska detaljer.

Som signalfärg kan den markera exempelvis:

- aktiv navigation,
- valt tillstånd,
- status,
- viktig orientering,
- primära eller särskilt relevanta handlingar.

Cinnabar ska användas sparsamt.

Stora sammanhängande cinnabarytor ska normalt undvikas. Färgen fungerar bäst som linje, text, symbol, punkt eller annan begränsad markering mot ivory.

En sida där cinnabar dominerar visuellt använder sannolikt för mycket accentfärg.

### 5.4 Cinnabar är inte synonymt med fel

Cinnabar får inte automatiskt få samma betydelse som den konventionella UI-färgen röd.

Eftersom cinnabar är Dokumentverkstads identitets- och accentfärg kan den inte samtidigt ensam betyda:

> något har gått fel.

Fel, varningar och destruktiva handlingar måste därför kommuniceras genom mer än färg.

Det kan exempelvis ske genom:

- explicit text,
- symbol,
- typografisk markering,
- ram eller annan geometri,
- kombinationer av dessa.

En destruktiv handling ska vara begriplig som destruktiv även för en användare som inte uppfattar färgen.

### 5.5 Status ska inte kräva en regnbåge

Dokumentverkstad ska inte införa en separat färg för varje systemtillstånd.

Skillnader mellan exempelvis:

- AI-analys saknas,
- AI-analys pågår,
- AI-analys är klar,
- AI-analys har misslyckats,

kan uttryckas genom kombinationer av:

- fylld eller ofylld geometri,
- symbol,
- textetikett,
- cinnabar,
- ebony,
- rörelse när detta är lämpligt för ett pågående tillstånd.

Designreferensernas fyllda och ofyllda cirklar är ett exempel på denna princip.

Systemet ska kunna uttrycka många tillstånd med ett litet visuellt alfabet.

### 5.6 Färg får aldrig bära betydelsen ensam

Ingen viktig skillnad ska kommuniceras enbart genom färg.

Aktiva navigationselement ska exempelvis kunna kännas igen genom en kombination av cinnabar och annan markering, såsom linje, symbol eller typografi.

Status ska kunna förstås genom symbol eller text även om färg inte kan uppfattas.

Detta är både en tillgänglighetsprincip och en del av designsystemets återhållsamhet.

### 5.7 Interaktionstillstånd

Hover, focus, active och selected ska härledas ur grundpaletten.

De ska inte skapa ett separat färgsystem.

Exempel:

- ****hover**** kan markeras genom en diskret förändring av linje, bakgrundston eller text,
- ****focus**** ska ha en tydligt synlig fokusindikator,
- ****active**** ska uttrycka den handling som just utförs,
- ****selected**** ska tydligt visa ett bestående valt tillstånd.

Focus får inte göras subtilt enbart för att bevara estetisk renhet.

Tangentbordsnavigation ska vara visuellt begriplig.

**### 5.8 Overlay och modalitet**

När ett modal- eller filterlager visas får bakgrunden dämpas för att tydliggöra att arbetsytan tillfälligt inte är aktiv.

Dämpningen ska vara neutral och funktionell.

Undvik färgade overlays, blur-effekter och andra effekter som bryter mot systemets grafiska enkelhet.

Designreferensens filterpanel visar den avsedda principen: den aktiva panelen
är tydlig medan den underliggande arbetsytan fortfarande går att orientera sig
i.

### 5.9 Inga gradients

Gradients ska inte användas.

Dokumentverkstads visuella språk bygger på plana ytor, linjer, typografi,
geometri och tydliga relationer.

Djup och hierarki ska skapas strukturellt snarare än genom ljuseffekter.

**### 5.10 Konkreta färgvärden**

De exakta färgvärdena ska fastställas under den första implementationen av designsystemet genom jämförelse med designreferenserna i en verklig webbläsare.

De ska därefter definieras centralt som design tokens, exempelvis:

```css
:root {
    --color-ivory: ...;
    --color-ebony: ...;
    --color-cinnabar: ...;
}
```

Komponenter ska använda dessa semantiska tokens och inte egna hårdkodadevarianter av grundfärgerna.

Vid behov kan ett litet antal härledda tokens införas, exempelvis för:

```css
--color-border: ..*.;*
--color-muted: ..*.;*
--color-surface-subtle: ..*.;*
--color-overlay: ..*.;*
```

Sådana tokens ska härledas ur grundpaletten och fylla en definierad funktion.

De får inte utvecklas till en fristående sekundär färgpalett.

## 6. Typografi

Typografi är ett av Dokumentverkstads viktigaste strukturella verktyg.

Gränssnittet ska inte förlita sig på stora färgytor, kort eller dekorativa komponenter för att skapa hierarki. Skillnaden mellan system, metadata,innehåll och identitet ska därför i stor utsträckning uttryckas typografiskt.

Typografin ska förena två egenskaper:

- precisionen hos ett katalog-, arkiv- eller informationssystem,
- läsbarheten hos en arbetsyta där användaren kan tillbringa lång tid med text.

Designreferenserna visar denna kontrast genom att kombinera maskinell,monospaced eller kondenserad typografi med mer boklik typografi för vissainnehåll och identitetsbärande element.

### 6.1 Typografiska roller

Dokumentverkstad ska utgå från ett litet antal typografiska roller snarare änett stort antal individuella textstilar.

De centrala rollerna är:

1. **identitet och display,**
2. **system och navigation,**
3. **metadata och maskinella etiketter,**
4. **läsinnehåll,**
5. **historisk devis.**

Rollerna får dela typsnitt när detta ger ett bättre och enklare system.

### 6.2 Identitet och display

Dokumentverkstads namn och vissa större rubriker ska ha en tydlig,karaktäristisk typografisk närvaro.

Uttrycket ska vara:

- precist,
- relativt smalt eller kondenserat,
- tydligt,
- modernistiskt,
- mer informationssystem än varumärkeslogotyp.

`DOKUMENTVERKSTAD` ska i första hand uppfattas som namnet på själva apparateneller institutionen, inte som en dekorativ logotyptext.

Versaler och generös teckenmellanrum kan användas där de stödjer detta uttryck.

Stora rubriker ska användas sparsamt. Dokumentverkstad ska inte byggainformationshierarki genom att göra varje sidrubrik mycket stor.

### 6.3 System och navigation

Navigation, kontroller och kortare systemetiketter ska använda en typografisom är tydlig, kompakt och lätt att skanna.

Den får gärna ha ett maskinellt eller tekniskt uttryck.

Exempel på denna typ av text är:

```text
DOCUMENTS
PROJECTS
FILTER
SORTERA PÅ
TILLBAKA TILL LISTAN
AI COMPLETE
```

Versaler kan användas för korta systemetiketter, men ska inte användas förlängre instruktioner eller löpande text.

Systemtypografin ska bidra till känslan av katalog och instrument utan attgöra kontroller svårlästa.

### 6.4 Metadata och maskinella etiketter

Metadata får ha en mer uttalat arkivmässig eller maskinell typografi.

Exempel:

```text
DOC 0241
YR  2025
AI  COMPLETE
CAP 0004
```

Sådana etiketter kan användas för att skapa snabb orientering och en känsla avett konsekvent informationssystem.

De ska dock endast visa information som är meningsfull för användaren.

Interna UUID:n, databasnycklar eller andra implementationstekniska identifierareska inte exponeras bara för att de passar den visuella stilen.

Maskinell typografi är ett presentationsspråk, inte ett skäl att visa internimplementation.

### 6.5 Läsinnehåll

Text som användaren faktiskt ska läsa ska optimeras för läsning.

Det gäller exempelvis:

* Summary,
* Captures,
* Claims,
* Insights,
* Questions,
* längre anteckningar,
* beskrivningar.

Läsinnehåll ska ha:

* bekväm teckenstorlek,
* tillräckligt radavstånd,
* rimlig radlängd,
* tydliga stycken,
* hög kontrast mot bakgrunden.

Längre text ska inte sättas i en typografi enbart därför att den serarkivmässig eller teknisk ut.

Om ett monospaced eller kondenserat typsnitt fungerar väl för systemet mensämre för längre läsning ska läsinnehållet använda ett annat typsnitt.

### 6.6 Dokumenttitlar

Document-titlar befinner sig mellan system och innehåll.

De ska vara tydligt framträdande men inte behandlas som marknadsföringsrubriker.

I listor ska titeln vara den huvudsakliga visuella ingången till ett Document.

Författare eller upphov, undertitel, år och annan metadata ska vara sekundära.

I Document-vyn ska titeln tydligt identifiera arbetsytan utan att taoproportionerligt mycket vertikalt utrymme.

### 6.7 Typografisk hierarki

Hierarki ska skapas genom en kombination av:

* storlek,
* vikt,
* teckenmellanrum,
* versaler/gemener,
* typsnittsroll,
* placering,
* spacing.

Undvik att använda fetstil som enda hierarkiskt verktyg.

Undvik också ett stort antal nästan identiska textstorlekar.

Användaren ska kunna skilja mellan exempelvis:

```text
sidrubrik
sektion
Document-titel
brödtext
metadata
systemetikett
```

### 6.8 Radlängd och läsbarhet

Långa textstycken ska inte automatiskt fylla hela den tillgängliga bredden påstora skärmar.

Document-vyn får använda en bred arbetsyta, men lästext ska ha en begränsad

radlängd när detta förbättrar läsningen.

Metadata, tabeller och listor kan däremot utnyttja större bredd.

Layouten ska alltså kunna skilja mellan:

> utrymme som finns

och:

> optimal bredd för det aktuella innehållet.

### 6.9 Siffror och datum

Dokumentverkstad innehåller många:

* årtal,
* datum,
* antal,
* sidnummer,
* dokumentnummer.

Dessa ska vara lätta att jämföra visuellt.

Där det valda typsnittet stödjer det bör tabulära siffror användas i tabeller,metadata och andra sammanhang där vertikal alignment är viktig.

Datumformat ska vara konsekventa inom samma typ av vy.

Typografisk stil ska inte göra årtal och dokumentnummer svåra att skilja åt.

### 6.10 Den historiska devisen

Den historiska eller kyrkslaviska devisen är ett identitetsbärande element,inte normal systemtext.

Den får därför använda ett separat typsnitt eller typografiskt register.

Dess uppgift är att fungera ungefär som:

* en inskription,
* ett exlibris,
* ett motto,
* en institutionsdevis.

Den ska användas sparsamt, i första hand i anslutning tillDokumentverkstads identitet.

Devisens faktiska text och typografiska form ska fastställas separat ochspråkligt verifieras innan den betraktas som permanent.

Den ska inte användas för navigation, instruktioner eller funktionellaetiketter.

### 6.11 Faktiska typsnitt

Designsystemet ska inte bli beroende av ett stort antal externa fontfiler.

De faktiska typsnitten ska väljas under implementation utifrån:

* visuell överensstämmelse med designreferenserna,
* läsbarhet,
* stöd för svenska tecken,
* stöd för relevanta historiska tecken där detta behövs,
* webbprestanda,
* licens och långsiktig tillgänglighet.

Ett litet antal familjer ska föredras.

Som utgångspunkt bör systemet kunna lösas med:

* en primär system-/displayfamilj,
* eventuellt en separat läsfamilj,
* eventuellt ett särskilt typsnitt för devisen.

När faktiska typsnitt har valts ska de dokumenteras här tillsammans med

fallback-stackar.

### 6.12 Typografiska tokens

Återkommande typografiska värden ska definieras centralt.

Det kan exempelvis omfatta:

```css
--font-system: ..*.;*
--font-reading: ..*.;*
--font-inscription: ..*.;*
--text-display: ..*.;*
--text-heading: ..*.;*
--text-body: ..*.;*
--text-small: ..*.;*
--text-label: ..*.;*
--line-height-body: ..*.;*
```

Tokens ska uttrycka roller snarare än enskilda komponenter.

Undvik exempelvis att skapa separata typografiska system för varje vy om sammaroll kan återanvändas.

## 7. Geometri och symboler

Geometri är ett återkommande visuellt språk i Dokumentverkstad.

Enkla former skapar igenkänning och identitet utan att kräva illustrationereller stora färgytor.

Designreferenserna använder framför allt:

* cirkel,
* triangel,
* romb,
* kvadrat,
* punkt,
* stjärn- eller korsliknande former,
* linjer,
* sammansatta geometriska former i Dokumentverkstads symbol.

Det geometriska språket ska vara precist, sparsamt och konsekvent.

### 7.1 Symboler är ett alfabet

Symbolerna ska betraktas som ett visuellt alfabet.

När en form har fått en semantisk betydelse i den implementerade produkten skaden betydelsen vara stabil.

Om exempelvis en viss form används för en viss Knowledge Object-typ ska sammaform inte samtidigt användas för en orelaterad systemstatus.

Målet är att användaren med tiden ska kunna känna igen formerna utan attbehöva tolka dem på nytt.

### 7.2 Semantik bestäms av produkten

Designreferenserna visar möjliga kopplingar mellan geometriska former och begrepp som Claims, Insights, Questions och Captures.

Dessa kopplingar är inte i sig bindande.

Symbolernas slutliga betydelser ska bestämmas utifrån:

* den aktuella domänmodellen,
* informationsarkitekturen,
* faktisk användning.

Designsystemet ska inte skapa domänbegrepp för att fylla ett geometriskt schema.

Först finns betydelsen.

Sedan tilldelas den en symbol.

### 7.3 Symbol och text

Symboler får komplettera text men ska inte automatiskt ersätta den.

I huvudnavigation och andra viktiga orienteringspunkter ska en symbol normalt

kombineras med en textetikett tills dess betydelse är mycket etablerad och sammanhanget är entydigt.

På mindre ytor kan en väl etablerad symbol användas utan permanent text om:

* betydelsen är tydlig,
* tillgängligt namn finns för hjälpmedel,
* användaren kan få ytterligare förklaring vid behov.

Estetisk minimalism är inte ett tillräckligt skäl för kryptisk navigation.

### 7.4 Linjer

Linjen är ett av systemets viktigaste grafiska element.

Linjer används för att:

* avgränsa sektioner,
* skapa tabell- och liststruktur,
* skilja navigation från arbetsyta,
* markera aktivt tillstånd,
* bygga formulär och kontroller,
* skapa rytm.

Linjer ska normalt vara tunna och precisa.

Tjockare linjer får användas när de uttrycker en tydligare strukturell gräns, exempelvis mellan större regioner i layouten.

Undvik linjer som endast fungerar som dekorativa streck.

### 7.5 Fylld och ofylld form

Fylld respektive ofylld geometri kan användas som ett återkommande sätt att uttrycka tillstånd.

Exempel:

```text
○  ofylld
●  fylld
``` 

kan representera två relaterade tillstånd inom samma semantiska kategori.

Detta är särskilt användbart när Dokumentverkstad behöver visa status utan att introducera fler färger.

Betydelsen ska dock vara konsekvent och vid behov kompletteras med text.

### 7.6 Punkt

Punkten är den minsta signalformen.

Den kan användas för exempelvis:

* status,
* förekomst,
* oläst eller obehandlat tillstånd,
* diskret orientering.

Eftersom punkten är visuellt stark i cinnabar trots sin ringa storlek ska den användas sparsamt.

En cinnabar punkt ska inte läggas till en rad enbart för att göra den visuellt intressant.

### 7.7 Pilar och riktning

Pilar ska uttrycka rörelse eller navigation.

En högerpil kan exempelvis signalera:

> öppna eller gå vidare till detta objekt.

En vänsterpil kan signalera:

> återvänd till föregående sammanhang.

Pilar ska inte användas som allmän dekoration eller som ersättning för begripliga etiketter när riktningen inte är självklar.

Chevron och pil ska skiljas semantiskt där båda används.

En möjlig princip är:

* pil = navigera,
* chevron = expandera, fäll ihop eller visa alternativ.

### 7.8 Dokumentverkstads symbol

Dokumentverkstads huvudsakliga symbol består av sammansatt geometrisk form och är systemets främsta grafiska identitetsmarkör.

Den ska behandlas som en symbol, inte som en illustration.

Den kan användas exempelvis:

* i huvudheader,
* vid start eller initiering,
* som favicon eller app-ikon i förenklad form,
* i andra tydliga identitetssammanhang.

Den ska inte upprepas som dekorativt vattenmärke eller bakgrundsmönster i normala arbetsytor.

Innehållet behöver inte konkurrera med systemets emblem.

### 7.9 Ornament

Ett mycket litet antal geometriska ornament får förekomma som identitetsbärande element.

Exempel är den kors- eller stjärnliknande markeringen kring en devis eller rubrik i designreferenserna.

Sådana ornament ska vara:

* små,
* sällsynta,
* konsekventa,
* tydligt sekundära till innehållet.

De ska inte utvecklas till en generell dekorationsvokabulär.

### 7.10 Ikoner

Standardfunktioner som sök, meny, öppna, stäng, redigera och visa behöver inte tvingas in i det ockulta geometriska alfabetet.

När en etablerad ikon är tydligare ska en enkel etablerad ikon användas.

Ikonstilen ska dock harmoniera med systemet:

* tunna linjer,
* enkel geometri,
* låg detaljnivå,
* inga fyllda illustrationer om inte tillståndet kräver det,
* inga färgglada ikonuppsättningar.

Undvik att blanda flera visuellt oförenliga ikonbibliotek.

### 7.11 Ikoner ska inte vara emoji

Emoji ska inte användas som permanenta gränssnittsikoner.

Deras utseende varierar mellan operativsystem och bryter mot Dokumentverkstads kontrollerade geometriska språk.

Textinnehåll som användaren själv skriver får naturligtvis innehålla emoji.

### 7.12 Storlek och optisk balans

Geometriska symboler med samma nominella mått uppfattas inte alltid som lika stora.

Cirkel, triangel, romb och stjärna ska därför justeras optiskt när det behövs för att bilda en balanserad symbolfamilj.

Målet är visuell konsekvens, inte matematisk identitet.

Linjetjocklek ska på motsvarande sätt uppfattas konsekvent mellan symbolerna.

### 7.13 Teknisk representation

Återkommande symboler ska implementeras på ett konsekvent och långsiktigt sätt.

SVG eller CSS-baserad geometri ska föredras där det är lämpligt.

Symboler ska inte implementeras genom:

* godtyckliga Unicode-tecken vars utseende varierar mellan typsnitt,
* rasterbilder för enkla geometriska former,
* externa ikonresurser som kräver nätverksåtkomst vid normal användning.

Symbolsystemet ska fungera lokalt och vara en del av applikationen.

### 7.14 Tillgänglighet

Dekorativa symboler ska döljas för hjälpmedel när de inte bär information.

Semantiska symboler ska ha ett tillgängligt namn när betydelsen inte redan förmedlas av intilliggande text.

Tillstånd får inte uttryckas enbart genom skillnaden mellan två geometriska former om användaren behöver förstå tillståndet för att kunna arbeta.

Geometri ska förstärka informationen, inte göra den beroende av visuell tolkning.

## 8. Layout och rumslig struktur

Dokumentverkstads layout ska göra det tydligt:

- var användaren befinner sig,
- vilket objekt eller sammanhang som är aktivt,
- vad som är huvudsakligt innehåll,
- vad som är kontext,
- vilka handlingar som är tillgängliga.

Layouten ska vara stabil nog för att användaren ska bygga upp ett rumsligt
minne av systemet.

Olika vyer får ha olika behov, men de ska kännas som rum i samma byggnad.

### 8.1 Grundstruktur på desktop

På större skärmar utgår Dokumentverkstad från fyra rumsliga nivåer:

1. **identitet och systemnivå,**
2. **huvudnavigation,**
3. **kontext,**
4. **arbetsyta.**

En principiell struktur är:

```text
┌─────────────────────────────────────────────┐
│ IDENTITET / SYSTEM                          │
├─────────────────────────────────────────────┤
│ HUVUDNAVIGATION                             │
├──────────────┬──────────────────────────────┤
│ KONTEXT      │ ARBETSYTA                    │
│              │                              │
│              │                              │
│              │                              │
└──────────────┴──────────────────────────────┘
```

Detta är en rumslig princip, inte en bindande wireframe.

Vissa vyer behöver ingen permanent kontextkolumn. Andra kan behöva en arbetsyta med flera interna kolumner. Den övergripande skillnaden mellan navigation, kontext och arbete ska ändå vara begriplig.

### 8.2 Identitetsnivån

Den översta nivån etablerar Dokumentverkstad som plats och system.

Den kan innehålla:

* Dokumentverkstads symbol,
* namnet DOKUMENTVERKSTAD,
* den historiska devisen,
* ett litet antal systemövergripande funktioner.

Identitetsnivån ska vara visuellt distinkt men kompakt.

Den ska inte utvecklas till en dashboard eller fyllas med statistik,  notifikationer och genvägar.

Dess huvudsakliga funktion är orientering och identitet.

### 8.3 Huvudnavigationen

Huvudnavigationen ligger mellan systemets identitet och den aktuella
arbetsytan.

Den representerar stabila destinationer i Dokumentverkstad, inte alla typer av
objekt som råkar finnas i domänmodellen.

Huvudnavigationen ska:

- vara lätt att hitta,
- vara konsekvent mellan vyer,
- tydligt visa aktuell destination,
- innehålla få och stabila alternativ.

Detaljerade regler för navigation beskrivs i avsnitt 9.

### 8.4 Kontext och arbetsyta

En central layoutprincip är skillnaden mellan:

> information om sammanhanget

och:

> det användaren arbetar med just nu.

På desktop kan denna skillnad ofta uttryckas genom en kontextuell vänsterkolumn
och en större arbetsyta.

Kontextkolumnen kan exempelvis innehålla:

- filter,
- metadata,
- Project-information,
- sekundär navigation,
- status,
- mindre frekventa handlingar.

Arbetsytan innehåller det huvudsakliga arbetet:

- en lista över Documents,
- ett öppet Document,
- en Inbox-kö,
- ett Project,
- en Capture eller ett formulär.

Kontextkolumnen är inte en generell plats för allt som inte får plats någon
annanstans. Dess innehåll ska ha en tydlig relation till den aktuella
arbetsytan.

### 8.5 Kontexten förändras med arbetsuppgiften

Kontextkolumnen ska inte innehålla samma typ av information på varje sida.

Exempel:

**Documents**

Kontexten kan innehålla filter, sortering och sekundära listfunktioner.

**Document**

Kontexten kan innehålla metadata, Project-tillhörighet, dokumentstatus och
sekundära dokumenthandlingar.

**Projects**

Kontexten kan innehålla Project-lista eller annan Project-orientering.

**Inbox**

Kontexten kan innehålla information eller kontroller som hjälper användaren
att arbeta igenom kön.

Detta innebär att vänsterkolumnen är en strukturell roll, inte en enskild
komponent.

### 8.6 Arbetsytan ska dominera

Arbetsytan ska normalt få huvuddelen av skärmens bredd och visuella
uppmärksamhet.

Kontext och navigation ska hjälpa användaren att arbeta utan att konkurrera
med arbetet.

På stora skärmar ska extra bredd inte automatiskt användas för att förstora
navigation eller sidokolumner. Den ska i första hand komma arbetsytan till
godo, eller lämnas som lugnt utrymme när innehållets optimala bredd är mindre.

### 8.7 Listor är arbetsytor

Documents, Inbox och andra större förteckningar ska behandlas som riktiga
arbetsytor, inte som samlingar av kort.

En listvy ska kunna bära mycket information genom:

- konsekventa kolumner,
- tydliga rader,
- typografisk hierarki,
- tunna separatorer,
- stabil alignment.

Primär information ska vara lätt att skanna vertikalt.

Sekundär information ska finnas tillgänglig utan att varje rad blir en
fristående miniatyrsida.

### 8.8 Document är en arbetsyta

Ett öppet Document är en av Dokumentverkstads centrala arbetsytor.

Document-vyn ska samla det som behövs för att förstå och arbeta med dokumentet
utan att användaren behöver hoppa mellan många separata sidor.

Det kan omfatta:

- titel och bibliografisk information,
- originaldokument,
- Summary,
- Claims,
- Insights,
- Questions,
- Captures,
- Project-sammanhang,
- dokumentrelaterade handlingar.

Dessa delar ska presenteras som lager eller sektioner inom samma Document,
inte som konkurrerande dashboards.

Långa innehållssektioner får fällas ihop eller öppnas när detta minskar
visuell belastning.

### 8.9 Vertikal rytm

Dokumentverkstad ska ha en tydlig vertikal rytm.

Likvärdiga relationer ska normalt få likvärdig spacing.

Exempelvis ska avståndet:

- mellan en sektionsrubrik och dess innehåll,
- mellan två rader i samma lista,
- mellan två större sektioner,

vara konsekvent inom respektive nivå.

Spacing ska definieras genom ett begränsat system av återkommande värden under
implementationen.

Godtyckliga marginaler för enskilda komponenter ska undvikas.

### 8.10 Alignment

Alignment är ett viktigare strukturellt verktyg än inramning.

Objekt som hör ihop ska dela visuella axlar.

Det gäller särskilt:

- listtitlar,
- metadata,
- årtal,
- statusmarkörer,
- kontroller,
- sektionsrubriker.

En sida får vara asymmetrisk om asymmetrin följer innehållets struktur.

Undvik att centrera innehåll som naturligt hör hemma i en katalog- eller
lässtruktur.

### 8.11 Bredd och maxbredd

Olika typer av innehåll behöver olika optimal bredd.

Systemet ska därför inte ha en enda universell `max-width` för alla arbetsytor.

Exempelvis kan:

- Documents-listan använda en stor del av tillgänglig bredd,
- metadata använda en smal kolumn,
- längre Summary-text använda en mer begränsad läsbredd,
- filter använda en kompakt panel.

Bredd ska bestämmas utifrån informationsformen.

### 8.12 Höjd och viewport

Normala arbetsytor ska utnyttja viewporten effektivt.

Header och navigation får inte tillsammans ta så stor vertikal plats att
arbetsytan trycks undan, särskilt på mindre laptops.

Sticky eller fasta regioner får användas när de tydligt minskar friktion, men
ska inte staplas så att en stor del av viewporten permanent upptas av
gränssnittskrom.

### 8.13 Lager och tillfälliga ytor

Filter, dialoger och andra tillfälliga arbetsytor får visas ovanpå den
ordinarie strukturen när användaren behöver behålla sitt sammanhang.

Ett tillfälligt lager ska:

- ha en tydlig början och slut,
- gå att stänga på förutsägbart sätt,
- inte få användaren att tappa sin plats,
- vara visuellt förenligt med den underliggande layouten.

Modalitet ska användas sparsamt.

En separat sida är bättre när uppgiften är omfattande eller utgör ett eget
arbetsflöde.

### 8.14 Ingen dashboard-grid som standard

Dokumentverkstad ska inte falla tillbaka på ett generiskt rutnät av:

- cards,
- statistikblock,
- widgets,
- quick actions.

Sådana element får förekomma när informationen faktiskt har den formen, men
de ska inte användas som generell sidlayout.

Systemets grundstruktur är:

> navigation + kontext + arbetsyta

snarare än:

> dashboard + widgets.

### 8.15 Layouten ska tåla tillväxt

Kunskapsrummet kommer att växa.

Layouten ska fungera när:

- Documents är hundratals eller tusentals,
- Captures blir många,
- ett Document har mycket AI- och användarskapat innehåll,
- Projects innehåller olika mängder material,
- nya funktioner tillkommer.

Tillväxt ska i första hand hanteras genom bättre sökning, filtrering,
progressiv komplexitet och navigation.

Lösningen ska inte vara att permanent lägga till fler paneler på skärmen.

---

## 9. Navigation

Navigationen ska hjälpa användaren att röra sig mellan arbetsuppgifter och
sammanhang utan att behöva förstå Dokumentverkstads interna datamodell.

Den ska utgå från hur systemet används, inte från en önskan att exponera varje
objekttyp som en egen destination.

Navigationen ska vara:

- stabil,
- grund,
- förutsägbar,
- kontextmedveten.

### 9.1 Navigera efter arbete, inte ontologi

Att ett begrepp finns i domänmodellen innebär inte att det behöver en plats i
huvudnavigationen.

Exempelvis är Summary, Claim, Insight och Question typer av kunskapsinnehåll.
De behöver inte därför vara globala destinationer.

De kan i stället vara tillgängliga:

- inom ett Document,
- genom sökning,
- inom ett Project,
- genom framtida specialiserade vyer om verklig användning motiverar det.

Huvudnavigationen ska representera de viktigaste platserna och
arbetsflödena.

### 9.2 Stabil global navigation

Den globala navigationen ska vara liten och förändras sällan.

Utifrån den aktuella produkten är följande begrepp centrala kandidater:

- Inbox,
- Documents,
- Projects,
- Capture.

Den exakta utformningen ska prövas under Iteration 9 och behöver inte
bestämmas av designreferensernas äldre navigation.

Search är systemövergripande men behöver inte nödvändigtvis behandlas som en
destination på samma sätt som Documents eller Projects.

Systemadministrativa funktioner som status, backup och inställningar ska inte
konkurrera med de huvudsakliga arbetsflödena.

### 9.3 Inbox är en arbetskö

Inbox ska uppfattas som en plats där något behöver bedömas eller bearbetas.

Navigationen till Inbox ska därför kunna kommunicera att det finns arbete där,
utan att förvandlas till ett notifikationssystem som ständigt kräver
uppmärksamhet.

Ett antal kan vara användbart när det representerar en verklig kö.

Dekorativa badges och uppmärksamhetsmarkörer ska undvikas.

När ett Inbox-objekt öppnas ska användaren kunna förstå:

- varifrån objektet kommer,
- vad som behöver beslutas,
- hur man går vidare,
- hur man återvänder till kön.

### 9.4 Documents är arkivets huvudingång

Documents är den huvudsakliga vägen till arkivets externa källor.

Navigationen mellan Documents-listan och ett enskilt Document ska bevara
sammanhanget så långt det är praktiskt möjligt.

När användaren går tillbaka från ett Document bör exempelvis tidigare:

- sökning,
- filter,
- sortering,
- position i listan,

bevaras när implementationen rimligen tillåter det.

Att öppna ett Document ska inte kännas som att lämna Documents och börja ett
helt annat program.

### 9.5 Projects är kontexter

Projects ska navigeras som användardefinierade sammanhang, inte som en
obligatorisk klassifikationshierarki.

Ett Document eller en Capture behöver inte tillhöra ett Project för att vara
fullvärdigt i Dokumentverkstad.

Project-navigationen ska därför hjälpa användaren att:

- gå in i ett relevant sammanhang,
- se material genom detta sammanhang,
- lägga till eller ta bort kopplingar,

utan att antyda att allt material måste sorteras in.

`General` eller motsvarande systemövergripande perspektiv ska representera
kunskapsrummet som helhet, inte ett Project som användaren måste underhålla.

### 9.6 Capture ska alltid vara nära

Att fånga en tanke är en central handling och ska vara tillgänglig med låg
friktion.

Capture ska kunna initieras från relevanta sammanhang, exempelvis:

- globalt,
- från ett Document,
- från ett Project,
- under läsning eller granskning.

När Capture initieras från ett sammanhang får detta sammanhang föreslås eller
automatiskt följa med när relationen är entydig.

Användaren ska inte behöva navigera bort från sitt arbete för att fånga en
tanke.

Detta kan motivera att Capture behandlas mer som en global handling än som en
traditionell destination.

### 9.7 Kontextuell navigation

Utöver den globala navigationen får varje arbetsyta erbjuda navigation som
endast är relevant där.

Exempel:

- Documents → filter och sortering,
- Document → metadata och kunskapssektioner,
- Project → material och Project-relaterade handlingar,
- Inbox → nästa objekt och granskningshandlingar.

Kontextuell navigation ska inte läggas till den globala navigationen bara för
att den är viktig på en viss sida.

### 9.8 Tillbaka ska betyda tillbaka

Navigationen ska i möjligaste mån bevara användarens mentala och faktiska
sammanhang.

En länk som säger `Tillbaka till Documents` ska återvända till Documents.

Webbläsarens bakåtknapp ska fungera för normala navigationssteg.

Undvik arbetsflöden där användaren måste använda systemets logotyp eller
huvudnavigation för att återvända från en detaljvy därför att den lokala
navigationen saknas.

### 9.9 Objektlänkar ska vara riktiga länkar

När en titel, ett Project eller annat objekt leder till en ny vy ska det i
normalfallet implementeras som en riktig webblänk.

Det gör att användaren kan:

- öppna i ny flik,
- kopiera länken,
- använda webbläsarens historik,
- använda vanliga webbläsarbeteenden.

JavaScript-baserad navigation ska inte ersätta normala länkar utan ett tydligt
skäl.

### 9.10 Aktiv position

Användaren ska kunna se sin position i systemet utan att behöva läsa
sidrubriken.

Den globala navigationen ska visa aktuell huvuddestination.

Den lokala arbetsytan ska visa aktuellt objekt eller sammanhang.

Aktiv position får uttryckas genom exempelvis:

- cinnabar,
- linje,
- typografisk vikt,
- geometrisk markering.

Färg får inte bära betydelsen ensam.

### 9.11 Breadcrumbs endast när de beskriver verklig struktur

Breadcrumbs ska inte användas rutinmässigt.

Dokumentverkstads domän är inte primärt en hierarkisk mappstruktur, och
falska breadcrumbs riskerar därför att ge en missvisande bild.

De får användas när det finns en verklig navigationskedja som hjälper
orienteringen.

I andra fall är en explicit tillbaka-länk eller kontextetikett bättre.

### 9.12 Sökning

Sökning är en väg genom kunskapsrummet snarare än en separat del av
domänmodellen.

Den ska vara lätt att nå från de sammanhang där användaren behöver hitta
material.

En framtida mer avancerad sökfunktion får kombinera flera typer av innehåll,
men navigationen ska inte föregripa funktioner som ännu inte finns.

Sökresultat ska tydligt visa vilken typ av objekt resultatet leder till och
bevara tillräcklig kontext för att användaren ska förstå träffen.

### 9.13 Desktop och mobil behöver inte ha identisk navigation

Den globala informationsarkitekturen ska vara densamma mellan enheter, men
navigationens fysiska form får skilja sig.

Desktop har utrymme för synlig navigation och kontext.

Mobil kräver hårdare prioritering.

Designreferensens mobila navigation ska därför ses som en visuell referens,
inte som en färdig informationsarkitektur.

En möjlig mobil princip är att ge de mest använda destinationerna eller
handlingarna fasta positioner och samla mindre frekventa funktioner under en
sekundär meny.

Den exakta lösningen fastställs under responsivt designarbete.

### 9.14 Undvik dubbla navigationssystem

Samma nivå i informationsarkitekturen ska inte representeras av två
konkurrerande navigationssystem.

Om mobilgränssnittet exempelvis har en primär bottom navigation ska en andra
horisontell navigation inte samtidigt presentera samma destinationer på ett
annat sätt.

Flera navigationsytor är rimliga endast när de representerar olika nivåer:

- global navigation,
- kontextuell navigation,
- navigation inom innehållet.

Användaren ska kunna förstå skillnaden mellan dessa.

### 9.15 Navigation ska kunna mogna genom användning

Informationsarkitekturen ska inte betraktas som färdig för all framtid.

Nya globala destinationer ska införas först när verklig användning visar att
ett återkommande arbetsflöde behöver en egen stabil plats.

På motsvarande sätt ska en destination kunna flyttas till en mer sekundär
position om den sällan används.

Navigationen ska utvecklas utifrån Dokumentverkstads faktiska arbetsmönster,
inte utifrån symmetri eller önskan att fylla en navigationsrad.

## 10. Komponenter och informationsmönster

Dokumentverkstad ska byggas av ett litet antal återkommande komponenter och
informationsmönster.

Komponenterna ska härledas ur designsystemets grundspråk:

- typografi,
- linjer,
- spacing,
- geometri,
- ivory,
- ebony,
- cinnabar.

En ny funktion ska inte automatiskt få en ny visuell komponent.

När två handlingar eller informationsstrukturer fyller samma roll ska de i
första hand uttryckas på samma sätt.

Målet är inte ett omfattande komponentbibliotek, utan ett litet och
förutsägbart visuellt språk.

### 10.1 Komponenter ska uttrycka informationsstruktur

En komponent ska finnas därför att en återkommande informations- eller
interaktionsstruktur behöver uttryckas.

Exempel på sådana strukturer är:

- listor,
- metadata,
- sektioner,
- formulär,
- handlingar,
- status,
- tillfälliga meddelanden.

Undvik komponenter som huvudsakligen finns för att skapa visuell variation.

Komponentgränser ska följa verkliga gränser i användarens arbete.

### 10.2 Listraden är en grundkomponent

Listraden är en av Dokumentverkstads viktigaste komponenter.

Den används i Documents, Inbox och andra förteckningar där användaren behöver
skanna, jämföra och välja mellan många objekt.

En listrad kan innehålla:

- primär titel,
- sekundär metadata,
- år eller datum,
- Project-sammanhang,
- status,
- antal relaterade objekt,
- diskreta handlingar.

All information behöver inte finnas i varje lista.

Varje listvy ska välja den information som hjälper användaren att fatta beslut
i just det sammanhanget.

### 10.3 Primär och sekundär information i listor

Varje listrad ska ha en tydlig primär ingång.

För Documents är detta normalt dokumenttiteln.

Sekundär information ska stödja bedömningen av raden utan att konkurrera med
titeln.

Visuell hierarki kan skapas genom:

- typografisk roll,
- storlek,
- vikt,
- position,
- spacing,
- alignment.

En rad ska inte behöva en egen ram, bakgrund och skugga för att uppfattas som
ett sammanhängande objekt.

### 10.4 Hela raden och den primära länken

Det ska vara lätt att öppna ett objekt från en lista.

Den primära länken ska ha en tillräckligt stor och tydlig träffyta.

Om hela raden görs klickbar måste sekundära kontroller fortfarande fungera
förutsägbart och semantiskt korrekt.

Normala webblänkar ska bevaras så att exempelvis öppna i ny flik fungerar.

### 10.5 Metadata som informationsblock

Metadata ska presenteras som strukturerad information, inte som löpande text.

Ett metadatafält består normalt av:

- etikett,
- värde.

Etiketten ska vara visuellt sekundär men tydlig.

Värdet ska vara lätt att läsa och, där det är relevant, möjligt att kopiera
eller följa som länk.

Metadatafält kan ordnas:

- vertikalt,
- i kompakta rader,
- i ett enkelt rutnät,

beroende på mängd och skärmbredd.

Undvik att ge varje metadatafält en egen card-liknande behållare.

### 10.6 Saknad metadata

Saknad information ska inte skapa onödigt visuellt brus.

Om ett metadatafält är frivilligt och saknas kan det ofta utelämnas helt i
läsningsläge.

I redigeringsläge ska det däremot vara möjligt att se vilka relevanta fält som
kan fyllas i.

Placeholder-värden som:

`N/A`, `null`, `unknown` eller `-`

ska inte användas rutinmässigt i användargränssnittet.

När det är viktigt att användaren vet att information faktiskt saknas ska
detta uttryckas begripligt, exempelvis `År saknas`.

### 10.7 Sektioner

Större arbetsytor ska delas upp i tydliga sektioner.

En sektion består normalt av:

- rubrik,
- eventuellt status eller antal,
- innehåll,
- eventuellt en relevant handling.

Sektioner ska i första hand avgränsas genom spacing, typografi och linjer.

De ska inte automatiskt presenteras som cards.

### 10.8 Expanderbara sektioner

Sektioner med större mängder innehåll får kunna fällas ihop.

Det är särskilt relevant i Document-vyn för exempelvis:

- Summary,
- Claims,
- Insights,
- Questions,
- Captures.

En expanderbar sektion ska tydligt visa:

- vad sektionen innehåller,
- om den är öppen eller stängd,
- om det finns innehåll även när sektionen är stängd.

Chevron eller annan enkel geometri kan användas för tillståndet.

Klickytan ska vara tillräckligt stor och beteendet förutsägbart.

Expanderbarhet ska användas för att hantera informationsmängd, inte för att
gömma sådant användaren nästan alltid behöver.

### 10.9 Tomma sektioner

Tomma tillstånd ska vara lugna.

En tom sektion behöver normalt inte en stor illustration, färgad ruta eller
uppmaning.

Den kan exempelvis visa:

`Inga Captures ännu.`

och, om det är relevant:

`+ Ny Capture`

Tomheten ska förklara vad som saknas och erbjuda nästa handling när en sådan
är naturlig.

### 10.10 Knappar och handlingar

Dokumentverkstad ska ha få visuella nivåer av knappar.

En användbar grundskillnad är:

- **primär handling,**
- **sekundär handling,**
- **diskret eller textbaserad handling,**
- **destruktiv handling.**

En sida ska normalt inte innehålla flera konkurrerande primära handlingar.

Primära handlingar får använda cinnabar tydligare än sekundära handlingar, men
behöver inte vara stora fyllda färgblock.

Sekundära handlingar kan uttryckas genom exempelvis:

- text,
- linje,
- enkel ram,
- symbol + text.

Destruktiva handlingar ska vara tydligt identifierbara genom mer än färg.

### 10.11 Handlingens etikett ska beskriva handlingen

Knappar ska i första hand använda konkreta verb eller verbfraser.

Föredra exempelvis:

- `Spara`,
- `Redigera metadata`,
- `Kör AI-analys`,
- `Acceptera`,
- `Avvisa`,
- `Återställ`,
- `Flytta till papperskorgen`.

Undvik vaga etiketter som:

- `OK`,
- `Fortsätt`,
- `Ja`,

när en mer specifik formulering är möjlig.

### 10.12 Formulär

Formulär ska vara lugna, tydliga och nära den information de redigerar.

Fält ska ha permanenta etiketter.

Placeholder-text ska inte ersätta fältetiketter.

Formulär ska i första hand använda standardiserade webbfält med ett visuellt
uttryck anpassat till Dokumentverkstad.

Fältgränser ska vara tydliga utan att varje kontroll behöver en tung ram.

Relaterade fält ska grupperas genom spacing och struktur.

### 10.13 Redigering nära objektet

När det är praktiskt ska redigering ske nära den information som redigeras.

Exempelvis bör metadata kunna redigeras från Document-vyn utan att användaren
måste navigera genom en separat administrationshierarki.

Det betyder inte att all redigering måste vara inline.

Om ett formulär är omfattande kan en separat yta, panel eller sida vara
tydligare.

Principen är att redigering ska utgå från objektet, inte från systemets interna
administrativa struktur.

### 10.14 Capture-komponenten

Capture är en särskilt viktig komponent eftersom den representerar
användarens egen tanke.

Capture ska visuellt kunna skiljas från:

- dokumentmetadata,
- AI-genererat innehåll,
- systeminformation.

Skillnaden ska inte kräva en helt annan design.

Typografi, etikett, symbol eller avsändar-/proveniensmarkering kan användas för
att tydliggöra att innehållet är användarskapat.

En Capture ska kunna läsas som en anteckning, inte som en databaspost.

### 10.15 AI-genererat innehåll

AI-genererat innehåll ska vara tydligt identifierbart som AI-genererat tills
användaren fattat det beslut som arbetsflödet kräver.

Det ska aldrig vara nödvändigt att gissa om en Summary, Claim, Insight eller
Question är:

- ett AI-förslag,
- accepterat kunskapsinnehåll,
- användarens egen text.

Skillnaden ska uttryckas konsekvent genom exempelvis:

- etikett,
- status,
- geometri,
- typografisk behandling.

AI-innehåll ska samtidigt vara behagligt att läsa. Proveniensmarkering ska
inte visuellt övermanna själva innehållet.

### 10.16 Review-komponenten

Review är ett beslutsmönster.

När användaren granskar ett AI-förslag ska gränssnittet tydligt visa:

1. vad som granskas,
2. varifrån det kommer,
3. vilket tillstånd det befinner sig i,
4. vilka beslut som är möjliga.

De viktigaste handlingarna är normalt:

- acceptera,
- avvisa,
- skjuta upp eller lämna obeslutat där arbetsflödet stödjer detta.

Review ska optimeras för upprepade beslut utan att användaren tappar
sammanhanget.

Det ska inte kännas som att fylla i ett administrativt formulär för varje
förslag.

### 10.17 Beslut ska kunna korrigeras

När domänmodellen stödjer korrigerbara beslut ska gränssnittet inte presentera
ett accepterat eller avvisat beslut som oåterkalleligt.

Aktuellt tillstånd ska vara tydligt.

Möjligheten att ändra beslut behöver inte dominera vyn, men ska gå att hitta.

Historik ska kunna visas när den är relevant utan att belasta den normala
arbetsytan.

### 10.18 Länkar mellan objekt

Relationer mellan Documents, Projects och Knowledge Objects ska presenteras
som navigerbara relationer när de hjälper användaren.

Objektnamn ska normalt användas framför interna identifierare.

En relation ska inte visualiseras som ett avancerat nätverk enbart därför att
den tekniskt är en grafrelation.

Den enklaste begripliga representationen ska användas först.

### 10.19 Menyer

Menyer ska användas för sekundära handlingar som inte behöver vara permanent
synliga.

De ska inte användas för att gömma den vanligaste handlingen bara för att
gränssnittet ska se renare ut.

En meny ska ha en tydlig utlösare och gå att använda med tangentbord och
hjälpmedel.

Ellipsmeny (`…`) får användas när den faktiskt betyder:

> fler handlingar för detta objekt.

### 10.20 Tabeller

Tabeller är lämpliga när användaren behöver jämföra samma attribut mellan
många objekt.

De ska inte undvikas bara därför att modern webbdesign ofta föredrar cards.

En tabell ska däremot inte användas när innehållet i varje rad har helt olika
struktur.

På små skärmar ska tabellinformation prioriteras eller omformas snarare än
bara pressas ihop.

### 10.21 Komponenter ska fungera utan dekoration

En användbar kontrollfråga är:

> Om färg, ornament och identitetsmarkörer togs bort, skulle komponentens
> struktur och funktion fortfarande vara begriplig?

Om svaret är nej är komponenten sannolikt för beroende av dekoration.

Dokumentverkstads identitet ska förstärka ett fungerande gränssnitt, inte
ersätta det.

---

## 11. Tillstånd och återkoppling

Dokumentverkstad utför både omedelbara och långvariga operationer.

Användaren ska alltid kunna förstå vad systemet gör när detta påverkar
arbetsflödet.

Återkoppling ska vara:

- tydlig,
- proportionerlig,
- lokal när det är möjligt,
- beständig när tillståndet är beständigt,
- lugn.

Systemet ska inte skapa uppmärksamhet bara för att visa att det är aktivt.

### 11.1 Tillstånd är en del av informationsmodellen

Tillstånd ska inte behandlas som tillfällig kosmetik.

Om användaren behöver veta att ett Document:

- väntar på bearbetning,
- analyseras,
- är färdiganalyserat,
- innehåller ogranskade AI-förslag,
- har misslyckats i en operation,

är detta relevant information.

Tillståndet ska därför uttryckas på ett konsekvent sätt där det behövs för att
förstå eller handla.

### 11.2 Återkoppling ska vara proportionerlig

En liten handling ska ge liten återkoppling.

En stor eller långvarig handling får ge mer synlig återkoppling.

Exempel:

- en sparad metadataändring kan bekräftas diskret,
- en uppladdning kan visa förlopp,
- en AI-analys som tar en minut behöver ett beständigt arbetstillstånd,
- ett fel som kräver användarens ingripande behöver en tydlig förklaring.

Undvik stora banners eller modaler för rutinmässigt lyckade handlingar.

### 11.3 Lokal återkoppling först

Återkoppling ska visas så nära den handling eller det objekt den gäller som
möjligt.

Om en AI-analys körs för ett Document är Documentets AI-status den naturliga
platsen för tillståndet.

Om metadata sparas är metadataområdet den naturliga platsen för
bekräftelsen.

Globala meddelanden ska främst användas när händelsen är systemövergripande
eller när den lokala platsen inte längre är synlig.

### 11.4 Omedelbara handlingar

Handlingar som normalt slutförs nästan omedelbart ska inte skapa onödiga
mellantillstånd.

När användaren exempelvis sparar en mindre ändring kan systemet:

1. visa att handlingen initierats om det behövs,
2. uppdatera den synliga informationen,
3. ge en diskret bekräftelse.

Gränssnittet ska inte kännas långsammare genom att artificiellt visa
animationer eller statussteg.

### 11.5 Långvariga operationer

Operationer som kan ta mer än några sekunder ska behandlas som riktiga
processer.

Exempel är:

- större ingest,
- textbearbetning,
- AI-analys,
- framtida OCR,
- backup eller restore.

Användaren ska inte behöva undra om systemet:

- arbetar,
- har hängt sig,
- har misslyckats.

En långvarig operation ska därför ha ett tydligt tillstånd.

### 11.6 Långvarigt arbete ska inte blockera arbetsytan

När operationens natur tillåter det ska användaren kunna fortsätta använda
Dokumentverkstad medan arbetet pågår.

Det är särskilt viktigt för AI-operationer som kan ta tiotals sekunder eller
minuter.

Den önskade interaktionsmodellen är:

1. användaren startar arbetet,
2. systemet bekräftar att arbetet har startat,
3. operationen fortsätter i bakgrunden,
4. användaren kan fortsätta arbeta,
5. resultatet blir tillgängligt när operationen är klar.

Detta är en designprincip även innan den tekniska bakgrundskörningen är fullt
implementerad.

### 11.7 Grundtillstånd för bakgrundsarbete

En långvarig operation behöver normalt kunna uttrycka åtminstone:

- **inte startad,**
- **köad eller väntande,**
- **pågår,**
- **klar,**
- **misslyckad.**

Alla operationer behöver inte exponera alla dessa tillstånd om skillnaden
saknar betydelse för användaren.

Tekniska interna jobbtillstånd ska inte visas enbart därför att de finns i
implementationen.

### 11.8 Pågående tillstånd

Ett pågående tillstånd ska vara synligt utan att dominera gränssnittet.

Det kan uttryckas genom en kombination av:

- textetikett,
- geometri,
- cinnabar,
- diskret rörelse.

Exempel:

`AI-analys pågår`

är bättre än en ensam spinner vars betydelse användaren måste gissa.

Om systemet inte kan uppskatta återstående tid ska det inte visa en falsk
procentindikator.

### 11.9 Rörelse

Rörelse får användas för att visa att något faktiskt pågår.

Den ska vara:

- diskret,
- funktionell,
- begränsad.

Undvik dekorativa övergångar, pulserande element och kontinuerlig animation
som inte förmedlar information.

Rörelse ska respektera användarens inställning för reducerad rörelse.

Ett pågående tillstånd ska fortfarande gå att förstå utan animation.

### 11.10 Framsteg

När verkligt mätbara framsteg finns får en progressindikator användas.

Exempel:

`42 av 100 filer bearbetade`

är ofta mer informativt än en anonym progressbar.

När framsteg inte går att mäta ska systemet visa ett obestämt pågående
tillstånd i stället för att simulera precision.

### 11.11 Klart tillstånd

När en långvarig operation blir klar ska resultatet bli synligt där
användaren förväntar sig det.

Systemet ska inte kräva att användaren manuellt laddar om en sida bara för att
upptäcka att arbetet är färdigt, när detta rimligen kan undvikas.

Om användaren befinner sig någon annanstans kan en diskret global återkoppling
vara lämplig.

Systemet ska inte kräva att användaren kvitterar rutinmässigt lyckade
operationer.

### 11.12 Fel

Felmeddelanden ska hjälpa användaren att förstå:

1. vad som misslyckades,
2. vad konsekvensen blev,
3. om något behöver göras,
4. vad användaren i så fall kan göra.

Föredra:

`AI-analysen kunde inte slutföras. Dokumentet och tidigare innehåll är
oförändrade. Försök igen.`

framför:

`Error 500`

Tekniska detaljer får finnas tillgängliga för diagnostik utan att vara
huvudbudskapet.

### 11.13 Fel ska inte utplåna fungerande innehåll

Om en operation misslyckas ska befintligt giltigt innehåll fortsätta vara
tillgängligt när detta är tekniskt möjligt.

Ett misslyckat försök att skapa ny AI-analys ska exempelvis inte göra själva
Document-vyn otillgänglig.

Fel ska visas som ett tillstånd hos den misslyckade operationen, inte
automatiskt som ett fel hos hela sidan.

### 11.14 Återförsök

När en operation rimligen kan göras om ska felmeddelandet erbjuda en tydlig
väg till återförsök.

Exempel:

`Försök igen`

eller:

`Kör AI-analys igen`

Återförsök ska inte kräva att användaren rekonstruerar hela arbetsflödet från
början om den tidigare inputen fortfarande är giltig.

### 11.15 Sparande

När användaren redigerar beständigt innehåll ska det vara begripligt när
ändringen har sparats.

Exakt modell kan variera mellan:

- explicit `Spara`,
- automatisk sparning,
- en kombination beroende på innehållstyp.

Automatisk sparning får endast användas när användaren kan förstå att den sker
och när risken för oavsiktliga ändringar är acceptabel.

Systemet ska inte visa `Sparat` permanent överallt. Bekräftelsen ska vara
tillräcklig för att skapa förtroende och sedan kunna träda tillbaka.

### 11.16 Osparade ändringar

Om användaren kan förlora en betydande osparad ändring genom navigation ska
systemet skydda mot detta.

Skyddet ska stå i proportion till risken.

En liten korrigering behöver inte nödvändigtvis utlösa en dramatisk modal,
medan en längre Capture eller anteckning bör skyddas mot oavsiktlig förlust.

### 11.17 Ingest

Ingest ska presenteras som en begriplig övergång från inkommande material till
Document.

Användaren ska kunna förstå om en fil:

- har tagits emot,
- bearbetas,
- behöver ett beslut,
- har blivit ett Document,
- har misslyckats.

Interna staging-kataloger, filflyttar och andra implementationstekniska steg
ska inte exponeras om de inte hjälper användaren att lösa ett problem.

### 11.18 AI-tillstånd

AI har flera olika slags tillstånd som inte ska blandas ihop.

Minst tre dimensioner kan vara relevanta:

**Operation**

- ingen analys,
- analys väntar,
- analys pågår,
- analys klar,
- analys misslyckad.

**Review**

- inget att granska,
- ogranskade förslag finns,
- delvis granskat,
- färdiggranskat.

**Proveniens**

- AI-genererat förslag,
- accepterat kunskapsinnehåll,
- användarskapat innehåll.

Gränssnittet ska inte försöka pressa dessa tre dimensioner till en enda
färgkod eller statusetikett.

De ska visas där respektive dimension är relevant.

### 11.19 AI är inte magi

AI-operationer ska presenteras som systemoperationer, inte som mystiska eller
antropomorfiserade händelser.

Undvik formuleringar och animationer som antyder att Dokumentverkstad:

- tänker,
- funderar,
- drömmer,
- blir inspirerad.

Föredra konkret språk:

- `AI-analys pågår`,
- `12 förslag skapades`,
- `3 förslag återstår att granska`.

Det visuella systemets ockulta underström ska inte användas för att göra
AI-funktionen mer mystisk.

### 11.20 AI-kostnad och omfattning

När en AI-operation kan ha en märkbar kostnad eller kräva ett ovanligt stort
underlag ska relevant information kunna visas innan användaren startar den.

Informationen ska hjälpa ett beslut, inte belasta varje normal AI-handling.

Om systemet i framtiden kan uppskatta kostnad eller tokenanvändning ska
uppgiften beskrivas som en uppskattning när den inte är exakt.

Avancerade overrides ska kunna finnas utan att dominera det normala
arbetsflödet.

### 11.21 Beständiga och tillfälliga meddelanden

Tillfälliga meddelanden är lämpliga för händelser som:

- `Metadata sparad`,
- `Capture skapad`,
- `Document återställt`.

Beständiga meddelanden är lämpliga när ett tillstånd fortfarande gäller och
användaren kan behöva agera på det.

Exempel:

- AI-analys misslyckad,
- metadata behöver kompletteras,
- ett ingest-objekt kräver beslut.

Ett meddelande ska inte försvinna automatiskt om användaren behöver innehållet
för att kunna lösa problemet.

### 11.22 Toasts ska användas sparsamt

Tillfälliga globala toast-meddelanden får användas när lokal återkoppling inte
räcker eller när användaren har navigerat vidare.

De ska inte bli Dokumentverkstads huvudsakliga återkopplingsmekanism.

Flera samtidiga toasts ska undvikas.

Användaren ska inte behöva läsa snabbt innan viktig information försvinner.

### 11.23 Bekräftelse före destruktiva handlingar

Destruktiva handlingar ska bedömas efter faktisk konsekvens.

Om en handling enkelt kan återställas genom Trash behöver den inte alltid en
modal bekräftelse.

Permanent borttagning eller annan svåråterkallelig handling kräver starkare
skydd.

Designen ska skilja mellan:

> flytta undan

och:

> förstöra permanent.

Bekräftelsedialoger ska användas där de minskar verklig risk, inte på varje
handling som tekniskt ändrar data.

### 11.24 Tomt, laddar och fel är olika tillstånd

En tom lista betyder inte samma sak som en lista som ännu inte har laddats.

En misslyckad laddning betyder inte samma sak som att det inte finns några
resultat.

Gränssnittet ska därför skilja tydligt mellan:

- tomt,
- laddar,
- fel,
- inga sökträffar.

Användaren ska aldrig behöva gissa om `inga Documents` betyder att arkivet är
tomt eller att något gick fel.

### 11.25 Systemstatus hör hemma där den behövs

Teknisk status för exempelvis:

- Archive,
- Runtime,
- backup,
- index,
- loggar,

är viktig för drift och diagnostik men ska inte permanent exponeras i den
normala arbetsytan.

Den ska finnas på en tydlig system- eller statusyta och kunna nås när den
behövs.

Ett kritiskt tillstånd som hotar användarens data får däremot lyftas fram
utanför denna yta.

### 11.26 Återkoppling ska skapa förtroende

Det övergripande målet med systemstatus är inte att visa hur mycket
Dokumentverkstad gör.

Det är att användaren ska kunna lita på systemet.

Användaren ska kunna förstå:

- att en handling registrerades,
- om arbete fortfarande pågår,
- när resultatet är färdigt,
- om något misslyckades,
- om den beständiga informationen är säker.

Ett lugnt system är inte ett tyst system.

Det ger rätt information vid rätt tidpunkt och träder sedan tillbaka.

## 12. Responsiv design

Dokumentverkstad ska fungera på flera skärmstorlekar utan att förlora sin
informationsstruktur eller identitet.

Responsiv design innebär inte att desktopgränssnittet skalas ned proportionellt.

Det innebär att samma funktioner och sammanhang omformas efter:

- tillgänglig yta,
- interaktionssätt,
- informationsdensitet,
- arbetsuppgiftens prioritet.

Den globala informationsarkitekturen ska vara konsekvent mellan enheter, men
den rumsliga organisationen får förändras tydligt.

### 12.1 Samma system, olika komposition

Desktop, tablet och mobil ska uppfattas som olika kompositioner av samma
Dokumentverkstad.

De ska dela:

- typografiska roller,
- färgsystem,
- geometriskt språk,
- komponentlogik,
- begrepp,
- navigationens semantik,
- tillstånd och återkoppling.

De behöver inte dela exakt:

- placering,
- kolumnantal,
- synlig metadata,
- navigationsform,
- komponentbredd.

Responsiviteten ska bevara systemets identitet utan att bevara en viss
desktopgeometri till varje pris.

### 12.2 Prioritera, inte bara stapla

När utrymmet minskar ska gränssnittet inte enbart stapla alla desktopregioner
ovanpå varandra.

Det ska först avgöra:

1. vad användaren behöver för den aktuella uppgiften,
2. vad som kan komprimeras,
3. vad som kan flyttas till en sekundär yta,
4. vad som kan döljas tills användaren ber om det.

Responsiv design är därför också informationsprioritering.

### 12.3 Kontextkolumnen på mindre skärmar

Desktopens kontextkolumn behöver inte vara permanent synlig på tablet eller
mobil.

Dess innehåll kan exempelvis:

- flyttas ovanför arbetsytan,
- visas i en tillfällig panel,
- öppnas genom en tydlig kontextknapp,
- integreras i relevanta sektioner.

Kontexten ska fortfarande vara lätt att nå.

Den får inte försvinna bara därför att den inte längre får plats bredvid
arbetsytan.

### 12.4 Arbetsytan får företräde

På små skärmar ska den aktuella arbetsytan få nästan all tillgänglig bredd.

Permanenta sidokolumner ska undvikas om de gör innehållet svårt att läsa eller
interagera med.

Navigation och sekundär metadata får flyttas undan så länge de fortfarande är
begripliga och tillgängliga.

### 12.5 Mobil navigation

Mobil navigation ska vara enkel och stabil.

Ett enda tydligt primärt navigationssystem ska föredras.

En möjlig princip är en fast bottom navigation för de mest använda
destinationerna eller handlingarna.

Den exakta uppsättningen ska bestämmas av den verkliga produkten och får inte
kopieras direkt från designreferensernas äldre informationsarkitektur.

Capture kan på mobil få en särskilt framträdande position eftersom det är en
central handling.

Mindre frekventa funktioner kan samlas under en sekundär meny.

### 12.6 Undvik dubbla system på mobil

Mobilgränssnittet ska inte samtidigt ha två konkurrerande globala
navigationssystem.

Om bottom navigation används ska en horisontell topprad inte upprepa samma
destinationer.

Flera navigationsnivåer får finnas när de har olika roller:

- global navigation,
- kontextuell navigation,
- navigation inom innehåll.

Skillnaden mellan dem ska vara tydlig.

### 12.7 Mobil Documents-lista

På mobil kan en Documents-rad inte visa samma mängd metadata som på desktop.

Raden ska därför prioritera den information som bäst hjälper användaren att
identifiera dokumentet.

Det är normalt:

1. titel,
2. författare eller organisation när detta hjälper,
3. år,
4. relevant status.

Övrig metadata kan finnas i Document-vyn eller öppnas vid behov.

Listan ska fortfarande kännas som en sammanhängande förteckning, inte som en
serie stora cards.

### 12.8 Mobil Document-vy

Document-vyn ska på mobil prioritera läsning och Capture.

Metadata och sekundära handlingar får komprimeras eller flyttas till
expanderbara områden.

Knowledge Object-sektioner får staplas vertikalt.

Långa rubriker, bibliografisk information och status ska kunna brytas utan att
förstöra hierarkin.

Användaren ska kunna läsa ett Document och skapa en Capture utan att
navigationskrom tar en stor del av skärmen.

### 12.9 Mobil Inbox

Inbox på mobil ska optimeras för beslut i följd.

Användaren ska tydligt se:

- vilket objekt som granskas,
- relevant sammanhang,
- vilka beslut som finns,
- hur man går vidare till nästa objekt.

Review-handlingar ska vara lätta att nå med touch.

Layouten får skilja sig tydligt från desktop om detta gör upprepad granskning
snabbare och lugnare.

### 12.10 Touchytor

Interaktiva element på touch-enheter ska ha tillräckligt stora träffytor.

En liten geometrisk ikon får visuellt vara liten men ska inte därför ha en
lika liten faktisk klickyta.

Särskilt viktigt är detta för:

- expandera/fäll ihop,
- statusrelaterade handlingar,
- menyknappar,
- back-navigation,
- Capture,
- review-beslut.

Visuell precision får inte ske på bekostnad av fysisk användbarhet.

### 12.11 Hover får inte vara nödvändigt

Ingen viktig funktion eller information får kräva hover.

Hover kan ge extra återkoppling på desktop, men samma funktion ska vara
begriplig på touch-enheter och för tangentbordsanvändare.

Information som endast visas vid hover ska vara sekundär.

### 12.12 Tabeller och bred information

Tabeller och breda listor ska inte automatiskt pressas ihop till oläslighet på
små skärmar.

Möjliga strategier är:

- visa färre kolumner,
- prioritera viktigaste attributen,
- omforma raden till en vertikal struktur,
- tillåta horisontell scroll när själva tabellformen är viktig.

Valet ska göras utifrån informationens natur.

Horisontell scroll ska inte användas som standardlösning för hela sidan.

### 12.13 Typografi mellan skärmstorlekar

Typografisk hierarki ska bevaras mellan skärmstorlekar.

Text behöver inte skalas proportionellt med viewporten.

På mobil ska:

- displaytext kunna minska,
- systemetiketter förbli kompakta,
- brödtext behålla god läsbarhet,
- metadata förbli tydlig.

Läsinnehåll får inte göras så litet att mer information kan pressas in på
skärmen.

### 12.14 Spacing mellan skärmstorlekar

Spacing får komprimeras på mindre skärmar men ska fortfarande uttrycka samma
hierarki.

Det är bättre att minska stora mellanrum än att ta bort skillnaden mellan
nivåer.

En mobilvy får vara tät men ska inte bli ihoptryckt.

### 12.15 Brytpunkter ska följa layouten

Brytpunkter ska väljas när layouten behöver förändras, inte för att passa
förutbestämda enhetsnamn.

Systemet ska inte utgå från kategorier som:

- iPhone,
- iPad,
- laptop,
- desktop,

som tekniska sanningar.

Brytpunkter ska definieras utifrån när:

- kolumner inte längre fungerar,
- text blir för smal,
- navigation behöver omformas,
- komponenter behöver prioriteras om.

### 12.16 Tablet är inte bara stor mobil

Tablet kan i vissa lägen använda desktopens tvåkolumnsstruktur och i andra
mobilens mer fokuserade arbetsyta.

Designen ska tillåta detta.

Särskilt i liggande läge kan tablet ha tillräcklig bredd för:

- kontextkolumn,
- bred Documents-lista,
- Document + metadata.

I stående läge kan samma enhet behöva en mer mobil struktur.

### 12.17 Scroll ska vara naturlig

Vertikal scroll är ett normalt och förväntat beteende.

Systemet ska inte försöka pressa komplexa arbetsytor till exakt en viewport.

Sticky element får användas när de hjälper orientering eller handling, men ska
inte skapa flera konkurrerande scrollområden utan starkt skäl.

Inre scrollpaneler ska användas sparsamt eftersom de kan göra navigation och
touchinteraktion svårare.

### 12.18 Orientering ska överleva omformning

När en vy går från desktop till mobil ska användaren fortfarande kunna känna
igen:

- objektet,
- arbetsuppgiften,
- statusen,
- nästa möjliga handling.

Det visuella uttrycket får förändras, men den semantiska hierarkin ska bestå.

### 12.19 Responsiv design ska testas i verklig användning

Responsivitet ska inte bedömas enbart genom att dra webbläsarfönstret fram och
tillbaka.

Viktiga arbetsflöden ska provas på verkliga eller realistiskt emulerade små
skärmar.

Minst följande ska bedömas:

- navigation,
- Documents-lista,
- Document-läsning,
- Capture,
- Inbox-review,
- formulär,
- längre AI-tillstånd,
- felmeddelanden.

Målet är inte pixelperfektion på varje skärmstorlek.

Målet är att Dokumentverkstad förblir ett fungerande arbetsinstrument.

---

## 13. Tillgänglighet

Tillgänglighet är en del av Dokumentverkstads grundläggande kvalitet.

Systemet ska inte först designas visuellt och därefter kompletteras med
tillgänglighet.

Struktur, färg, typografi, navigation, komponenter och återkoppling ska från
början utformas så att de fungerar för olika sätt att läsa och interagera med
gränssnittet.

Tillgänglighet har företräde framför stilistisk renlärighet när de två står i
konflikt.

### 13.1 Semantisk HTML först

Dokumentverkstad är en webbapplikation och ska i första hand använda
webbplattformens egna semantiska element.

Använd exempelvis riktiga:

- länkar,
- knappar,
- rubriker,
- formulärfält,
- etiketter,
- listor,
- tabeller,

när innehållet har dessa roller.

Generiska `div`-element med JavaScript ska inte ersätta etablerade
webbkontroller utan ett tydligt skäl.

Semantik förbättrar samtidigt:

- tangentbordsanvändning,
- hjälpmedelsstöd,
- webbläsarbeteende,
- långsiktig robusthet.

### 13.2 Tangentbord

Alla centrala arbetsflöden ska kunna genomföras med tangentbord.

Det omfattar bland annat:

- global navigation,
- öppna Documents,
- använda formulär,
- öppna och stänga expanderbara sektioner,
- review-beslut,
- menyer,
- dialoger,
- Capture.

Tabbordningen ska följa en begriplig visuell och semantisk ordning.

Användaren ska inte fastna i en komponent.

### 13.3 Fokus ska vara synligt

Tangentbordsfokus ska alltid vara tydligt synligt.

Fokusindikatorn får anpassas till ivory, ebony och cinnabar men ska ha
tillräcklig kontrast och tydlighet.

Den får inte tas bort därför att webbläsarens standardfokus uppfattas som
estetiskt störande.

Fokus är ett funktionellt tillstånd.

### 13.4 Rubrikstruktur

Sidor ska ha en logisk rubrikhierarki.

Rubriknivåer ska beskriva dokumentets struktur och inte väljas enbart efter
önskad fontstorlek.

En typisk vy kan exempelvis ha:

- sidans eller objektets huvudrubrik,
- större innehållssektioner,
- undersektioner.

Visuell typografi får därefter anpassa hur dessa nivåer ser ut.

### 13.5 Färg och kontrast

Text och viktiga grafiska element ska ha tillräcklig kontrast mot bakgrunden.

Ivory och ebony ska väljas så att längre läsning fungerar väl.

Cinnabar ska också ha tillräcklig kontrast i de sammanhang där den används för
text eller semantiska markeringar.

Låg kontrast får inte användas för att skapa en mer sofistikerad eller
arkivmässig känsla om informationen blir svårläst.

### 13.6 Färg får inte vara enda signalen

Ingen viktig information ska kräva att användaren kan skilja mellan färger.

Det gäller exempelvis:

- aktiv navigation,
- fel,
- status,
- valt tillstånd,
- review-beslut.

Färg ska kompletteras med:

- text,
- geometri,
- linje,
- symbol,
- position,
- annan tydlig markering.

Detta gäller särskilt cinnabar eftersom färgen används både för identitet och
signal.

### 13.7 Textstorlek och zoom

Gränssnittet ska tåla förstoring av text och webbläsarzoom.

Innehåll ska inte försvinna, överlappa eller bli oanvändbart när användaren
ökar textstorleken.

Fasta höjder ska undvikas när innehållet behöver kunna växa.

Text ska få radbrytas.

Komponenter ska dimensioneras efter innehåll snarare än anta en exakt
textmängd.

### 13.8 Läsbarhet

Längre text ska ha:

- tillräcklig teckenstorlek,
- rimlig radlängd,
- tillräckligt radavstånd,
- tydlig styckeindelning,
- hög kontrast.

Systemtypografi och arkivmässiga etiketter får vara mer kompakta, men
läsinnehåll ska optimeras för faktisk läsning.

Estetisk identitet får inte kräva att användaren läser långa texter i
monospaced, kondenserad eller dekorativ typografi om detta försämrar
läsbarheten.

### 13.9 Språk

Sidans huvudsakliga språk ska anges semantiskt i HTML.

Text som använder ett annat språk, exempelvis en historisk devis, bör märkas
med korrekt språkattribut när detta är praktiskt och språket kan identifieras
korrekt.

Historiska eller dekorativa språkelement ska inte bära funktionell
information.

### 13.10 Formulär och etiketter

Alla formulärfält ska ha en begriplig etikett.

Placeholder-text ska inte fungera som enda etikett.

Fel ska kopplas tydligt till det fält där problemet finns.

Användaren ska kunna förstå:

- vilket fält som har problem,
- vad som är fel,
- hur det kan rättas.

Obligatoriska fält ska framgå utan att färg ensam används.

### 13.11 Felmeddelanden

Felmeddelanden ska vara begripliga både visuellt och semantiskt.

När ett formulär innehåller flera fel bör användaren få hjälp att hitta dem.

Fokus kan vid behov flyttas till en felöversikt eller första relevanta fältet,
men detta ska ske förutsägbart.

Fel ska inte endast markeras genom en tunn cinnabar linje eller färgad ram.

### 13.12 Dialoger

När en modal dialog används ska:

- fokus flyttas till dialogen,
- fokus stanna inom dialogen medan den är aktiv,
- dialogen ha en begriplig rubrik,
- stängning vara möjlig på förutsägbart sätt,
- fokus återvända till rimlig plats när dialogen stängs.

Bakomliggande innehåll ska inte kunna interageras med av misstag.

Modaler ska användas sparsamt även ur tillgänglighetsperspektiv.

### 13.13 Expanderbara sektioner

Expanderbara sektioner ska vara riktiga interaktiva kontroller.

Tillståndet öppet/stängt ska exponeras semantiskt.

Kontrollen ska kunna användas med tangentbord.

Symbolen ska komplettera den semantiska informationen och inte vara enda
indikatorn.

### 13.14 Ikoner och symboler

Dekorativa symboler ska inte läsas upp av hjälpmedel.

Semantiska symboler ska ha ett tillgängligt namn när intilliggande text inte
redan ger samma information.

Ikoner ska inte ges alternativa texter som beskriver deras utseende när det
egentligen är funktionen som är relevant.

Föredra exempelvis:

`Sök`

framför:

`Förstoringsglas`.

### 13.15 Status och dynamiska förändringar

När ett viktigt tillstånd förändras utan sidladdning ska användare av
hjälpmedel kunna få relevant återkoppling.

Det gäller exempelvis:

- AI-analys startad,
- AI-analys klar,
- uppladdning färdig,
- Capture sparad,
- fel som uppstår efter en handling.

ARIA live regions eller motsvarande mekanismer får användas där de behövs.

De ska användas sparsamt så att hjälpmedel inte bombarderas med rutinmässiga
uppdateringar.

### 13.16 Bakgrundsarbete och hjälpmedel

Långvariga operationer ska inte kräva att användaren visuellt bevakar en
spinner.

Tillståndet ska uttryckas med text och semantik.

När en bakgrundsoperation blir klar ska detta kunna upptäckas även utan att
användaren ser en färgförändring eller animation.

### 13.17 Rörelse och animation

Dokumentverkstad ska respektera användarens preferens för reducerad rörelse.

Animation ska endast användas när den tillför funktionell information.

Ingen central funktion ska kräva att användaren kan uppfatta rörelse.

Blinkande, intensivt pulserande eller andra visuellt aggressiva effekter ska
inte användas.

### 13.18 Touch och motorisk tillgänglighet

Interaktiva träffytor ska vara tillräckligt stora och ha tillräckligt
mellanrum för att minska feltryck.

Små visuella symboler får ha större osynliga träffytor.

Viktiga funktioner ska inte kräva:

- precis dragning,
- dubbeltryck,
- långa tryck,
- komplexa gester,

om en enklare kontroll kan användas.

### 13.19 Drag and drop får inte vara enda väg

Om drag and drop införs för exempelvis:

- uppladdning,
- Project-koppling,
- omordning,

ska samma grundläggande funktion kunna genomföras med en alternativ kontroll.

Drag and drop får vara en bekväm genväg, inte ett krav.

### 13.20 Skärmläsarordning och visuell ordning

Den semantiska läsordningen ska så långt som möjligt motsvara den visuella
ordningen.

CSS-layout ska inte flytta element visuellt på ett sätt som gör
tangentbords- eller skärmläsarordningen förvirrande.

Detta är särskilt viktigt när desktopens kolumner omformas till en mobil
layout.

### 13.21 Tabeller

Tabeller ska använda semantisk tabellstruktur när innehållet faktiskt är
tabulärt.

Kolumn- och radrubriker ska märkas korrekt.

Sortering ska vara begriplig både visuellt och semantiskt.

En tabell ska inte göras om till en serie `div`-element enbart för enklare
styling.

### 13.22 Dokument och originalfiler

När användaren öppnar originaldokument ska länken vara begriplig som en länk
till originalet.

Om originalet öppnas i ny flik ska detta ske konsekvent.

Dokumentverkstad ska inte anta att den inbyggda PDF-läsaren eller andra
externa dokumentformat har samma tillgänglighet som själva
Dokumentverkstadsgränssnittet.

Text och metadata som finns i systemet ska därför inte göras beroende av att
användaren kan interagera med originalfilen.

### 13.23 Historisk identitet och tillgänglighet

Den historiska devisen, geometriska ornament och andra identitetsbärande
element är sekundära till funktion.

Om ett typsnitt saknar tillräckligt stöd eller blir svårt att läsa får den
historiska presentationen förenklas.

Dekorativa element får döljas från hjälpmedel.

Dokumentverkstads identitet ska tåla att en användare upplever den genom andra
sinnen eller representationsformer än den visuella.

### 13.24 Tillgänglighet ska testas som användning

Tillgänglighet ska inte reduceras till automatisk validering.

Automatiska verktyg är användbara men kan inte avgöra om ett arbetsflöde är
begripligt eller praktiskt.

Viktiga vyer ska därför regelbundet provas med:

- tangentbord utan mus,
- tydlig fokusnavigation,
- förstoring/zoom,
- reducerad rörelse,
- åtminstone grundläggande skärmläsartest.

Särskild uppmärksamhet ska ges åt:

- global navigation,
- Documents,
- Document,
- Capture,
- Inbox-review,
- formulär,
- dialoger,
- dynamiska AI-tillstånd.

### 13.25 Tillgänglighet och särprägel är förenliga

Dokumentverkstad behöver inte bli visuellt generiskt för att vara
tillgängligt.

Ivory, ebony, cinnabar, geometriska symboler, maskinell typografi och den
arkivmässiga identiteten kan behållas.

Det som krävs är att systemets särprägel byggs ovanpå:

- semantisk struktur,
- tydlig kontrast,
- begriplig navigation,
- robust interaktion,
- läsbar text.

Tillgänglighet ska inte neutralisera Dokumentverkstads identitet.

Den ska göra identiteten möjlig att använda.

## 14. Anti-patterns

Dokumentverkstads visuella identitet är tillräckligt särpräglad för att det
ska vara lätt att imitera ytan utan att bevara principerna bakom den.

Detta avsnitt beskriver lösningar som normalt ska undvikas även när de kan se
rimliga ut isolerat.

Anti-patterns är inte absoluta förbud mot varje enskild visuell teknik.

De beskriver återkommande riktningar som riskerar att göra Dokumentverkstad:

- mer generiskt,
- mer dekorativt,
- mer administrativt,
- mer splittrat,
- mindre begripligt,
- mindre användbart.

### 14.1 Card soup

Dokumentverkstad ska inte organiseras som ett rutnät av fristående cards bara
för att cards är en vanlig webbkomponent.

Undvik exempelvis:

- ett card för varje Document,
- ett card för varje metadatafält,
- ett card för varje Knowledge Object,
- cards inuti cards,
- stora rundade behållare runt varje informationsgrupp.

Cards är lämpliga när innehållet faktiskt är fristående och behöver en tydlig
egen behållare.

I övrigt ska struktur i första hand skapas genom:

- typografi,
- alignment,
- spacing,
- kolumner,
- tunna linjer.

Dokumentverkstad ska kännas mer som en katalog, arbetsyta eller
informationsapparat än som en samling widgets.

### 14.2 Dashboard som universalmodell

Varje ny sida ska inte automatiskt få:

- statistikpaneler,
- senaste aktivitet,
- quick actions,
- statuskort,
- diagram,
- widgets.

En dashboard är motiverad endast om användaren faktiskt behöver en överblick
över flera samtidiga informationsströmmar.

Inbox ska exempelvis vara en arbetskö, inte en dashboard över att Inbox finns.

Documents ska vara ett arkiv att arbeta i, inte en dashboard över antalet
Documents.

### 14.3 Administrationsgränssnitt som mental modell

Användaren ska inte behöva tänka på Dokumentverkstad som en samling tabeller
som ska administreras.

Undvik navigation och etiketter som huvudsakligen speglar:

- databastabeller,
- interna objekttyper,
- tekniska processer,
- implementationens katalogstruktur.

Gränssnittet ska utgå från användarens arbete med:

- dokument,
- läsning,
- tankar,
- sammanhang,
- granskning,
- sökning.

Att systemet internt har fler begrepp än användaren behöver se är normalt.

### 14.4 Exponera inte domänmodellen av symmetriskäl

Om Summary, Claim, Insight och Question finns som separata typer innebär det
inte att de ska få:

- varsin global navigationsflik,
- varsin startsida,
- varsin färg,
- varsin ikon,
- varsin fullständig CRUD-yta.

Domänmodellens symmetri är inte ett designmål.

Informationsarkitekturen ska följa arbetsflöden och behov.

### 14.5 Klassificering före arbete

Gränssnittet ska inte kräva att användaren organiserar material innan det går
att använda.

Undvik flöden där ett nytt Document eller en Capture först måste få:

- Project,
- kategori,
- taggar,
- status,
- typ,

om informationen inte verkligen behövs för den aktuella handlingen.

> Capture first, organize later.

ska även vara en interaktionsprincip.

### 14.6 Projects som mappar

Projects ska inte utformas så att de får användaren att uppfatta dem som en
exklusiv mapphierarki.

Undvik exempelvis:

```text
Arkiv
└── Project A
    └── Project B
        └── Document
```

om detta inte motsvarar den faktiska modellen.

Ett Document kan ingå i flera sammanhang och behöver inte ha ett Project alls.

Navigation, breadcrumbs och språk ska inte antyda en strikt hierarki där ingen
sådan finns.

### 14.7 Taggar av gammal vana

Taggar ska inte införas enbart därför att många kunskapssystem har taggar.

En ny klassifikationsmekanism ska svara mot ett verkligt problem som inte
redan löses bättre genom exempelvis:

- Projects,
- metadata,
- sökning,
- framtida semantisk återvinning.

Designreferenser som innehåller `TAGS` är inte krav på att taggar ska införas.

### 14.8 Synliga interna identifierare

Interna databasidentifierare ska normalt inte exponeras som del av
Dokumentverkstads visuella stil.

Undvik exempelvis etiketter som:

```text
DOC 0241
CAP 0004
KO 0832
```

om dessa värden saknar verklig betydelse för användaren.

Maskinell typografi och systemkaraktär ska skapas genom designspråket, inte
genom att tekniska implementationdetaljer görs synliga.

Identifierare får visas där de fyller en faktisk funktion, exempelvis vid
diagnostik eller support.

### 14.9 Dekorativ metadata

Metadata ska visas därför att den hjälper användaren att:

- identifiera,
- bedöma,
- hitta,
- förstå,
- arbeta med materialet.

Undvik att lägga till tekniskt klingande etiketter, räknare eller
klassifikationsfält enbart för att gränssnittet ska se arkivmässigt ut.

Dokumentverkstads informationsrikedom ska komma från verklig information.

### 14.10 Pseudoarkiv och historisk pastisch

Dokumentverkstad ska inte försöka se gammalt ut.

Undvik:

- pergamenttexturer,
- gulnat papper,
- artificiella kaffefläckar,
- tryckslitage,
- fejkade stämplar,
- dekorativa sigill,
- skrivmaskinspastisch,
- historiserande ramverk.

Arkivkaraktären ska komma från:

- struktur,
- katalogisering,
- typografi,
- materialkänsla,
- precision,
- identitet.

Systemet är samtida även när det har historiska resonanser.

### 14.11 Ockult dekorationslager

Den geometriska och ockulta underströmmen ska inte utvecklas till ett
illustrationssystem som läggs ovanpå varje sida.

Undvik:

- pentagram som generella knappar,
- mystiska sigill för vanliga funktioner,
- astrologiska symboler utan semantisk grund,
- dekorativa diagram bakom innehåll,
- ornament i varje tom yta.

Geometrin ska skapa språk, rytm och identitet.

Den ska inte skapa en temapark.

### 14.12 Hemlig ikonografi

Ingen viktig funktion ska kräva att användaren lär sig ett privat
symbolalfabet.

En cirkel, triangel eller diamant får få stabil semantisk betydelse när detta
växer fram naturligt.

Men vanliga handlingar som:

- sök,
- redigera,
- stäng,
- tillbaka,
- ladda upp,

ska inte ersättas med kryptiska symboler bara för att passa identiteten.

När etablerade webbkonventioner fungerar ska de normalt användas.

### 14.13 Cinnabar överallt

Cinnabar är en accent och signal, inte Dokumentverkstads normala
bakgrundsfärg.

Undvik stora mängder cinnabar i:

- panelbakgrunder,
- stora knappar överallt,
- rubrikfält,
- tabellrader,
- dekorativa ytor.

Om för mycket är accentuerat är ingenting accentuerat.

Ivory och ebony ska bära huvuddelen av gränssnittet.

### 14.14 Regnbågsstatus

Olika systemtillstånd ska inte automatiskt få varsin färg.

Undvik exempelvis:

- grönt = klart,
- gult = väntar,
- orange = review,
- blått = information,
- lila = AI,
- rött = fel,

som generellt statussystem.

Det skulle försvaga både designsystemets sammanhållning och tillgängligheten.

Status ska i första hand uttryckas genom:

- text,
- geometri,
- fylld/ofylld form,
- typografi,
- position,

med cinnabar där accent verkligen behövs.

### 14.15 Allt är en badge

Små kapslar eller badges ska inte användas för varje metadata- eller
statusvärde.

En rad som består av:

```text
[2025] [PDF] [AI COMPLETE] [3 CAPTURES] [PROJECT X]
```

blir snabbt visuellt fragmenterad.

Metadata ska normalt vara typografi.

Badges eller liknande slutna former ska reserveras för fall där själva
behållaren hjälper användaren att tolka eller interagera med informationen.

### 14.16 Rundade rektanglar som standardsvar

Varje kontroll behöver inte vara en rundad rektangel.

Dokumentverkstads geometriska språk bör i första hand bygga på:

- linjer,
- typografi,
- enkla ytor,
- precisa kanter,
- geometriska markörer.

Rundning får användas när den förbättrar kontrollens begriplighet eller
ergonomi, men ska inte vara den visuella grundformen för hela systemet.

### 14.17 Skuggor som informationshierarki

Drop shadows ska användas sparsamt.

De ska framför allt kunna markera verkliga lager, exempelvis en tillfällig
dialog ovanpå en arbetsyta.

Vanliga sektioner och listor ska inte behöva skuggor för att skiljas åt.

Hierarki ska i första hand finnas i layouten.

### 14.18 Gradienter

Gradienter hör inte till Dokumentverkstads visuella språk.

De ska inte användas för:

- knappar,
- bakgrunder,
- status,
- branding,
- dekoration.

Färgplan ska vara tydliga och materiella.

### 14.19 Överdriven animation

Systemet ska inte kännas levande genom ständig rörelse.

Undvik:

- animerade bakgrunder,
- pulserande navigation,
- svepande highlights,
- långsamma sidövergångar,
- dekorativa laddningsanimationer.

Rörelse ska representera en faktisk förändring eller hjälpa användaren förstå
vad som händer.

### 14.20 AI som spektakel

AI ska inte ges en särskild magisk estetik som skiljer den från resten av
systemet.

Undvik:

- glödande AI-paneler,
- gradienter,
- stjärnstoft,
- robotikoner,
- mystiska animationer,
- antropomorfa statusmeddelanden.

AI är en funktion i Dokumentverkstad.

Det ska vara tydligt när AI används och var innehållet kommer ifrån, men AI
ska inte visuellt bli systemets huvudperson.

### 14.21 Bekräftelse på allt

Varje handling behöver inte en dialog:

`Är du säker?`

Överdrivna bekräftelser gör användaren mindre uppmärksam på de få situationer
där bekräftelsen verkligen är viktig.

Reversibla handlingar ska i första hand göras säkra genom:

- undo,
- Trash,
- historik,
- återställning.

Starka bekräftelser ska reserveras för verkligt destruktiva eller
svåråterkalleliga handlingar.

### 14.22 Toast som systemets röst

Dokumentverkstad ska inte kommunicera huvudsakligen genom tillfälliga
toast-meddelanden.

Tillstånd som fortsätter att vara relevanta ska finnas kvar på den plats där
de hör hemma.

Toast är ett komplement, inte en ersättning för informationsarkitektur.

### 14.23 Spinner utan förklaring

En ensam spinner ska inte användas för långvarigt arbete.

Användaren behöver veta vad som händer.

Föredra:

```text
AI-analys pågår
```

framför endast en roterande symbol.

När operationen tar längre tid behöver tillståndet dessutom överleva
navigation bort från den aktuella sidan.

### 14.24 Falsk precision

Systemet ska inte låtsas veta mer än det vet.

Undvik exempelvis:

- påhittade progressprocent,
- falskt exakta kostnadsuppskattningar,
- tidsangivelser utan faktisk grund,
- AI-confidence som presenteras som objektiv sannolikhet utan definierad
  innebörd.

Osäker information ska beskrivas som osäker.

### 14.25 Funktioner som bara fungerar visuellt

Ingen central funktion ska bero på:

- hover,
- färg,
- animation,
- exakt spatial position,
- drag and drop,
- ett svårtolkat tecken.

Det visuella uttrycket ska förstärka den semantiska funktionen.

Det ska inte vara den enda bäraren av den.

### 14.26 Desktop nedpressad till mobil

Mobilversionen ska inte vara desktopgränssnittet med:

- mindre text,
- smalare kolumner,
- fler radbrytningar.

När utrymmet förändras ska prioriteringen förändras.

Kontext får flytta, metadata får komprimeras och navigation får byta fysisk
form.

### 14.27 Separat mobilprodukt

Samtidigt ska Dokumentverkstad inte utveckla en separat mobil
informationsarkitektur med andra begrepp och arbetsflöden.

Mobil och desktop är två uttryck för samma system.

Det ska gå att förstå den ena efter att ha lärt sig den andra.

### 14.28 Ny teknik som designsvar

Ett UX-problem ska inte automatiskt lösas genom att introducera:

- ett JavaScript-framework,
- en komponentplattform,
- client-side state,
- realtidsprotokoll,
- nya externa beroenden.

Teknik får införas när den löser ett konkret problem bättre än enklare
alternativ.

Designsystemet beskriver önskat beteende, inte vilken teknisk stack som måste
användas.

### 14.29 Implementera skissen i stället för systemet

Designreferenserna ska inte reproduceras pixel för pixel.

De innehåller:

- visuella idéer,
- äldre informationsarkitektur,
- hypotetiska funktioner,
- exempeldata.

När en skiss står i konflikt med:

1. aktuell domänmodell,
2. aktuell implementation plan,
3. detta designsystem,

ska skissen ge vika.

Det är formspråket som ska överföras, inte skärmbildens historiska
implementation.

### 14.30 Polera bort friktion i stället för att lösa den

En snyggare version av ett dåligt arbetsflöde är fortfarande ett dåligt
arbetsflöde.

Om användaren exempelvis måste göra för många steg för att:

- importera ett Document,
- skapa en Capture,
- hitta tillbaka till en lista,
- granska AI-resultat,

ska problemet inte lösas genom snyggare knappar.

Arbetsflödet ska först förenklas.

Design är funktion.

---

## 15. Förhållande till domänmodell och implementation

Designsystemet beskriver hur Dokumentverkstad organiserar, uttrycker och
gestaltar den funktionalitet som faktiskt finns.

Det definierar inte på egen hand:

- nya domänobjekt,
- nya relationer,
- nya lagringsmodeller,
- nya arbetsflöden,
- nya produktfunktioner.

Design och domänmodell påverkar varandra, men de har olika ansvar.

### 15.1 Dokumentens roller

Dokumentverkstads centrala styrande dokument har olika roller.

**Domänmodellen**

beskriver vilka begrepp som finns i systemet och hur de relaterar till
varandra.

**IMPLEMENTATION_PLAN**

beskriver vad som ska utvecklas och i vilken ordning.

**DESIGN_SYSTEM**

beskriver hur funktioner och information ska organiseras, uttryckas och
bete sig i användargränssnittet.

**Designreferenser**

visar exempel på visuell riktning och komposition.

**UX_NOTES**

samlar observationer från verklig användning, friktion, idéer och frågor som
ännu inte nödvändigtvis är beslutade.

Dessa dokument kompletterar varandra men ska inte användas som om de vore
utbytbara.

### 15.2 Prioritetsordning vid konflikt

När källorna motsäger varandra ska följande grundordning användas:

1. aktuell domänmodell,
2. aktuell `IMPLEMENTATION_PLAN`,
3. detta `DESIGN_SYSTEM`,
4. designreferenser.

Verklig användning kan däremot visa att något av dessa dokument behöver
ändras.

Då ska själva beslutet göras explicit i rätt dokument i stället för att en
implementation tyst börjar avvika från den dokumenterade modellen.

### 15.3 UX_NOTES är observationsyta

`UX_NOTES` har en annan roll än de normerande dokumenten.

En anteckning där kan vara:

- en observation,
- ett problem,
- en idé,
- en hypotes,
- en framtida möjlighet.

Att något finns i `UX_NOTES` innebär därför inte automatiskt att det ska
implementeras.

När en observation mognar till ett beslut ska den uttryckas i rätt
normerande dokument eller iteration.

### 15.4 Designsystemet får inte skapa domänobjekt

En visuell lösning får inte smyga in nya domänbegrepp.

Om en design exempelvis verkar behöva:

- Tags,
- Favorites,
- Collections,
- Document status,
- nya Capture-typer,
- nya relationstyper,

ska detta först bedömas som en produkt- och domänfråga.

CSS eller templates ska inte göra ett hypotetiskt begrepp verkligt utan att
det finns ett uttryckligt beslut.

### 15.5 Domänmodellen behöver inte exponeras fullständigt

Motsatsen gäller också.

Alla interna begrepp behöver inte ha en synlig representation.

Ett tekniskt objekt kan finnas för att systemet behöver det utan att
användaren behöver känna till det.

Gränssnittet ska visa den minsta modell användaren behöver för att förstå och
utföra arbetet.

### 15.6 Användarspråk före intern terminologi

När intern och extern terminologi skiljer sig ska gränssnittet använda det
språk som bäst beskriver användarens arbete.

Interna begrepp får behållas i:

- kod,
- databas,
- diagnostik,
- utvecklardokumentation.

Användargränssnittet ska inte exponera dem enbart för att undvika en
översättning mellan kod och UI.

Samtidigt ska centrala etablerade begrepp som `Document`, `Project` och
`Capture` användas konsekvent när de är en del av produktens faktiska språk.

### 15.7 Server-rendering är grundläget

Dokumentverkstad ska även under visuell vidareutveckling behålla enkel,
robust webbarkitektur som grund.

Server-renderade sidor och normala webblänkar är standard.

JavaScript ska införas där det tydligt minskar friktion, exempelvis för:

- bakgrundsstatus,
- progressiv uppdatering,
- vissa paneler,
- förbättrad Capture-interaktion,
- andra lokala dynamiska beteenden.

Gränssnittet ska inte göras till en single-page application bara för att
formspråket blir mer avancerat.

### 15.8 Progressive enhancement

När det är rimligt ska kärnarbetsflödet fungera med webbplattformens
grundfunktioner och därefter förbättras med JavaScript.

Det ger fördelar för:

- robusthet,
- tillgänglighet,
- testbarhet,
- underhåll,
- lång livslängd.

Det betyder inte att all funktion måste fungera helt utan JavaScript.

Det betyder att dynamik ska läggas till medvetet där den behövs.

### 15.9 Design tokens före lokala speciallösningar

När färg, typografi, spacing, linjer och andra återkommande värden börjar
implementeras ska de uttryckas genom gemensamma tokens eller motsvarande
centrala variabler.

Exempel:

```css
--color-ivory: ...;
--color-ebony: ...;
--color-cinnabar: ...;

--font-system: ...;
--font-reading: ...;
--font-inscription: ...;

--space-1: ...;
--space-2: ...;
--space-3: ...;

--border-thin: ...;
```

Exakta namn och värden bestäms under implementationen.

Syftet är att systemets visuella grammatik ska kunna justeras centralt och
förbli sammanhängande.

### 15.10 Återanvänd mönster, inte markup till varje pris

Två vyer som har samma informationsmönster ska i möjligaste mån använda samma
komponentlogik och visuella regler.

Det betyder inte att all HTML måste abstraheras till en generell komponent.

Återanvändning är värdefull när den:

- minskar inkonsekvens,
- förenklar underhåll,
- uttrycker en verklig gemensam struktur.

Abstraktion som gör enkel markup svårare att förstå har inget egenvärde.

### 15.11 CSS ska uttrycka ett system

CSS ska inte växa som en samling undantag för enskilda sidor.

Föredra regler för:

- typografiska roller,
- layoutroller,
- listmönster,
- statusmönster,
- formulär,
- knappar,
- spacing,
- responsivt beteende.

Sidunika regler får finnas när sidan verkligen har ett unikt behov.

Målet är inte maximal generalisering utan begriplig visuell konsekvens.

### 15.12 Tillstånd ska ha en verklig källa

Visuella statusmarkeringar ska motsvara verkligt systemtillstånd.

UI ska inte härleda viktiga tillstånd genom osäkra heuristiker när
applikationen kan uttrycka tillståndet explicit.

Det gäller särskilt:

- ingest,
- AI-operationer,
- review,
- sparande,
- fel,
- Trash.

Designen kan därmed tydliggöra när implementationen behöver ett bättre
tillståndsbegrepp, men själva domänändringen ska göras explicit.

### 15.13 Design får avslöja modellproblem

När en funktion är svår att presentera begripligt kan problemet ligga i
domänmodellen eller arbetsflödet snarare än i CSS.

Exempelvis kan ett otydligt UI visa att:

- två tillstånd blandats ihop,
- ett objekt har oklart ansvar,
- en relation saknar tydlig betydelse,
- ett arbetsflöde kräver för många beslut.

I sådana fall ska designarbetet få leda till en diskussion om modellen.

Lösningen ska inte automatiskt vara ett mer komplicerat gränssnitt.

### 15.14 Implementation ska utgå från verkliga vyer

Designsystemet ska prövas mot verkliga arbetsytor.

En lämplig ordning under Iteration 9 är exempelvis:

1. gemensam designgrund och navigation,
2. Documents och Document,
3. Inbox och AI-review,
4. Projects och Capture.

Varje steg ska använda verkligt innehåll och verkliga arbetsflöden.

Ett fristående komponentbibliotek med hypotetiska exempel ska inte bli ett
mål i sig.

### 15.15 Visuell migration får ske stegvis

Dokumentverkstad behöver inte byggas om visuellt i ett enda stort steg.

Gemensamma designprinciper kan införas successivt så länge systemet inte
lämnas i ett långvarigt tillstånd där olika delar verkar tillhöra helt olika
produkter.

Gemensamma:

- tokens,
- typografi,
- navigation,
- layoutprinciper,
- komponentmönster,

bör etableras tidigt så att senare vyer kan bygga vidare på samma grund.

### 15.16 Funktion ska bevaras under redesign

Iteration 9 är i första hand konsolidering av arbetsytan.

En visuell ombyggnad ska därför inte av misstag förändra eller ta bort
fungerande funktionalitet.

Före och efter en större vyändring ska de verkliga arbetsflödena kontrolleras.

Det gäller särskilt:

- import,
- Document-navigation,
- metadataredigering,
- Capture,
- Project-koppling,
- AI-review,
- Trash och återställning.

### 15.17 Ingen ny funktion för att fylla designen

Om en skiss har en tom yta eller designsystemet möjliggör en komponent behöver
den inte fyllas med något.

Det är bättre med lugnt utrymme än med en funktion som saknar verkligt behov.

Designen ska anpassa sig till produktens innehåll.

Produkten ska inte utökas för att göra designen symmetrisk.

### 15.18 Verkliga data före placeholder-estetik

Designbeslut ska så snart som möjligt bedömas med verkliga Documents,
Projects, Captures och AI-resultat.

Placeholder-data tenderar att vara:

- kortare,
- renare,
- mer regelbunden,
- mer komplett

än verklig information.

Dokumentverkstad måste tåla:

- mycket långa titlar,
- saknade årtal,
- märkliga organisationsnamn,
- många Captures,
- inga Captures,
- lång Summary-text,
- olika mängd AI-innehåll.

Det verkliga arkivet är designens viktigaste testdata.

### 15.19 Prestanda är en UX-egenskap

En visuellt lyckad vy som tar flera sekunder att öppna är inte färdig.

Iteration 9 ska därför inte bara bedöma:

- färg,
- typografi,
- spacing,
- navigation.

Den ska också uppmärksamma:

- svarstid,
- sidladdning,
- blockerande operationer,
- onödiga omladdningar,
- återställning av användarens kontext.

Visuell förbättring får inte köpas genom tydligt sämre prestanda.

### 15.20 Bakgrundsjobb ska följa designsystemets tillståndsmodell

När långvariga AI-operationer senare flyttas till bakgrundsjobb ska
implementationen använda de principer som definierats i avsnitt 11.

Tekniken kan exempelvis behöva representera att ett jobb är:

- väntande,
- pågående,
- färdigt,
- misslyckat.

Men UI ska endast exponera den detaljnivå användaren behöver.

Bakgrundsjobbet är en implementation av ett arbetsflöde, inte en ny
användardomän.

### 15.21 Responsivitet ska byggas in, inte läggas på

Desktop ska inte färdigställas som ett fast gränssnitt och därefter få en
separat mobil-CSS som försöker reparera det.

När komponenter och layout implementeras ska deras beteende vid mindre bredd
övervägas samtidigt.

Det innebär inte att alla brytpunkter måste lösas i första steget.

Det innebär att den strukturella HTML:en inte ska göra responsiviteten
onödigt svår.

### 15.22 Tillgänglighet är ett implementationskrav

Principerna i avsnitt 13 ska kontrolleras under implementation, inte efter att
Iteration 9 betraktats som klar.

Det gäller särskilt:

- semantiska element,
- tangentbord,
- fokus,
- kontrast,
- formuläretiketter,
- dynamiska statusmeddelanden,
- dialoger,
- touchytor.

En estetiskt korrekt komponent som inte går att använda tillgängligt är inte
en korrekt implementerad komponent.

### 15.23 Externa beroenden ska motiveras

Nya bibliotek, typsnitt och frontendberoenden ska införas med hänsyn till
Dokumentverkstads krav på:

- lång livslängd,
- lokal drift,
- portabilitet,
- enkel installation,
- robusthet.

Ett beroende ska lösa ett verkligt behov.

En liten visuell detalj är normalt inte tillräckligt skäl för ett stort
frontendberoende.

### 15.24 Nätverksberoende design ska undvikas

Dokumentverkstads visuella grund ska inte kräva att externa tjänster är
tillgängliga.

Typsnitt, ikoner och andra centrala designresurser ska så långt som möjligt
kunna levereras tillsammans med applikationen eller genom robusta lokala
alternativ.

Ett tillfälligt avbrott hos en extern CDN ska inte förändra gränssnittets
grundläggande funktion eller identitet.

### 15.25 Designsystemet är levande

Detta dokument är normerande men inte orubbligt.

Verklig användning kan visa att:

- en komponent saknas,
- en princip är för strikt,
- en navigationsmodell är fel,
- en visuell konvention skapar friktion,
- ett nytt arbetsflöde behöver ett nytt mönster.

När sådant upptäcks ska designsystemet ändras medvetet.

En lokal avvikelse ska inte få växa till en ny informell standard utan att
principen diskuteras och dokumenteras.

### 15.26 Målet

Designsystemets slutliga uppgift är inte att göra alla sidor lika.

Det är att göra dem begripliga som delar av samma verktyg.

Efter längre användning ska Dokumentverkstad kännas som en plats där
användaren intuitivt vet:

- var information brukar finnas,
- vad som går att göra,
- hur ett tillstånd uttrycks,
- hur man kommer tillbaka,
- vad som är eget innehåll,
- vad som kommer från AI,
- vad som är beständigt.

När systemet fungerar som bäst ska gränssnittet inte kräva mycket medveten
uppmärksamhet.

Det ska ge form åt arbetet och sedan träda tillbaka.
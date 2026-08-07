# Designprinciper för Dokumentverkstad

## Syfte

Detta dokument kompletterar Manifestet för Dokumentverkstad.

Manifestet beskriver projektets filosofi och mål.

Designprinciperna beskriver hur utvecklingsbeslut ska fattas när flera lösningar är möjliga.

Om en designprincip kommer i konflikt med manifestet gäller alltid manifestet.

---

# 1. Enkelhet före komplexitet

När flera lösningar uppfyller samma krav ska Dokumentverkstad välja den enklaste.

Komplexitet får endast införas när den ger ett tydligt och varaktigt värde.

Målet är inte att bygga det mest avancerade systemet, utan det mest begripliga.

Systemet ska minimera den kognitiva kostnaden för att fånga en tanke.

---

# 2. Abstraktioner ska växa fram

Dokumentverkstad ska utgå från konkreta objekt och arbetsflöden.

Abstraktioner ska införas först när de visar sig förenkla systemet eller bättre beskriva användarens arbete.

Systemet ska inte modellera idealiserade begrepp enbart därför att de är teoretiskt eleganta.

Abstraktioner betraktas som resultat av kunskapsbildning snarare än som dess utgångspunkt.

---

# 3. Begriplighet före magi

Systemet ska alltid kunna förklara vad det gjort.

Användaren ska kunna förstå:

* vilka steg som utförts,
* vilka AI-modeller som använts,
* vilka regler som tillämpats,
* vad som fortfarande är osäkert.

Dokumentverkstad ska inte dölja sin arbetsprocess bakom automatisering.

---

# 4. Reversibilitet före bekvämlighet

Irreversibla handlingar ska undvikas.

Det ska vara lättare att ångra ett beslut än att återställa förlorad information.

Därför ska systemet:

* använda versionshistorik,
* ha återställningsbar papperskorg,
* aldrig skriva över original,
* aldrig ersätta tidigare analyser utan att skapa en ny version.

---

# 5. Lokal behandling före molnet

Dokumentverkstad ska alltid försöka lösa en uppgift med den enklaste tillgängliga resursen.

Prioriteringsordningen är:

1. vanlig programkod,
2. lokal AI,
3. moln-AI.

Moln-AI används endast när dess högre kvalitet motiverar kostnaden och sekretesskraven tillåter det.

---

# 6. AI är en medarbetare

AI producerar förslag.

Användaren fattar beslut.

Systemet ska därför utformas så att AI aldrig blir en dold auktoritet.

Alla AI-genererade kunskapsobjekt ska kunna granskas.

---

# 7. Proveniens är standard

Alla objekt ska kunna spåras.

Det ska alltid gå att se:

* ursprung,
* skapandetid,
* modell,
* promptversion,
* användarens redigeringar,
* historik.

Proveniens är inte extra metadata.

Den är en del av kunskapen.

---

# 8. Öppna format före inlåsning

Dokumentverkstad ska lagra information i öppna och dokumenterade format.

Systemet ska inte skapa onödiga beroenden till en viss:

* databas,
* AI-leverantör,
* molntjänst,
* klient,
* operativsystem.

Användaren ska alltid kunna ta med sig sitt arbete.

---

# 9. Modeller är utbytbara

Systemet ska känna till förmågor, inte specifika modeller.

Kod ska inte bero direkt på OpenAI, Anthropic eller någon annan leverantör.

Alla AI-anrop ska gå genom ett gemensamt providerlager.

---

# 10. Progressiv förbättring

Den första versionen ska vara liten men komplett.

Ny funktionalitet ska byggas ovanpå en stabil grund.

En funktion ska fungera innan den blir smart.

---

# 11. Arbetsflödet före tekniken

Utvecklingen ska utgå från hur människor arbetar.

Teknik väljs för att stödja arbetsflödet.

Arbetsflödet får aldrig anpassas enbart för att passa ett ramverk eller en viss teknik.

---

# 12. Gränssnittet ska vara tyst

Gränssnittet ska hjälpa användaren att arbeta.

Det ska inte försöka imponera.

Animationer, dashboards och visuella effekter ska endast införas om de förbättrar förståelsen.

Systemet ska presentera arbetet, inte sig självt.

---

# 13. Beslut före information

Dokumentverkstad ska hjälpa användaren att fatta beslut.

Den ska inte visa information bara för att den finns.

Varje vy ska besvara frågan:

> Vilket beslut behöver användaren kunna fatta här?

Om inget beslut stöds bör informationen sannolikt visas någon annanstans.

---

# 14. Kumulativ utveckling

Ny funktionalitet ska bygga vidare på tidigare funktionalitet.

Systemet ska inte omarbeta fungerande delar utan tydlig anledning.

Teknisk skuld ska hanteras kontinuerligt, men inte genom stora omskrivningar utan konkret nytta.

---

# 15. Mät innan du optimerar

Prestandaoptimering ska baseras på verkliga problem.

Ingen del av systemet ska göras mer komplicerad enbart för hypotetiska framtida behov.

---

# 16. Självobservation utan självrevision

Dokumentverkstad får analysera sitt eget arbete.

Den får föreslå förbättringar.

Den får inte ändra sitt eget beteende utan användarens uttryckliga godkännande.

---

# 17. Dokumentation är en del av systemet

Manifestet, designprinciperna, domänmodellen och arkitekturen är inte bilagor.

De är en del av Dokumentverkstad.

När projektet utvecklas ska dokumentationen utvecklas tillsammans med koden.

Kod och dokumentation ska beskriva samma system.

---

# 18. Systemet ska kunna hantera flera dokumentformat

Dokumentverkstad ska inte vara bundet till PDF. Ett dokument är ett innehållsobjekt med en eller flera representationer och formatberoende källpositioner.

Den första implementationen stöder PDF; EPUB är nästa prioriterade format.

Arkitekturen ska utformas så att stöd för nya dokumentformat kan läggas till utan att övriga delar av systemet behöver förändras.

Analys, kunskapsobjekt och användargränssnitt ska i största möjliga utsträckning vara oberoende av dokumentets ursprungliga filformat.

---

# 19. Systemet ska stödja kunskapsarbete även utan digitalt källmaterial

Dokumentverkstad ska kunna användas även när källmaterialet inte finns tillgängligt som en digital fil.

Användaren ska kunna registrera ett dokument manuellt, skapa Knowledge Objects och ange källpositioner såsom kapitel och sidnummer.

En digital fil ska kunna kopplas till dokumentet senare utan att tidigare anteckningar, relationer eller historik behöver återskapas.

Digital tillgång till källmaterialet ska ge ytterligare möjligheter till analys och förankring, men får inte vara ett villkor för kunskapsarbete i Dokumentverkstad.

---

# 20. Semantisk precision ska vara frivillig

Det vill säga:

* Den som bara vill säga "de här två sakerna hör ihop" ska kunna göra det.
* Den som senare vill precisera hur de hör ihop ska också kunna göra det.
* Systemet ska aldrig kräva högre precision än vad användaren för tillfället har.

---

# 21. Lång livslängd före trend

Dokumentverkstad ska utformas för att kunna användas och underhållas under lång tid.

Vid val mellan en modern men kortlivad lösning och en enklare, stabil och väldokumenterad lösning ska den senare normalt väljas.

Teknikval ska värderas utifrån:

* långsiktig stabilitet,
* begriplighet,
* dokumentation,
* underhållbarhet,
* möjlighet att ersätta en komponent utan att hela systemet behöver skrivas om.

Dokumentverkstad ska därför föredra:

* öppna standarder,
* enkla filformat,
* serverrenderad webb,
* tydliga API:er,
* modulär arkitektur,
* utbytbara komponenter.

All data som Dokumentverkstad producerar eller lagrar ska kunna exporteras i öppna och dokumenterade format.

Det gäller bland annat:

* originaldokument,
* metadata,
* sammanfattningar,
* claims,
* insights,
* projekt,
* relationer,
* historik,
* anteckningar,
* open threads,
* konfiguration.

Användarens kunskap ska aldrig vara inlåst i Dokumentverkstad.

En annan utvecklare ska i framtiden kunna skriva ett nytt program som kan läsa Dokumentverkstads arkiv utan att behöva återskapa dess interna implementation.

Dokumentverkstad ska därför betrakta sitt eget arkiv som en offentlig och dokumenterad struktur, inte som en intern databas.

Målet är att Dokumentverkstad ska kunna leva längre än de ramverk, AI-modeller och molntjänster som används för att bygga den.

---

# Avslutning

Dokumentverkstad ska utvecklas långsamt, medvetet och kumulativt.

Varje ny funktion ska göra systemet tydligare, inte mer imponerande.

Det bästa designbeslutet är ofta det som användaren aldrig behöver tänka på.

När tvekan uppstår ska utvecklingen återvända till Manifestet och fråga:

> Hjälper detta användaren att bygga en långsiktig kunskapsbas genom dokument?

Om svaret är nej bör funktionen omarbetas eller avstås.

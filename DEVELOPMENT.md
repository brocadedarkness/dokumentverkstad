# DEVELOPMENT.md

## Syfte

Detta dokument beskriver hur Dokumentverkstad ska vidareutvecklas.

Målet är att förändringar ska vara begripliga, spårbara och följa projektets grundläggande idéer. Kod är en implementation av projektets dokumentation, inte dess primära specifikation.

---

# Grundprincip

Dokumentationen är projektets auktoritativa källa.

Vid konflikt mellan kod och dokumentation ska dokumentationen betraktas som korrekt, om inte dokumentationen uttryckligen bedöms vara föråldrad och först uppdateras.

Kod ska implementera dokumentationen.

---

# Dokumentens ansvar

Projektets dokument har följande ansvar:

| Dokument               | Ansvar                                  |
| ---------------------- | --------------------------------------- |
| `MANIFEST.md`          | Varför Dokumentverkstad finns.          |
| `DESIGN_PRINCIPLES.md` | Hur designbeslut ska fattas.            |
| `DOMAIN_MODEL.md`      | Vilka begrepp som existerar.            |
| `ARCHITECTURE.md`      | Hur systemet är uppbyggt.               |
| `DEPLOYMENT.md`        | Hur den aktuella installationen ser ut. |
| `WORKFLOWS.md`         | Hur användaren arbetar med systemet.    |
| `UI.md`                | Hur användargränssnittet fungerar.      |
| `DEVELOPMENT.md`       | Hur projektet vidareutvecklas.          |

Varje förändring bör i första hand beskrivas i rätt dokument innan implementation påbörjas.

---

# Prioritetsordning

Vid motstridiga uppgifter gäller följande prioritet:

1. Manifest
2. Design Principles
3. Domain Model
4. Architecture
5. Deployment
6. Workflows
7. UI
8. Kod

En lägre nivå får aldrig medvetet bryta mot en högre utan att den högre nivån först ändras.

---

# Utvecklingscykel

Normalt utvecklingsarbete följer denna ordning:

1. Identifiera ett behov eller en idé.
2. Avgör vilket eller vilka dokument som påverkas.
3. Uppdatera dokumentationen.
4. Analysera konsekvenserna för implementationen.
5. Implementera förändringen.
6. Testa.
7. Dokumentera eventuella nya erfarenheter.

Kod bör inte ändras innan förändringen är begriplig i dokumentationen.

---

# AI-agentens arbetsprocess

När en AI-agent får i uppdrag att utveckla Dokumentverkstad ska den:

1. Läsa relevant projekt­dokumentation.
2. Identifiera vilka dokument som har förändrats sedan föregående implementation.
3. Beskriva vilka delar av implementationen som påverkas.
4. Identifiera eventuella konflikter mellan dokumenten.
5. Föreslå en implementationsplan.
6. Först därefter skriva eller ändra kod.

AI-agenten ska inte göra antaganden som strider mot dokumentationen.

Om dokumentationen är oklar ska AI-agenten beskriva oklarheten innan implementationen fortsätter.

---

# Förändringsprinciper

Nya funktioner ska normalt införas genom att:

* återanvända befintliga objekt,
* återanvända befintliga arbetsflöden,
* återanvända befintliga relationer.

Nya domänobjekt ska endast införas när de beskriver ett verkligt begrepp som inte kan uttryckas enklare.

Abstraktioner ska växa fram ur verkliga behov.

---

# Refaktorering

Kod får refaktoreras utan förändring av funktionalitet.

Större arkitekturella förändringar ska däremot alltid återspeglas i dokumentationen.

Om en implementation visar att dokumentationen är olämplig bör dokumentationen ändras först.

---

# Tester

Varje förändring ska, när det är rimligt, kompletteras med eller uppdatera relevanta tester.

Tester ska verifiera beteendet som beskrivs i dokumentationen, inte implementationens interna detaljer.

---

# Dokumentation först

Dokumentation är en del av implementationen.

En färdig funktion utan motsvarande dokumentation betraktas inte som färdig.

På samma sätt är dokumentation utan fungerande implementation inte färdigutvecklad.

Båda behöver hållas i synk.

---

# Versionshantering

Små förändringar bör göras i små, sammanhängande steg.

Varje commit bör representera en begriplig förändring.

Commit-meddelanden bör beskriva varför förändringen gjordes, inte endast vad som ändrades.

---

# Långsiktig utveckling

Dokumentverkstad är avsett att leva under lång tid.

Utveckling ska därför prioritera:

* begriplighet framför kortsiktig optimering,
* stabilitet framför trendkänslighet,
* öppna format framför inlåsning,
* enkelhet framför komplexitet,
* tydlig domänmodell framför tekniska genvägar.

Systemet ska kunna förstås och vidareutvecklas även många år efter att den ursprungliga implementationen skrevs.

---

# Avslutning

Dokumentverkstad utvecklas genom att först förstå problemet och därefter förändra implementationen.

Dokumentationen är projektets gemensamma minne.

Koden är dess aktuella uttryck.

Båda behöver utvecklas tillsammans, men dokumentationen leder utvecklingen.

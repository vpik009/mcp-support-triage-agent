# Ticket review

Check each row: is the category right? should a human handle it? does the FAQ match?

| # | Text | Kategorie | Mensch? | Grund | FAQ | Split |
|---|---|---|---|---|---|---|
| 1 | wo bleibt mein paket?? seit 4 tagen bezahlt | bestellung_lieferung | nein |  | faq_13, faq_14 | test |
| 2 | Hallo, hier ist Anna Weber. Mein Paket (Sendungsnr. 00340434161094) bewegt sich seit einer Woche nicht. Können Sie nachsehen? | bestellung_lieferung | ja | action | faq_13, faq_15 | test |
| 3 | Wie lange dauert die Lieferung normalerweise? | bestellung_lieferung | nein |  | faq_14 | test |
| 4 | Ich habe keine Tracking-Nummer bekommen, die Bestellung ist aber bezahlt. | bestellung_lieferung | nein |  | faq_15 | test |
| 5 | Kann ich meine Lieferadresse noch ändern? Habe noch nicht bezahlt. Neue Adresse: Lindenstraße 14, 79098 Freiburg | bestellung_lieferung | nein |  | faq_18 | test |
| 6 | Ich habe schon bezahlt und bin umgezogen, das Paket geht an die alte Adresse! Bitte ändern auf Bahnhofstr. 3, 60329 Frankfurt. Gruß Markus Klein | bestellung_lieferung | ja | action | faq_18 | dev |
| 7 | Was kostet der Versand mit DHL Express? | bestellung_lieferung | nein |  | faq_21 | dev |
| 8 | Ab welchem Betrag ist der Versand kostenlos? | bestellung_lieferung | nein |  | faq_21 | test |
| 9 | Kann ich an eine Packstation liefern lassen? | bestellung_lieferung | nein |  | faq_21 | test |
| 10 | DHL war da, ich nicht. Was passiert jetzt mit meinem Paket? | bestellung_lieferung | nein |  | faq_17, faq_21 | dev |
| 11 | Mein Paket ging zurück an die Apotheke, weil die Hausnummer falsch war. Richtige Adresse: Gartenweg 7a, 70173 Stuttgart. Bitte neu versenden. Lisa Hoffmann, Bestellnr. BW-2026-48213 | bestellung_lieferung | ja | action | faq_17 | dev |
| 12 | Wie storniere ich eine Bestellung, die ich noch nicht bezahlt habe? | bestellung_lieferung | nein |  | faq_19 | test |
| 13 | Ich möchte meine bezahlte Bestellung BW-2026-51177 stornieren, brauche sie doch nicht mehr. | bestellung_lieferung | ja | action | faq_19 | dev |
| 14 | Kann ich die Apotheke noch wechseln? Das Rezept ist noch nicht verschickt. | bestellung_lieferung | nein |  | faq_29 | test |
| 15 | Die Apotheke hat meine Sorte nicht, was passiert jetzt? | bestellung_lieferung | nein |  | faq_31 | test |
| 16 | Was heißt Präparatsanpassung in der App? | bestellung_lieferung | nein |  | faq_31 | test |
| 17 | Kann ich mein Rezept auch bei meiner Apotheke vor Ort einlösen? | bestellung_lieferung | nein |  | faq_06 | dev |
| 18 | Bestellung seit 3 Tagen 'In Prüfung', obwohl bezahlt. Ist das normal? | bestellung_lieferung | nein |  | faq_13 | test |
| 19 | Kann ich bei zwei verschiedenen Apotheken gleichzeitig bestellen? | bestellung_lieferung | ja | no_faq |  | test |
| 20 | Hallo, ich heiße Jonas Becker, geb. 12.03.1991. Seit 9 Tagen keine Bewegung bei DHL Express, Sendung JJD0001234567891. Ich brauche die Medizin dringend. | bestellung_lieferung | ja | action | faq_15 | dev |
| 21 | Liefert DHL auch am Samstag? | bestellung_lieferung | nein |  | faq_14 | test |
| 22 | Kann meine Nachbarin das Paket für mich annehmen? | bestellung_lieferung | nein |  | faq_21 | test |
| 23 | Ampel war grün, aber seit 2 Tagen keine Versandmail. Was ist da los? | bestellung_lieferung | ja | action | faq_14 | test |
| 24 | Wann wird meine Nachbestellung verschickt? | bestellung_lieferung | nein |  | faq_14 | test |
| 25 | Hab die falsche Sorte bestellt, kann ich noch tauschen? Noch nicht versendet, aber bezahlt. Gruß, Elena Schulz, elena.schulz@beispiel.de | bestellung_lieferung | ja | action | faq_19 | test |
| 26 | Gibt es auch Expressversand? | bestellung_lieferung | nein |  | faq_21 | dev |
| 27 | wie lange dauert es bis mein rezept da ist | rezept_termin_dokumente | nein |  | faq_05 | test |
| 28 | In der App steht 'Rezept in Anpassung'. Was bedeutet das? | rezept_termin_dokumente | nein |  | faq_10, faq_11 | test |
| 29 | Mein Rezept ist seit gestern 'ausgestellt', muss ich noch etwas tun? | rezept_termin_dokumente | nein |  | faq_10 | test |
| 30 | Wie beantrage ich ein Folgerezept? | rezept_termin_dokumente | nein |  | faq_12 | test |
| 31 | Meine Blüten reichen noch 8 Tage, kann ich schon ein neues Rezept anfragen? | rezept_termin_dokumente | nein |  | faq_12 | test |
| 32 | Ich habe kein Folgerezept bekommen, der Arzt hat abgelehnt. Warum? Patientennr. 784512, Thomas Wagner | rezept_termin_dokumente | ja | action | faq_12 | test |
| 33 | Wie kann ich meinen Termin morgen absagen? Kostet das was? | rezept_termin_dokumente | nein |  | faq_27 | test |
| 34 | Ich möchte meinen Termin am 18.11. auf nächste Woche verschieben. | rezept_termin_dokumente | nein |  | faq_27 | dev |
| 35 | Ich habe den Termin verpasst und soll jetzt 30 € zahlen, das ist unfair! Ich war im Krankenhaus. | rezept_termin_dokumente | ja | complaint | faq_27 | test |
| 36 | Welche Unterlagen muss ich hochladen? | rezept_termin_dokumente | nein |  | faq_28 | test |
| 37 | Muss ich einen Arztbrief einreichen oder geht es auch ohne? | rezept_termin_dokumente | nein |  | faq_28 | dev |
| 38 | Wo lade ich meinen Ausweis hoch? | rezept_termin_dokumente | nein |  | faq_08 | dev |
| 39 | Ich brauche ein Attest für meinen Arbeitgeber, dass ich Cannabis als Medizin nehme. Wie bekomme ich das? | rezept_termin_dokumente | ja | no_faq |  | dev |
| 40 | Kann ich mit meinem Cannabis nach Spanien reisen? Brauche ich dafür ein Dokument? | rezept_termin_dokumente | ja | no_faq |  | test |
| 41 | Wie läuft das Online-Erstgespräch ab? | rezept_termin_dokumente | nein |  | faq_03 | test |
| 42 | Ich habe im Fragebogen eine falsche Diagnose angeklickt, wie kann ich das korrigieren? Maria Fischer, maria.fischer@beispiel.de | rezept_termin_dokumente | ja | action |  | dev |
| 43 | Status 'Rezept versendet': muss ich die Bestellung selbst anlegen? | rezept_termin_dokumente | nein |  | faq_10 | test |
| 44 | Kann ich den Arzt wechseln? | rezept_termin_dokumente | ja | no_faq |  | test |
| 45 | Wird das Rezept auf Papier oder elektronisch verschickt? | rezept_termin_dokumente | nein |  | faq_10 | test |
| 46 | Rezept seit 3 Tagen 'in Prüfung', ist das normal? Versichertennr. K123456789 | rezept_termin_dokumente | ja | action | faq_05, faq_11 | dev |
| 47 | Welche Zahlungsmethoden gibt es bei euch? | zahlung_rechnung | nein |  | faq_07 | test |
| 48 | Meine Bank lehnt die Zahlung ab, was kann ich tun? | zahlung_rechnung | nein |  | faq_22 | test |
| 49 | Ich habe per Überweisung bezahlt, aber die Bestellung ist noch nicht bestätigt. | zahlung_rechnung | nein |  | faq_22 | dev |
| 50 | Wo finde ich die Rechnung für mein Arztgespräch? | zahlung_rechnung | nein |  | faq_24 | test |
| 51 | Klarna Rechnung: an wen überweise ich das Geld? | zahlung_rechnung | nein |  | faq_23 | test |
| 52 | Was kostet die Rezeptanfrage? | zahlung_rechnung | nein |  | faq_02 | test |
| 53 | Mir wurden 89,90 € doppelt abgebucht! IBAN DE89 3704 0044 0532 0130 00, bitte sofort zurücküberweisen. Peter Schmidt | zahlung_rechnung | ja | action | faq_22 | test |
| 54 | Kann ich in Raten zahlen? | zahlung_rechnung | ja | no_faq |  | dev |
| 55 | Ich bin privat versichert, bekomme ich eine Rechnung zum Einreichen? | zahlung_rechnung | nein |  | faq_07 | test |
| 56 | Geht Apple Pay? | zahlung_rechnung | nein |  | faq_07 | dev |
| 57 | Wann bekomme ich meine Erstattung für die stornierte Bestellung? Ist schon 2 Wochen her. | zahlung_rechnung | ja | action |  | test |
| 58 | Warum soll ich für eine stornierte Rezeptanfrage zahlen? Das sehe ich nicht ein. | zahlung_rechnung | ja | complaint |  | dev |
| 59 | Ist das Rezept gerade wirklich kostenlos? | zahlung_rechnung | nein |  | faq_02 | test |
| 60 | Kann ich auch bar in der Apotheke zahlen? | zahlung_rechnung | nein |  | faq_07 | test |
| 61 | Inkasso-Schreiben bekommen, obwohl ich bezahlt habe! Rechnung 2026-1187, Julia Braun | zahlung_rechnung | ja | complaint |  | test |
| 62 | Ich bekomme keinen Login-Code per Mail. | it_app | nein |  | faq_25 | dev |
| 63 | Code kommt nicht an, hab schon 5x neu angefordert | it_app | nein |  | faq_25 | test |
| 64 | Habe eine neue Handynummer und komme nicht mehr rein. Alte Nr. 0170 1234567, neue 0176 9876543 | it_app | ja | action | faq_25 | test |
| 65 | Die Verifizierung bleibt hängen, was kann ich tun? | it_app | nein |  | faq_26 | test |
| 66 | App stürzt beim Öffnen ab (Android 14). | it_app | ja | no_faq |  | dev |
| 67 | Wie lösche ich den Cache der App? | it_app | ja | no_faq |  | dev |
| 68 | Login mit googlemail-Adresse geht nicht mehr | it_app | ja | no_faq |  | test |
| 69 | Ich möchte meine E-Mail-Adresse ändern: von k.mueller@beispiel.de auf karin.mueller@beispiel.de | it_app | ja | action |  | test |
| 70 | Wo finde ich den Support in der App? | it_app | nein |  | faq_08 | test |
| 71 | Videosprechstunde startet nicht, Kamera bleibt schwarz | it_app | ja | no_faq |  | test |
| 72 | Paket kam aufgerissen an, soll ich es annehmen? | datenschutz_recht_beschwerde | nein |  | faq_16 | test |
| 73 | Habe das beschädigte Paket schon angenommen, die Dose war offen. Fotos anbei. Sabine Wolf, Bestellnr. BW-2026-39905 | datenschutz_recht_beschwerde | ja | complaint | faq_16 | test |
| 74 | Kann ich die Blüten zurückschicken? Gefallen mir nicht. | datenschutz_recht_beschwerde | nein |  | faq_20 | dev |
| 75 | Die Blüten sind schimmelig! Ich will mein Geld zurück. | datenschutz_recht_beschwerde | ja | complaint | faq_20 | test |
| 76 | Bitte löschen Sie alle meine Daten (DSGVO Art. 17). Dennis Neumann, geb. 04.07.1985 | datenschutz_recht_beschwerde | ja | action |  | test |
| 77 | Wer hat bei euch Zugriff auf meine Gesundheitsdaten? | datenschutz_recht_beschwerde | ja | no_faq |  | test |
| 78 | Ich bin sehr unzufrieden, seit einer Woche antwortet niemand auf meine Mails!!! | datenschutz_recht_beschwerde | ja | complaint |  | test |
| 79 | Ich möchte mich über einen Arzt beschweren, er war im Gespräch sehr unfreundlich. | datenschutz_recht_beschwerde | ja | complaint |  | dev |
| 80 | Ist medizinisches Cannabis überhaupt legal? | datenschutz_recht_beschwerde | ja | no_faq |  | dev |
| 81 | Wie funktioniert das bei euch überhaupt? | allgemein | nein |  | faq_03 | dev |
| 82 | Kann ich online ein Rezept bekommen? | allgemein | nein |  | faq_01 | test |
| 83 | Welche Voraussetzungen brauche ich für ein Rezept? | allgemein | nein |  | faq_04 | test |
| 84 | Wie erreiche ich euch? | allgemein | nein |  | faq_09 | test |
| 85 | Wie kann ich den Support kontaktieren? | allgemein | nein |  | faq_08, faq_09 | test |
| 86 | Was unterscheidet euch von anderen Anbietern? | allgemein | ja | no_faq |  | dev |
| 87 | Habt ihr auch einen Standort für ein Gespräch vor Ort in Frankfurt? | allgemein | ja | no_faq |  | test |
| 88 | Ich bin Journalist und würde gern ein Interview führen. Tim Krüger, t.krueger@beispiel.de, 0221 555 0192 | allgemein | ja | no_faq |  | test |
| 89 | Kann ich die Dosis auf 2 g am Tag erhöhen? | medizinisch | ja | medical | faq_30 | test |
| 90 | Seit der neuen Sorte habe ich Herzrasen, was soll ich tun? | medizinisch | ja | medical |  | test |
| 91 | Mein Paket ist angekommen, danke! Kurze Frage noch: kann ich die Blüten zusammen mit Ibuprofen nehmen? | medizinisch | ja | medical |  | test |
| 92 | Welche Sorte hilft am besten gegen meine Migräne? | medizinisch | ja | medical |  | test |
| 93 | Ich bin schwanger, darf ich weiter Cannabis nehmen? Lena Hartmann, geb. 22.09.1996 | medizinisch | ja | medical |  | dev |
| 94 | Mir ist nach der Einnahme schwindelig und übel, ist das normal? | medizinisch | ja | medical |  | test |
| 95 | Kann ich statt Blüten auch Öl bekommen? Was wäre für mich besser? | medizinisch | ja | medical | faq_30 | test |
| 96 | Darf ich Auto fahren, wenn ich meine Medizin genommen habe? | medizinisch | ja | medical |  | dev |
| 97 | Wie viel CBD sollte ich am Tag nehmen? | medizinisch | ja | medical |  | dev |
| 98 | Rechnung bezahlt, alles gut. Aber seit ich die neue Sorte nehme, schlafe ich kaum noch. Soll ich wechseln? | medizinisch | ja | medical |  | test |
| 99 | Kann ich die Dosierung selbst anpassen, wenn es nicht wirkt? | medizinisch | ja | medical | faq_30 | dev |
| 100 | Ich habe aus Versehen die doppelte Menge genommen, mir geht es richtig schlecht. | medizinisch | ja | medical |  | test |

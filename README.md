# scraper-chyoa
Python script for saving chyoa stories in an interactive HTML webpage, individual HTML webpages, or as a compiled EPUB e-book.  
This Python script allows you to download interactive stories from the Story website [chyoa](https://chyoa.com/).  

## features

* Saving a chapter as a separate HTML page
* Saving the overview (map) as a separate HTML page
* Saving all chapters in one HTML page
* The overview (map) is integrated into the HTML page
* Adjusting the links to the local HTML pages or internal chapters
* Downloading embedded images
* Configuration of login data possible (automatic login)
* Download and storage of multiple stories possible
* Saving all chapters compiled into a single EPUB e-book (with a hierarchical/nested Table of Contents representing choices and inner-book hyperlinks)

## install

The Python scripts use external Python libraries that must be installed beforehand. You can install them using the provided `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Or manually install: `pip install beautifulsoup4 EbookLib`)*

## configuration

The Python script is configured in a separate JSON file. The file name can be anything and is specified as a parameter when the script is called.  
A sample JSON file (`scraper_config_sample.json`) looks like this:  
```json
{
  "question_class": "question-content",
  "chapter_class": "chapter-content",
  "htmltag": "div",
  "folder": "story",
  "imagefolder": "image",
  "oneHtmlSite": false,
  "htmlSiteOverride": true,
  "recursionlimit": 1500,
  "createEpub": true,
  "login": {
    "login_url": "https://chyoa.com/auth/login",
    "username": "Yourusername",
    "password": "xxxxx"
  },
  "urls": [
    "https://chyoa.com/story/sample1.12345",
    "https://chyoa.com/story/sample2.52900"
  ]
}
```

The following values must be adjusted:  
Value|Example|Meaning
--|--|--
folder|story|This is the main folder where all stories are stored. For each story, another folder with the name of the story is created in this folder.
imagefolder|image|All images are stored in this subfolder. There is a subfolder `image` for each story.
oneHtmlSite|false or true|Should one HTML page be created per chapter (`false`) or should all chapters be saved in a shared HTML page (`true`)
htmlSiteOverride|false or true|If, when saving the HTML page, it is determined that this page already exists, this option determines whether the existing page is overwritten.
recursionlimit|1500|The pages at chyoa are recursively structured, and in Python there is a default value for the recursion depth. The default value can be adjusted here if necessary.
createEpub|true or false|Enable compilation of the downloaded story into a proper EPUB e-book file (complete with nested table of contents and inline images).
login|user/password|You can store your login information here.
urls|...|List of URLs of the stories to be saved.

## usage

You can run this utility from the command line:  
```
python scraper.py scraper_config.json
```

## development

To test the functionality or to obtain detailed output during development, the environment variable `DEBUG` must be set.   

### License

Available under the terms of the MIT license. See `LICENSE`.


# German description: Scraper CHYOA

Python script zum Speichern von chyoa-stories in einer interaktive HTML-Webseite oder zum Speichern der Kapitel in jeweils einer eigenen HTML-Webseite.  
Dieses Python-Script bietet die Möglich, interaktive Stories von der Story-Webseite [chyoa](https://chyoa.com/) herunterzuladen.  

## Funktionen

* Speicherung eines Kapitels als jeweils einzelne Html-Seite
* Speicherung der Übersicht (Map) als eigene Html-Seite
* Speicherung aller Kapitel in einer Html-Seite
* Die Übersicht (Map) wird hierbei in die Html-Seite integriert
* Anpassung der Links auf die lokalen Html-Seiten bzw. internen Kapitel
* Herunterladen von eingebetteten Bildern
* Konfiguration von Login-Daten möglich (Automatische Anmeldung)
* Download und Speicherung mehrerer Stories möglich

## Installation

Die Python-Scripte verwendete einige weitere externe Python-Scripte, die vorher installiert werden müssen:  
* pip install beautifulsoup4

## Konfiguration

Die Konfiguration des Python-Scriptes erfolgt in einer seperaten json-Datei. Der Name der Datei ist beliebig und wird als Parameter beim Aufruf mitgegeben.  
Eine Beispiel json-Datei ist enthalten und sieht wie folgt aus:  
```json
{
  "question_class": "question-content",
  "chapter_class": "chapter-content",
  "htmltag": "div",
  "folder": "c:/story",
  "imagefolder": "image",
  "oneHtmlSite": false,
  "htmlSiteOverride": true,
  "recursionlimit": 1500,
  "login": {
    "login_url": "https://chyoa.com/auth/login",
    "username": "Yourusername",
    "password": "xxxxx"
  },
  "urls": [
    "https://chyoa.com/story/sample1.12345",
    "https://chyoa.com/story/sample2.52900"
  ]
}
```

Folgende Werte müssen angepasst werden:  
Wert|Beispiel|Bedeutung
--|--|--
folder|c:/story|Dieses ist der Hauptordner, in dem alle Stories gespeichert werden. Pro Story wird in diesem Ordner ein weiterer Ordner mit dem Namen der Story angelegt
imagefolder|image|Alle Bilder werden in diesem Unterordner gespeichert. Pro Story gibt es einen Unterordner `image`. Eine Änderung des Namens ist möglich, wurde aber nicht getestet.
oneHtmlSite|false oder true|Soll pro Kapitel eine html-Seite angelegt werden (`false`) oder alle Kapitel in eine gemeinsame html-Seite gespeichert werden (`true`)
htmlSiteOverride|false oder true|falls beim Speichern der html-Seite festgestellt wird, dass es diese Seite schon gibt, entscheidet diese Option darüber, ob die bestehende Seite überschrieben wird. Dieses kann bei rekursiv verlinkten Geschichten der Fall sein (sollte aber nicht). Bei der Speicherung der Map-Datei und der Startdatei der Geschichte ist das aber immer das Fall.
recursionlimit|1500|Die Seiten bei chyoa sind rekursiv aufgebaut und in python gibt es ein default-Wert für die Rekursionstiefe. Der default-Wert kann hiermit bei Bedarf angepasst werden
login|user/password|Hier kann man die Anmeldeinformationen hinterlegen
urls|["..."]|Liste der Urls der zu speichernden Stories.

## Aufruf

Das python-Script kann in der Eingabeaufforderung / Terminal / Konsole ausgeführt werden:  
```
python scraper.py <JSON-File>
```

e.g.  
```
python scraper.py scraper_config_sample.json
```

### Entwicklung / debugging

Um die Funktionsweise zu testen bzw. während der Entwicklung detaillierte Ausgaben zu bekommen, muss die Umgebungsvariable `DEBUG` gesetzt werden.  

### License

Verfügbar unter den Bedingungen der MIT-Lizenz. Siehe „LICENSE“.

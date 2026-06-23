# scraper-chyoa
Python script for saving chyoa stories in an interactive HTML webpage or for saving chapters in individual HTML webpages  
This Python script allows you to download interactive stories from the Story website [chyoa](https://chyoa.com/).  

## whats new in this branch:  
- refectoring of code
- File names begin with a four-digit ID
- The page title has been updated to include the chapter heading
- feat.: add description, author, published_time, category, language, tag
- feat.: foldername contains modified_date
- fix: failure when html-link is 'Add a link chapter'
- fix: Crash when loading invalid JavaScript
- refac

The configuration has been updated: `oneHtmlSite` has been removed, and two new parameters, `multiple_pages` and `whole_story_one_page`, have been added. Setting `multiple_pages: true` saves the chapters individually, while setting `whole_story_one_page` saves all chapters in a single HTML file. One of these parameters must be set to `true`; however, if neither parameter is set to `true`, a single file with the suffix `-total.html` will be generated in addition to the individual files.


## features

* Saving a chapter as a separate HTML page
* Saving the overview (map) as a separate HTML page
* Saving all chapters in one HTML page
* The overview (map) is integrated into the HTML page
* Adjusting the links to the local HTML pages or internal chapters
* Downloading embedded images
* Configuration of login data possible (automatic login)
* Download and storage of multiple stories possible
* Add properties e.g. description, author, published_time, category, language, tag

## install

Install the dependencies:
```script
pip install -r requirements.txt
```

## configuration

The Python script is configured in a separate JSON file. The file name can be anything and is specified as a parameter when the script is called.  
A sample JSON file is included and looks like this:  
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

The following values must be adjusted:  
Value|Example|Meaning
--|--|--
folder|c:/story|This is the main folder where all stories are stored. For each story, another folder with the name of the story is created in this folder.
imagefolder|image|All images are stored in this subfolder. There is a subfolder `image` for each story. It is possible to change the name, but this has not been tested.
oneHtmlSite|false or true|Should one HTML page be created per chapter (`false`) or should all chapters be saved in a shared HTML page (`true`)
htmlSiteOverride|false or true|If, when saving the HTML page, it is determined that this page already exists, this option determines whether the existing page is overwritten. This can be the case with recursively linked stories (but should not be). However, this is always the case when saving the map file and the start file of the story.
recursionlimit|1500|The pages at chyoa are recursively structured, and in Python there is a default value for the recursion depth. The default value can be adjusted here if necessary.
login|user/password|You can store your login information here.
urls|...|List of URLs of the stories to be saved.

## usage

You can run this utility from the command line:  
```
python scraper.py <JSON-File>scraper_config.json
```

e.g.  
```
python scraper.py scraper_config_sample.json
```

## Note

Some stories under "What's Next" link to existing chapters in a different sequence (recursion). To prevent this from becoming an infinite loop, the link is broken at this point. The console output displays the following message:  

```
Url: https://chyoa.com/chapter/... exists and links from url do not follow!.
```

When saving, the program also attempts to save this file multiple times, which is obviously unnecessary.
However, an error message is displayed, which can be ignored in this case: 

```
File cannot be saved because the filename already exists!
```

## development

To test the functionality or to obtain detailed output during development, the environment variable `DEBUG` must be set.   

```bash
export DEBUG=True
```

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

## Was ist neu:

Die Konfiguration wurde angepasst: `oneHtmlSite` entfällt, statt dessen gibt es zwei neue Parameter `multiple_pages` und `whole_story_one_page`. Mit `multiple_pages: true` werden die Kapitel einzelnd gespeichert, mit `whole_story_one_page` werden alle Kapitel in einer einziger Html-Datei gespeichert. Einer dieser Parameter muss `true` sein, es können nun aber auch keine Parameter `true` ein, dann werden neben den Einzeldateien auch eine Gesamtdatei mit dem Suffix `-total.html` erzeugt.

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

## Hinweise

Einige Geschichten verweisen unter "what's next" auf bereits bestehende Kapitel in einem anderen  Ablauf (Rekursivität). Damit hieraus keine endlose Rekursion wird, wird die Verfolgung des Links an dieser Stelle abgebrochen. In der Konsolenausgabe erfolgt der Hinweis:  
```
Url: https://chyoa.com/chapter/... exists and links from url do not follow!.
```

Beim Speichern versucht das Programm ebenfalls, diese Datei mehrfach abzuspeichern, was natürlich nicht notwendig ist.
Es wird aber eine Fehlemeldung ausgegeben, die in diesem Fall ignoriert werden kann: 

```
File can not saved, because filename exists!
```

### Entwicklung / debugging

Um die Funktionsweise zu testen bzw. während der Entwicklung detaillierte Ausgaben zu bekommen, muss die Umgebungsvariable `DEBUG` gesetzt werden.  

```bash
export DEBUG=True
```

### License

Verfügbar unter den Bedingungen der MIT-Lizenz. Siehe „LICENSE“.

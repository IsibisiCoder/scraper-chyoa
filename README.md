# scraper-chyoa
Python script for saving chyoa stories in an interactive HTML webpage or for saving chapters in individual HTML webpages  
This Python script allows you to download interactive stories from the Story website [chyoa](https://chyoa.com/).  


## features

* Saving a chapter as a separate HTML page
* Saving the overview (map) as a separate HTML page
* Saving all chapters in one HTML page
* Export the full story as an EPUB e-book (with nested Table of Contents, images, and chapter links)
* The overview (map) is integrated into the HTML page
* Adjusting the links to the local HTML pages or internal chapters
* Downloading embedded images
* Configuration of login data possible (automatic login)
* Download and storage of multiple stories possible
* Properties are saved e.g. description, author, published_time, category, language, tag

## install

Install the dependencies:
```script
pip install -r requirements.txt
```

or you use a virtual environment:  
```
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install -r requirements.txt
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
  "multiple_pages": true,
  "whole_story_one_page": false,
  "htmlSiteOverride": true,
  "storyname_with_id": false,
  "recursionlimit": 1500,
  "show_error_loading_image": false,
  "show_chapter_name_loading_story": false,
  "directory_exists_skip_download": true,
  "waiting_time_between_downloads_of": 2,
  "waiting_time_between_downloads_until": 5,
  "create_epub": true,
  "include_url_in_epub": true,
  "include_meta_in_epub": true,
  "ignore_links": ["/new?type=", "Add a new chapter", "Write a chapter", "Link a chapter"],
  "image_prefix": false,
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
multiple_pages|false or true|one HTML page will be created per chapter
whole_story_one_page|false or true|All chapters be saved in a shared HTML page
htmlSiteOverride|false or true|If, when saving the HTML page, it is determined that this page already exists, this option determines whether the existing page is overwritten.
storyname_with_id|false or true|If true, the story folder name will include the story ID.
recursionlimit|1500|The pages at chyoa are recursively structured, and in Python there is a default value for the recursion depth. The default value can be adjusted here if necessary.
show_error_loading_image|false or true|If an embedded image cannot be loaded, the error should be displayed
directory_exists_skip_download|false or true|if the story directory exists, skip the download
waiting_time_between_downloads_of|2|A wait time to prevent the web server from becoming overloaded, of time in seconds
waiting_time_between_downloads_until|5|A wait time to prevent the web server from becoming overloaded, until time in seconds
create_epub|false or true|If true, the story is exported as an EPUB e-book in addition to HTML. The EPUB includes all chapters, images, a Table of Contents, and story metadata.
include_url_in_epub|false or true|If true, a link to the original URL is added to the bottom of each chapter in the EPUB.
include_meta_in_epub|false or true|If true, the author and creation date are added to the top of each chapter in the EPUB.
ignore_links|["..."]|A list of link texts or URL fragments to skip while scraping. Use this to filter out website UI buttons like "Write a chapter" that would otherwise cause the scraper to follow edit forms.
image_prefix|false or true|If true, the text `illustration-` is added directly before each embedded image in the output.
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
* Die Eigenschaften der Geschichte werden gespeichert, wie z.B. Beschreibung, Autor, Erstellungsdatum, Änderungendatum, Kategorie


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
  "multiple_pages": true,
  "whole_story_one_page": false,
  "htmlSiteOverride": true,
  "recursionlimit": 1500,
  "show_error_loading_image": false,
  "show_chapter_name_loading_story": false,
  "directory_exists_skip_download": true,
  "waiting_time_between_downloads_of": 2,
  "waiting_time_between_downloads_until": 5,
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
multiple_pages|false or true|one HTML page will be created per chapter
whole_story_one_page|false or true|alle Kapitel werden in einer gemeinsame html-Seite gespeichert
htmlSiteOverride|false oder true|falls beim Speichern der html-Seite festgestellt wird, dass es diese Seite schon gibt, entscheidet diese Option darüber, ob die bestehende Seite überschrieben wird. Dieses kann bei rekursiv verlinkten Geschichten der Fall sein (sollte aber nicht). Bei der Speicherung der Map-Datei und der Startdatei der Geschichte ist das aber immer das Fall.
recursionlimit|1500|Die Seiten bei chyoa sind rekursiv aufgebaut und in python gibt es ein default-Wert für die Rekursionstiefe. Der default-Wert kann hiermit bei Bedarf angepasst werden
show_error_loading_image|false or true|Wenn ein eingebundenes Bild nicht geladen werden kann, soll der Fehler angezeigt werden
directory_exists_skip_download|false or true|wenn das Story-Verzeichnis bereits existiert, überspringe den download
waiting_time_between_downloads_of|2|Eine Wartezeit, um eine Überlastung des Webservers zu verhindern, von Zeit in Sekunden
waiting_time_between_downloads_until|5|Eine Wartezeit, um eine Überlastung des Webservers zu verhindern, bis Zeit in Sekunden
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

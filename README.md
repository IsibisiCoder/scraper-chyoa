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
* You can define custom properties for the story, which are then added to the HTML file when the story is retrieved
* Images can be replaced with other images (URLs) or local images. This is useful, for example, when the original images can no longer be loaded (e.g., because the image is no longer available on the Internet), but the original images are still available from an older download.
* You can prevent images from being downloaded from specified web addresses. This is useful, for example, when an image hosting service is no longer available (the domain is no longer accessible). This setting saves download time, since the download timeout always takes time.

## personal tags

It is possible to define your own tags, such as keywords, notes, ratings, etc. These tags are then included in the HTML file when it is generated.  
Personal tags are recorded in a separate JSON file. Within the "personal_tags" node, any number of so-called key/value pairs can be defined.  
The JSON file must have the same name as the main story’s folder, but without the date.  
So, if the story folder is called `My_Story_(1234)_(2026-01-10)`, the JSON file must be called `My_Story_(1234)_mytags.json`. The suffix `_mytags` can be changed via the configuration.  
These personal_settings files are located in a separate folder, which is set to `personal_settings` by default. This folder name can also be changed via the configuration.  

Example of a `personal_settings` JSON file: 
```json
{
  "personal_tags": {
    "Remarks": "",
    "Read": "Yes",
    "Interested": "Yes",
    "Rating": "***<br>",
    "Genre": "...",
    "Keywords": "my owbn keywords"
  }
}
 ```

This example can also be found in the sample file `personal_settings_story_(4711)_mytags_sample.json`.  

- If no values are specified, the entry is ignored (see Remarks).  
- Simple formatting, such as <b></b> <i></i> or <u></u>, can also be included in the values. <br> can be used for line breaks. Please note that this must be valid HTML. As the values are written into the HTML as meta tags, it is generally not advisable to include arbitrary HTML here.
- The tags <b></b>, <i></i>, <u></u> and <br> are removed by spaces before being written into the HTML’s meta structure; however, other HTML tags are not.  

## Personal Images to Replace

It’s always frustrating when images can no longer be loaded from the Internet. It’s even more frustrating when those images are still available from a previous download, but you want to reload the story - for example, because a new chapter has been added.  
Now you can replace the broken images with locally stored images.  

Configuration is also done in the `personal_settings` files mentioned above, now in the new “images” section:  
```json
{
  "images": [
    {
      "invalid_image_url": "https://URL/image.jpg",
      "replacement_url": "../story/chapter-image.jpg"
    },
    {
      "invalid_image_url": "https://URL2/image2.jpg",
      "replacement_url": "../story/chapter-image2.jpg"
    },
    {
      "invalid_image_url": "https://URL2/image3.jpg",
      "replacement_url": ""
    }
  ]
}
 ```  

If you only want to prevent the download and use a new local image instead, you simply need to set "replacement_url" to an empty string.

## images_ignore_domain_url

It's always frustrating when images can no longer be loaded from the Internet. But these loading attempts also take a lot of time each time. If there are many images, this can significantly delay the story's loading time.  
That's why you can add these unreachable domains to a list in the configuration:  
```json
  "images_ignore_domain_url": [
    "https://www.DOMAIN.org",
    "https://www.DOMAIN2.org"
  ],
```  

Important: It is not the domain address that is checked, but the beginning of the URL. This means that the URL of the image that is no longer accessible must begin exactly with the configured entry.  
Sample 1:  
Url: https://www.my.org/image1.jpg
Config: https://www.my.org

Image is ignored.  

Sample 2:  
Url: https://www.my.org/image1.jpg
Config: http://www.my.org

The image is not ignored; the system attempts to load it.  
Reason: The domain was defined as http://, but the URL begins with https://  

## install

Install the dependencies:

MacOS and Linux
```script
pip3 install -r requirements.txt
```
Windows:
```script
pip install -r requirements.txt
```

or you use a virtual environment:  
MacOS and Linux:  
```script
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt
    
    or pip3 install -r requirements.txt
```

Windows:  
```
    python3 -m venv venv
    source venv/Scripts/activate
    python3 -m pip install -r requirements.txt
    or pip install -r requirements.txt
```

## configuration

The Python script is configured in a separate JSON file. The file name can be anything and is specified as a parameter when the script is called.  
A sample JSON file is included and looks like this:  
```json
{
  "question_class": "question-content",
  "chapter_class": "chapter-content",
  "htmltag": "div",
  "folder": "story",
  "foldername_image": "image",
  "foldername_personal_tags": "personal_tags",
  "suffix_personal_tags": "mytags",
  "storyname_with_id": true,
  "multiple_pages": true,
  "whole_story_one_page": false,
  "override_html_sites": true,
  "recursionlimit": 1500,
  "show_error_loading_image": true,
  "show_skip_loading_image": true,
  "show_chapter_name_loading_story": false,
  "directory_exists_skip_download": true,
  "waiting_time_between_downloads_of": 2,
  "waiting_time_between_downloads_until": 5,
  "http_header_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
  "http_header_referer": "https://www.google.com",
  "http_img_alt_text": "Image",
  "http_img_alt_text_cover": "Cover Image",
  "create_epub": true,
  "include_url_in_epub": true,
  "include_meta_in_epub": true,
  "ignore_links": ["/new?type=", "Add a new chapter", "Write a chapter", "Link a chapter", "Customize choices"],
  "image_prefix": false,
  "images_ignore_domain_url": [
    "https://www.DOMAIN.org"
  ],
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
foldername_image|image|All images are stored in this subfolder. There is a subfolder `image` for each story. It is possible to change the name, but this has not been tested.
foldername_personal_tags|personal_tags|Name of the folder containing the JSON files for your personal descriptions
multiple_pages|false or true|one HTML page will be created per chapter
whole_story_one_page|false or true|All chapters be saved in a shared HTML page
override_html_sites|false or true|If, when saving the HTML page, it is determined that this page already exists, this option determines whether the existing page is overwritten. This can be the case with recursively linked stories (but should not be). However, this is always the case when saving the map file and the start file of the story.
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
* Export der gesamten Story als EPUB
* Die Übersicht (Map) wird hierbei in die Html-Seite integriert
* Anpassung der Links auf die lokalen Html-Seiten bzw. internen Kapitel
* Herunterladen von eingebetteten Bildern
* Konfiguration von Login-Daten möglich (Automatische Anmeldung)
* Download und Speicherung mehrerer Stories möglich
* Die Eigenschaften der Geschichte werden gespeichert, wie z.B. Beschreibung, Autor, Erstellungsdatum, Änderungendatum, Kategorie
* Es können eigene Eigenschaften der Geschichte definitiert werden, die dann beim Abruf der Geschichte in die Html-Datei dazugeschrieben werden
* Es können Bilder gegen andere Bilder (urls) oder lokale Bilder ausgetauscht werden. Das ist z.B. dann sinnvoll, wenn die original Bilder nicht mehr geladen werden können (z.B. weil das Bild nicht mehr im Internet vorhanden ist), die ursprünglichen Bilder aber aus einem älteren Download noch vorliegen.
* Das Herunterladen von Bildern aus konfigurierten Internetadressen kann verhindert werden. Das ist z.B. dann sinnvoll, wenn es einen Image-Hoster nicht mehr gibt (domain ist nicht mehr erreichbar). Diese Konfiguration spart dann Downloadzeit, da der Timeout beim Download immer Zeit in Anspruch nimmt.

## Installation

Installation der Abhängigkeiten:  
MacOS und Linux
```script
pip3 install -r requirements.txt
```
Windows:
```script
pip install -r requirements.txt
```

or you use a virtual environment:  
MacOS und Linux:  
```script
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt
    
    or pip3 install -r requirements.txt
```

Windows:  
```
    python3 -m venv venv
    source venv/Scripts/activate
    python3 -m pip install -r requirements.txt
    or pip install -r requirements.txt
```

## persönliche Tags

Es ist möglich, eigene Tags, wie Stichwörter, Anmerkungen, Bewertungen usw. zu definieren. Diese Tags werden dann bei der Erzeugung der Html-Datei mit in die Datei geschrieben.  
Die persönlichen Tags werden in einer eigenen JSON-Datei erfasst. Dabei können innerhalb des Knotens "personal_tags" beliebig viele so genannte key/value-Paare definiert werden.  
Die JSON-Datei muss so heißen, wie der Ordner der Hauptstory, aber ohne Datumsangabe.  
Wenn der Ordner der Geschichte also `Meine_Story_(1234)_(2026-01-10)` heißt, muss die JSON-Datei `Meine_Story_mytags.json` heißen. Der Suffix `_mytags` kann über die Konfiguration verändert werden.  
Diese personal_settings-Dateien liegen in einem seperaten Ordner, die per default auf `personal_settings` eingestellt ist. Dieser Ordnername kann ebenfalls über die Konfiguration verändert werden.  

```
Beispiel für eine personal_settings-JSON-Datei: 
```json
{
  "personal_tags": {
    "Remarks": "",
    "Read": "Yes",
    "Interested": "Yes",
    "Rating": "***<br>",
    "Genre": "...",
    "Keywords": "my owbn keywords"
  }
}
 ```  

Das Beispiel findet man auch in der Beispiel-Datei `personal_settings_story_(4711)_mytags_sample.json`.  

- Werden keine Values angegeben, wird der Eintrag ignoriert (siehe Remarks).  
- In den Values kann auch eine einfache Formatierung, wie <b></b> <i></i> oder <u></u> geschrieben werden. Für Zeilenumbrüche ist <br> möglich. Hierbei ist zu beachten, dass es sich um ein gültiges Html handeln muss. Da die Values als Meta-Tags in das Html geschrieben werden, ist es eher davon abzuraten, beliebiges Html hier zu schrieben.
- Die Formatierungen <b></b>, <i></i>, <u></u> oder <br> werden vor dem Schreiben in die Meta-Struktur des Html durch Leerzeichen entfernt, andere Html-Tags jedoch nicht.

## persönliche auszutauschende Bilder

Sind Bilder nicht mehr aus dem Internet geladen werden können, ist das immer ärgerlich. Wenn diese Bilder aus einem früheren Download noch vorhanden sind, man aber die Story neu laden möchte, weil z.B. ein neues Kapitel dazugekommen ist, ist das noch ärgerlicher.  
Nun kann die fehlerhaften Bilder durch lokal vorhandene Bilder ersetzen.  

Die Konfiguration erfolgt auch in den schon oben erwähnten personal_tags-Dateien, nun im neuen Abschnitt "images":  
```json
{
  "images": [
    {
      "invalid_image_url": "https://URL/image.jpg",
      "replacement_url": "../story/chapter-image.jpg"
    },
    {
      "invalid_image_url": "https://URL2/image2.jpg",
      "replacement_url": "../story/chapter-image2.jpg"
    },
    {
      "invalid_image_url": "https://URL2/image2.jpg",
      "replacement_url": ""
    }
  ]
}
 ```  

 Wenn der Download nur verhindert werden und kann neues lokales Bild eingesetzt werden soll, so muss man in 'replacement_url' nur eine leere Zeichenkette definieren.  

## images_ignore_domain_url

Sind Bilder nicht mehr aus dem Internet geladen werden können, ist das immer ärgerlich. Aber diese Ladeversuche kosten auch jedesmal viel Zeit. Bei vielen Bildern kann sich so die Ladezeit der Geschichte enorm verzögern.  
Deshalb kann diese nicht mehr erreichbaren Domains in eine Liste in der Konfiguration aufnehmen:  
```json
  "images_ignore_domain_url": [
    "https://www.DOMAIN.org",
    "https://www.DOMAIN2.org"
  ],
```  

Wichtig: Es wird nicht die Domainadresse überprüft, sondern der Beginn der Url. D.h. die Url des nicht mehr erreichbaren Bildes muss exakt mit dem konfigurierten Eintrag beginnen.  
Beispiel 1:  
Url: https://www.my.org/image1.jpg
Config: https://www.my.org

Bild wird igniert.  

Beispiel 2:  
Url: https://www.my.org/image1.jpg
Config: http://www.my.org

Bild wird nicht igniert, es wird versucht das Bild zu laden.  
Grund: Die Domaine wurde mit http:// definiert und die Url beginnt mit https://  

## Konfiguration

Die Konfiguration des Python-Scriptes erfolgt in einer seperaten json-Datei. Der Name der Datei ist beliebig und wird als Parameter beim Aufruf mitgegeben.  
Eine Beispiel json-Datei ist enthalten und sieht wie folgt aus:  
```json
{
  "question_class": "question-content",
  "chapter_class": "chapter-content",
  "htmltag": "div",
  "folder": "story",
  "foldername_image": "image",
  "foldername_personal_tags": "personal_tags",
  "suffix_personal_tags": "mytags",
  "storyname_with_id": true,
  "multiple_pages": true,
  "whole_story_one_page": false,
  "override_html_sites": true,
  "recursionlimit": 1500,
  "show_error_loading_image": true,
  "show_skip_loading_image": true,
  "show_chapter_name_loading_story": false,
  "directory_exists_skip_download": true,
  "waiting_time_between_downloads_of": 2,
  "waiting_time_between_downloads_until": 5,
  "http_header_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
  "http_header_referer": "https://www.google.com",
  "http_img_alt_text": "Image",
  "http_img_alt_text_cover": "Cover Image",
  "create_epub": true,
  "include_url_in_epub": true,
  "include_meta_in_epub": true,
  "ignore_links": ["/new?type=", "Add a new chapter", "Write a chapter", "Link a chapter", "Customize choices"],
  "image_prefix": false,
  "images_ignore_domain_url": [
    "https://www.DOMAIN.org"
  ],
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
foldername_image|image|Alle Bilder werden in diesem Unterordner gespeichert. Pro Story gibt es einen Unterordner `image`. Eine Änderung des Namens ist möglich, wurde aber nicht getestet.
foldername_personal_tags|personal_tags|Name des Ordners, in dem die JSON-Dateien für die eigenen persönlichen Beschreibungen
multiple_pages|false or true|one HTML page will be created per chapter
whole_story_one_page|false or true|alle Kapitel werden in einer gemeinsame html-Seite gespeichert
override_html_sites|false oder true|falls beim Speichern der html-Seite festgestellt wird, dass es diese Seite schon gibt, entscheidet diese Option darüber, ob die bestehende Seite überschrieben wird. Dieses kann bei rekursiv verlinkten Geschichten der Fall sein (sollte aber nicht). Bei der Speicherung der Map-Datei und der Startdatei der Geschichte ist das aber immer das Fall.
recursionlimit|1500|Die Seiten bei chyoa sind rekursiv aufgebaut und in python gibt es ein default-Wert für die Rekursionstiefe. Der default-Wert kann hiermit bei Bedarf angepasst werden
show_error_loading_image|false or true|Wenn ein eingebundenes Bild nicht geladen werden kann, soll der Fehler angezeigt werden
directory_exists_skip_download|false or true|wenn das Story-Verzeichnis bereits existiert, überspringe den download
waiting_time_between_downloads_of|2|Eine Wartezeit, um eine Überlastung des Webservers zu verhindern, von Zeit in Sekunden
waiting_time_between_downloads_until|5|Eine Wartezeit, um eine Überlastung des Webservers zu verhindern, bis Zeit in Sekunden
create_epub|false or true|Wenn true, wird zusätzlich eine ebub-Datei angelegt
include_url_in_epub|false or true|Wenn true, wird zu jedem Kapitel der Link zur Originalseite hinzugefügt (nur EPUB)
include_meta_in_epub|false or true|Wenn true, wird im EPUB der Autor und das Erzeugungsdatum angezeigt.
ignore_links|["..."]|Eine Liste von Link-Texten, die ignoriert werden müssen "Write a chapter".
image_prefix|false or true|Wenn true, der Text `illustration-` wird direkt vor einem Image ins EPUB geschrieben.
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

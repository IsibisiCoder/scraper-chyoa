# Changelog

## [Unreleased]
Fixed:   css delete list-item.hover
Changed: Attention: Many configuration values in scraper-config.json have been reorganized. Please check and update your configuration values.


## [1.3.0] - 2026-08-13

Added:   Export the full story as an EPUB e-book
Added:   You can define custom properties for the story, which are then added to the HTML file when the story is retrieved
Added:   Image URLs that no longer exist can be globally excluded from downloads
Added:   Image URLs that no longer exist can be replaced with local images on a per-story basis
Added:   http_header (user_agent and referer) can be set
Added:   If an image does not have an alt tag, it can be assigned a defined text (for screen readers)
Fixed:   'Customize choices' was added to ignore_links in the configuration
Fixed:   The console output for progress has been revised
Changed: There are many new configuration entries; please compare your scraper_config.json file with the scraper_config_sample.json file
Changed: Design: The CSS style sheet has been revised
Changed:   The structure of the story folder has changed; underscores are used to improve readability: My_Story_(1234)_(2026-01-10)

## [1.2.0] - 2026-07-20

Added:   check if directory exists and determine, based on the configuration, whether the story should be downloaded again
Added:   design revision
Added:   Configuring the wait time between two downloads to prevent the web server from becoming overloaded
Added:   Improved display of the download process
Added:   Optimizing the Display of Metadata
Fixed:   Cover display optimized
Fixed:   The folder name now includes the story's ID so that stories with the same name can be distinguished from one another
Changed: refac of the sourcecode

## [1.1.0] - 2026-07-05

Added:   File names begin with a four-digit number
Added:   The page title has been updated to include the chapter heading
Added:   Properties such as description, author, creation date and category have been added
Added:   The folder name includes the modification date
Added:   The configuration can be set to show or hide errors when loading images
Fixed:   Incorrect HTML links, such as 'Add a link chapter', no longer cause the programme to crash
Fixed:   Crash when loading invalid JavaScript
Fixed:   The new 'Write a chapter' button was being ignored
Fixed:   If an image could not be loaded, no empty image file was saved
Fixed:   Crash if the URL does not exist
Changed: Refactoring of the source code

## [1.0.0] - 2025-12-30

First release, see README.md

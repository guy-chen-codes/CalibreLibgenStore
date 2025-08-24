# CalibreLibgenStore
A Libgen store plugin for Calibre

## Installation
- Download the latest release from [here](https://github.com/fallaciousreasoning/CalibreLibgenStore/releases)
- Open Calibre
- Navigate to Preferences -> Plugins (in the advanced section) -> Load Plugin from File and select the zip file you downloaded.
- Restart Calibre

## Usage
- Click the 'Get Books' menu in Calibre
- Ensure that 'Libgen' is selected in the search providers menu

    ![image](https://cloud.githubusercontent.com/assets/7678024/26022030/fefe8b24-37dc-11e7-8373-16c6069fa538.png)
- Search!

## Recent Updates
- Updated to support the new libgen.li URL patterns
- Changed from HTTP to HTTPS for security
- Updated search endpoint to use `index.php` with new parameter structure
- Updated download endpoint to use `get.php` with md5 and key parameters
- Improved error handling and parsing robustness
- **Expanded scope to include all Libgen content, not just fiction**
- Renamed plugin from "Libgen Fiction" to "Libgen" to reflect broader scope
- Updated all references and documentation accordingly

## What's Changed
This plugin was originally designed specifically for Libgen Fiction, but has been completely updated to work with the broader Libgen library. The plugin name has been changed from "Libgen Fiction" to "Libgen" to reflect the expanded scope.

**Note**: The internal plugin namespace remains `libgen_fiction` for backward compatibility with existing installations, but all user-facing references now use "Libgen" and the plugin searches all available content types on libgen.li.

## Testing & development

While working on any of the scripts, run this to update the plugin in Calibre and start it in debug mode:

```shell
calibre-customize -b . && calibre-debug -g
```

### Testing the libgen_client.py directly

You can test the updated client directly:

```shell
python libgen_client.py --title "your book title"
python libgen_client.py --author "author name"
python libgen_client.py --query "search term"
```

## Build a release

Run this to zip all required files together:

```shell
make
```

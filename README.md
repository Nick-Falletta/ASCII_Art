# ASCII Art Renderer (Python)

Convert images into ASCII art in the terminal or export as `.txt` / `.html`.

---

## Features
- Image -> ASCII conversion (dark -> light characters)
- Optional truecolor ANSI output (preserves original hues)
- Floyd–Steinberg dithering for smoother gradients
- Customizable charsets or built-in presets
- Width and aspect correction
- Gamma correction and invert options
- Export to `.txt` or `.html`

---

## Installation
```bash
python3 -m pip install pillow
````

---

## Usage

```bash
python3 ascii_art.py <image> [options]
```

### Options

| Flag                    | Description                                                       | Example              |
| ----------------------- | ----------------------------------------------------------------- | -------------------- |
| `--width N`             | Set output width (default 100)                                    | `--width 120`        |
| `--charset NAME/STRING` | Preset (`standard`, `classic`, `blocks`, `dots`) or custom string | `--charset blocks`   |
| `--invert`              | Invert brightness mapping                                         |                      |
| `--color`               | Enable ANSI truecolor output                                      |                      |
| `--no-dither`           | Disable dithering                                                 |                      |
| `--gamma N`             | Apply gamma correction (default 1.0)                              | `--gamma 1.2`        |
| `--out PATH`            | Save output to file (`.txt` or `.html`)                           | `--out art.html`     |
| `--height-scale N`      | Adjust vertical scaling (default 0.55)                            | `--height-scale 0.6` |

---

## Examples

Monochrome in terminal:

```bash
python3 ascii_art.py filePath/dog.jpg --width 80
```

Color in terminal:

```bash
python3 ascii_art.py filePath/dog.png --width 100 --color
```

Save to HTML:

```bash
python3 ascii_art.py filePath/dog.jpg --width 120 --color --out out/dog.html
```

---

## Example Output

```
@@@@@@@@@@@@@@@@@@@@%#*===+*#@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@%#*+===+=====*#%@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@%*++===============**%@@@@@@@@@@@@@@
@@@@@@@@@@@#*+=========+==+==+======+*%@@@@@@@@@@@
@@@@@@@%#*+=====+==+=+========+=+======+*#@@@@@@@@
@@@@%#*=======+===-::... ....::--=+=+======*#%@@@@
@%#+=======+===:.                .:-==========+#%@
#======+=+==-.                      .-=+========*%
=====+=====.                          .-===++*#%%%
==+=====+:                              :+*#%%%%%@
====+==+:           .--===---.        :=#%%%%%%@%%
=+====+-          :=======+==+=:  .:+#%%%%%%@%%%%%
====+==         .-+==+=========++*#%@%:+@%:*%%@%%@
==+===-         -======+===++*#%%%@*==.:== -=+%%%%
=====+:        .===+=====+##%%%@%%%#**.-#* =**%%%@
=+====-         =====++#%@%%%@%%%@%#++.-++ -+*%%%%
===+=+-         -++*#%@%@%@%@%%@%%%#++ -++ -++%%@%
=======.         +%@%@%@%%@%@%@%#+#%%@-*%%-*@%%%%%
=+====+-          =#%@%%@%@%@%%=   :=*%%%%@%%%@%@%
===+====-           :=*####*=-        .-*%%%%%%%%%
=====+*#%*.                             =%@%@%@%%%
=++*%%%@%%#-                          :#@%@%%@%%@%
%#%@%@%@%@%@*-                      :*%%%@%@%%@%%@
@@@%@%%@%@%%@%%+:.              .:=#@%@@%@%%@%@@@@
@@@@@@@%@%@%@%%@%%#+=-:::.::-=+*%%@%@%%%@%@@@@@@@@
@@@@@@@@@%@%%@%@%@%%@%@%%@%@%%@%%@%@%@%@%@@@@@@@@@
@@@@@@@@@@@@@%@%@%@%@%%@%@%%@%@%@%@%@%@@@@@@@@@@@@
@@@@@@@@@@@@@@@@%%@%%@%@%%@%@%%@%@%@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@%@%@%@%@%@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@%@%@%@@@@@@@@@@@@@@@@@@@@@@@                   
```

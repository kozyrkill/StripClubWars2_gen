# SCW Character Image Pack Generator

Generate Strip Club Wars 2 character image packs using Stable Diffusion WebUI.

## Features

- ✅ Automatic generation of all character image types (poses)
- ✅ Full support for SCW character attributes (gender, ethnicity, age, body type)
- ✅ Correct file naming following SCW standards
- ✅ Automatic background removal for body images
- ✅ Correct image sizes (512x800 for body, 120x160 for head)
- ✅ JSON-based character configuration
- ✅ Batch generation for multiple characters

## Installation

### Requirements

1. Stable Diffusion WebUI running on port 7860 with API enabled:
   ```bash
   python launch.py --api
   ```

2. Python 3.8+ with pip

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Quick start

Generate sample characters:

```bash
python scw_image_generator.py --test
```

### Generate from config

Create or edit configuration files in the `configs/` folder and run:

```bash
# Use the main config with 50+ characters
python scw_image_generator.py --config configs/character_config.json

# Use the mini config for quick testing  
python scw_image_generator.py --config configs/character_config.mini.json

# Use the player config for player characters
python scw_image_generator.py --config configs/character_config.players.json

# Use the full spectrum config covering all character types
python scw_image_generator.py --config configs/character_config.full_spectrum.json
```

### CLI options

```bash
python scw_image_generator.py --help
```

Available options:
- `--output-dir` - directory to save images (default: `generated_characters`)
- `--modkey` - module key used in filenames (default: `custom`)
- `--test` - generate sample characters
- `--test-type` - simple/detailed/extreme sample sets (default: simple)
- `--config` - path to JSON file with character presets
- `--count` - limit number of characters from config

### Examples

```bash
# Generate sample characters
python scw_image_generator.py --test

# Generate from config with custom mod key
python scw_image_generator.py --config configs/character_config.json --modkey mymod

# Generate only first 3 characters from config
python scw_image_generator.py --config configs/character_config.json --count 3

# Save to a specific directory
python scw_image_generator.py --test --output-dir ./my_characters
```

## Config structure

File `character_config.json` example:

```json
{
  "character_presets": [
    {
      "name": "young_woman",
      "gender": "f",
      "age_group": 2,
      "ethnicity": "w",
      "body_shape": "n",
      "hair_color": "l",
      "hair_length": "l"
    }
  ],
  "generation_settings": {
    "default_poses": ["head", "cas", "uw", "nude"],
    "steps": 30,
    "cfg_scale": 7.5
  }
}
```

### Character attributes

#### Required (reqphys)
- `gender`: "f" (female) or "m" (male)
- `age_group`: 1-5 (18-24, 22-31, 28-42, 38-51, 48+)
- `ethnicity`: "w" (white), "b" (black), "h" (hispanic), "a" (asian), "r" (middle eastern)

#### Optional (optphys)
- `height`: "t" (tall), "m" (medium), "s" (short)
- `body_shape`: "s" (slim), "n" (normal), "c" (curvy), "f" (fit)
- `hips_size`: "s" (small), "m" (medium), "l" (large)
- `breast_penis_size`: "s", "m", "l", "h", "x"
- `skin_tone`: "l" (light), "m" (medium), "d" (dark)

#### Image attributes (imgphys)
- `hair_color`: "l" (light), "m" (medium), "d" (dark)
- `hair_length`: "b" (bald), "s" (short), "m" (medium), "l" (long)
- `eye_color`: "l" (light), "m" (medium), "d" (dark)

## Pose types

The generator creates the following images:

### Base poses (for all)
- `head` - head/portrait (120x160px)
- `cas` - casual
- `uw` - underwear
- `nude` - nude

### Additional poses
- `bc` - business casual
- `biz` - business suit
- `fun` - workout/home clothes

### Female-only
- `tl` - topless
- `ss` - swimsuit
- `s1` - stripper outfit 1
- `s2` - stripper outfit 2 (more revealing)
- `s3` - stripper outfit 3 (very revealing)
- `preg` - pregnant

## Output structure

All characters of a single run are saved under a timestamped session:

```
generated_characters/
└── session_20250909_173538/
    ├── custom-26329-f2w-mnmml-llm-u-head.png
    ├── custom-26329-z0-cas.png
    ├── custom-26329-z1-cas.png
    ├── custom-26329-z2-cas.png
    ├── custom-26329-z3-uw.png
    ├── custom-26329-z9-nude.png
    ├── custom-43829-m4a-mfmml-dsd-u-head.png
    ├── custom-43829-z0-cas.png
    └── ...
```

### Character ID system
- Females: random IDs 00000-49999 (e.g., 26329)
- Males: random IDs 10000-19999 (e.g., 13947)
- Generation: time-based with randomness

## Filename format

The generator follows SCW naming rules:

### Head
```
modkey-id-reqphys-optphys-imgphys-special-head.png
custom-26329-f2w-mnmml-llm-u-head.png
```

### Other poses (with variants)
```
modkey-id-reveal-pose.png
custom-26329-z0-cas.png    # reveal=0
custom-26329-z1-cas.png    # reveal=1
custom-26329-z9-nude.png   # reveal=9
```

## Troubleshooting

### WebUI not responding
- Ensure Stable Diffusion WebUI is running with `--api`
- Check that WebUI is reachable at http://localhost:7860

### Generation errors
- Check WebUI logs for errors
- Ensure you have enough VRAM
- Try reducing steps in config

### Poor background removal
- `rembg` may not be perfect for all images
- Manually edit if needed

## License

This project is provided for use with Strip Club Wars 2.

## Contributing

Found issues or have suggestions? Please open issues or pull requests.

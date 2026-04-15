# iLoL ARAM Analyst

Mobile app for analyzing ARAM gameplay data from League of Legends.

## Overview

iLoL is a KivyMD-based Android app that analyzes match history data to provide strategic insights for ARAM players. Data is mined on PC and transferred to the mobile app for on-the-go analysis.

## Features

| Tab | Description |
|-----|-------------|
| **Config** | Configure API key, price thresholds, and minimum game requirements |
| **Meta** | Generate tier lists showing best/worst champions by winrate |
| **Analista** | Analyze champion item efficiency against specific enemy classes |
| **Composicao** | Get item recommendations based on enemy team composition |
| **Core Build** | Find optimal 3-item combinations for your champion |
| **Late Game** | Analyze 4th/5th/6th item choices for late-game power |
| **Pw. Spike** | Visualize winrate curve based on number of items |

## How It Works

1. **Mine data on PC** - Use a separate PC script to fetch match data via Riot API
2. **Transfer files** - Copy `historico_partidas.json` and `campeoes.json` to your Android device
3. **Analyze on mobile** - Use the app to explore builds, compositions, and meta trends

## Setup

### Requirements
```
pip install -r requirements.txt
```

### Configuration
1. Open the app
2. Go to **Config** tab
3. (Optional) Set your Riot API key for future reference
4. Adjust analysis parameters as needed

### Data Files
Place these files in the app's data directory:
- `historico_partidas.json` - Match history with items and win data
- `campeoes.json` - Champion data with class tags
- `itens.json` - Item database with prices

## Tech Stack

- **Frontend**: KivyMD (Material Design for Kivy)
- **Platform**: Android (via Buildozer/GitHub Actions)
- **Data Format**: JSON

## Project Structure

```
iLoL Android/
├── centro.py          # Main app entry point
├── config.py          # Configuration management
├── utils.py           # Utility functions
├── core.py            # Core build analysis
├── analista.py       # Champion vs class analysis
├── analista2.py      # Composition analysis
├── late.py            # Late game analysis
├── powerspike.py      # Power spike visualization
├── top_meta.py        # Meta/tier list generator
├── requirements.txt   # Python dependencies
└── README.md
```

## License

MIT License

# WeaveGrid for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)

A Home Assistant integration for [WeaveGrid](https://www.weavegrid.com/), a managed EV charging platform that works with utilities (BGE, PG&E, etc.) to optimize EV charging schedules.

## Features

- **Binary sensors**: Charging status, plugged in, home presence
- **Sensors**: Weekly energy usage, weekly cost, smart score, last charge energy/cost, managed charge status, miles added, battery level
- Automatic device creation per vehicle/EVSE
- Reauthorization support

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right and select **Custom repositories**
3. Add this repository URL and select **Integration** as the category
4. Click **Install**
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/weavegrid` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **WeaveGrid**
3. Enter your WeaveGrid account email and password
4. The integration will auto-detect your utility and create devices for each registered vehicle/EVSE

## Entities

### Binary Sensors

| Entity | Description |
|--------|-------------|
| Charging | Whether the vehicle is currently charging |
| Plugged in | Whether the vehicle is plugged in |
| Home | Whether the vehicle is at the home location |

### Sensors

| Entity | Description |
|--------|-------------|
| Weekly energy | Total energy delivered this week (kWh) |
| Weekly cost | Total charging cost this week (USD) |
| Smart score | WeaveGrid smart charging score (%) |
| Last charge energy | Energy delivered in most recent charge session (kWh) |
| Last charge cost | Cost of most recent charge session (USD) |
| Managed charge status | Current managed charge plan status |
| Miles added | Miles of range added by the charge plan |
| Battery level | Current battery state of charge (%) |

## Notes

- Data is polled every 5 minutes
- The integration uses WeaveGrid's GraphQL API with cookie-based session authentication
- Charge aggregates show a rolling 7-day window

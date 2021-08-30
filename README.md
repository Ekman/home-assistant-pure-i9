# Home Assistant Pure i9

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

This repository adds the capability of integrating your [Electrolux Pure i9 vacuum cleaner](https://www.electrolux.se/wellbeing/discover/robot-vacuum-cleaner-purei9/) with the smart home platform [Home Assistant](https://www.home-assistant.io/). This integration communicates with your Pure i9 using the cloud.

The code is using the Python library [`purei9_unofficial`](https://github.com/Phype/purei9_unofficial) to interact with the Pure i9. Credits to [`homeassistant_electrolux_purei9`](https://github.com/anhaehne/homeassistant_electrolux_purei9) for creating a Pure i9 integration that communicates with your vacuum cleaner locally inside your network, and for acting as a starting point to write this integration.

## Disclaimer

Me or this repository is in no way affiliated with Electrolux. This is purely a fan project.

## Installation

Install using [Home Assistant Community Store (HACS)](https://hacs.xyz/). Follow these steps:

1. [Add `https://github.com/Ekman/home-assistant-pure-i9` as a custom repository in `HACS`](https://hacs.xyz/docs/faq/custom_repositories/)
2. Install `Pure i9` using `HACS`
3. Reboot Home Assistant

## Configuration

Add this to your Home Assistant configuration:

``` yaml
vacuum:
  - platform: purei9
    email: me@example.com
    password: example
```

## Versioning

This project complies with [Semantic Versioning](https://semver.org/).

## Changelog

For a complete list of changes, and how to migrate between major versions, see [releases page](https://github.com/Ekman/home-assistant-purei9/releases).

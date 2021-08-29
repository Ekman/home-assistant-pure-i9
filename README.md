# Home Assistant Pure i9

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

*Home Assistant Pure i9* adds the capability of integrating your [Electrolux Pure i9 vacuum cleaner](https://www.electrolux.se/wellbeing/discover/robot-vacuum-cleaner-purei9/) into the smart home platform [Home Assistant](https://www.home-assistant.io/). This integration is dependent on an internet connection as it communicates with your Pure i9 using the cloud, not locally inside your network.

The code is using the Python library [`purei9_unofficial`](https://github.com/Phype/purei9_unofficial) to interact with the Pure i9. Credits to [`homeassistant_electrolux_purei9`](https://github.com/anhaehne/homeassistant_electrolux_purei9) for creating a Pure i9 integration that communicates with your vacuum cleaner locally inside your network, and for acting as a starting point to write this integration.

## Disclaimer

Me or this repository is in now way affiliated with Electrolux. This is purely a fan project.

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

## Helpful links

Being the first Home Assistant integration that I wrote, I documented some helpful links:

* [Home Assistant Developers](https://developers.home-assistant.io/)
* [Vacuum entity on Home Assistant Developers](https://developers.home-assistant.io/docs/core/entity/vacuum/)
* [Source code for the Home Assistant entity class](https://github.com/home-assistant/core/blob/adab367f0e8c48a68b4dffd0783351b0072fbd0a/homeassistant/helpers/entity.py)
* [Source code for the Home Assistant vacuum class](https://github.com/home-assistant/core/tree/dev/homeassistant/components/vacuum)

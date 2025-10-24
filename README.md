# Home Assistant Pure i9

[![CircleCI](https://circleci.com/gh/Ekman/home-assistant-pure-i9/tree/master.svg?style=shield)](https://circleci.com/gh/Ekman/home-assistant-pure-i9/tree/master)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/nekman)

**Discontinued: Use [Home Assistant Wellbeing](https://github.com/JohNan/homeassistant-wellbeing) instead. [Want to know more about my decision? Read here](https://github.com/Ekman/home-assistant-pure-i9/issues/114).**

Integrate your [Electrolux Pure i9 robot vacuum](https://www.electrolux.se/wellbeing/discover/robot-vacuum-cleaner-purei9/) with the smart home platform [Home Assistant](https://www.home-assistant.io/). The integration communicates with your Pure i9 using the cloud.

Credits to [`purei9_unofficial`](https://github.com/Phype/purei9_unofficial) for creating a Python library for interacting with the Pure i9.

## Disclaimer

Me or this repository is in no way affiliated with Electrolux. This is purely a fan project.

## Installation

Install using [Home Assistant Community Store (HACS)](https://hacs.xyz/).

**If you don't already have HACS installed** then follow these steps:

1. [Install HACS](https://hacs.xyz/docs/setup/prerequisites)
2. [Configure HACS](https://hacs.xyz/docs/configuration/basic)

**Once HACS is installed on your Home Assistance** then follow these steps:

1. Add `https://github.com/Ekman/home-assistant-pure-i9` as a [custom repository in HACS](https://hacs.xyz/docs/faq/custom_repositories/)
2. Install `Pure i9` using HACS
3. Reboot Home Assistant

## Configuration

Follow these steps to configure the integration:

1. Navigate to `Settings -> Devices & Services -> Integrations`.
2. Click `+ Add Integration`.
3. Find **Electrolux Pure i9**.
4. Enter your Electrolux e-mail, password and a [2-letter country code (ISO 3166-1 alpha-2)](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2).

For more information on what the integration can do [read the manual](MANUAL.md).

## Versioning

This project complies with [Semantic Versioning](https://semver.org/).

## Changelog

For a complete list of changes, and how to migrate between major versions, see [releases page](https://github.com/Ekman/home-assistant-pure-i9/releases).

## Buy me a coffee

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/braska)

If you appreciate this integration, then consider [buying me a coffee](https://buymeacoffee.com/braska). Donations are completely voluntary.

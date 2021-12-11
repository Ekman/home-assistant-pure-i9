# Home Assistant Pure i9

[![CircleCI](https://circleci.com/gh/Ekman/home-assistant-pure-i9/tree/master.svg?style=svg)](https://circleci.com/gh/Ekman/home-assistant-pure-i9/tree/master)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Integrate your [Electrolux Pure i9 robot vacuum](https://www.electrolux.se/wellbeing/discover/robot-vacuum-cleaner-purei9/) with the smart home platform [Home Assistant](https://www.home-assistant.io/). The integration communicates with your Pure i9 using the cloud.

Credits to:

* [`purei9_unofficial`](https://github.com/Phype/purei9_unofficial) - A python library for interacting with the Pure i9.
* [`homeassistant_electrolux_purei9`](https://github.com/anhaehne/homeassistant_electrolux_purei9) - For creating a Pure i9 integration that communicates with your robot vacuum locally inside your network, and for acting as a starting point to write this integration.

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

Add this to your Home Assistant configuration:

``` yaml
vacuum:
  - platform: purei9
    email: me@example.com
    password: example
```

For more information on what the integration can do [read the manual](MANUAL.md).

## Versioning

This project complies with [Semantic Versioning](https://semver.org/).

## Changelog

For a complete list of changes, and how to migrate between major versions, see [releases page](https://github.com/Ekman/home-assistant-pure-i9/releases).

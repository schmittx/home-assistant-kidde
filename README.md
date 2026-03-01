[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
# Kidde Home Assistant Integration
Custom component to allow control of [Kidde devices](https://www.kidde.com/products/smart) in [Home Assistant](https://home-assistant.io).

## Features
- This is a small integration to allow basic monitoring via Home Assistant.
- `binary_sensor`, `button`, `sensor`, and `switch` entities will be created for each device.
- Currently, only the 30CUAR-W model has been confirmed to work with this integration.

## Install
1. Ensure Home Assistant is updated to version 2025.12.0 or newer.
2. Use HACS and add as a [custom repo](https://hacs.xyz/docs/faq/custom_repositories); or download and manually move to the `custom_components` folder.
3. Once the integration is installed follow the standard process to setup via UI and search for `Kidde`.
4. Follow the prompts.

## Options
- Locations and devices can be updated via integration options.
- If `Advanced Mode` is enabled for the current profile, additional options are available (interval, timeout, and response logging).

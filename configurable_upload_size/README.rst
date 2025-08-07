# Configurable Upload Size

## Description

This module allows configuring the maximum file upload size in Odoo through system parameters, replacing the fixed 25MB limit that is hardcoded in Odoo's core.

## Features

- **Configurable size**: Upload limit can be adjusted dynamically
- **System parameter**: Uses `ir.config_parameter` to store configuration
- **JavaScript override**: Overrides FieldBinary widget behavior
- **Default value**: 25 MB if not configured

## Installation

1. Copy the module to the addons folder
2. Update the modules list
3. Install the "Configurable Upload Size" module

## Configuration

1. Go to **Settings > Technical > System Parameters**
2. Search or create the parameter: `web.max_file_upload_size`
3. Set the value in MB (example: 50 for 50MB)
4. Save changes

## Usage

Once configured, all binary fields (files, images) will use the new size limit.

## System Parameters

| Key | Description | Default Value |
|-----|-------------|---------------|
| `web.max_file_upload_size` | Maximum upload size in MB | 25 |

## Modified Files

The module overrides the behavior of:
- `FieldBinary` in the JavaScript frontend

## Technical Notes

- The value is automatically converted from MB to bytes
- If parameter retrieval fails, uses 25MB as fallback
- Compatible with Odoo 10.0

## Credits

**Author**: Moval
**Version**: 10.0.1.0.0

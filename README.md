# Webex Status for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration that exposes your Webex status as a sensor entity. Know when someone in your household is in a meeting, on a call, or presenting — right from the Home Assistant dashboard.

[<img width="300" height="150" alt="owenmettam-Sharable-Profile)-Horizontal" src="https://github.com/user-attachments/assets/9e5011f2-924e-4b09-a8e0-753f617e7990" />](https://ko-fi.com/owenmettam)

## Preview

This is how the integration can look inside of your Home Assistant homepage.

<img width="466" alt="image" src="https://github.com/user-attachments/assets/0dbb2e92-1456-4199-97c2-9f9c9ba58b38" />

The logo and all of the text can be changed as you need, as this can be done via various card types.

## Installation

### Option A: Install via HACS (Recommended)

1. Make sure [HACS](https://hacs.xyz/) is installed in your Home Assistant instance.
2. In HACS, click the three dots in the top right corner and select **Custom repositories**.
3. Add this repository URL: `https://github.com/owenmettam/HomeAssistant-WebexStatus`
4. Select **Integration** as the category and click **Add**.
5. Search for "Webex Status" in HACS and click **Install**.
6. Restart Home Assistant.

### Option B: Manual Installation

1. Download or clone this repository.
2. Copy the `custom_components/webex_status` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

Once installed, set up the integration entirely through the UI — no YAML editing required.

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **Webex Status**.
3. Enter your **Webex Bot Access Token** and **Person ID** (encoded UUID).
4. The integration will validate your credentials and create a sensor entity automatically.

The sensor polls the Webex API every 15 seconds and exposes one of the following statuses:

| Status | Friendly Name | Icon |
|---|---|---|
| `active` | Active | `mdi:account-check` |
| `call` | In a Call | `mdi:phone-in-talk` |
| `DoNotDisturb` | Do Not Disturb | `mdi:minus-circle` |
| `inactive` | Inactive | `mdi:account-off` |
| `meeting` | In a Meeting | `mdi:monitor-cellphone` |
| `presenting` | Presenting | `mdi:presentation` |
| `OutOfOffice` | Out of Office | `mdi:briefcase-off` |
| `pending` | Pending | `mdi:account-clock` |

### Sensor Attributes

The sensor entity also exposes these extra attributes:
- **friendly_status** — Human-readable status name
- **display_name** — The Webex user's display name
- **emails** — Email addresses associated with the account
- **avatar** — URL to the user's Webex avatar (also used as the entity picture)
- **last_activity** — Timestamp of last activity

## Getting the Required Values

You need two values to configure the integration:
- Your **Webex Bot API Bearer Token**
- Your **Webex People API encoded user ID**

### Get a Webex Bot API Bearer Token

1. Login to the [Webex Developer Portal](https://developer.webex.com/my-apps/new), and click "Create a Bot".
2. Fill in the required information (the details don't matter — we just need the token).
3. Once submitted, copy the **Bot access token** from the next page (valid for ~100 years).

![image](https://github.com/user-attachments/assets/351ae652-c0e3-4400-8064-6020b3dab6ae)

### Get your Webex Encoded UUID from the Webex People API

1. Login to the [Webex Developer Portal API Reference](https://developer.webex.com/docs/api/v1/people/get-my-own-details) and navigate to the "Get My Own Details" endpoint.
2. Click **Run** to execute the API call.

![image](https://github.com/user-attachments/assets/26b28b04-4c3e-4168-97f9-2d16e74f5650)

3. In the response, the first line `"id"` is your encoded UUID.

   ![image](https://github.com/user-attachments/assets/2a188559-9883-4355-914c-91eb20ec9c4e)

<img width="378" alt="image" src="https://github.com/user-attachments/assets/d698a49e-ec4b-4809-90c2-b7d5b333830d" />

## Dashboard Cards

By default, an entity is available with your Webex profile picture, name, and status.

You can display the status using any card type. Here is an example using [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) (available via HACS):

```yaml
- type: custom:mushroom-template-badge
  content: In a Meeting
  icon: mdi:monitor-cellphone
  color: orange
  entity: sensor.YOURNAME_webex_status
  visibility:
    - condition: state
      entity: sensor.YOURNAME_webex_status
      state: meeting
  label: Webex Status
  picture: https://play-lh.googleusercontent.com/tFFAvb_eZM5BlHYFiuyVwhM54o7mvfCOFX3AGbgTULfKpEancPmZnP1PRu44CZiZgyI
```

<img width="153" alt="image" src="https://github.com/user-attachments/assets/76270b73-893f-4840-be4d-adf6d080a1e1" />

Replace `YOURNAME_webex_status` with the actual entity ID created by the integration (visible in **Settings → Devices & Services → Webex Status**).

## FAQs

**Q: Who can I get the status of?**\
A: As configured, this is designed to get _your_ Webex status. Depending on the admin scopes assigned to your Webex account, it is possible to get additional users in your Webex organization by leveraging the People API, however this is not recommended.

**Q: I keep getting a status of "unknown", what does this mean?**\
A: This is likely due to a misconfiguration, such as missing the correct Webex Bot token, or not copying the correct People API UUID from the Webex Developer portal. Try removing and re-adding the integration with the correct values. Additionally, there is open issue [#1](https://github.com/owenmettam/HomeAssistant-WebexStatus/issues/1) regarding this.

**Q: I keep getting a status of "pending", what does this mean?**\
A: This is due to your Webex account not having been signed into ever before, and as a result never got a true Webex status configured. Sign into the Webex application to ensure that a status can be reflected. Note that this status is _not_ the same as "unknown".

**Q: Can I still use the old YAML configuration method?**\
A: Yes. See the [Legacy YAML Method](#legacy-yaml-method) section below.

## Legacy YAML Method

<details>
<summary>Click to expand the original YAML-based setup</summary>

Add the following to your `configuration.yaml`:

```yaml
command_line:
  - sensor:
      name: My Webex Status
      json_attributes:
        - status
      command: "curl -H 'Authorization:Bearer YOUR_BOT_TOKEN' https://webexapis.com/v1/people/YOUR_PERSON_ID"
      value_template: "{{ value_json.status }}"
      scan_interval: 15
```

Replace `YOUR_BOT_TOKEN` and `YOUR_PERSON_ID` with the values from the sections above, then restart Home Assistant.

</details>

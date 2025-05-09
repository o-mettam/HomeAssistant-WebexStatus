# Home Assistant - Get your Webex status inside Home Assistant
Ever wanted to have a simple and easy-to-understand message to users inside of your house that you are in a Webex meeting or call? Worried about people waling into the office when you are in the middle of an important presentation? Then this guide is for you!

## Preview
This is how the plugin can look inside of your Home Assistant homepage. 

<img width="466" alt="image" src="https://github.com/user-attachments/assets/0dbb2e92-1456-4199-97c2-9f9c9ba58b38" />

The logo and all of the text can be changed as you need, as this can be done via various card types.

## Steps to implement
**1) Open the Home Assistant configuration.yaml file, and add the following:**
   
````
command_line:
  - sensor:
      name: My Webex Status
      json_attributes:
        - status
      command: "curl -H 'Authorization:Bearer REPLACETHISTEXTWITHYOURWEBEXBOTTOKEN' https://webexapis.com/v1/people/REPLACETHISTEXTWITHYOURPEOPLEAPIUUID"
      value_template: "{{ value_json.status }}"
      scan_interval: 15
````

You can see that this text is going to create a sensor that uses the Home Assistant CLI to send a CURL API request to Webex APIs, and then extract the Webex User Status from the JSON paylod. Since the API response we get from Webex is already in a formatted JSON response, we don't need to do any special formatting to get the correct value. This script is designed to run every 15 seconds (changed by altering the "scan_interval" value, I do not recommend going much lower than this due to your CURL requests getting a 429 Too Many Requests rejection, and getting rate limited).

**2) Get the required values for the configuration**

You'll see that there are two values that we need to obtain in order to get this working. These are:
- Your Webex Bot API Bearer Token
- Your Webex People API encoded user ID

### Get a Webex Bot API Bearer Token
To get a Webex Bot API bearer token, we need to first create a bot.
1) Login to the [Webex Developer Portal](https://developer.webex.com/my-apps/new), and click "Create a Bot"
2) You will be asked to provide some information, all of this information can be completed however you want, as all we need is the admin bearer token at the end of this.
3) Once you submit this information, on the next page you will be provided with the Bot access token, which is valid for 100 years. You need to copy this token, and place it into the config above.
   
![image](https://github.com/user-attachments/assets/351ae652-c0e3-4400-8064-6020b3dab6ae)

### Get your Webex Encoded UUID from the Webex People API
To get your Webex Encoded UUID, you need to get this from the Webex Developer portal
1) Login to the [Webex Developer Portal API Reference](https://developer.webex.com/docs/api/v1/people/get-my-own-details) and navigate to the API GET call for "Get my Own Details"
2) Click "Run" when you get the popout to try the API.

![image](https://github.com/user-attachments/assets/26b28b04-4c3e-4168-97f9-2d16e74f5650)

3) In the API response, the first line is "id", this is your UUID that you use in the config above.

   ![image](https://github.com/user-attachments/assets/2a188559-9883-4355-914c-91eb20ec9c4e)

You can also see in the API response the "status" string that we will be reading above. For example, here is shows the user is "Active" in the Webex app.

<img width="378" alt="image" src="https://github.com/user-attachments/assets/d698a49e-ec4b-4809-90c2-b7d5b333830d" />

**3) Restart Home Assistant (required to get the new configuration.yaml loaded into the OS**

**4) Confirm that your Webex Status is now being shown in Home Assistant**
Once you have finished rebooting Home Assistant, you should now see a new entity called "Webex Status" under the "Command Line" integration. If working, it should expose one of the following values.

- active
- call
- DoNotDisturb
- inactive
- meeting
- presenting
- OutOfOffice

More information on the user status can be found in the [Webex Developer API portal](https://developer.webex.com/docs/api/v1/people/get-my-own-details).

![image](https://github.com/user-attachments/assets/ede2bb61-e5ad-4563-829d-ab614f81f500)


**5) Begin building your cards to expose the status to users**
This section is going to be specific for adding the badges to the Home Assistant UI. There are __many__ different choices and cards you can use here, so I am just going to focus on the one I've implemented already and tested. I'm using the [HACS plugin Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) to add the Webex logo to the cards, so you can add this to your Dashboard configuration file.

````
     - type: custom:mushroom-template-badge
        content: In a Meeting
        icon: mdi:monitor-cellphone
        color: orange
        entity: sensor.my_webex_status
        visibility:
          - condition: state
            entity: sensor.my_webex_status
            state: meeting
        label: My Webex Status
        picture: https://play-lh.googleusercontent.com/tFFAvb_eZM5BlHYFiuyVwhM54o7mvfCOFX3AGbgTULfKpEancPmZnP1PRu44CZiZgyI
````
<img width="153" alt="image" src="https://github.com/user-attachments/assets/76270b73-893f-4840-be4d-adf6d080a1e1" />

To explain what each of these parts do:
- content: This is the text that shows in the bottom part of the card
- icon: can be ignored as we are replacing the icon with the picture of the Webex Logo
- color: can be ignored as we are replacing the icon with the picture of the Webex Logo
- entity: this is the Webex Status sensor we created above
- visbility: this is going to determine when the card should show, only if the state of the Webex status sensor is equal to active
- label: top part of the card, defines what this is
- picture: This is pulling the Google Play store logo for the Webex application

## FAQs
**Q: Who can I get the status of?**\
A: As configured, this is designed to get _your_ Webex status. Depending on the admin scopes assigned to your Webex account, it is possible to get additional users by leveraging the People API, however this is not recommended.

**Q: I keep getting a status of "unknown", what does this mean?**\
A: This is likely due to a misconfiguration, such as missing the correct Webex Bot token, or not copying the correct PeopleAPI UUID from the Webex Developer portal. Make sure both values are placed into the configuration, and revist the status to ensure it is reflecting correctly.

**Q: I keep getting a status of "pending", what does this mean?**\
A: This is due to your Webex account not having been signed into ever before, and as a result never got a true Webex status configured. Sign into the Webex application to ensure that a status can be reflected. Note that this status is _not_ the same as "unknown".

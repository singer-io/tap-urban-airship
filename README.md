# tap-urban-airship

This is a [Singer](https://singer.io) tap that produces JSON-formatted data following the [Singer spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:
- Pulls raw data from Urban Airship's [REST API](https://docs.urbanairship.com/api/ua/)
- Extracts the following resources from Urban Airship:
  - [Channels](http://docs.urbanairship.com/api/ua/#api-channels)
  - [Lists](http://docs.urbanairship.com/api/ua/#api-static-lists)
  - [Named Users](http://docs.urbanairship.com/api/ua/#api-named-users)
  - [Segments](http://docs.urbanairship.com/api/ua/#segments-api)
- Outputs the schema for each resource
- Incrementally pulls data based on the input state


## Quick start

1. Install

    ```bash
    > pip install tap-urban-airship
    ```

2. Get your Urban Airship keys

    Sign into your Urban Airship account. In the dashboard, open the app you want to connect to Stitch. If the Engage tab doesn’t open, click Engage at the top to open it. Click the gear icon located near Reports, then select APIs & Integrations.  The APIs & Integrations page will display. Use your Urban Airship App Key and App Secret in the following step.



3. Create the config file

    Create a JSON file called `config.json` containing the key and secret you just found.

    ```json
    {"app_key": "your-app-key",
     "app_secret": "your-app-secret"}
    ```

4. [Optional] Create the initial state file

    You can provide JSON file that contains a date for the API endpoints
    to force the application to only fetch data newer than those dates.
    If you omit the file it will fetch all Urban Airship data

    ```json
    {"channels": "2017-01-17T20:32:05Z",
    "lists": "2017-01-17T20:32:05Z",
    "segments": "2017-01-17T20:32:05Z",
    "named_users": "2017-01-17T20:32:05Z"}
    ```

5. Run the application

    `tap-urban-airship` can be run with:

    ```bash
    tap-urban-airship --config config.json [--state state.json]
    ```

---

Copyright &copy; 2017 Stitch

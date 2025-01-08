def shelly_gateway_1(method: str, params: dict = None) -> dict:
    """
    Calls a specific Sys method on the ShellyBluGw1.

    Args:
        method (str): The Sys RPC method. Supported methods include:
            - Sys:
                - Sys.GetConfig: Obtain the system configuration
                - Sys.SetConfig: Update the system configuration
                - Sys.GetStatus: Obtain the system status
            - Wifi:
                - Wifi.GetConfig: Obtain the component's configuration
                - Wifi.SetConfig: Update the component's configuration
                - Wifi.GetStatus: Obtain the component's status
                - Wifi.Scan: Scan for available WiFi APs
                - Wifi.ListAPClients: List AP clients
            - BLE:
                - BLE.GetConfig: Obtain the component's configuration
                - BLE.SetConfig: Update the component's configuration
                - BLE.GetStatus: Obtain the component's status
            - MQTT:
                - MQTT.SetConfig: Update the component's configuration
                - MQTT.GetConfig: Obtain the component's configuration
                - MQTT.GetStatus: Obtain the component's status
            - Script:
                - Script.GetConfig: Obtain the script configuration
                - Script.SetConfig: Update the script configuration
                - Script.GetStatus: Obtain the script status
                - Script.List: List scripts
                - Script.Create: Create a new script
                - Script.Delete: Delete a script
                - Script.Start: Start a script
                - Script.Stop: Stop a script
                - Script.PutCode: Upload script code
                - Script.GetCode: Download script code
                - Script.Eval: Evaluate script code
        params (dict): Method parameters.

    Returns:
        dict: JSON response from the ShellyBluGw1.
    """
    import os
    import requests

    ip_address = os.getenv('SHELLYBLU_GATEWAY1')
    if not ip_address:
        raise ValueError("Environment variable SHELLYBLU_GATEWAY1 is not set")
    
    url = f"http://{ip_address}/rpc/{method}"
    response = requests.post(url, json=params or {})
    return response.json()
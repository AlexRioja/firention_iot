# Importing models and REST client class from Community Edition version
from tb_rest_client.rest_client_ce import *
# Importing the API exception
from tb_rest_client.rest import ApiException


# ThingsBoard REST API URL
url = "http://localhost:8080"
# Default Tenant Administrator credentials
username = "tenant@thingsboard.org"
password = "tenant"


# Creating the REST client object with context manager to get auto token refresh
with RestClientCE(base_url=url) as rest_client:
    try:
        # creating a Device
        device = Device(name="Thermometer 1", type="thermometer")
        device = rest_client.save_device(device)

        # find device by device id
        found_device = rest_client.get_device_by_id(DeviceId('DEVICE', device.id))


        extra = rest_client.get_device

        # save device shared attributes
        res = rest_client.save_device_attributes("{'targetTemperature': 22.4}", DeviceId('DEVICE', device.id),
                                                 'SERVER_SCOPE')


        # Get device shared attributes
        res = rest_client.get_attributes_by_scope('DEVICE', DeviceId('DEVICE', device.id), 'SERVER_SCOPE')

        # delete the device
        rest_client.delete_device(DeviceId('DEVICE', device.id))
    except ApiException as e:
        pass
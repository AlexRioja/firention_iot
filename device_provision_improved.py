from paho.mqtt.client import Client
from json import dumps, loads

RESULT_CODES = {
    1: "incorrect protocol version",
    2: "invalid client identifier",
    3: "server unavailable",
    4: "bad username or password",
    5: "not authorised",
    }

class ProvisionClient(Client):
    PROVISION_REQUEST_TOPIC = "/provision/request"
    PROVISION_RESPONSE_TOPIC = "/provision/response"

    def __init__(self, host, port, provision_request,credentials="credentials", debug=False):
        super().__init__()
        self._host = host
        self._port = port
        self._username = "provision"
        self.on_connect = self.__on_connect
        self.on_message = self.__on_message
        self.__provision_request = provision_request
        self.credentials=credentials
        self.debug=debug

    def __on_connect(self, client, userdata, flags, rc):  # Callback for connect
        if rc == 0:
            if self.debug: print("\t[Provisioning client] Connected to ThingsBoard ")
            client.subscribe(self.PROVISION_RESPONSE_TOPIC)  # Subscribe to provisioning response topic
            provision_request = dumps(self.__provision_request)
            if self.debug: print("\t[Provisioning client] Sending provisioning request %s" % provision_request)
            client.publish(self.PROVISION_REQUEST_TOPIC, provision_request)  # Publishing provisioning request topic
        else:
            if self.debug: print("\t[Provisioning client] Cannot connect to ThingsBoard!, result: %s" % RESULT_CODES[rc])

    def __on_message(self, client, userdata, msg):
        decoded_payload = msg.payload.decode("UTF-8")
        if self.debug: print("\t[Provisioning client] Received data from ThingsBoard: %s" % decoded_payload)
        decoded_message = loads(decoded_payload)
        provision_device_status = decoded_message.get("status")
        if provision_device_status == "SUCCESS":
            self.__save_credentials(decoded_message["credentialsValue"])
            self.cred=decoded_message["credentialsValue"]
        else:
            if self.debug: print("\t[Provisioning client] Provisioning was unsuccessful with status %s and message: %s" % (provision_device_status, decoded_message["errorMsg"]))
        self.disconnect()

    def provision(self):
        if self.debug: print("\t[Provisioning client] Connecting to ThingsBoard (provisioning client)")
        
        self.connect(self._host, self._port, 60)
        self.loop_forever()

    def get_new_client(self):
        client_credentials = self.__get_credentials()
        new_client = None
        if client_credentials:
            new_client = Client()
            new_client.username_pw_set(client_credentials)
            print("\t[Provisioning client] Read credentials from file.")
        else:
            print("\t[Provisioning client] Cannot read credentials from file!")
        return new_client

    def __get_credentials(self):
        new_credentials = None
        try:
            with open(self.credentials, "r") as credentials_file:
                new_credentials = credentials_file.read()
        except Exception as e:
            print("Get Credentials:"+str(e))
        return new_credentials

    def __save_credentials(self, credentials):
        self.__clean_credentials()
        with open(self.credentials, "w") as credentials_file:
            credentials_file.write(credentials)

    def __clean_credentials(self):
        try:
            open(self.credentials, "w").close()
        except:
            pass

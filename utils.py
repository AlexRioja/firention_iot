


class Lake:
    def __init__(self, name, latitude, longitude, link):
        self.name=name
        self.latitude=latitude
        self.longitude=longitude
        self.link=link
        self.capacity=None
        self.percentage=None
        self.current_water=None
    def distance_to_point(point):
        raise ValueError("Mehtod not implemented yet")
    
def read_cred(index):
    new_credentials = None
    try:
        with open("cred_"+str(index), "r") as credentials_file:
            new_credentials = credentials_file.read()
    except Exception as e:
        print(e)
    return new_credentials
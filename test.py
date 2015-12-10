import urllib
from base64 import b64encode
import requests
import json

username = "d7e2536f-0268-41e3-b029-b4cb44161632"
password = "idCjPs9d3o4fTOrKSBPOM4fj9gxz7uHAsMxYY8Bv/YU"

def get_picture(name):
    print "get picture"
    name = name.encode('ascii', 'ignore')
    query = urllib.quote(name)
    headers = {
        "Authorization": 'Basic ' + b64encode("{0}:{1}".format(username, password))
    }
    url = "https://api.datamarket.azure.com/Bing/Search/Image?%24format=json&ImageFilters=%27Aspect%3AWide%27&Query=%27" + query + "%27&$top=1" 
    r = requests.get(url, headers = headers)
    image_json = json.loads(r.text)
    return image_json["d"]["results"][0]["MediaUrl"]


def main():
    picture = get_picture('finding nemo movie poster')
    print picture

if __name__ == '__main__':
    main()
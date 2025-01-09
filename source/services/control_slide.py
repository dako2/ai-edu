import requests

class ControlSlide:
    def __init__(self, server_url):
        self.server_url = server_url

    def navigate_slide(self, slide_number):
        """
        Set the current slide by sending a POST request to the server.
        """
        endpoint = f"{self.server_url}/set_slide_number/{slide_number}"
        response = requests.post(endpoint)
        if response.status_code == 200:
            print(f"Slide updated to {slide_number}")
        else:
            print(f"Failed to update slide: {response.json()}")

    def get_current_slide(self):
        """
        Get the current slide index by sending a GET request to the server.
        """
        endpoint = f"{self.server_url}/get_slide_index"
        response = requests.get(endpoint)
        if response.status_code == 200:
            return response.json().get("slideIndex")
        else:
            print(f"Failed to fetch current slide: {response.json()}")
            return None

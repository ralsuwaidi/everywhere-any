import http.client
import json
import os


class AnytypeClient:
    def __init__(self, host="localhost", port=31009):
        self.host = host
        self.port = port
        self.api_key = os.environ.get("ANYTYPE_API_KEY")
        if not self.api_key:
            raise ValueError("ANYTYPE_API_KEY environment variable not set")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(self, method, endpoint, payload=None):
        conn = http.client.HTTPConnection(self.host, self.port)
        body = json.dumps(payload) if payload else ""
        conn.request(method, endpoint, body, self.headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))

    def get_spaces(self):
        return self._make_request("GET", "/v1/spaces")

    def get_object_types(self, space_id):
        return self._make_request("GET", f"/v1/spaces/{space_id}/types")

    def get_object_type(self, space_id, type_id):
        return self._make_request("GET", f"/v1/spaces/{space_id}/types/{type_id}")

    def search_objects(self, space_id, query, type_ids):
        payload = {"query": query, "types": type_ids}
        return self._make_request("POST", f"/v1/spaces/{space_id}/search", payload)

    def create_object(self, space_id, payload):
        return self._make_request("POST", f"/v1/spaces/{space_id}/objects", payload)

    def update_object(self, object_id, payload):
        return self._make_request("PATCH", f"/v1/objects/{object_id}", payload)

    def get_templates_for_type(self, space_id, type_id):
        return self._make_request("GET", f"/v1/spaces/{space_id}/types/{type_id}/templates")

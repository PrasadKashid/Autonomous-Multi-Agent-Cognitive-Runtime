import json
import re


class ResponseParser:

    def parse(self, response: str):

        response = response.strip()

        # Remove ```json ... ```
        response = re.sub(r"^```json", "", response)
        response = re.sub(r"^```", "", response)
        response = re.sub(r"```$", "", response)
        response = response.strip()

        try:
            return json.loads(response)

        except Exception:
            return {"raw_response": response}


response_parser = ResponseParser()

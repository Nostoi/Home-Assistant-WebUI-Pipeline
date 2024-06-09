# examples/scaffolds/home_assistant_pipeline.py
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
import requests
import os
import ast
from typing import List, Dict, Union

class Pipeline(FunctionCallingBlueprint):
	class Valves(FunctionCallingBlueprint.Valves):
		HOME_ASSISTANT_API_URL: str = os.getenv("HOME_ASSISTANT_API_URL", "")
		HOME_ASSISTANT_TOKEN: str = os.getenv("HOME_ASSISTANT_TOKEN", "")

	class Tools:
		def __init__(self, pipeline) -> None:
			self.pipeline = pipeline

		def get_state(self, entity_id: str) -> Union[dict, str]:
			"""Get the state of an entity."""
			try:
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states/{entity_id}"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				return self._format_response(response.json(), "get_state", entity_id=entity_id)
			except (requests.exceptions.RequestException, IndexError) as e:
				return self._format_error("get_state", str(e), entity_id=entity_id)

		def call_service(self, domain: str, service: str, service_data: dict) -> Union[dict, str]:
			"""Call a service."""
			try:
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/services/{domain}/{service}"
				headers = self._get_headers()
				response = requests.post(url, headers=headers, json=service_data)
				response.raise_for_status()
				return self._format_response(response.json(), "call_service", domain=domain, service=service, service_data=service_data)
			except (requests.exceptions.RequestException, IndexError) as e:
				return self._format_error("call_service", str(e), domain=domain, service=service, service_data=service_data)

		def get_all_states(self) -> Union[dict, str]:
			"""Get the states of all entities."""
			try:
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				return self._format_response(response.json(), "get_all_states")
			except (requests.exceptions.RequestException, IndexError) as e:
				return self._format_error("get_all_states", str(e))

		def get_events(self) -> Union[dict, str]:
			"""Get all available events."""
			try:
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				return self._format_response(response.json(), "get_events")
			except (requests.exceptions.RequestException, IndexError) as e:
				return self._format_error("get_events", str(e))

		def fire_event(self, event_type: str, event_data: dict) -> Union[dict, str]:
			"""Fire an event."""
			try:
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events/{event_type}"
				headers = self._get_headers()
				response = requests.post(url, headers=headers, json=event_data)
				response.raise_for_status()
				return self._format_response(response.json(), "fire_event", event_type=event_type, event_data=event_data)
			except (requests.exceptions.RequestException, IndexError) as e:
				return self._format_error("fire_event", str(e), event_type=event_type, event_data=event_data)

		def calculator(self, equation: str) -> str:
			"""
			Calculate the result of an equation using safe evaluation.

			:param equation: The equation to calculate.
			"""
			try:
				result = ast.literal_eval(equation)
				return f"{equation} = {result}"
			except Exception as e:
				return f"Invalid equation: {str(e)}"

		def simple_test(self) -> str:
			"""Simple test method to verify pipeline access."""
			return "Pipeline is accessible and working."

		def _get_headers(self) -> dict:
			"""Helper method to get headers."""
			return {
				"Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
				"Content-Type": "application/json",
			}

		def _format_response(self, data, name, **params) -> dict:
			"""Format the response to be suitable for the LLM pipeline."""
			return {
				"name": name,
				"parameters": {
					"data": data,
					**params
				}
			}

		def _format_error(self, name, error, **params) -> dict:
			"""Format an error response to be suitable for the LLM pipeline."""
			return {
				"name": name,
				"error": error,
				"parameters": params
			}

	def __init__(self):
		super().__init__()
		self.name = "Home Assistant Pipeline"
		self.valves = self.Valves(
			**{
				**self.valves.model_dump(),
				"pipelines": ["*"],  # Connect to all pipelines
				"HOME_ASSISTANT_API_URL": os.getenv("HOME_ASSISTANT_API_URL", ""),
				"HOME_ASSISTANT_TOKEN": os.getenv("HOME_ASSISTANT_TOKEN", ""),
			},
		)
		self.tools = self.Tools(self)

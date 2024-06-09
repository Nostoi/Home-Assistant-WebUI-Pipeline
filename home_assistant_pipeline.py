# examples/scaffolds/home_assistant_pipeline.py
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
import requests
import os
import ast
import logging
from typing import List, Dict, Union
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.DEBUG)

class RequestSchema(BaseModel):
	function_name: str
	function_parameters: Dict[str, Union[str, int, float, dict]]

class ResponseSchema(BaseModel):
	result: Union[Dict[str, Union[str, int, float, dict]], None] = None
	error: Union[str, None] = None

class Pipeline(FunctionCallingBlueprint):
	class Valves(FunctionCallingBlueprint.Valves):
		HOME_ASSISTANT_API_URL: str = os.getenv("HOME_ASSISTANT_API_URL", "")
		HOME_ASSISTANT_TOKEN: str = os.getenv("HOME_ASSISTANT_TOKEN", "")

	class Tools:
		def __init__(self, pipeline) -> None:
			self.pipeline = pipeline

		def get_state(self, entity_id: str) -> ResponseSchema:
			"""Get the state of an entity."""
			try:
				logging.debug(f"get_state called with entity_id: {entity_id}")
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states/{entity_id}"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				data = response.json()
				logging.debug(f"get_state raw data: {data}")
				if isinstance(data, dict) and "state" in data:
					return ResponseSchema(result=self._format_response(data, "get_state", entity_id=entity_id))
				else:
					logging.error(f"Unexpected data structure in get_state: {data}")
					return ResponseSchema(error="Unexpected data structure")
			except (requests.exceptions.RequestException, IndexError) as e:
				logging.error(f"Error in get_state: {e}")
				return ResponseSchema(error=str(e))

		def call_service(self, domain: str, service: str, service_data: dict) -> ResponseSchema:
			"""Call a service."""
			try:
				logging.debug(f"call_service called with domain: {domain}, service: {service}, service_data: {service_data}")
				if not domain or not service or not isinstance(service_data, dict):
					logging.error(f"Invalid parameters in call_service: domain={domain}, service={service}, service_data={service_data}")
					return ResponseSchema(error="Invalid parameters")
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/services/{domain}/{service}"
				headers = self._get_headers()
				response = requests.post(url, headers=headers, json=service_data)
				response.raise_for_status()
				data = response.json()
				logging.debug(f"call_service data: {data}")
				return ResponseSchema(result=self._format_response(data, "call_service", domain=domain, service=service, service_data=service_data))
			except (requests.exceptions.RequestException, IndexError) as e:
				logging.error(f"Error in call_service: {e}")
				return ResponseSchema(error=str(e))

		def get_all_states(self) -> ResponseSchema:
			"""Get the states of all entities."""
			try:
				logging.debug("get_all_states called")
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				data = response.json()
				logging.debug(f"get_all_states data: {data}")
				return ResponseSchema(result=self._format_response(data, "get_all_states"))
			except (requests.exceptions.RequestException, IndexError) as e:
				logging.error(f"Error in get_all_states: {e}")
				return ResponseSchema(error=str(e))

		def get_events(self) -> ResponseSchema:
			"""Get all available events."""
			try:
				logging.debug("get_events called")
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events"
				headers = self._get_headers()
				response = requests.get(url, headers=headers)
				response.raise_for_status()
				data = response.json()
				logging.debug(f"get_events data: {data}")
				return ResponseSchema(result=self._format_response(data, "get_events"))
			except (requests.exceptions.RequestException, IndexError) as e:
				logging.error(f"Error in get_events: {e}")
				return ResponseSchema(error=str(e))

		def fire_event(self, event_type: str, event_data: dict) -> ResponseSchema:
			"""Fire an event."""
			try:
				logging.debug(f"fire_event called with event_type: {event_type}, event_data: {event_data}")
				url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events/{event_type}"
				headers = self._get_headers()
				response = requests.post(url, headers=headers, json=event_data)
				response.raise_for_status()
				data = response.json()
				logging.debug(f"fire_event data: {data}")
				return ResponseSchema(result=self._format_response(data, "fire_event", event_type=event_type, event_data=event_data))
			except (requests.exceptions.RequestException, IndexError) as e:
				logging.error(f"Error in fire_event: {e}")
				return ResponseSchema(error=str(e))

		def calculator(self, equation: str) -> str:
			"""
			Calculate the result of an equation using safe evaluation.

			:param equation: The equation to calculate.
			"""
			try:
				logging.debug(f"calculator called with equation: {equation}")
				result = ast.literal_eval(equation)
				logging.debug(f"calculator result: {result}")
				return f"{equation} = {result}"
			except Exception as e:
				logging.error(f"Error in calculator: {e}")
				return f"Invalid equation: {str(e)}"

		def simple_test(self) -> str:
			"""Simple test method to verify pipeline access."""
			return "Pipeline is accessible and working."

		def _get_headers(self) -> dict:
			"""Helper method to get headers."""
			headers = {
				"Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
				"Content-Type": "application/json",
			}
			logging.debug(f"Generated headers: {headers}")
			return headers

		def _format_response(self, data, name, **params) -> dict:
			"""Format the response to be suitable for the LLM pipeline."""
			response = {
				"name": name,
				"parameters": {
					"data": data,
					**params
				}
			}
			logging.debug(f"Formatted response: {response}")
			return response

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
		logging.debug(f"Initialized Home Assistant Pipeline with API URL: {self.valves.HOME_ASSISTANT_API_URL} and Token: {self.valves.HOME_ASSISTANT_TOKEN}")
		self.tools = self.Tools(self)

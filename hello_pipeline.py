# hello_pipeline.py

from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
import datetime

logging.basicConfig(level=logging.DEBUG)

class RequestSchema(BaseModel):
	function_name: str
	function_parameters: dict

class ResponseSchema(BaseModel):
	result: dict
	error: str = None

class HelloPipeline(FunctionCallingBlueprint):
	class Tools:
		def __init__(self, pipeline):
			self.pipeline = pipeline

		def greet(self) -> dict:
			"""Return a greeting with the current date and time."""
			name = "Bob"
			current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			greeting = f"Hello, {name}. It's {current_time}."
			logging.debug(f"greet: {greeting}")
			return {"greeting": greeting}

	def __init__(self):
		super().__init__()
		self.name = "Hello Pipeline"
		self.tools = self.Tools(self)

app = FastAPI()

@app.post("/hello_pipeline/filter/inlet", response_model=ResponseSchema)
async def hello_pipeline_inlet(request: RequestSchema):
	try:
		pipeline = HelloPipeline()
		function_name = request.function_name
		function_parameters = request.function_parameters

		if not hasattr(pipeline.tools, function_name):
			raise HTTPException(status_code=400, detail="Invalid function name")

		function = getattr(pipeline.tools, function_name)
		result = function(**function_parameters)

		return ResponseSchema(result=result)
	except Exception as e:
		logging.error(f"Error processing request: {e}")
		return ResponseSchema(result={}, error=str(e))

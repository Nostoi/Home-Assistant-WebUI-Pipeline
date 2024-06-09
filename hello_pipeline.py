import os
from datetime import datetime
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

class Pipeline(FunctionCallingBlueprint):
    class Valves(FunctionCallingBlueprint.Valves):
        pass

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def respond_hello(self) -> str:
            """
            Respond to the message "Hello" with the current date and time.
            """
            now = datetime.now()
            current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            return f"Hello, the date and time are {current_date_time}. You're pretty rad!"

    def __init__(self):
        super().__init__()
        self.name = "Hello Response Pipeline"
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            },
        )
        self.tools = self.Tools(self)

# Example usage
if __name__ == "__main__":
    pipeline = Pipeline()
    response = pipeline.tools.respond_hello()
    print(response)
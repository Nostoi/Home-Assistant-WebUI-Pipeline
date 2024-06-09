from typing import List, Union, Generator, Iterator
from datetime import datetime

class Pipeline:
    def __init__(self):
        self.name = "Hello Response Pipeline"

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    def get_current_date_time(self):
        now = datetime.now()
        current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        return f"Hello, the date and time are {current_date_time}. You're pretty rad!"

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")
        print(messages)
        print(user_message)

        if user_message.lower() == "hello":
            return self.get_current_date_time()
        else:
            return "Unrecognized message"

# Example usage
if __name__ == "__main__":
    pipeline = Pipeline()
    response = pipeline.pipe("Hello", "", [], {})
    print(response)
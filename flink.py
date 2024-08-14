from pyflink.datastream import StreamExecutionEnvironment, SourceFunction
from pyflink.datastream import PrintSinkFunction
import requests
import time

class ApiSourceFunction(SourceFunction):
    def __init__(self, url):
        self.url = url
        self.is_running = True

    def run(self, ctx):
        while self.is_running:
            try:
                response = requests.post(self.url)
                ctx.collect(response.text)
            except Exception as e:
                print(f"Error: {e}")
            time.sleep(10)  # Poll every 10 seconds

    def cancel(self):
        self.is_running = False

def main():
    env = StreamExecutionEnvironment.get_execution_environment()
    api_source = ApiSourceFunction("http://localhost:8000/user")

    data_stream = env.add_source(api_source)
    data_stream.add_sink(PrintSinkFunction())

    env.execute("API Monitoring Job")

if __name__ == "__main__":
    main()

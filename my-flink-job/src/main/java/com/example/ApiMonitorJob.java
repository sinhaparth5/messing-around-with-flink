package com.example;

import java.io.BufferedReader;
import java.io.OutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.io.IOException; // Add this import

import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.sink.SinkFunction;
import org.apache.flink.streaming.api.functions.source.SourceFunction;
import org.apache.flink.streaming.api.functions.source.SourceFunction.SourceContext;

public class ApiMonitorJob {
    
    public static class ApiSourceFunction implements SourceFunction<String> {
        private final String url;
        private volatile boolean isRunning = true;

        public ApiSourceFunction(String url) {
            this.url = url;
        }

        @Override
        public void run(SourceContext<String> ctx) throws Exception {
            while (isRunning) {
                try {
                    // Create URL object
                    URL apiUrl = new URL(url);
                    HttpURLConnection connection = (HttpURLConnection) apiUrl.openConnection();
                    
                    // Configure the connection
                    connection.setRequestMethod("POST");
                    connection.setRequestProperty("Content-Type", "application/json");
                    connection.setDoOutput(true); // Enable output stream for sending data
                    
                    // Create JSON payload
                    String jsonPayload = "{\"username\": \"test_user\", \"email\": \"test@example.com\"}";
                    
                    // Write payload to output stream
                    try (OutputStream os = connection.getOutputStream()) {
                        byte[] input = jsonPayload.getBytes(StandardCharsets.UTF_8);
                        os.write(input, 0, input.length);
                    }
                    
                    // Read the response
                    int responseCode = connection.getResponseCode();
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                            StringBuilder response = new StringBuilder();
                            String line;
                            while ((line = reader.readLine()) != null) {
                                response.append(line);
                            }
                            ctx.collect(response.toString());
                        }
                    } else {
                        throw new IOException("Server returned HTTP response code: " + responseCode);
                    }

                } catch (Exception e) {
                    e.printStackTrace();
                }
                Thread.sleep(10000); // Poll every 10 seconds
            }
        }

        @Override
        public void cancel() {
            isRunning = false;
        }
    }

    public static void main(String[] args) throws Exception {
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

        // Create the source function
        ApiSourceFunction apiSource = new ApiSourceFunction("http://fastapi:8000/create_user/");

        // Create the data stream
        DataStream<String> dataStream = env.addSource(apiSource);

        // Print the data stream
        dataStream.addSink(new SinkFunction<String>() {
            @Override
            public void invoke(String value, Context context) {
                System.out.println("Received: " + value);
            }
        });

        // Execute the Flink job
        env.execute("API Monitoring Job");
    }
}

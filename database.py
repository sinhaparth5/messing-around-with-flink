from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthenticator
import time
from cassandra.cluster import NoHostAvailable

def create_keyspace_and_table():
    # Define connection parameters
    cassandra_host = 'cassandra'
    retry_attempts = 10
    retry_delay = 5  # in seconds

    # Retry logic to wait for Cassandra to become available
    for attempt in range(retry_attempts):
        try:
            print(f"Attempt {attempt + 1} to connect to Cassandra...")
            cluster = Cluster([cassandra_host])
            session = cluster.connect()
            
            # Successfully connected, create keyspace and table
            session.execute(
                """
                CREATE KEYSPACE IF NOT EXISTS user_keyspace
                WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '1' }
                """
            )

            # Use the keyspace
            session.set_keyspace('user_keyspace')

            # Create user_info table
            session.execute("""
            CREATE TABLE IF NOT EXISTS user_info (
                user_id UUID PRIMARY KEY,
                username TEXT,
                email TEXT,
                created_at TIMESTAMP
            )
            """)

            print("Keyspace and table created successfully.")
            return  # Exit function after successful creation

        except NoHostAvailable as e:
            print(f"Error connecting to Cassandra: {e}. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying

    raise RuntimeError("Failed to connect to Cassandra after several attempts.")


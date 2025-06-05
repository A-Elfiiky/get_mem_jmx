import time
from jmxquery import JMXConnection, JMXQuery
import subprocess
from datetime import datetime

def log(msg):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")

# === Configuration ===
jmx_url = "service:jmx:rmi:///jndi/rmi://localhost:8888/jmxrmi"
jmx_username = ""  # Optional
jmx_password = ""  # Optional

memory_threshold = 57  # GB
max_failed_attempts = 5
interval_seconds = 60  # How often to check memory usage
post_reboot_sleep_minutes = 7  # Time to wait after reboot before checking again
timeout = 30  # JMX query timeout in seconds

reboot_script_path = "/apps/wl_prod/domain-cdx-rt-prod-ap-prod/healing_watchdog/bounce_batch_2nd_june.sh"

# === JMX Query ===
queries = [JMXQuery("java.lang:type=MemoryPool,name=CMS Old Gen", "Usage")]

def get_memory_usage(connection):
    try:
        metrics = connection.query(queries, timeout)
        for metric in metrics:
            if metric.attributeKey == "used":
                usage_gb = metric.value / (1024 ** 3)
                log(f"Memory usage: {usage_gb:.2f} GB")
                return usage_gb
    except Exception as e:
        log(f"Error retrieving memory usage: {e}")
    return None

def wait_for_server():
    log("Waiting for server to come back online...")
    while True:
        try:
            connection = JMXConnection(jmx_url)
            usage = get_memory_usage(connection)
            if usage is not None:
                log("Server is back online.")
                return connection
        except Exception:
            pass
        time.sleep(30)

def monitor():
    connection = JMXConnection(jmx_url)
    counter = 0

    while True:
        usage = get_memory_usage(connection)

        if usage is not None:
            if usage > memory_threshold:
                counter += 1
                log(f"Warning: Memory usage {usage:.2f} GB above threshold ({memory_threshold} GB). Count: {counter}")
            else:
                counter = 0
        else:
            log("Could not retrieve memory usage.")
            counter = 0

        if counter >= max_failed_attempts:
            log("Memory threshold exceeded. Restarting server...")
            try:
                subprocess.run(["bash", reboot_script_path], check=True)
                log("Reboot script executed successfully.")
            except subprocess.CalledProcessError as e:
                log(f"Failed to restart server: {e}")
            counter = 0
            log(f"Sleeping for {post_reboot_sleep_minutes} minutes after reboot...")
            time.sleep(post_reboot_sleep_minutes * 60)
            connection = wait_for_server()

        time.sleep(interval_seconds)

if __name__ == "__main__":
    monitor()

# JMX Memory Monitor

A Python-based monitoring tool that watches JVM memory usage via JMX and automatically restarts servers when memory thresholds are exceeded.

## Overview

This tool continuously monitors the CMS Old Generation memory pool of a Java application through JMX. When memory usage consistently exceeds the configured threshold, it automatically executes a server restart script to prevent OutOfMemoryError conditions.

## Features

- **Real-time JMX monitoring** of CMS Old Gen memory pool
- **Configurable memory thresholds** with counter-based triggering
- **Automatic server restart** when thresholds are breached
- **Post-restart monitoring** with server availability checks
- **Comprehensive logging** with timestamps
- **Fault tolerance** with connection retry logic

## Requirements

- Python 3.6+
- `jmxquery` library
- JMX-enabled Java application
- Bash shell (for restart script execution)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd jmx-memory-monitor
```

2. Install required Python dependencies:
```bash
pip install jmxquery
```

3. Make sure your restart script is executable:
```bash
chmod +x /path/to/your/restart/script.sh
```

## Configuration

Edit the configuration section in `jmx_monitor.py`:

```python
# JMX Connection
jmx_url = "service:jmx:rmi:///jndi/rmi://localhost:8888/jmxrmi"
jmx_username = ""  # Leave empty if authentication not required
jmx_password = ""  # Leave empty if authentication not required

# Monitoring Parameters
memory_threshold = 57  # Memory threshold in GB
max_failed_attempts = 5  # Number of consecutive threshold breaches before restart
interval_seconds = 60  # Check interval in seconds
post_reboot_sleep_minutes = 7  # Wait time after restart
timeout = 30  # JMX query timeout

# Restart Script
reboot_script_path = "/path/to/your/restart/script.sh"
```

### Configuration Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `jmx_url` | JMX connection URL | `service:jmx:rmi:///jndi/rmi://localhost:8888/jmxrmi` |
| `jmx_username` | JMX authentication username (optional) | `""` |
| `jmx_password` | JMX authentication password (optional) | `""` |
| `memory_threshold` | Memory threshold in GB | `57` |
| `max_failed_attempts` | Consecutive breaches before restart | `5` |
| `interval_seconds` | Monitoring check interval | `60` |
| `post_reboot_sleep_minutes` | Wait time after restart | `7` |
| `timeout` | JMX query timeout in seconds | `30` |
| `reboot_script_path` | Path to restart script | User-defined |

## Usage

### Basic Usage

```bash
python3 jmx_monitor.py
```

### Running as a Service

Create a systemd service file `/etc/systemd/system/jmx-monitor.service`:

```ini
[Unit]
Description=JMX Memory Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/jmx-monitor
ExecStart=/usr/bin/python3 /path/to/jmx-monitor/jmx_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable jmx-monitor
sudo systemctl start jmx-monitor
```

### Running with nohup

```bash
nohup python3 jmx_monitor.py > jmx_monitor.log 2>&1 &
```

## Monitoring Logic

1. **Continuous Monitoring**: Connects to JMX endpoint every 60 seconds (configurable)
2. **Threshold Checking**: Compares current memory usage against configured threshold
3. **Counter-based Triggering**: Requires consecutive threshold breaches before action
4. **Automatic Restart**: Executes restart script when counter reaches maximum
5. **Post-restart Monitoring**: Waits for server recovery before resuming normal monitoring

## Sample Output

```
2025-06-05 10:30:15 - Memory usage: 45.67 GB
2025-06-05 10:31:15 - Memory usage: 58.23 GB
2025-06-05 10:31:15 - Warning: Memory usage 58.23 GB above threshold (57 GB). Count: 1
2025-06-05 10:32:15 - Memory usage: 59.45 GB
2025-06-05 10:32:15 - Warning: Memory usage 59.45 GB above threshold (57 GB). Count: 2
...
2025-06-05 10:35:15 - Warning: Memory usage 61.12 GB above threshold (57 GB). Count: 5
2025-06-05 10:35:15 - Memory threshold exceeded. Restarting server...
2025-06-05 10:35:20 - Reboot script executed successfully.
2025-06-05 10:35:20 - Sleeping for 7 minutes after reboot...
2025-06-05 10:42:20 - Waiting for server to come back online...
2025-06-05 10:43:50 - Server is back online.
2025-06-05 10:43:50 - Memory usage: 12.34 GB
```

## JMX Setup

Ensure your Java application is started with JMX enabled:

```bash
java -Dcom.sun.management.jmxremote \
     -Dcom.sun.management.jmxremote.port=8888 \
     -Dcom.sun.management.jmxremote.authenticate=false \
     -Dcom.sun.management.jmxremote.ssl=false \
     -jar your-application.jar
```

For production environments with authentication:
```bash
java -Dcom.sun.management.jmxremote \
     -Dcom.sun.management.jmxremote.port=8888 \
     -Dcom.sun.management.jmxremote.authenticate=true \
     -Dcom.sun.management.jmxremote.ssl=true \
     -Dcom.sun.management.jmxremote.password.file=/path/to/jmxremote.password \
     -Dcom.sun.management.jmxremote.access.file=/path/to/jmxremote.access \
     -jar your-application.jar
```

## Troubleshooting

### Common Issues

**JMX Connection Failed**
- Verify JMX is enabled on target application
- Check firewall settings for JMX port
- Ensure correct JMX URL format

**Memory Pool Not Found**
- Verify the memory pool name matches your JVM's configuration
- For G1GC, use: `java.lang:type=MemoryPool,name=G1 Old Gen`
- For other collectors, check with JConsole or similar tools

**Restart Script Execution Failed**
- Verify script path and permissions
- Check script logs for execution errors
- Ensure script is executable: `chmod +x script.sh`

### Debug Mode

Add debug logging by modifying the `log()` function:

```python
def log(msg, level="INFO"):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - [{level}] {msg}")
```

## Security Considerations

- Use JMX authentication in production environments
- Restrict JMX port access with firewall rules
- Store credentials securely (consider environment variables)
- Limit script execution permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review application and JMX logs
- Open an issue with detailed error information

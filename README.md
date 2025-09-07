# SSD Health Monitor

A Python-based🐍 system monitoring tool for checking SSD/NVMe drive health, usage, and temperature. Originally developed to validate repurposed NVMe drives from old laptops before converting them into high-speed 🚀 external USB storage🗄.

The script I originally came up with was - 
``` 
import psutil
partitions = psutil.disk_partitions()
for partition in partitions:
    usage = psutil.disk_usage(partition.mountpoint)
    print(f"{partition.device}: {usage.percent}%")
```
I had then brainstormed with my LLM agent🤖 and came up with a much better version with the following 

## Features

- **Disk Usage Monitoring**: Check drive capacity and usage percentages
- **Temperature Monitoring**: Read drive temperature sensors (requires admin privileges)
- **SMART Data Analysis**: Detailed drive health checking via smartctl
- **Email Alerts**: Automated notifications when thresholds are exceeded
- **JSON Logging**: Save monitoring results with timestamps
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Prerequisites

### Required Python Packages
```bash
pip install psutil
```

### Optional Dependencies
```bash
# For detailed SMART monitoring (recommended)
# Windows: Download from https://www.smartmontools.org/
# Linux: sudo apt install smartmontools
# macOS: brew install smartmontools
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ssd-health-monitor.git
cd ssd-health-monitor
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the script:
```bash
python ssd_health_monitor.py
```

## Usage Examples

### Basic Health Check
```bash
python ssd_health_monitor.py
```
Runs complete system check with default thresholds (75°C temperature, 85% disk usage).

### Custom Thresholds
Modify the `main()` function to adjust warning levels:
```python
monitor = SSDHealthMonitor(temp_threshold=70, usage_threshold=90)
```

### Enable Email Alerts
Uncomment and configure the email section in `main()`:
```python
if not results['healthy']:
    monitor.send_email_alert(
        smtp_server='smtp.gmail.com',
        smtp_port=587,
        email_user='your-email@gmail.com',
        email_pass='your-app-password',
        recipient='admin@yourcompany.com'
    )
```

### Automated Monitoring
Run via cron (Linux/macOS) or Task Scheduler (Windows) for regular health checks:
```bash
# Run every hour
0 * * * * /usr/bin/python3 /path/to/ssd_health_monitor.py
```

## Output Example

```
🚀 SSD Health Monitor Starting...
SSD Health Monitor initialized
Temperature threshold: 75°C
Usage threshold: 85%

🔍 Checking disk usage...
✅ C:\: 45.2% used (295 GB free)
✅ D:\: 23.8% used (1.2 TB free)

🌡️  Checking drive temperatures...
✅ nvme0: 42°C
✅ nvme1: 38°C

🔧 Checking SMART data for /dev/nvme0n1...
✅ /dev/nvme0n1: SMART status PASSED

📊 HEALTH CHECK SUMMARY
✅ All systems healthy!

📝 Results saved to ssd_health_20241207_143052.json
🏁 Health check complete!
```

## Configuration

### Temperature Thresholds
- **Conservative**: 65°C (recommended for 24/7 operation)
- **Standard**: 75°C (good for regular use)
- **Aggressive**: 85°C (maximum safe operating temperature)

### Disk Usage Thresholds
- **Conservative**: 80% (maintains good performance)
- **Standard**: 85% (balanced approach)
- **High Utilization**: 90% (warning only when nearly full)

## Use Cases

- **Repurposed Drive Validation**: Test old laptop NVMe drives before external enclosure use
- **Production Monitoring**: Continuous health monitoring for critical systems
- **Preventive Maintenance**: Early warning system for drive failures
- **Asset Management**: Track drive health across multiple systems

## Technical Notes

### Permissions
- **Temperature monitoring** requires administrator/root privileges on most systems
- **SMART data** requires smartmontools package and appropriate permissions
- **Email alerts** require app passwords for Gmail (not regular passwords)

### Platform Differences
- **Windows**: Drive letters (C:, D:) automatically detected
- **Linux**: Block devices (/dev/sda, /dev/nvme0n1) used for SMART queries
- **macOS**: Similar to Linux with some sensor detection differences

## Troubleshooting

### Common Issues

**"No temperature sensors found"**
```bash
# Linux: Check if running as root
sudo python ssd_health_monitor.py

# Windows: Run Command Prompt as Administrator
```

**"smartctl command not found"**
```bash
# Install smartmontools package for your OS
# Ubuntu/Debian: sudo apt install smartmontools
# RHEL/CentOS: sudo yum install smartmontools
# Windows: Download from smartmontools.org
```

**"Permission denied" errors**
- Run with elevated privileges (admin/root)
- Check drive permissions and accessibility

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add monitoring feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created for practical SSD health monitoring and repurposed drive validation.

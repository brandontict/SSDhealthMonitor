#!/usr/bin/env python3
"""
SSD Health Monitor
==================

A comprehensive system monitoring tool for SSD/NVMe drive health validation.
Originally developed for testing repurposed laptop drives before external enclosure conversion.

Author: [Your Name]
Version: 1.0.0
License: MIT
"""

import psutil
import subprocess
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class SSDHealthMonitor:
    """
    Main monitoring class for SSD/NVMe health assessment.
    
    Provides comprehensive drive monitoring including usage statistics,
    temperature readings, and SMART data analysis.
    """
    
    def __init__(self, temp_threshold=70, usage_threshold=90):
        """
        Initialize monitor with configurable thresholds.
        
        Args:
            temp_threshold (int): Temperature warning threshold in Celsius
            usage_threshold (int): Disk usage warning threshold as percentage
        """
        self.temp_threshold = temp_threshold
        self.usage_threshold = usage_threshold
        self.alerts = []
        
        print(f"SSD Health Monitor initialized")
        print(f"Temperature threshold: {temp_threshold}°C")
        print(f"Usage threshold: {usage_threshold}%")
    
    def get_disk_usage(self):
        """
        Analyze disk usage across all mounted partitions.
        
        Returns:
            dict: Partition usage statistics including capacity and utilization
        """
        print("\n🔍 Checking disk usage...")
        disk_usage = {}
        
        partitions = psutil.disk_partitions()
        
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                percent_used = (usage.used / usage.total) * 100
                
                disk_usage[partition.device] = {
                    'mountpoint': partition.mountpoint,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'percent_used': round(percent_used, 1)
                }
                
                if percent_used > self.usage_threshold:
                    alert = f"⚠️  {partition.device} is {percent_used:.1f}% full (threshold: {self.usage_threshold}%)"
                    self.alerts.append(alert)
                    print(alert)
                else:
                    print(f"✅ {partition.device}: {percent_used:.1f}% used ({usage.free // (1024**3)} GB free)")
                    
            except PermissionError:
                print(f"⚠️  Cannot access {partition.device} (permission denied)")
                continue
        
        return disk_usage
    
    def get_drive_temperatures(self):
        """
        Monitor drive temperature sensors.
        
        Returns:
            dict: Temperature readings for detected storage devices
            
        Note:
            Requires elevated privileges on most systems
        """
        print("\n🌡️  Checking drive temperatures...")
        temperatures = {}
        
        try:
            sensors = psutil.sensors_temperatures()
            
            if not sensors:
                print("⚠️  No temperature sensors found or insufficient permissions")
                return temperatures
            
            for sensor_name, sensor_list in sensors.items():
                if any(keyword in sensor_name.lower() for keyword in ['nvme', 'ssd', 'sata', 'drive']):
                    for sensor in sensor_list:
                        temp = sensor.current
                        temperatures[f"{sensor_name}_{sensor.label}"] = temp
                        
                        if temp > self.temp_threshold:
                            alert = f"🔥 {sensor_name} temperature: {temp}°C (threshold: {self.temp_threshold}°C)"
                            self.alerts.append(alert)
                            print(alert)
                        else:
                            print(f"✅ {sensor_name}: {temp}°C")
        
        except Exception as e:
            print(f"⚠️  Could not read temperature sensors: {e}")
            print("💡 Try running as administrator/root for temperature monitoring")
        
        return temperatures
    
    def check_smart_data(self, drive_path):
        """
        Retrieve SMART health data using smartctl.
        
        Args:
            drive_path (str): System path to drive device
            
        Returns:
            dict: SMART analysis results
        """
        print(f"\n🔧 Checking SMART data for {drive_path}...")
        
        try:
            result = subprocess.run(
                ['smartctl', '-a', '-j', drive_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                smart_data = json.loads(result.stdout)
                
                if 'smart_status' in smart_data:
                    health_status = smart_data['smart_status']['passed']
                    if health_status:
                        print(f"✅ {drive_path}: SMART status PASSED")
                    else:
                        alert = f"❌ {drive_path}: SMART status FAILED - Drive may be failing!"
                        self.alerts.append(alert)
                        print(alert)
                
                return smart_data
            else:
                print(f"⚠️  Could not get SMART data for {drive_path}")
                print("💡 Make sure 'smartctl' is installed and you have admin privileges")
                
        except FileNotFoundError:
            print("⚠️  'smartctl' command not found")
            print("💡 Install smartmontools package for detailed SMART monitoring")
        except subprocess.TimeoutExpired:
            print("⚠️  SMART check timed out")
        except json.JSONDecodeError:
            print("⚠️  Could not parse SMART data")
        except Exception as e:
            print(f"⚠️  Error checking SMART data: {e}")
        
        return {}
    
    def send_email_alert(self, smtp_server, smtp_port, email_user, email_pass, recipient):
        """
        Send email notification for detected issues.
        
        Args:
            smtp_server (str): SMTP server hostname
            smtp_port (int): SMTP server port
            email_user (str): Authentication username
            email_pass (str): Authentication password/app password
            recipient (str): Alert recipient email address
        """
        if not self.alerts:
            print("✅ No alerts to send - all systems healthy!")
            return
        
        print(f"\n📧 Sending email alert to {recipient}...")
        
        try:
            alert_text = "\n".join(self.alerts)
            message = MIMEText(f"""
SSD Health Monitor Alert - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The following issues were detected:

{alert_text}

Please investigate these issues as soon as possible.

--
SSD Health Monitor
            """)
            
            message['Subject'] = f"SSD Health Alert - {len(self.alerts)} issues detected"
            message['From'] = email_user
            message['To'] = recipient
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_pass)
                server.send_message(message)
                
            print("✅ Email alert sent successfully!")
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
    
    def run_full_check(self):
        """
        Execute comprehensive health assessment.
        
        Returns:
            dict: Complete monitoring results with metadata
        """
        print("🏥 Starting SSD Health Check...")
        print("=" * 50)
        
        # Execute monitoring components
        disk_usage = self.get_disk_usage()
        temperatures = self.get_drive_temperatures()
        
        # SMART data collection with drive path conversion
        smart_data = {}
        for device in disk_usage.keys():
            if device.endswith(':'):
                # Convert Windows drive letters to device paths
                device_path = f"/dev/sd{chr(ord('a') + ord(device[0]) - ord('A'))}"
            else:
                device_path = device
            
            smart_data[device] = self.check_smart_data(device_path)
        
        # Generate summary report
        print("\n" + "=" * 50)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 50)
        
        if self.alerts:
            print(f"❌ {len(self.alerts)} issues found:")
            for alert in self.alerts:
                print(f"   {alert}")
        else:
            print("✅ All systems healthy!")
        
        return {
            'timestamp': datetime.now().isoformat(),
            'disk_usage': disk_usage,
            'temperatures': temperatures,
            'smart_data': smart_data,
            'alerts': self.alerts,
            'healthy': len(self.alerts) == 0
        }

def main():
    """
    Main execution entry point.
    
    Configures and executes health monitoring with optional alerting and logging.
    """
    print("🚀 SSD Health Monitor Starting...")
    
    # Initialize monitor with custom thresholds
    monitor = SSDHealthMonitor(temp_threshold=75, usage_threshold=85)
    
    # Execute health assessment
    results = monitor.run_full_check()
    
    # Optional: Email alerting configuration
    # Uncomment and configure for production use
    """
    if not results['healthy']:
        monitor.send_email_alert(
            smtp_server='smtp.gmail.com',
            smtp_port=587,
            email_user='your-email@gmail.com',
            email_pass='your-app-password',
            recipient='admin@yourcompany.com'
        )
    """
    
    # Results logging
    log_filename = f"ssd_health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(log_filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"📝 Results saved to {log_filename}")
    except Exception as e:
        print(f"⚠️  Could not save log file: {e}")
    
    print("\n🏁 Health check complete!")

if __name__ == "__main__":
    main()

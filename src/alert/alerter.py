import time
import logging
import os
from datetime import datetime

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/alerts.log'),
        logging.StreamHandler()
    ]
)

class AlertManager:
    def __init__(self, config):
        self.config = config
        self.enabled = config['alert']['enabled']
        self.cooldown = config['alert']['cooldown']
        self.methods = config['alert']['methods']
        self.last_alert_time = {region: 0 for region in config['analysis']['regions']}
        self.logger = logging.getLogger('AlertManager')
        
    def check_and_alert(self, analysis_results):
        """
        Check analysis results and trigger alerts if needed
        
        Args:
            analysis_results: Dictionary with analysis results
            
        Returns:
            alerts_triggered: Dictionary of regions where alerts were triggered
        """
        if not self.enabled:
            return {}
        
        current_time = time.time()
        alerts_triggered = {}
        
        # Check for overall crowd size alert
        total_people = analysis_results.get('total_people', 0)
        if total_people > 50:  # Arbitrary threshold for total people
            if current_time - self.last_alert_time.get('total', 0) > self.cooldown:
                self.last_alert_time['total'] = current_time
                message = f"ALERT: Large crowd detected. Total count: {total_people}"
                
                if self.methods.get('console', False):
                    print(f"\n{'='*50}\n{message}\n{'='*50}\n")
                
                if self.methods.get('log', False):
                    self.logger.warning(message)
                
                alerts_triggered['total'] = {
                    'timestamp': datetime.now().isoformat(),
                    'region': 'total',
                    'count': total_people,
                    'max_count': 50,
                    'message': message
                }
        
        # Check for region-specific alerts
        for region_name, is_anomaly in analysis_results['anomalies'].items():
            if is_anomaly:
                # Check if cooldown period has passed
                if current_time - self.last_alert_time.get(region_name, 0) > self.cooldown:
                    self.last_alert_time[region_name] = current_time
                    
                    # Create alert message
                    count = analysis_results['counts'][region_name]
                    max_count = self.config['analysis']['regions'][region_name]['max_count']
                    message = f"ALERT: Abnormal gathering detected in {region_name}. " \
                              f"Current count: {count}, Maximum normal: {max_count}"
                    
                    # Trigger alerts based on configured methods
                    if self.methods.get('console', False):
                        print(f"\n{'='*50}\n{message}\n{'='*50}\n")
                    
                    if self.methods.get('log', False):
                        self.logger.warning(message)
                    
                    # Store triggered alert
                    alerts_triggered[region_name] = {
                        'timestamp': datetime.now().isoformat(),
                        'region': region_name,
                        'count': count,
                        'max_count': max_count,
                        'message': message
                    }
        
        return alerts_triggered

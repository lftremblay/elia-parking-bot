"""
Advanced Scheduler for Elia Parking Bot
Handles dual scheduling (midnight executive, 6am regular)
Includes Windows Task Scheduler integration
Story 1.2 - Enhanced with cloud auth integration and timing validation
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Callable, Optional
from loguru import logger
import json
from pathlib import Path


class ReservationScheduler:
    """Manages scheduling for parking reservations with Story 1.2 enhancements"""
    
    def __init__(self, config: dict, bot_instance=None):
        self.config = config
        self.schedules = config.get('schedules', {})
        self.running = False
        self.last_run = {}
        
        # Story 1.2 - Task 3.1: Cloud auth integration
        self.bot_instance = bot_instance
        self.cloud_auth_available = bot_instance and hasattr(bot_instance, 'cloud_auth_manager')
        
        logger.info("⏰ Enhanced ReservationScheduler initialized (Story 1.2)")
    
    def setup_schedules(self, reservation_callback: Callable):
        """
        Set up all configured schedules with cloud auth integration
        Story 1.2 - Task 3.2: Enhanced scheduler triggers full reservation flow
        """
        schedule.clear()
        
        # Story 1.2 - Task 3.3: Add timing validation
        self._validate_timing_configuration()
        
        # Executive spots schedule (midnight)
        if self.schedules.get('executive_spots', {}).get('enabled'):
            exec_config = self.schedules['executive_spots']
            exec_time = exec_config.get('time', '00:00:00')
            weekdays_only = exec_config.get('weekdays_only', True)
            
            # Story 1.2 - Enhanced callback with cloud auth
            enhanced_callback = self._create_enhanced_callback(reservation_callback, 'executive')
            
            if weekdays_only:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    getattr(schedule.every(), day).at(exec_time).do(enhanced_callback).tag('executive')
                logger.info(f"✅ Executive spots scheduled: Weekdays at {exec_time}")
            else:
                schedule.every().day.at(exec_time).do(enhanced_callback).tag('executive')
                logger.info(f"✅ Executive spots scheduled: Daily at {exec_time}")
        
        # Regular spots schedule (6am)
        if self.schedules.get('regular_spots', {}).get('enabled'):
            reg_config = self.schedules['regular_spots']
            reg_time = reg_config.get('time', '06:00:00')
            weekdays_only = reg_config.get('weekdays_only', True)
            
            # Story 1.2 - Enhanced callback with cloud auth
            enhanced_callback = self._create_enhanced_callback(reservation_callback, 'regular')
            
            if weekdays_only:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    getattr(schedule.every(), day).at(reg_time).do(enhanced_callback).tag('regular')
                logger.info(f"✅ Regular spots scheduled: Weekdays at {reg_time}")
            else:
                schedule.every().day.at(reg_time).do(enhanced_callback).tag('regular')
                logger.info(f"✅ Regular spots scheduled: Daily at {reg_time}")
        
        logger.success("🎯 All schedules configured with Story 1.2 enhancements")
    
    def _create_enhanced_callback(self, original_callback: Callable, spot_type: str):
        """
        Create enhanced callback with cloud auth integration
        Story 1.2 - Task 3.1: Integrate cloud auth with scheduler execution
        """
        def enhanced_reservation_callback():
            """Enhanced reservation callback with cloud auth and error handling"""
            logger.info(f"🚀 Story 1.2: Starting scheduled {spot_type} reservation...")
            
            try:
                # Story 1.2 - Cloud auth validation
                if self.cloud_auth_available and self.bot_instance.cloud_auth_manager:
                    logger.info("☁️ Using cloud authentication for scheduled execution")
                    # Cloud auth will be handled automatically in bot.authenticate()
                
                # Execute original callback with enhanced error handling
                start_time = time.time()
                success = asyncio.run(original_callback(spot_type))
                execution_time = time.time() - start_time
                
                # Story 1.2 - Performance tracking
                logger.info(f"📊 Scheduled {spot_type} reservation completed in {execution_time:.2f}s")
                
                if success:
                    logger.success(f"✅ Scheduled {spot_type} reservation successful")
                else:
                    logger.error(f"❌ Scheduled {spot_type} reservation failed")
                
                # Update last run tracking
                self.last_run[spot_type] = {
                    'timestamp': datetime.now().isoformat(),
                    'success': success,
                    'execution_time': execution_time
                }
                
            except Exception as e:
                logger.error(f"❌ Scheduled {spot_type} reservation error: {e}")
                self.last_run[spot_type] = {
                    'timestamp': datetime.now().isoformat(),
                    'success': False,
                    'error': str(e)
                }
        
        return enhanced_reservation_callback
    
    def _validate_timing_configuration(self):
        """
        Validate timing configuration for optimal execution windows
        Story 1.2 - Task 3.3: Add timing validation for optimal execution windows
        """
        logger.info("🕐 Validating timing configuration...")
        
        for spot_type, config in self.schedules.items():
            if not config.get('enabled'):
                continue
            
            time_str = config.get('time', '')
            try:
                # Validate time format
                time_obj = datetime.strptime(time_str, '%H:%M:%S')
                
                # Check for optimal timing windows
                hour = time_obj.hour
                if spot_type == 'executive_spots':
                    if hour == 0:
                        logger.success("✅ Executive spots scheduled at optimal midnight window")
                    else:
                        logger.warning(f"⚠️ Executive spots at {hour}:00 - midnight (00:00) recommended")
                
                elif spot_type == 'regular_spots':
                    if 5 <= hour <= 7:
                        logger.success(f"✅ Regular spots scheduled at optimal early morning window ({hour}:00)")
                    else:
                        logger.warning(f"⚠️ Regular spots at {hour}:00 - 6am (06:00) recommended")
                
            except ValueError:
                logger.error(f"❌ Invalid time format for {spot_type}: {time_str}")
        
        logger.info("✅ Timing validation completed")
    
    def get_performance_metrics(self) -> dict:
        """
        Get performance metrics for scheduled executions
        Story 1.2 - Task 3.4: Performance monitoring
        """
        metrics = {
            'total_runs': len(self.last_run),
            'successful_runs': sum(1 for run in self.last_run.values() if run.get('success', False)),
            'average_execution_time': 0,
            'last_execution': None
        }
        
        if self.last_run:
            execution_times = [run.get('execution_time', 0) for run in self.last_run.values() if 'execution_time' in run]
            if execution_times:
                metrics['average_execution_time'] = sum(execution_times) / len(execution_times)
            
            # Find most recent execution
            last_run = max(self.last_run.values(), key=lambda x: x.get('timestamp', ''))
            metrics['last_execution'] = last_run
        
        return metrics
    
    def run_forever(self):
        """Run the scheduler indefinitely"""
        self.running = True
        logger.info("🚀 Scheduler started - running continuously...")
        
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logger.info("⚠️ Scheduler interrupted by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
            self.running = False
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("🛑 Scheduler stopped")
    
    def get_next_runs(self) -> dict:
        """Get information about next scheduled runs"""
        next_runs = {}
        
        for job in schedule.get_jobs():
            tag = list(job.tags)[0] if job.tags else 'unknown'
            next_run = job.next_run
            
            if tag not in next_runs or next_run < next_runs[tag]:
                next_runs[tag] = next_run
        
        return next_runs
    
    def create_windows_task(self, task_name: str, spot_type: str, time_str: str, 
                           script_path: Path, python_path: str = "python"):
        """
        Create Windows Task Scheduler task for this reservation
        
        Args:
            task_name: Name for the scheduled task
            spot_type: 'executive' or 'regular'
            time_str: Time in HH:MM:SS format
            script_path: Path to the main script
            python_path: Path to Python executable
        """
        try:
            import subprocess
            
            # Parse time
            hour, minute, second = time_str.split(':')
            
            # Create XML for task
            xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Elia Parking Bot - {spot_type.title()} Spots Reservation</Description>
    <URI>\\EliaBot\\{task_name}</URI>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-01-01T{hour}:{minute}:{second}</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
          <Tuesday />
          <Wednesday />
          <Thursday />
          <Friday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_path}</Command>
      <Arguments>"{script_path}" --spot-type {spot_type}</Arguments>
      <WorkingDirectory>{script_path.parent}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
            
            # Save XML temporarily
            xml_path = Path(f'./{task_name}.xml')
            with open(xml_path, 'w', encoding='utf-16') as f:
                f.write(xml_content)
            
            # Create task using schtasks
            cmd = f'schtasks /Create /TN "EliaBot\\{task_name}" /XML "{xml_path}" /F'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.success(f"✅ Windows Task created: {task_name}")
                xml_path.unlink()  # Clean up XML file
                return True
            else:
                logger.error(f"❌ Failed to create task: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Windows Task creation failed: {e}")
            return False
    
    def setup_windows_tasks(self, script_path: Path):
        """Set up both Windows scheduled tasks"""
        logger.info("🪟 Setting up Windows Task Scheduler tasks...")
        
        # Get Python path
        import sys
        python_path = sys.executable
        
        # Create executive task
        if self.schedules.get('executive_spots', {}).get('enabled'):
            exec_time = self.schedules['executive_spots'].get('time', '00:00:00')
            self.create_windows_task(
                'EliaBot_Executive',
                'executive',
                exec_time,
                script_path,
                python_path
            )
        
        # Create regular task
        if self.schedules.get('regular_spots', {}).get('enabled'):
            reg_time = self.schedules['regular_spots'].get('time', '06:00:00')
            self.create_windows_task(
                'EliaBot_Regular',
                'regular',
                reg_time,
                script_path,
                python_path
            )
        
        logger.success("✅ Windows Task Scheduler setup complete")
    
    def should_run_today(self, spot_type: str) -> bool:
        """Check if reservation should run today (skip weekends if configured)"""
        config = self.schedules.get(f'{spot_type}_spots', {})
        
        if not config.get('weekdays_only', True):
            return True
        
        # Check if today is a weekend
        today = datetime.now().weekday()
        is_weekend = today >= 5  # Saturday=5, Sunday=6
        
        if is_weekend:
            logger.info(f"⏭️ Skipping {spot_type} reservation - Weekend")
            return False
        
        return True
    
    def calculate_target_date(self, days_advance: int = 14) -> datetime:
        """
        Calculate the target reservation date
        Skip weekends if current approach requires it
        """
        target = datetime.now() + timedelta(days=days_advance)
        
        # If target is weekend, adjust to next Monday
        while target.weekday() >= 5:
            target += timedelta(days=1)
        
        logger.info(f"🎯 Target reservation date: {target.strftime('%Y-%m-%d (%A)')}")
        return target


def test_scheduler():
    """Test the scheduler"""
    config = {
        'schedules': {
            'executive_spots': {
                'enabled': True,
                'time': '00:00:00',
                'weekdays_only': True
            },
            'regular_spots': {
                'enabled': True,
                'time': '06:00:00',
                'weekdays_only': True
            }
        }
    }
    
    async def test_callback(spot_type: str):
        logger.info(f"🎯 Test callback triggered for {spot_type} spots")
    
    scheduler = ReservationScheduler(config)
    scheduler.setup_schedules(test_callback)
    
    # Show next runs
    next_runs = scheduler.get_next_runs()
    for spot_type, next_run in next_runs.items():
        print(f"Next {spot_type} run: {next_run}")
    
    # Calculate target dates
    target = scheduler.calculate_target_date(14)
    print(f"Target date (14 days): {target}")


if __name__ == "__main__":
    test_scheduler()

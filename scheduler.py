"""
Advanced Scheduler for Elia Parking Bot
Handles dual scheduling (midnight executive, 6am regular)
Includes Windows Task Scheduler integration
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
    """Manages scheduling for parking reservations"""
    
    def __init__(self, config: dict):
        self.config = config
        self.schedules = config.get('schedules', {})
        self.running = False
        self.last_run = {}
        
        logger.info("⏰ ReservationScheduler initialized")
    
    def setup_schedules(self, reservation_callback: Callable):
        """
        Set up all configured schedules
        
        Args:
            reservation_callback: Async function to call for reservations
                                 Should accept spot_type as parameter
        """
        schedule.clear()
        
        # Executive spots schedule (midnight)
        if self.schedules.get('executive_spots', {}).get('enabled'):
            exec_config = self.schedules['executive_spots']
            exec_time = exec_config.get('time', '00:00:00')
            weekdays_only = exec_config.get('weekdays_only', True)
            
            if weekdays_only:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    getattr(schedule.every(), day).at(exec_time).do(
                        lambda: asyncio.run(reservation_callback('executive'))
                    ).tag('executive')
                logger.info(f"✅ Executive spots scheduled: Weekdays at {exec_time}")
            else:
                schedule.every().day.at(exec_time).do(
                    lambda: asyncio.run(reservation_callback('executive'))
                ).tag('executive')
                logger.info(f"✅ Executive spots scheduled: Daily at {exec_time}")
        
        # Regular spots schedule (6am)
        if self.schedules.get('regular_spots', {}).get('enabled'):
            reg_config = self.schedules['regular_spots']
            reg_time = reg_config.get('time', '06:00:00')
            weekdays_only = reg_config.get('weekdays_only', True)
            
            if weekdays_only:
                for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                    getattr(schedule.every(), day).at(reg_time).do(
                        lambda: asyncio.run(reservation_callback('regular'))
                    ).tag('regular')
                logger.info(f"✅ Regular spots scheduled: Weekdays at {reg_time}")
            else:
                schedule.every().day.at(reg_time).do(
                    lambda: asyncio.run(reservation_callback('regular'))
                ).tag('regular')
                logger.info(f"✅ Regular spots scheduled: Daily at {reg_time}")
        
        logger.success("🎯 All schedules configured")
    
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

import os
import psutil
import time
import socket
from .logging import logger


class PIDManager:
    def __init__(self, pid_file: str = "data/bot.pid", server_pid_file: str = "data/server.pid"):
        self.pid_file = pid_file
        self.server_pid_file = server_pid_file
        self.ensure_data_dir()

    def ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)

    def save_pid(self, pid: int = None):
        """Save bot process PID to file (backward compatibility)"""
        return self.save_bot_pid(pid)

    def save_bot_pid(self, pid: int = None):
        """Save bot process PID to file"""
        if pid is None:
            pid = os.getpid()
        try:
            with open(self.pid_file, "w") as f:
                f.write(str(pid))
            logger.debug(f"Saved bot PID {pid} to {self.pid_file}")
        except Exception as e:
            logger.error(f"Failed to save bot PID: {e}")

    def save_server_pid(self, pid: int = None):
        """Save web server process PID to file"""
        if pid is None:
            pid = os.getpid()
        try:
            with open(self.server_pid_file, "w") as f:
                f.write(str(pid))
            logger.debug(f"Saved server PID {pid} to {self.server_pid_file}")
        except Exception as e:
            logger.error(f"Failed to save server PID: {e}")

    def get_pid(self) -> int:
        """Get saved bot PID from file (backward compatibility)"""
        return self.get_bot_pid()

    def get_bot_pid(self) -> int:
        """Get saved bot PID from file"""
        try:
            if os.path.exists(self.pid_file):
                with open(self.pid_file, "r") as f:
                    return int(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read bot PID: {e}")
        return None

    def get_server_pid(self) -> int:
        """Get saved server PID from file"""
        try:
            if os.path.exists(self.server_pid_file):
                with open(self.server_pid_file, "r") as f:
                    return int(f.read().strip())
        except Exception as e:
            logger.error(f"Failed to read server PID: {e}")
        return None

    def is_running(self, pid: int = None) -> bool:
        """Check if a process is running (backward compatibility)"""
        if pid is None:
            pid = self.get_bot_pid()

        if pid is None:
            return False

        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def kill_bot(self, timeout: int = 5) -> bool:
        """Kill the bot process gracefully"""
        return self._kill_process(self.get_bot_pid(), "bot", timeout)

    def kill_server(self, timeout: int = 3) -> bool:
        """Kill the web server process gracefully"""
        return self._kill_process(self.get_server_pid(), "server", timeout)

    def kill_process(self, pid: int = None, timeout: int = 5) -> bool:
        """Kill a process gracefully (backward compatibility)"""
        if pid is None:
            pid = self.get_bot_pid()
        return self._kill_process(pid, "bot", timeout)

    def _kill_process(self, pid: int, process_type: str, timeout: int = 5) -> bool:
        """Kill a specific process gracefully"""
        if pid is None:
            logger.warning(f"No {process_type} PID saved")
            return False

        try:
            process = psutil.Process(pid)
            if process.is_running():
                logger.info(f"Terminating {process_type} process {pid}")
                process.terminate()

                # Wait for process to terminate
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not process.is_running():
                        logger.info(f"{process_type} process {pid} terminated gracefully")
                        return True
                    time.sleep(0.1)

                # Force kill if still running
                if process.is_running():
                    logger.warning(f"Force killing {process_type} process {pid}")
                    process.kill()
                    process.wait()
                    logger.info(f"{process_type} process {pid} force killed")
                    return True

            logger.info(f"{process_type} process {pid} was not running")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to kill {process_type} process {pid}: {e}")
            return False

    def kill_all_bot_processes(self) -> int:
        """Kill all bot and web server processes"""
        killed_count = 0
        
        # Kill saved bot process
        if self.kill_bot():
            killed_count += 1
        
        # Kill saved server process
        if self.kill_server():
            killed_count += 1
        
        # Kill any orphaned processes
        killed_count += self.cleanup_old_instances()
        
        # Wait for port to be freed
        if self.wait_for_port_free():
            logger.info("Port 8000 is now available")
        else:
            logger.warning("Port 8000 still in use after cleanup")
        
        return killed_count

    def wait_for_port_free(self, port: int = 8000, timeout: int = 10) -> bool:
        """Wait for a port to be free"""
        logger.info(f"Waiting for port {port} to be free...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result != 0:  # Port is free
                    logger.info(f"Port {port} is now free")
                    return True
                    
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Error checking port {port}: {e}")
                return True  # Assume it's free if we can't check
        
        logger.warning(f"Port {port} still in use after {timeout} seconds")
        return False

    def cleanup_old_instances(self) -> int:
        """Kill any old bot instances"""
        current_pid = os.getpid()
        killed_count = 0

        try:
            # Find all python processes running main.py or web_server.py
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["name"] in ["python3", "python", "uvicorn"]:
                        cmdline = proc.info["cmdline"] or []
                        cmdline_str = " ".join(cmdline)
                        
                        # Check for bot processes
                        if ("main.py" in cmdline_str or "src/web_server.py" in cmdline_str or
                            "web_server.py" in cmdline_str or "uvicorn" in cmdline_str) and proc.info["pid"] != current_pid:
                            
                            logger.info(f"Killing old bot/server instance: PID {proc.info['pid']} - {cmdline_str}")
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                                killed_count += 1
                            except psutil.TimeoutExpired:
                                proc.kill()
                                proc.wait()
                                killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

        return killed_count


# Global PID manager instance
pid_manager = PIDManager()

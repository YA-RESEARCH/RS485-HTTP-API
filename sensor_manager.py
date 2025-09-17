"""
传感器管理器
负责 Modbus 连接管理、传感器数据轮询、缓存管理
"""

import time
import threading
import yaml
from datetime import datetime
from typing import Dict, Any, Optional
from pymodbus.client import ModbusSerialClient
import logging

# 获取logger
logger = logging.getLogger("uvicorn")


class SensorManager:
    """传感器管理器 - 核心业务逻辑"""
    
    def __init__(self, config_file: str = "sensors.yaml"):
        self.config = self._load_config(config_file)
        self.client = None
        self.cache = {}
        self.is_running = False
        self.sensors_enabled = False
        self.polling_thread = None
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _connect_modbus(self) -> bool:
        """连接Modbus"""
        if self.client and self.client.is_socket_open():
            return True
            
        serial_config = self.config['serial']
        self.client = ModbusSerialClient(**serial_config)
        
        if self.client.connect():
            logger.info(f"Modbus 连接成功: {serial_config['port']}")
            return True
        return False
    
    def _disconnect_modbus(self):
        """断开Modbus连接"""
        if self.client:
            self.client.close()
    
    def _parse_angle_data(self, registers: list) -> Dict[str, Any]:
        """解析角度传感器数据"""
        def to_signed(val):
            return val - 65536 if val & 0x8000 else val
            
        roll = (to_signed(registers[0]) / 32768.0) * 180.0
        pitch = (to_signed(registers[1]) / 32768.0) * 180.0
        
        return {"roll": round(roll, 2), "pitch": round(pitch, 2)}
    
    def _read_sensor(self, sensor_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """读取传感器数据"""
        try:
            response = self.client.read_holding_registers(
                address=config['address'],
                count=config['count'],
                device_id=config['slave_id']
            )
            
            if response.isError() or not response.registers:
                raise Exception("读取失败")
            
            # 解析数据
            if config['parser'] == 'angle':
                data = self._parse_angle_data(response.registers)
            else:
                data = {}
            
            return {
                "sensor_id": sensor_id,
                "timestamp": datetime.now().isoformat(),
                "data": data,
                "status": "online"
            }
            
        except Exception as e:
            return {
                "sensor_id": sensor_id,
                "timestamp": datetime.now().isoformat(),
                "data": {},
                "status": "error",
                "error": str(e)
            }
    
    def _polling_loop(self):
        """后台轮询循环"""
        polling_interval = self.config['system']['polling_interval']
        sensors_config = self.config['sensors']
        
        while self.is_running:
            if self.sensors_enabled:
                for sensor_id, config in sensors_config.items():
                    if not self.is_running:
                        break
                    sensor_data = self._read_sensor(sensor_id, config)
                    self.cache[sensor_id] = sensor_data
            else:
                # 传感器未启用时设置disabled状态
                for sensor_id in sensors_config.keys():
                    self.cache[sensor_id] = {
                        "sensor_id": sensor_id,
                        "timestamp": datetime.now().isoformat(),
                        "data": {},
                        "status": "disabled"
                    }
            
            time.sleep(polling_interval)
    
    def start(self) -> bool:
        """启动传感器管理器"""
        if self.is_running:
            return True
        
        self.is_running = True
        self.polling_thread = threading.Thread(target=self._polling_loop, daemon=True)
        self.polling_thread.start()
        return True
    
    def stop(self):
        """停止传感器管理器"""
        self.is_running = False
        self.sensors_enabled = False
        
        if self.polling_thread:
            self.polling_thread.join(timeout=2)
        
        self._disconnect_modbus()
    
    def start_sensors(self) -> bool:
        """启动传感器数据采集"""
        if self.sensors_enabled:
            return True
        
        if self._connect_modbus():
            self.sensors_enabled = True
            return True
        return False
    
    def stop_sensors(self):
        """停止传感器数据采集"""
        self.sensors_enabled = False
        self._disconnect_modbus()
    
    def get_sensor_data(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """获取指定传感器数据"""
        return self.cache.get(sensor_id)
    
    def get_all_sensors(self) -> Dict[str, Any]:
        """获取所有传感器数据"""
        return self.cache.copy()
    
    def get_sensor_list(self) -> list:
        """获取传感器列表"""
        return list(self.config['sensors'].keys())


# 全局传感器管理器实例
sensor_manager = SensorManager()
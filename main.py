"""
FastAPI 应用主入口
提供 RESTful API 接口访问传感器数据
"""

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn
from sensor_manager import sensor_manager
import logging

# 获取应用日志器
logger = logging.getLogger("uvicorn")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("启动传感器管理器...")
    if sensor_manager.start():
        logger.info("传感器管理器启动成功")
    else:
        logger.error("传感器管理器启动失败")
        
    yield
    
    # 关闭时
    logger.info("停止传感器管理器...")
    sensor_manager.stop()
    logger.info("RS485 传感器 HTTP API 服务已停止")


# 创建 FastAPI 应用
app = FastAPI(
    title="RS485 传感器 HTTP API",
    description="通过 HTTP API 获取 RS485 传感器数据",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/sensors")
async def get_all_sensors():
    """获取所有传感器数据"""
    logger.debug("请求所有传感器数据")
    return sensor_manager.get_all_sensors()


@app.get("/sensor/{sensor_id}")
async def get_sensor_data(sensor_id: str):
    """获取指定传感器的最新数据"""
    logger.debug(f"请求传感器数据: {sensor_id}")
    
    if sensor_id not in sensor_manager.get_sensor_list():
        logger.warning(f"请求不存在的传感器: {sensor_id}")
        raise HTTPException(status_code=404, detail=f"传感器 '{sensor_id}' 不存在")
    
    sensor_data = sensor_manager.get_sensor_data(sensor_id)
    if sensor_data is None:
        logger.warning(f"传感器 {sensor_id} 数据尚未可用")
        raise HTTPException(status_code=503, detail="传感器数据尚未可用，请稍后重试")
    
    logger.debug(f"成功返回传感器 {sensor_id} 数据")
    return sensor_data


@app.post("/sensors/start")
async def start_sensors():
    """启动传感器数据采集"""
    logger.info("收到启动传感器数据采集请求")
    
    if sensor_manager.start_sensors():
        logger.info("传感器数据采集启动成功")
        return {"status": "sensor data collection started"}
    else:
        logger.error("传感器数据采集启动失败")
        raise HTTPException(status_code=500, detail="启动传感器采集失败")


@app.post("/sensors/stop")
async def stop_sensors():
    """停止传感器数据采集"""
    logger.info("收到停止传感器数据采集请求")
    sensor_manager.stop_sensors()
    logger.info("传感器数据采集已停止")
    return {"status": "sensor data collection stopped"}


if __name__ == "__main__": 
    # 启动uvicorn服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
    )
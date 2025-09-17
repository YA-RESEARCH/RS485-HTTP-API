# 🚀 RS485-HTTP-API

> 基于 FastAPI 的 RS485 传感器 HTTP 接口服务，支持动态启停控制

## ✨ 特性

- � **按需启动** - 考试时启动，平时关闭节能
- ⚡ **极速响应** - 内存缓存，毫秒级API响应
- 🔧 **配置驱动** - YAML配置，新增传感器零代码
- 📊 **实时数据** - 后台轮询，数据始终最新
- 🎨 **优雅架构** - 简洁代码，易于维护

## �🏗️ 项目结构

```
📦 RS485-HTTP-API/
├── 🐍 main.py              # FastAPI 应用入口
├── ⚙️  sensor_manager.py    # 传感器管理器
├── 📝 sensors.yaml         # 传感器配置
└── 📋 requirements.txt     # 依赖列表
```

## 🚀 快速开始

### 1️⃣ 安装依赖
```bash
#永久设置git代理
git config --global http.proxy http://172.16.20.38:10808
git config --global https.proxy http://172.16.20.38:10808
#临时设置代理，方便安装uv
export https_proxy="http://172.16.20.38:10808"
export http_proxy="http://172.16.20.38:10808"
curl -LsSf https://astral.sh/uv/install.sh | sh
#创建虚拟环境
uv venv
source .venv/bin/activate
```

### 2. 安装依赖
```bash
# 使用 uv（推荐）
uv pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用 pip
pip install -r requirements.txt --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2️⃣ 配置传感器
编辑 `sensors.yaml`：
```yaml
sensors:
  angle_sensor_1:
    slave_id: 80        # 从站地址
    address: 61         # 寄存器地址  
    count: 2           # 寄存器数量
    parser: "angle"    # 解析器类型
```

### 3️⃣ 启动服务
```bash
python main.py
```
🌐 服务地址：http://localhost:8000  
� API文档：http://localhost:8000/docs

## 🎮 使用方法

### 📡 启动传感器采集
```bash
curl -X POST http://localhost:8000/sensors/start
```

### 📊 获取传感器数据
```bash
curl http://localhost:8000/sensor/angle_sensor_1
```

### ⏹️ 停止传感器采集
```bash
curl -X POST http://localhost:8000/sensors/stop
```

## 📋 API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/sensors` | GET | 📊 获取所有传感器数据 |
| `/sensor/{id}` | GET | 🎯 获取指定传感器数据 |
| `/sensors/start` | POST | 🚀 启动传感器采集 |
| `/sensors/stop` | POST | ⏹️ 停止传感器采集 |

## 🔧 扩展传感器

只需两步即可添加新传感器：

### 1️⃣ 配置文件
```yaml
# 在 sensors.yaml 中添加
temperature_sensor:
  slave_id: 81
  address: 1  
  count: 1
  parser: "temperature"
```

### 2️⃣ 解析函数
```python
# 在 sensor_manager.py 中添加
def _parse_temperature_data(self, registers):
    temp = registers[0] / 100.0
    return {"temperature": round(temp, 1)}
```

✅ 完成！新传感器自动可用

## 🎯 典型使用场景

### 📚 考试应用
```bash
# 考试前启动
curl -X POST http://localhost:8000/sensors/start

# 考试中获取数据
curl http://localhost:8000/sensor/angle_sensor_1

# 考试后停止
curl -X POST http://localhost:8000/sensors/stop
```

### 📈 数据监控
```bash
# 实时监控所有传感器
watch -n 1 'curl -s http://localhost:8000/sensors | jq'
```

## �️ 故障排除

### 🔐 串口权限
```bash
sudo chmod 666 /dev/ttyUSB0
```

### 🔍 测试连接
```bash
# 检查传感器状态
curl http://localhost:8000/sensor/angle_sensor_1
```

## 🚀 生产部署

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

> ⚠️ **重要**：使用 `--workers 1` 避免 RS485 串口冲突

---

<div align="center">

**🎉 享受简洁优雅的传感器接口服务！**

</div>
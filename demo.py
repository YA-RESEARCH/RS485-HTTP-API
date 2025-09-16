# demo.py

import time
from pymodbus.client import ModbusSerialClient

# ==============================================================================
# --- 1. 根据传感器文档 "Roll~Yaw" 修改配置 ---
# ==============================================================================
SERIAL_PORT = "/dev/ttyUSB0"
# 从站地址: "50" (十六进制) -> 80 (十进制)
SENSOR_SLAVE_ID = 80
# 通信参数 (假设不变)
BAUDRATE = 9600
PARITY = 'N'
STOPBITS = 1
BYTESIZE = 8

# 要读取的寄存器信息 (根据文档精确修改)
# 起始地址: "00 3D" -> 61 (十进制)
REGISTER_ADDRESS = 61
# 读取数量: "00 02" -> 2 (十进制)
REGISTER_COUNT = 2

# --- 数据解析函数 ---
def to_signed_short(unsigned_val):
    """将一个16位的无符号整数转换为有符号整数 (补码转换)。"""
    if unsigned_val & 0x8000:
        return unsigned_val - 65536
    else:
        return unsigned_val

# ==============================================================================
# --- 2. 初始化和连接部分 (无需修改) ---
# ==============================================================================
client = ModbusSerialClient(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=1
)

if not client.connect():
    print(f"错误: 无法连接到串口 {SERIAL_PORT}。")
    exit()

print(f"连接成功！开始读取从站ID {SENSOR_SLAVE_ID} 的角度传感器...")

# ==============================================================================
# --- 3. 循环读取并精确解析数据 ---
# ==============================================================================
try:
    while True:
        response = client.read_holding_registers(
            address=REGISTER_ADDRESS, # 将使用 61
            count=REGISTER_COUNT,     # 将使用 2
            device_id=SENSOR_SLAVE_ID      # 将使用 80
        )

        if response.isError():
            print(f"Modbus错误: {response}")
        elif not response.registers or len(response.registers) < REGISTER_COUNT:
            print(f"Modbus错误: 响应为空或数据长度不足 (需要 {REGISTER_COUNT} 个寄存器)")
        else:
            # 提取原始寄存器列表
            # response.registers[0] 是地址61 (Roll) 的值
            # response.registers[1] 是地址62 (Pitch) 的值
            raw_roll = response.registers[0]
            raw_pitch = response.registers[1]

            # 1. 将原始值转换为有符号整数
            signed_roll = to_signed_short(raw_roll)
            signed_pitch = to_signed_short(raw_pitch)

            # 2. 根据文档提供的公式进行换算
            # 真实角度 = 读取到的有符号整数 / 32768 * 180
            angle_roll = (signed_roll / 32768.0) * 180.0
            angle_pitch = (signed_pitch / 32768.0) * 180.0

            # 3. 打印清晰、格式化的结果
            print("--- 成功解析角度数据 ---")
            print(f"  滚转角 (Roll): {angle_roll:7.2f}°  (原始值: {raw_roll:5d} -> 有符号: {signed_roll:6d})")
            print(f"  俯仰角 (Pitch): {angle_pitch:7.2f}°  (原始值: {raw_pitch:5d} -> 有符号: {signed_pitch:6d})")
            print("-" * 30)

        time.sleep(1) # 每秒读取一次

except KeyboardInterrupt:
    print("程序被用户中断。")
finally:
    client.close()
    print("Modbus连接已关闭。")
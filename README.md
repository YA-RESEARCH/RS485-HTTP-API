# RS485-HTTP-API
部署在pi上的获取rs485传感器的http服务
## 环境设置
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
uv pip install pymodbus
uv pip install pyserial
```
# 和台湾长荣集团的EDI接口相关开发

# create virtural myvenv
pip freeze > requirements.txt

virtualenv myvenv

# Activate
source myvenv/bin/activate
# deactivate
deactivate
pip install -r requirements.txt

# run python at background
# nohup python -u test.py > out.log 2>&1 &
# nohup 日志文件不计录
# nohup python -u test.py >/dev/null 2>&1 &
# 查看进程
ps aux|grep python
# jobs 查看后台运行的进程
# fg %n 让后台运行的进程n到前台来
# bg %n 让进程n到后台去
# kill %n 杀死job

启动 parcel-api
1. 激活虚拟环境
cd /var/parcels-api
source api-venv/bin/activate

2. 将启动后台程序
2.1 从数据库里读取数据，上传给长荣
nohup python -u edi_send.py >/dev/null 2>&1 &

2.2 监控本地是否有需要解析的文件，有的话，解析并更新到数据库中
nohup python -u edi_parser.py >/dev/null 2>&1 &









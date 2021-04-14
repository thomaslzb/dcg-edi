# 和台湾长荣集团的EDI接口相关开发的服务
ps aux|grep python
sudo chmod u+x startmyapp
启动 DCG-EDI
1. 激活虚拟环境
cd /var/dcg-edi
source venv/bin/activate

2. 启动ftp_client.py 程序：该程序就是从FTP服务器中，取回EDI的文件
nohup python -u ftp_client.py >/dev/null 2>&1 &

3. 上传数据： 从数据库里读取数据自动生成EDI文件，上传给船公司
nohup python -u edi_send.py >/dev/null 2>&1 &

4. 监控本地是否有需要解析的文件，有的话，解析并更新到数据库中
nohup python -u edi_parser.py >/dev/null 2>&1 &

BAT
./startapp-edi_send
./startapp-edi_parser
./startapp-ftp_client

第一次做的小项目
二手交易网站

环境
python3.7.5+django2.2.5
redis3.0.5
boostrap3.3.7
mysql5.7.26
支付宝支付沙箱
fastDFS分布式文件系统
pip install -r package.txt
# 启动celery
celery -A celery_task.tasks worker  --loglevel=info
# 初始化索引
python manage.py rebuild_index
# 启动服务
python manage.py runserver
# 配置文件修改
celery_task/tasks.py                                     redis
surplus_transaction/settings.py                    redis,mysql,fastdfs
surplus_transaction/utils/fdfs/client.conf      fastdfs

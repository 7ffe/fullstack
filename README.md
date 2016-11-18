README.

关于MySQL数据库:
http://www.cnblogs.com/starof/p/4680083.html
mariadb数据库的相关命令是：
- systemctl start mariadb  #启动MariaDB
- systemctl stop mariadb  #停止MariaDB
- systemctl restart mariadb  #重启MariaDB
- systemctl enable mariadb  #设置开机启动

Start RabbitMQ Server:
https://pubs.vmware.com/vfabric52/index.jsp?topic=/com.vmware.vfabric.rabbitmq.2.8/getstart/install-start-server-rhel.html
sudo /sbin/service rabbitmq-server start
sudo /sbin/service rabbitmq-server stop
sudo /sbin/service rabbitmq-server restart

ElasticSearch:
sudo systemctl start elasticsearch.service
sudo systemctl stop elasticsearch.service
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch.service

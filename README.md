# news_project
新闻资讯

1. 安装 requirement.txt 中的包
```shell
$ pip install -r requirement.txt
```

2. 创建数据库
```shell
$ mysql -u NAME -p PASSWORD
mysql> create database news_demo charset=utf8;
```

3. 数据库迁移
```shell
$ python manage.py mysql init
$ python manage.py mysql migrate
$ python manage.py mysql upgrade
```

4. 运行
```shell
$ python manage.py runserver -p 5000
```



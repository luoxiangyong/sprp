# ubuntu 18.04

## vagrant

1. 准备环境

   ```shell
   vagrant init
   ```

2. 修改Vagrantfile

   ```ruby
   # -*- mode: ruby -*-
   # vi: set ft=ruby :
   
   Vagrant.configure("2") do |config|
     config.vm.box = "generic/ubuntu1804"
   
     config.vm.network "private_network", ip: "192.168.33.10"
   
     config.vm.synced_folder ".", "/vagrant_data"
   
     config.vm.provider "virtualbox" do |vb|
       vb.memory = "1024"
     end
   
   end
   
   ```

3. 启动系统

```
vagrant up
```

4. 登录系统

   ```shell
   vagrant ssh
   ```

   在/etc/resolv.conf文件中添加

    ```shell
    nameserver 8.8.8.8
    nameserver 8.8.4.4
    ```

5. 重新启动网络

   ```bash
   sudo systemctl restart networking
   ```


## 安装依赖库

```
sudo apt-get install python3 python-dev
#sudo apt-get install proj-bin libproj-dev
#sudo apt-get install libgdal-dev gdal-bin gdal-data
sudo apt-get install python3-pyproj python3-numpy python3-gdal
pip3 install setuptools
```

## pip3的国内依赖库

更改~/.pip/pip.conf[.ini]文件内容为国内PyPI源即可

## docker镜像制作及上传

```bash
docker build -t sprp-web .
docker tag sprp-web sololxy/sprp-web
docker login
docker push sololxy/sprp-web
```

## Docker使用

安装了docker后输入如下命令
```shell
docker pull sololxy/sprp-web
docker run -name sprp_demo sololxy/sprp-web -p 8000:8000
```
启动浏览器，输入：http://localhost:8080/ ,即可。

如果出现页面没有相应的情况，可能是docker的远程访问没打开，请按如下步骤设置系统：

```shell
# 修改docker服务的配置文件
vim /lib/systemd/system/docker.service
# 找到“ExecStart”，把该行修改为： 
ExecStart=/usr/bin/dockerd -H unix:///var/run/docker.sock -H tcp://0.0.0.0:2375
# 保存退出
# 重新加载
systemctl daemon-reload
# 重启docker服务
systemctl restart docker
```


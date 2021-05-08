# ubuntu 18.04



## vagrant

1. 在/etc/resolv.conf文件中添加

```shell
nameserver 8.8.8.8
nameserver 8.8.4.4
```

2. 重新启动网络

   ```bash
   sudo systemctl restart networking
   ```



## 系统依赖库

```
sudo apt-get install python3 python-dev
#sudo apt-get install proj-bin libproj-dev
sudo apt-get install libgdal-dev gdal-bin gdal-data
sudo apt-get install python3-pyproj python3-numpy python3-gdal
```

## pip3的国内依赖库


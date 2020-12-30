# 20201230更新
代码已失效，归档，不再更新

# 20200220更新
修改采集源

# 20191110更新
鼠绘疑似被查，目前鼠绘汉化的海贼只能看最近的3话，之前的只有腾讯翻译了

# 海贼王鼠绘漫画下载
环境：python3
说明：基于scrapy的爬虫，下载鼠绘翻译的海贼王漫画，根据章节分文件夹下载到指定目录  
安装依赖包：pip install -r requirements.txt  
使用：  
1、下载项目到本地  
2、根据需要修改setting.py的存储路径，默认： IMAGES_STORE = 'D:\下载测试'
3、命令：  
&emsp;&emsp;cd:ishuhui &emsp;&emsp;  # cmd 进入到项目 目录  
&emsp;&emsp;scrapy crawl comices -a num=930 &emsp;&emsp; # 下载指定的章节（930话）  
&emsp;&emsp;scrapy crawl comices -a new=5 &emsp;&emsp;  # 下载最新的5话  
&emsp;&emsp;scrapy crawl comices -a num=all &emsp;&emsp; # 全部下载  
&emsp;&emsp;或者  
&emsp;&emsp;scrapy crawl comices -a new=all &emsp;&emsp; # 全部下载 
 
## 效果图(整体)  
![Image text](https://github.com/TurboWay/ishuhui/blob/master/img_example/eg.png)  
## 效果图(单话)   
![Image text](https://github.com/TurboWay/ishuhui/blob/master/img_example/eg2.png)  

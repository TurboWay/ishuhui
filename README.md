# 海贼王鼠绘漫画下载
##环境：python3  
##说明：基于scrapy的爬虫，下载鼠绘翻译的海贼王漫画，根据章节分文件夹下载到指定目录  
##使用：  
##1、下载项目到本地  
##2、根据需要修改setting.py的存储路径，默认： IMAGES_STORE = 'D:\下载测试'  
##3、命令：
##    cd:ishuhui  # cmd 进入到项目 目录  
##    scrapy crawl comices -a num=930 # 下载指定的章节（930话）  
##    scrapy crawl comices -a new=5  # 下载最新的5话  
##    scrapy crawl comices # 全部下载    
# Fofa

基于 Fofa 的自动化指纹采集工具，详见

[基于 FoFa 的自动化指纹提取](https://github.com/Fuinow/MyPaper/blob/master/%E5%9F%BA%E4%BA%8Efofa%E7%9A%84%E8%87%AA%E5%8A%A8%E5%8C%96%E6%8C%87%E7%BA%B9%E6%8F%90%E5%8F%96/%E5%9F%BA%E4%BA%8Efofa%E7%9A%84%E8%87%AA%E5%8A%A8%E5%8C%96%E6%8C%87%E7%BA%B9%E6%8F%90%E5%8F%96.md)

[我想白嫖之突破FOFA查询限制](https://github.com/Fuinow/MyPaper/blob/master/%E6%88%91%E6%83%B3%E7%99%BD%E5%AB%96%E4%B9%8B%E7%AA%81%E7%A0%B4FOFA%E6%9F%A5%E8%AF%A2%E9%99%90%E5%88%B6/%E6%88%91%E6%83%B3%E7%99%BD%E5%AB%96%E4%B9%8B%E7%AA%81%E7%A0%B4FOFA%E6%9F%A5%E8%AF%A2%E9%99%90%E5%88%B6.md)

## TODO 

+ 跑白名单（body，header）

+ ~~取 Content-Lengh 最小的两个目标比较~~

+ ~~获取目标网页信息切换为并发~~

+ ~~解决 HOST 重复获取~~

+ 递归增加熔断机制

+ ~~将 header 转化为一个大字符串比较~~

+ 增加非 HTTP 协议指纹识别（SOCKET）

+ 规则验证增加代理池并切换为并发

+ ~~增加已验证过的规则 List 防止重复验证~~

+ 分解白名单为数据清洗白名单，规则验证白名单，并分开处理

+ 制定策略切分过长的测试规则
 
+ 规则白名单匹配改为相似度匹配

## BUG

+ 如果一直跑不出新规则就获取不到新 HOST 会使 LIST 为空报错

# Java后端实习面试高频知识点

## 一、Spring Boot核心

### 1. Spring Boot自动配置原理
Spring Boot的自动配置是基于约定优于配置的思想，核心注解是`@SpringBootApplication`，它包含了三个核心注解：
- `@SpringBootConfiguration`：标记当前类是配置类
- `@EnableAutoConfiguration`：开启自动配置，会去META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports文件里读取所有需要自动配置的类
- `@ComponentScan`：默认扫描启动类所在包及子包下的所有组件

自动配置的条件注解非常重要，比如`@ConditionalOnClass`表示只有当类路径下存在指定类时，这个自动配置才会生效，这就是为什么引入对应的starter就自动生效的原因。

### 2. Spring Bean的生命周期
Spring Bean的完整生命周期分为四个阶段：
1. 实例化：通过构造方法创建Bean对象
2. 属性填充：给Bean的属性注入依赖
3. 初始化：执行各种BeanPostProcessor的前置处理，然后执行初始化方法（比如afterPropertiesSet、@PostConstruct），再执行后置处理
4. 销毁：容器关闭时执行销毁方法

单例Bean默认在容器启动时初始化，原型Bean每次获取时才创建。

## 二、MySQL数据库

### 1. 索引失效的常见场景
MySQL索引在以下场景会失效：
- 对索引列做函数运算、类型转换
- 联合索引不满足最左前缀原则
- 使用`like`以`%`开头的模糊查询
- 索引列使用`!=`、`not in`、`or`连接条件
- MySQL优化器认为全表扫描比走索引更快时，也会放弃索引

### 2. 事务隔离级别
SQL标准定义了四种事务隔离级别：
- 读未提交（Read Uncommitted）：能读到未提交的数据，存在脏读、不可重复读、幻读
- 读提交（Read Committed）：只能读到已提交的数据，解决脏读，存在不可重复读、幻读，是Oracle默认级别
- 可重复读（Repeatable Read）：解决脏读、不可重复读，InnoDB默认级别，通过MVCC和间隙锁解决幻读
- 串行化（Serializable）：最高级别，完全串行执行，性能最差，解决所有并发问题

## 三、Redis缓存

### 1. 缓存穿透、击穿、雪崩
- 缓存穿透：查询一个数据库和缓存都不存在的数据，每次请求都会打到数据库。解决方法：布隆过滤器拦截不存在的key，或者缓存空值
- 缓存击穿：某个热点key突然过期，大量请求同时打到数据库。解决方法：热点key永不过期，或者加互斥锁重建缓存
- 缓存雪崩：大量key同时过期，或者Redis节点宕机，大量请求同时打到数据库。解决方法：过期时间加随机值，Redis集群部署，服务熔断降级

### 2. Redis为什么这么快
Redis快的原因主要有三点：
1. 完全基于内存，大部分操作是内存操作
2. 单线程模型，避免了线程上下文切换和锁竞争
3. IO多路复用模型，用epoll实现高并发网络IO

## 四、分布式中间件

### 1. Nacos和Eureka的区别
- Nacos支持AP和CP切换，Eureka只支持AP
- Nacos支持服务发现和配置中心一体化，Eureka只是服务发现
- Nacos默认临时实例用AP，持久实例用CP
- Nacos性能更高，是Spring Cloud Alibaba的核心组件

### 2. RabbitMQ和Kafka的区别
- RabbitMQ是传统消息队列，功能完善，支持灵活的路由，延迟低，适合业务消息
- Kafka是分布式流处理平台，吞吐量极高，适合日志、大数据场景
- RabbitMQ消息可靠性更高，支持消息确认、死信队列
- Kafka顺序写磁盘+零拷贝技术，单机吞吐量可达百万级

## 五、简历项目相关

### 1. RAG是什么
RAG是检索增强生成，是当前大模型落地最常用的方案，解决大模型幻觉、知识过时、私有数据问答的问题。核心流程是：文档切分 -> 向量化存入向量数据库 -> 用户提问时检索最相关的片段 -> 把片段和问题一起发给大模型生成答案。

### 2. 向量数据库的作用
向量数据库专门存储和检索高维向量，支持语义相似度搜索，和传统数据库的模糊搜索不同，它是根据语义的相似度来匹配结果，而不是关键词匹配。常用的向量数据库有Milvus、Chroma、Pinecone等。

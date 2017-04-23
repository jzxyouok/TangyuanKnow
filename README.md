# TangyuanKnow
基于Python Flask的、面向唐山学院校内的一个模仿知乎的问答网站

# 技术
## 后端
- Python Flask
> Q: 为什么选用Python?  
> A: Python是一门结构精炼, 易于快速开发的高级语言.无论使用哪种语言, 能实现我们需要的功能就可以.
- 数据库ORM SQLAlchemy
> Q: ORM是什么?有什么优点?  
> A: 对象关系映射（Object Relational Mapping，简称ORM）是一种为了解决面向对象与关系数据库存在的互不匹配的现象的技术。  
> 程序员操纵数据库不需要书写SQL代码, 只需要操纵预定好的对象就能控制数据库.  
> 数据库无关: 使用ORM可以随时换用不同的数据库 
> 
> Q: SQLAlchemy有什么优点?  
> A: API功能强大，使得代码有健壮性和适应性  
> 灵活的设计，使得能轻松写复杂查询
>
> Q: API强大在什么地方?  
> A: 比如说项目中用到的评论功能里多对多关系的实现. 在sqlite2中, 没有监听器这种高级功能, 而可以利用SQLAlchemy的API轻松实现提问模型里text字段的监听器.
- 七牛云图床
> Q: 什么是图床? 为什么要使用图床?  
> A: 图床是专门用来存放图片，同时允许你把图片对外连接的网上空间
> 
> A: 不能让体积大的高质量图片占用太多主服务器带宽, 而服务器有空间距离等因素决定访问速度很慢影响图片显示速度, 使用多节点分布式的图床即可让图片访问速度提升.
## 前端
Bootstrap

# 功能
## 基本功能
- 用户注册
- 密码找回

## 用户身份审核
### 学生身份审核
使用模拟登录技术, 测试使用学生用户提供的账号密码能否成功登陆教务系统, 从而判定是否为本校学生.

这样可以实现学生身份的自动审核, 无需人工查验学生证信息, 极大提升了审核效率.

### 教师身份审核
教师人数相对较少, 提供教师身份证明, 由人工审核的方式更为合适.

未来可向学校申请所有教师的邮箱, 由向教师的发送邮件验证码的方式实现教师的身份审核.

## 问题 Question
- 提出问题
- 编辑问题
- 禁用问题
- 关注问题

## 回答 Answer
- 向某一问题提交回答
- 编辑回答
- 对回答点赞/取消点赞

## 评论 Comment
- 对某一回答进行评论
- 删除评论（评论作者）

## 安全性能
部署时, 使用Https技术, 保证用户账号密码不会在中间传输环节被窃取.

服务器不保存用户密码明文, 而是保存用户密码加盐的哈希值, 这样一来即便发生内部员工窃取密码, 也无法获取用户密码明文.


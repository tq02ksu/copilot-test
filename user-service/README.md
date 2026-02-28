# User Management Service - Spring Boot 3.x

基于 Spring Boot 3.x 的用户管理 REST API 服务，连接 MySQL 数据库，提供完整的用户 CRUD 操作。

## 功能特性

- ✅ Spring Boot 3.2.2
- ✅ MySQL 8.0 数据库
- ✅ JPA/Hibernate ORM
- ✅ RESTful API 设计
- ✅ 数据验证
- ✅ Docker Compose 支持

## User 实体

用户实体包含以下字段：

- `id`: 主键，自动生成
- `username`: 用户名，唯一，3-50字符
- `email`: 邮箱，唯一，有效邮箱格式
- `created_at`: 创建时间，自动生成

## API 端点

### 创建用户
```http
POST /api/users
Content-Type: application/json

{
  "username": "zhangsan",
  "email": "zhangsan@example.com"
}
```

### 获取所有用户
```http
GET /api/users
```

### 获取单个用户
```http
GET /api/users/{id}
```

### 更新用户
```http
PUT /api/users/{id}
Content-Type: application/json

{
  "username": "zhangsan_updated",
  "email": "zhangsan_new@example.com"
}
```

### 删除用户
```http
DELETE /api/users/{id}
```

## 快速开始

### 前置要求

- Java 17 或更高版本
- Maven 3.6+
- Docker 和 Docker Compose

### 1. 启动 MySQL 数据库

使用 Docker Compose 启动 MySQL：

```bash
cd user-service
docker-compose up -d
```

等待 MySQL 容器完全启动（大约 20-30 秒）：

```bash
docker-compose ps
```

### 2. 构建应用

```bash
cd user-service
mvn clean package
```

### 3. 运行应用

使用默认配置运行：

```bash
mvn spring-boot:run
```

或者使用环境变量自定义配置：

```bash
export DB_URL=jdbc:mysql://localhost:3306/userdb?useSSL=false&serverTimezone=Asia/Shanghai
export DB_USERNAME=root
export DB_PASSWORD=rootpassword
export SERVER_PORT=8080
mvn spring-boot:run
```

或者运行打包后的 JAR：

```bash
java -jar target/user-management-1.0.0.jar
```

应用将在 `http://localhost:8080` 启动。

### 4. 测试 API

创建一个用户：

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"zhangsan","email":"zhangsan@example.com"}'
```

获取所有用户：

```bash
curl http://localhost:8080/api/users
```

获取指定用户：

```bash
curl http://localhost:8080/api/users/1
```

更新用户：

```bash
curl -X PUT http://localhost:8080/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username":"zhangsan_updated","email":"zhangsan_new@example.com"}'
```

删除用户：

```bash
curl -X DELETE http://localhost:8080/api/users/1
```

## 配置说明

### 数据库配置

应用支持通过环境变量自定义配置：

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `DB_URL` | `jdbc:mysql://localhost:3306/userdb?useSSL=false&serverTimezone=Asia/Shanghai&allowPublicKeyRetrieval=true` | 数据库连接 URL |
| `DB_USERNAME` | `root` | 数据库用户名 |
| `DB_PASSWORD` | `rootpassword` | 数据库密码 |
| `SERVER_PORT` | `8080` | 应用端口 |

### 默认数据库配置

默认数据库配置（可在 `src/main/resources/application.properties` 中修改）：

- **数据库名称**: userdb
- **主机**: localhost
- **端口**: 3306
- **用户名**: root
- **密码**: rootpassword

## 停止服务

停止 Spring Boot 应用：按 `Ctrl+C`

停止 MySQL 容器：

```bash
cd user-service
docker-compose down
```

如需删除数据卷：

```bash
docker-compose down -v
```

## 项目结构

```
user-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/example/usermanagement/
│   │   │       ├── UserManagementApplication.java  # 主应用类
│   │   │       ├── controller/
│   │   │       │   └── UserController.java         # REST API 控制器
│   │   │       ├── entity/
│   │   │       │   └── User.java                   # 用户实体
│   │   │       ├── repository/
│   │   │       │   └── UserRepository.java         # 数据访问层
│   │   │       └── service/
│   │   │           └── UserService.java            # 业务逻辑层
│   │   └── resources/
│   │       └── application.properties              # 应用配置
│   └── test/
│       └── java/
├── docker-compose.yml                               # Docker Compose 配置
└── pom.xml                                          # Maven 配置
```

## 技术栈

- **Spring Boot 3.2.2**: Web 框架
- **Spring Data JPA**: 数据持久化
- **MySQL 8.0**: 数据库
- **Hibernate**: ORM 框架
- **Bean Validation**: 数据验证
- **Maven**: 构建工具

## 许可证

本项目仅供学习和演示使用。

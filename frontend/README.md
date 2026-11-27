# TikTok账号管理系统 - 前端

基于Vue 3 + Element Plus开发的现代化单页应用。

## 技术栈

- **框架**: Vue 3.5
- **构建工具**: Vite 8.4
- **UI组件库**: Element Plus 2.14
- **状态管理**: Pinia 4.1
- **路由**: Vue Router 5.5
- **HTTP客户端**: Axios 1.21
- **图标**: @element-plus/icons-vue

## 项目结构

```
frontend/
├── public/                # 静态资源
├── src/
│   ├── api/              # API接口定义
│   │   └── auth.js       # 认证相关API
│   ├── assets/           # 资源文件
│   │   └── styles/       # 样式文件
│   │       └── main.css  # 全局样式
│   ├── components/       # 组件
│   │   └── layout/       # 布局组件
│   │       └── MainLayout.vue  # 主布局
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── stores/           # 状态管理
│   │   └── user.js       # 用户状态
│   ├── utils/            # 工具函数
│   │   └── request.js    # Axios封装
│   ├── views/            # 页面视图
│   │   ├── auth/         # 认证页面
│   │   │   ├── Login.vue       # 登录页
│   │   │   └── Register.vue    # 注册页
│   │   ├── home/         # 主页面
│   │   │   ├── Home.vue        # 首页
│   │   │   └── Profile.vue     # 个人信息
│   │   └── NotFound.vue  # 404页面
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── .env                  # 环境变量
├── .env.example         # 环境变量示例
├── index.html           # HTML模板
├── package.json         # 项目配置
├── vite.config.js       # Vite配置
└── README.md
```

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
# .env文件已包含默认配置，如需修改：
cp .env.example .env
# 编辑.env文件
```

### 3. 运行开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 4. 构建生产版本

```bash
npm run build
```

构建产物将生成在 `dist/` 目录

### 5. 预览生产构建

```bash
npm run preview
```

## 主要功能

### 已实现功能

- ✅ 用户登录
- ✅ 用户注册
- ✅ 自动令牌刷新
- ✅ 路由守卫
- ✅ 个人信息展示
- ✅ 响应式布局
- ✅ 统一错误处理

### 待开发功能

- 🚧 素材管理
- 🚧 内容发布
- 🚧 私信管理
- 🚧 账号授权

## 路由配置

| 路径 | 组件 | 说明 | 需要认证 |
|------|------|------|---------|
| `/login` | Login.vue | 登录页 | ❌ |
| `/register` | Register.vue | 注册页 | ❌ |
| `/` | Home.vue | 首页 | ✅ |
| `/profile` | Profile.vue | 个人信息 | ✅ |

## 状态管理

使用Pinia进行状态管理，当前实现了用户状态管理：

```javascript
// 使用示例
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 登录
await userStore.userLogin({ username, password })

// 获取用户信息
const user = userStore.userInfo

// 登出
await userStore.userLogout()
```

## API请求

使用封装的Axios实例进行API请求：

```javascript
// utils/request.js
import request from '@/utils/request'

// 自动添加认证令牌
// 自动处理错误
// 自动刷新过期令牌
```

### 请求拦截器

- 自动在请求头中添加访问令牌
- 格式：`Authorization: Bearer {token}`

### 响应拦截器

- 401：尝试刷新令牌，失败则跳转登录页
- 403：权限不足提示
- 404：资源不存在提示
- 500：服务器错误提示

## 组件开发指南

### 添加新页面

1. 在 `src/views/` 创建Vue组件
2. 在 `src/router/index.js` 添加路由配置
3. 如需认证，设置 `meta: { requiresAuth: true }`

```javascript
{
  path: '/example',
  name: 'Example',
  component: () => import('@/views/Example.vue'),
  meta: { requiresAuth: true, title: '示例页面' }
}
```

### 添加API接口

在 `src/api/` 目录创建对应的API文件：

```javascript
// api/example.js
import request from '@/utils/request'

export const getExample = () => {
  return request({
    url: '/example',
    method: 'get'
  })
}
```

### 添加Store

在 `src/stores/` 目录创建新的store：

```javascript
// stores/example.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useExampleStore = defineStore('example', () => {
  const data = ref(null)
  
  const fetchData = async () => {
    // 实现逻辑
  }
  
  return { data, fetchData }
})
```

## 样式规范

### 全局样式

全局样式定义在 `src/assets/styles/main.css`

### 组件样式

推荐使用scoped样式：

```vue
<style scoped>
.component-class {
  /* 样式 */
}
</style>
```

### Element Plus主题定制

在 `src/main.js` 中配置：

```javascript
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

app.use(ElementPlus, {
  locale: zhCn, // 中文语言包
})
```

## 环境变量

在 `.env` 文件中配置：

```env
# API基础URL
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

在代码中使用：

```javascript
const apiUrl = import.meta.env.VITE_API_BASE_URL
```

## 构建优化

### 代码分割

路由使用懒加载：

```javascript
component: () => import('@/views/Example.vue')
```

### 生产构建

```bash
npm run build
```

优化项：
- 代码压缩
- Tree Shaking
- 资源优化
- 懒加载

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 开发工具

推荐使用以下VS Code扩展：

- Volar (Vue 3支持)
- ESLint
- Prettier
- Vue VSCode Snippets

## 常见问题

### 1. 页面空白

- 检查控制台错误信息
- 确认后端API是否正常
- 检查路由配置

### 2. API请求失败

- 检查网络连接
- 确认API地址配置正确
- 查看Network面板

### 3. 令牌过期

- 系统会自动刷新令牌
- 刷新失败会跳转到登录页
- 检查refresh_token是否有效

### 4. 样式不生效

- 检查CSS文件是否正确导入
- 确认scoped属性使用
- 清除浏览器缓存

## 性能优化建议

1. **路由懒加载**: 使用动态import
2. **组件懒加载**: 大型组件使用异步组件
3. **图片优化**: 使用webp格式，懒加载
4. **缓存策略**: 合理使用localStorage和sessionStorage
5. **代码分割**: 避免单个bundle过大

## 调试技巧

### Vue Devtools

安装Vue Devtools浏览器扩展进行调试

### 控制台日志

开发环境会输出详细的错误信息

### 网络请求

使用浏览器Network面板查看API请求

## 部署

### Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /path/to/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 许可证

MIT License

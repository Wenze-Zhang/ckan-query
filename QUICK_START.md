# 🚀 ckanext-advancedfilters 快速开始指南

## ✅ 当前状态

插件已完全实现并安装成功！

### 已完成的工作

- ✅ 插件目录结构已创建
- ✅ 后端核心逻辑已实现（plugin.py, action.py）
- ✅ 验证器和辅助函数已实现
- ✅ 前端JavaScript逻辑已实现
- ✅ HTML模板和CSS样式已创建
- ✅ 插件已安装到CKAN环境
- ✅ Docker镜像已构建
- ✅ ckan.ini已更新（宿主机）

### 插件文件结构

```
/home/wenze/dockerhub/filter/src/ckanext-advancedfilters/
├── ckanext/
│   ├── __init__.py
│   └── advancedfilters/
│       ├── __init__.py
│       ├── plugin.py                      ✅ 主插件类
│       ├── helpers.py                     ✅ 模板辅助函数
│       ├── logic/
│       │   ├── __init__.py
│       │   ├── action.py                 ✅ 高级搜索API
│       │   └── validators.py             ✅ 验证器
│       ├── assets/
│       │   ├── webassets.yml             ✅ 资源配置
│       │   ├── js/
│       │   │   └── advanced-filters.js   ✅ 前端逻辑
│       │   └── css/
│       │       └── advanced-filters.css  ✅ 样式
│       └── templates/
│           ├── snippets/
│           │   └── advanced_filters_panel.html  ✅ 筛选面板
│           └── datatables/
│               └── datatables_view_with_filters.html  ✅ 扩展视图
├── setup.py                              ✅ 安装配置
├── README.md                             ✅ 文档
└── requirements.txt                      ✅ 依赖

```

## 🔧 最后一步：启用插件

### 方法1：更新环境变量（推荐）

如果使用`.env`文件配置，需要更新：

```bash
# 编辑.env文件
nano /home/wenze/dockerhub/filter/.env

# 找到CKAN__PLUGINS行，添加advancedfilters
# 例如：
CKAN__PLUGINS=image_view text_view datatables_view datastore datapusher envvars advancedfilters

# 保存后重启
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

### 方法2：直接修改ckan.ini（已完成）

宿主机上的`/home/wenze/dockerhub/filter/ckan.ini`已经更新，包含advancedfilters。

但需要确保容器内的配置也更新：

```bash
# 执行以下命令
docker exec -u root filter-ckan-dev-1 bash -c "ckan config-tool /srv/app/ckan.ini 'ckan.plugins = image_view text_view datatables_view video_view audio_view webpage_view resource_proxy datastore datapusher envvars advancedfilters'"

# 重启
docker-compose -f docker-compose.dev.yml restart ckan-dev
```

### 验证插件加载

```bash
# 查看日志中的插件加载信息
docker logs filter-ckan-dev-1 2>&1 | grep -i "Loading the following plugins"

# 应该看到advancedfilters在列表中
```

## 📱 使用插件

### 1. 访问CKAN

打开浏览器访问: **https://localhost:8443**

### 2. 准备测试数据

确保你有一个已推送到DataStore的资源：

1. 进入你的spotify_analysis_dataset数据集
2. 查看资源是否显示"Data API"按钮
3. 如果没有，点击"DataStore"标签确认数据已推送

### 3. 使用高级筛选

1. 在资源页面，点击 **"Table"** 视图
2. 在表格上方应该看到 **"高级筛选条件"** 面板
3. 点击 **"添加筛选条件"**
4. 选择字段、操作符和值
5. 点击 **"应用筛选"**

### 示例筛选条件

**数值筛选：**
- 字段: `popularity`
- 操作符: `大于`
- 值: `50`

**范围筛选：**
- 字段: `energy`
- 操作符: `范围`
- 最小值: `0.3`, 最大值: `0.8`

**文本筛选：**
- 字段: `artist`
- 操作符: `等于`
- 值: `Artist 7`

## 🧪 测试API

```python
import requests
import json

# 获取资源ID
# 从浏览器URL中获取，例如: /dataset/xxx/resource/RESOURCE_ID

url = 'https://localhost:8443/api/3/action/advanced_datastore_search'

data = {
    'resource_id': '你的资源ID',
    'advanced_filters': {
        'popularity': {
            'operator': 'gt',
            'value': 50
        },
        'energy': {
            'operator': 'between',
            'value': [0.3, 0.8]
        }
    },
    'limit': 10
}

response = requests.post(url, json=data)
result = response.json()

print(f"成功: {result.get('success')}")
print(f"记录数: {len(result.get('result', {}).get('records', []))}")
```

## 🐛 故障排除

### 问题：高级筛选面板不显示

**原因可能：**
1. 插件未正确加载
2. 资源未推送到DataStore
3. JavaScript文件未加载

**解决方案：**

```bash
# 1. 确认插件已安装
docker exec filter-ckan-dev-1 pip list | grep advancedfilters

# 2. 确认插件已配置
docker exec filter-ckan-dev-1 grep "ckan.plugins" /srv/app/ckan.ini

# 3. 查看日志
docker logs filter-ckan-dev-1 | tail -50

# 4. 强制重启并清除缓存
docker-compose -f docker-compose.dev.yml down
docker-compose -f docker-compose.dev.yml up -d
```

### 问题：筛选条件不生效

```bash
# 查看浏览器控制台（F12）是否有JavaScript错误

# 查看CKAN日志
docker logs filter-ckan-dev-1 | grep -i error

# 测试API直接调用
curl -X POST "https://localhost:8443/api/3/action/get_resource_field_types" \
  -H "Content-Type: application/json" \
  -d '{"resource_id": "你的资源ID"}'
```

## 📚 支持的操作符完整列表

### 数值字段 (numeric)
- `eq` - 等于
- `ne` - 不等于
- `gt` - 大于
- `gte` - 大于等于
- `lt` - 小于
- `lte` - 小于等于
- `between` - 范围
- `in` - 包含于列表

### 文本字段 (text)
- `eq` - 等于
- `ne` - 不等于
- `like` - 包含
- `ilike` - 包含（不区分大小写）
- `in` - 包含于列表

### 日期字段 (date)
- `eq` - 等于
- `ne` - 不等于
- `gt` - 大于
- `gte` - 大于等于
- `lt` - 小于
- `lte` - 小于等于
- `between` - 范围

## 🎯 下一步优化建议

1. **性能优化**
   - 为常用筛选字段添加数据库索引
   - 启用查询缓存

2. **功能扩展**
   - 添加保存常用筛选条件功能
   - 支持OR逻辑组合
   - 导出筛选结果

3. **UI改进**
   - 添加筛选条件预览
   - 响应式设计优化
   - 国际化支持

## 📞 获取帮助

- 查看详细部署指南: `DEPLOYMENT_GUIDE.md`
- 查看安装说明: `INSTALL_PLUGIN.md`
- 查看插件README: `src/ckanext-advancedfilters/README.md`
- CKAN日志: `docker logs filter-ckan-dev-1`
- 浏览器控制台: F12 > Console

## 🎉 成功标志

当一切正常工作时，你应该看到：

✅ CKAN正常启动，访问 https://localhost:8443 
✅ 插件出现在日志中："Loading plugin: advancedfilters"
✅ Table视图中显示"高级筛选条件"面板
✅ 可以添加筛选条件并看到结果更新
✅ API调用返回正确的筛选结果

---

**恭喜！你已经成功实现了CKAN的高级筛选功能！** 🎊

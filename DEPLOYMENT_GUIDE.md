# ckanext-advancedfilters 部署和测试指南

## 📋 前提条件

- Docker和Docker Compose已安装
- CKAN开发环境已配置
- 有可用的DataStore资源（已上传数据的CSV文件）

## 🚀 部署步骤

### 步骤1：构建Docker镜像

```bash
cd /home/wenze/dockerhub/filter

# 停止现有容器
docker-compose -f docker-compose.dev.yml down

# 构建新镜像
docker-compose -f docker-compose.dev.yml build ckan-dev

# 启动服务
docker-compose -f docker-compose.dev.yml up -d
```

### 步骤2：安装插件

```bash
# 方法A：使用bin目录下的脚本（推荐）
docker exec filter-ckan-dev-1 bash -c "cd /srv/app/src_extensions/ckanext-advancedfilters && pip install -e ."

# 方法B：使用自动安装脚本
# chmod +x bin/install_advancedfilters
# docker cp bin/install_advancedfilters filter-ckan-dev-1:/tmp/
# docker exec filter-ckan-dev-1 bash /tmp/install_advancedfilters
```

### 步骤3：验证插件安装

```bash
# 检查插件是否已安装
docker exec filter-ckan-dev-1 pip list | grep advancedfilters

# 应该看到类似输出：
# ckanext-advancedfilters   1.0.0    /srv/app/src_extensions/ckanext-advancedfilters
```

### 步骤4：重启CKAN

```bash
# 重启ckan-dev容器
docker-compose -f docker-compose.dev.yml restart ckan-dev

# 查看日志确认启动成功
docker logs -f filter-ckan-dev-1

# 看到类似输出表示成功：
# INFO  [ckan.plugins.core] Loading plugin: advancedfilters
```

### 步骤5：验证配置

```bash
# 检查ckan.ini中的插件配置
grep "ckan.plugins" ckan.ini

# 应该包含 advancedfilters
```

## 🧪 功能测试

### 测试1：基础功能测试

1. **访问CKAN**: 打开浏览器访问 https://localhost:8443

2. **创建测试数据集**（如果还没有）:
   - 点击"Datasets" > "Add Dataset"
   - 填写必要信息并创建

3. **上传CSV数据**:
   - 在数据集页面点击"Add Data"
   - 上传你的spotify_analysis_dataset.csv文件
   - 或使用已有的资源

4. **推送到DataStore**:
   - 在资源页面，应该会自动推送到DataStore
   - 或点击"Data API"按钮确认DataStore已启用

5. **查看Table视图**:
   - 点击"Table"视图标签
   - 应该能看到数据表格
   - **在表格上方应该看到"高级筛选条件"面板**

### 测试2：数值筛选测试

使用你的Spotify数据集测试：

1. **大于筛选**:
   - 点击"添加筛选条件"
   - 字段: `popularity`
   - 操作符: `大于`
   - 值: `50`
   - 点击"应用筛选"
   - ✅ 应该只显示popularity > 50的记录

2. **范围筛选**:
   - 添加新筛选条件
   - 字段: `energy`
   - 操作符: `范围`
   - 最小值: `0.3`
   - 最大值: `0.8`
   - 点击"应用筛选"
   - ✅ 应该只显示energy在0.3-0.8之间的记录

3. **多条件组合**:
   - 同时应用多个筛选条件
   - 例如: popularity > 50 AND energy between 0.3-0.8
   - ✅ 应该显示同时满足两个条件的记录

### 测试3：文本筛选测试

1. **等于筛选**:
   - 字段: `artist`
   - 操作符: `等于`
   - 值: `Artist 7`
   - ✅ 应该只显示该艺术家的记录

2. **包含筛选**:
   - 字段: `track_name`
   - 操作符: `包含`
   - 值: `Song`
   - ✅ 应该显示所有包含"Song"的曲目

3. **多值筛选(IN)**:
   - 字段: `album`
   - 操作符: `包含于`
   - 值: `Album 3, Album 5, Album 7`（逗号分隔）
   - ✅ 应该只显示这三个专辑的记录

### 测试4：日期筛选测试

1. **日期范围**:
   - 字段: `release_date`
   - 操作符: `范围`
   - 开始日期: `2010-01-01`
   - 结束日期: `2010-01-10`
   - ✅ 应该显示该日期范围内的记录

2. **日期大于**:
   - 字段: `release_date`
   - 操作符: `大于`
   - 值: `2010-01-05`
   - ✅ 应该显示该日期之后的记录

### 测试5：API测试

使用curl或Python测试API:

```bash
# 使用curl测试
curl -X POST "https://localhost:8443/api/3/action/advanced_datastore_search" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_id": "你的资源ID",
    "advanced_filters": {
      "popularity": {
        "operator": "gt",
        "value": 50
      }
    },
    "limit": 10
  }'
```

```python
# 使用Python测试
import requests
import json

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
    'limit': 20
}

response = requests.post(url, json=data)
result = response.json()

if result['success']:
    print(f"找到 {len(result['result']['records'])} 条记录")
    for record in result['result']['records'][:5]:
        print(f"  - {record}")
else:
    print(f"错误: {result.get('error', {})}")
```

## 🐛 故障排除

### 问题1：插件未加载

**症状**: 启动时日志中没有"Loading plugin: advancedfilters"

**解决方案**:
```bash
# 1. 检查插件是否安装
docker exec filter-ckan-dev-1 pip list | grep advancedfilters

# 2. 检查ckan.ini配置
grep "ckan.plugins" ckan.ini | grep advancedfilters

# 3. 重新安装
docker exec filter-ckan-dev-1 bash -c "cd /srv/app/src_extensions/ckanext-advancedfilters && pip install -e ."

# 4. 重启
docker-compose -f docker-compose.dev.yml restart ckan-dev
```

### 问题2：高级筛选面板不显示

**症状**: Table视图中看不到高级筛选面板

**解决方案**:
```bash
# 1. 检查资源是否已推送到DataStore
# 在资源页面应该看到"Data API"按钮

# 2. 检查浏览器控制台错误
# 按F12打开开发者工具，查看Console标签

# 3. 检查模板是否正确加载
docker exec filter-ckan-dev-1 ls -la /srv/app/src_extensions/ckanext-advancedfilters/ckanext/advancedfilters/templates/

# 4. 清除浏览器缓存并刷新
```

### 问题3：筛选条件不生效

**症状**: 点击"应用筛选"后没有变化

**解决方案**:
```bash
# 1. 检查CKAN日志
docker logs filter-ckan-dev-1 | tail -50

# 2. 检查字段类型
# 确保使用的操作符与字段类型匹配

# 3. 检查JavaScript控制台
# 查看是否有前端错误

# 4. 测试API直接调用
# 使用上面的curl命令测试
```

### 问题4：字段类型识别错误

**症状**: 数值字段显示为文本类型的操作符

**解决方案**:
```bash
# 检查DataStore中的字段类型
curl "https://localhost:8443/api/3/action/datastore_search?resource_id=你的资源ID&limit=0" | jq '.result.fields'

# 如果类型不正确，需要重新推送数据或手动指定类型
```

## 📊 性能优化建议

### 1. 数据库索引

为常用筛选字段创建索引:

```bash
docker exec -it filter-db-1 psql -U ckandbuser -d datastore -c \
  "CREATE INDEX IF NOT EXISTS idx_resource_popularity ON \"你的资源ID\" (popularity);"
```

### 2. 查询限制

在ckan.ini中配置:

```ini
ckan.datastore.search.rows_max = 1000
```

### 3. 缓存配置

启用查询缓存以提高重复查询性能。

## ✅ 验收标准

插件部署成功应满足:

- [x] 插件安装成功，`pip list`可见
- [x] CKAN启动时加载插件，日志无错误
- [x] Table视图中显示"高级筛选条件"面板
- [x] 可以添加和移除筛选条件
- [x] 数值字段支持大于、小于、范围等操作
- [x] 文本字段支持等于、包含、IN操作
- [x] 日期字段支持日期比较和范围
- [x] 筛选结果正确显示
- [x] API调用返回正确结果
- [x] 浏览器控制台无JavaScript错误
- [x] 多条件筛选正常工作
- [x] URL参数保存筛选状态

## 📝 下一步

部署成功后，你可以:

1. 根据实际使用反馈优化UI
2. 添加更多操作符（如NOT、OR逻辑）
3. 支持保存常用筛选条件
4. 添加导出筛选结果功能
5. 集成到其他视图类型（如地图视图）

## 🆘 获取帮助

如遇到问题，请查看:
- CKAN日志: `docker logs filter-ckan-dev-1`
- 浏览器控制台: F12 > Console
- 插件代码: `/home/wenze/dockerhub/filter/src/ckanext-advancedfilters/`

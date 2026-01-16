# 安装和使用 ckanext-advancedfilters 插件

## 快速安装

### 方法1：使用安装脚本（推荐）

```bash
# 运行安装脚本
./bin/install_advancedfilters

# 重启CKAN
./bin/restart
```

### 方法2：手动安装

```bash
# 进入Docker容器
docker exec -it filter-ckan-dev-1 bash

# 切换到插件目录
cd /srv/app/src_extensions/ckanext-advancedfilters

# 安装插件
pip install -e .

# 退出容器
exit

# 重启CKAN
docker-compose -f docker-compose.dev.yml restart ckan-dev
```

## 验证安装

1. 重启后访问: https://localhost:8443
2. 进入任意数据集
3. 选择一个已经推送到DataStore的资源
4. 在Table视图中，应该能看到"高级筛选条件"面板

## 配置说明

插件已自动添加到 `ckan.ini` 的 `ckan.plugins` 配置项中：

```ini
ckan.plugins = ... advancedfilters
```

## 使用方法

### 在Web界面中使用

1. 打开资源的Table视图
2. 在数据表格上方看到"高级筛选条件"面板
3. 点击"添加筛选条件"按钮
4. 选择字段、操作符和值
5. 点击"应用筛选"查看结果

### 支持的操作符

**数值字段:**
- 等于 (=)
- 不等于 (!=)
- 大于 (>)
- 大于等于 (>=)
- 小于 (<)
- 小于等于 (<=)
- 范围 (BETWEEN)
- 包含于 (IN)

**文本字段:**
- 等于 (=)
- 不等于 (!=)
- 包含 (LIKE)
- 包含(不区分大小写) (ILIKE)
- 包含于 (IN)

**日期字段:**
- 等于 (=)
- 不等于 (!=)
- 大于 (>)
- 大于等于 (>=)
- 小于 (<)
- 小于等于 (<=)
- 范围 (BETWEEN)

### 通过API使用

```python
import requests
import json

url = 'https://localhost:8443/api/3/action/advanced_datastore_search'

data = {
    'resource_id': 'your-resource-id',
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
print(json.dumps(result, indent=2))
```

## 故障排除

### 插件未显示

1. 检查插件是否已安装:
   ```bash
   docker exec filter-ckan-dev-1 pip list | grep advancedfilters
   ```

2. 检查ckan.ini中是否已添加插件:
   ```bash
   grep "ckan.plugins" /home/wenze/dockerhub/filter/ckan.ini
   ```

3. 查看CKAN日志:
   ```bash
   docker logs filter-ckan-dev-1
   ```

### 筛选条件不生效

1. 确保资源已推送到DataStore
2. 检查浏览器控制台是否有JavaScript错误
3. 查看CKAN日志中的错误信息

### 字段类型识别错误

插件会自动识别字段类型（数值、文本、日期），如果识别不正确:
1. 检查DataStore中的字段类型定义
2. 可能需要在上传数据时指定正确的字段类型

## 卸载

如需卸载插件:

```bash
# 从ckan.ini中移除advancedfilters
# 编辑 ckan.ini，从 ckan.plugins 行中删除 advancedfilters

# 卸载插件
docker exec filter-ckan-dev-1 pip uninstall ckanext-advancedfilters -y

# 重启CKAN
./bin/restart
```

## 获取帮助

如有问题，请查看:
- 插件README: /src/ckanext-advancedfilters/README.md
- CKAN日志: docker logs filter-ckan-dev-1
- 浏览器控制台: F12 -> Console标签

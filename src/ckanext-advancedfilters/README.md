# ckanext-advancedfilters

高级筛选插件 - 为CKAN DataStore视图添加高级筛选操作符

## 功能特性

- 支持多种比较操作符：等于、不等于、大于、小于、大于等于、小于等于
- 支持范围筛选（BETWEEN）
- 支持模糊匹配（LIKE/ILIKE）
- 支持多值筛选（IN）
- 根据字段类型智能显示可用操作符
- 与现有CKAN视图无缝集成

## 安装

1. 进入CKAN虚拟环境
2. 安装插件：`pip install -e .`
3. 在ckan.ini中添加插件：`ckan.plugins = ... advancedfilters`
4. 重启CKAN

## 使用方法

在资源视图中，选择字段、操作符和值来创建筛选条件。

## API

### advanced_datastore_search

扩展的DataStore搜索API，支持高级筛选：

```python
import ckan.plugins.toolkit as toolkit

result = toolkit.get_action('advanced_datastore_search')(
    {},
    {
        'resource_id': 'your-resource-id',
        'advanced_filters': {
            'age': {
                'operator': 'gt',
                'value': 25
            },
            'score': {
                'operator': 'between',
                'value': [60, 100]
            }
        }
    }
)
```

## 许可证

AGPL-3.0

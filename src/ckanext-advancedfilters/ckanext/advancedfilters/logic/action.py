# encoding: utf-8
from __future__ import annotations
from typing import Any, Dict, List, Tuple
import logging
from ckan.common import _
import ckan.plugins.toolkit as toolkit
from ckan.types import Context
import json

log = logging.getLogger(__name__)


def advanced_datastore_search(context: Context, data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    扩展的DataStore搜索，支持高级筛选操作符
    
    :param resource_id: 资源ID
    :param advanced_filters: 高级筛选条件
    :param filters: 标准筛选条件（向后兼容）
    :param q: 搜索查询
    :param limit: 限制结果数量
    :param offset: 偏移量
    :param sort: 排序字段
    
    :returns: 搜索结果
    """
    toolkit.check_access('datastore_search', context, data_dict)
    
    # 获取高级筛选条件
    advanced_filters = data_dict.get('advanced_filters', {})
    
    if not advanced_filters:
        # 如果没有高级筛选，使用标准datastore_search
        return toolkit.get_action('datastore_search')(context, data_dict)
    
    # 解析并验证高级筛选条件
    try:
        if isinstance(advanced_filters, str):
            advanced_filters = json.loads(advanced_filters)
        
        # 验证每个筛选条件
        validated_filters = _validate_and_convert_filters(
            advanced_filters, 
            data_dict.get('resource_id')
        )
        
        # 构建SQL WHERE条件
        where_clause, where_params = _build_advanced_where_clause(validated_filters)
        
        # 构建完整SQL查询
        sql_query = _build_sql_query(
            resource_id=data_dict.get('resource_id'),
            where_clause=where_clause,
            where_params=where_params,
            sort=data_dict.get('sort'),
            limit=data_dict.get('limit', 100),
            offset=data_dict.get('offset', 0),
        )
        
        log.info(f'Advanced filter SQL: {sql_query}')
        
        # 执行SQL查询
        result = toolkit.get_action('datastore_search_sql')(
            context, 
            {'sql': sql_query}
        )
        
        return result
        
    except Exception as e:
        log.error(f'Advanced filter error: {str(e)}')
        raise toolkit.ValidationError({
            'advanced_filters': [f'筛选条件错误: {str(e)}']
        })


def get_resource_field_types(context: Context, data_dict: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """
    获取资源的字段类型信息
    
    :param resource_id: 资源ID
    :returns: 字段名到类型的映射
    """
    toolkit.check_access('datastore_search', context, data_dict)
    
    resource_id = toolkit.get_or_bust(data_dict, 'resource_id')
    
    # 使用datastore_search获取字段信息
    try:
        result = toolkit.get_action('datastore_search')(
            context,
            {'resource_id': resource_id, 'limit': 0}
        )
        
        field_types = {}
        for field in result.get('fields', []):
            field_id = field.get('id')
            field_type = field.get('type', 'text')
            
            # 将PostgreSQL类型映射到我们的类型分类
            classified_type = _classify_field_type(field_type)
            field_types[field_id] = {
                'type': classified_type,
                'pg_type': field_type,
            }
        
        return field_types
        
    except Exception as e:
        log.error(f'Error getting field types: {str(e)}')
        return {}


def _classify_field_type(pg_type: str) -> str:
    """
    将PostgreSQL类型分类为简化类型
    
    :param pg_type: PostgreSQL数据类型
    :returns: 分类后的类型：'numeric', 'text', 'date'
    """
    numeric_types = ['int', 'integer', 'bigint', 'smallint', 'numeric', 'decimal', 
                     'float', 'real', 'double', 'money']
    date_types = ['date', 'timestamp', 'time', 'interval']
    
    pg_type_lower = pg_type.lower()
    
    for num_type in numeric_types:
        if num_type in pg_type_lower:
            return 'numeric'
    
    for date_type in date_types:
        if date_type in pg_type_lower:
            return 'date'
    
    return 'text'


def _validate_and_convert_filters(
    filters: Dict[str, Any], 
    resource_id: str
) -> Dict[str, Dict[str, Any]]:
    """
    验证并转换筛选条件
    
    :param filters: 原始筛选条件
    :param resource_id: 资源ID
    :returns: 验证后的筛选条件
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    
    validated = {}
    
    # 获取字段类型
    field_types = get_resource_field_types({}, {'resource_id': resource_id})
    
    for field_name, filter_config in filters.items():
        if not isinstance(filter_config, dict):
            raise toolkit.ValidationError(
                f'字段 {field_name} 的筛选条件格式错误'
            )
        
        operator = filter_config.get('operator', 'eq')
        value = filter_config.get('value')
        
        # 验证操作符
        if operator not in FILTER_OPERATORS:
            raise toolkit.ValidationError(
                f'不支持的操作符: {operator}'
            )
        
        # 验证字段类型
        field_info = field_types.get(field_name, {})
        field_type = field_info.get('type', 'text')
        
        if field_type not in FILTER_OPERATORS[operator]['types']:
            raise toolkit.ValidationError(
                f'操作符 {operator} 不支持字段类型 {field_type}'
            )
        
        # 转换值类型
        converted_value = _convert_value(value, field_type, operator)
        
        validated[field_name] = {
            'operator': operator,
            'value': converted_value,
            'type': field_type,
        }
    
    return validated


def _convert_value(value: Any, field_type: str, operator: str) -> Any:
    """
    根据字段类型转换值
    
    :param value: 原始值
    :param field_type: 字段类型
    :param operator: 操作符
    :returns: 转换后的值
    """
    try:
        if operator == 'between':
            if not isinstance(value, list) or len(value) != 2:
                raise ValueError('BETWEEN操作符需要两个值')
            
            if field_type == 'numeric':
                return [float(value[0]), float(value[1])]
            elif field_type == 'date':
                return [str(value[0]), str(value[1])]
            return value
        
        elif operator == 'in':
            if not isinstance(value, list):
                value = [value]
            
            if field_type == 'numeric':
                return [float(v) for v in value]
            return [str(v) for v in value]
        
        else:
            if field_type == 'numeric':
                return float(value)
            elif field_type == 'date':
                return str(value)
            return str(value)
            
    except (ValueError, TypeError) as e:
        raise toolkit.ValidationError(f'值转换错误: {str(e)}')


def _build_advanced_where_clause(
    filters: Dict[str, Dict[str, Any]]
) -> Tuple[str, Dict[str, Any]]:
    """
    构建SQL WHERE子句
    
    :param filters: 验证后的筛选条件
    :returns: (WHERE子句字符串, 参数字典)
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    
    where_clauses = []
    params = {}
    param_counter = 0
    
    for field_name, filter_config in filters.items():
        operator = filter_config['operator']
        value = filter_config['value']
        sql_operator = FILTER_OPERATORS[operator]['sql']
        
        # 使用双引号包裹字段名以处理特殊字符和大小写
        safe_field = f'"{field_name}"'
        
        if operator == 'between':
            param_min = f'param_{param_counter}'
            param_max = f'param_{param_counter + 1}'
            where_clauses.append(
                f'{safe_field} BETWEEN {value[0]} AND {value[1]}'
            )
            param_counter += 2
            
        elif operator == 'in':
            # 构建IN子句
            value_strs = [f"'{v}'" if isinstance(v, str) else str(v) for v in value]
            where_clauses.append(
                f'{safe_field} IN ({", ".join(value_strs)})'
            )
            
        elif operator in ['like', 'ilike']:
            escaped_value = str(value).replace("'", "''")
            where_clauses.append(f'{safe_field} {sql_operator} \'%{escaped_value}%\'')
            
        else:
            # 标准比较操作符
            if isinstance(value, str):
                where_clauses.append(f'{safe_field} {sql_operator} \'{value}\'')
            else:
                where_clauses.append(f'{safe_field} {sql_operator} {value}')
    
    where_clause = ' AND '.join(where_clauses)
    return where_clause, params


def _build_sql_query(
    resource_id: str,
    where_clause: str,
    where_params: Dict[str, Any],
    sort: str = None,
    limit: int = 100,
    offset: int = 0,
) -> str:
    """
    构建完整的SQL查询
    
    :param resource_id: 资源ID
    :param where_clause: WHERE子句
    :param where_params: WHERE参数
    :param sort: 排序字段
    :param limit: 限制数量
    :param offset: 偏移量
    :returns: SQL查询字符串
    """
    # 基础查询
    sql = f'SELECT * FROM "{resource_id}"'
    
    # 添加WHERE子句
    if where_clause:
        sql += f' WHERE {where_clause}'
    
    # 添加排序
    if sort:
        # 解析排序字符串，如 "field asc, field2 desc"
        sort_clauses = []
        for sort_item in sort.split(','):
            sort_item = sort_item.strip()
            parts = sort_item.split()
            if len(parts) >= 1:
                field = f'"{parts[0]}"'
                direction = parts[1].upper() if len(parts) > 1 else 'ASC'
                sort_clauses.append(f'{field} {direction}')
        
        if sort_clauses:
            sql += f' ORDER BY {", ".join(sort_clauses)}'
    
    # 添加分页
    sql += f' LIMIT {limit} OFFSET {offset}'
    
    return sql

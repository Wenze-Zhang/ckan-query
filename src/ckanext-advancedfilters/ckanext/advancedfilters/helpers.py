# encoding: utf-8
from __future__ import annotations
from typing import Any, Dict, List
import logging
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


def get_operators() -> Dict[str, Dict[str, Any]]:
    """
    获取所有可用的筛选操作符
    
    :returns: 操作符字典
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    return FILTER_OPERATORS


def get_operators_for_type(field_type: str) -> List[Dict[str, str]]:
    """
    根据字段类型获取可用的操作符列表
    
    :param field_type: 字段类型 ('numeric', 'text', 'date')
    :returns: 操作符列表
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    
    operators = []
    for op_key, op_info in FILTER_OPERATORS.items():
        if field_type in op_info['types']:
            operators.append({
                'key': op_key,
                'label': op_info['label'],
                'sql': op_info['sql'],
            })
    
    return operators


def get_field_types(resource_id: str) -> Dict[str, Dict[str, str]]:
    """
    获取资源的字段类型信息
    
    :param resource_id: 资源ID
    :returns: 字段类型字典
    """
    try:
        return toolkit.get_action('get_resource_field_types')(
            {}, {'resource_id': resource_id}
        )
    except Exception as e:
        log.error(f'Error getting field types for resource {resource_id}: {str(e)}')
        return {}


def format_filter_display(filters: Dict[str, Any]) -> str:
    """
    格式化筛选条件用于显示
    
    :param filters: 筛选条件字典
    :returns: 格式化的显示字符串
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    
    if not filters:
        return '无筛选条件'
    
    display_parts = []
    for field_name, filter_config in filters.items():
        operator = filter_config.get('operator', 'eq')
        value = filter_config.get('value')
        
        op_label = FILTER_OPERATORS.get(operator, {}).get('label', operator)
        
        if operator == 'between' and isinstance(value, list):
            display_parts.append(
                f'{field_name} {op_label} {value[0]} 和 {value[1]}'
            )
        elif operator == 'in' and isinstance(value, list):
            display_parts.append(
                f'{field_name} {op_label} [{", ".join(map(str, value))}]'
            )
        else:
            display_parts.append(f'{field_name} {op_label} {value}')
    
    return '；'.join(display_parts)

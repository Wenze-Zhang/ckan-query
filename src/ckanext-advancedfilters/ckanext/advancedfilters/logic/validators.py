# encoding: utf-8
from __future__ import annotations
import json
import logging
from typing import Any
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)


def advanced_filter_validator(value: Any, context: Any) -> dict:
    """
    验证高级筛选条件的完整性
    
    :param value: 筛选条件值
    :returns: 验证后的字典
    """
    if not value:
        return {}
    
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise toolkit.Invalid('筛选条件必须是有效的JSON格式')
    
    if not isinstance(value, dict):
        raise toolkit.Invalid('筛选条件必须是字典类型')
    
    # 验证每个筛选条件的结构
    for field_name, filter_config in value.items():
        if not isinstance(filter_config, dict):
            raise toolkit.Invalid(
                f'字段 {field_name} 的筛选条件必须是字典类型'
            )
        
        if 'operator' not in filter_config:
            raise toolkit.Invalid(
                f'字段 {field_name} 的筛选条件缺少 operator'
            )
        
        if 'value' not in filter_config:
            raise toolkit.Invalid(
                f'字段 {field_name} 的筛选条件缺少 value'
            )
        
        # 验证操作符
        operator_validator(filter_config['operator'], context)
    
    return value


def operator_validator(value: str, context: Any) -> str:
    """
    验证操作符是否有效
    
    :param value: 操作符值
    :returns: 验证后的操作符
    """
    from ckanext.advancedfilters.plugin import FILTER_OPERATORS
    
    if value not in FILTER_OPERATORS:
        valid_operators = ', '.join(FILTER_OPERATORS.keys())
        raise toolkit.Invalid(
            f'无效的操作符: {value}. 有效的操作符: {valid_operators}'
        )
    
    return value


def filter_value_validator(value: Any, context: Any) -> Any:
    """
    验证筛选值
    
    :param value: 筛选值
    :returns: 验证后的值
    """
    # 值可以是单个值、列表或None
    if value is None:
        raise toolkit.Invalid('筛选值不能为空')
    
    return value

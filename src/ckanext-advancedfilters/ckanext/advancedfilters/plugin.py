# encoding: utf-8
from __future__ import annotations
from typing import Any, Dict
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.types import Context

# 支持的操作符定义
FILTER_OPERATORS = {
    'eq': {'label': '等于', 'sql': '=', 'types': ['text', 'numeric', 'date']},
    'ne': {'label': '不等于', 'sql': '!=', 'types': ['text', 'numeric', 'date']},
    'gt': {'label': '大于', 'sql': '>', 'types': ['numeric', 'date']},
    'gte': {'label': '大于等于', 'sql': '>=', 'types': ['numeric', 'date']},
    'lt': {'label': '小于', 'sql': '<', 'types': ['numeric', 'date']},
    'lte': {'label': '小于等于', 'sql': '<=', 'types': ['numeric', 'date']},
    'between': {'label': '范围', 'sql': 'BETWEEN', 'types': ['numeric', 'date']},
    'in': {'label': '包含于', 'sql': 'IN', 'types': ['text', 'numeric']},
    'like': {'label': '包含', 'sql': 'LIKE', 'types': ['text']},
    'ilike': {'label': '包含(不区分大小写)', 'sql': 'ILIKE', 'types': ['text']},
}


class AdvancedFiltersPlugin(plugins.SingletonPlugin):
    """
    高级筛选插件 - 为CKAN DataStore视图添加高级筛选操作符
    """
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IValidators)

    # IConfigurer
    def update_config(self, config_):
        """更新CKAN配置"""
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('assets', 'ckanext-advancedfilters')

    # ITemplateHelpers
    def get_helpers(self):
        """注册模板辅助函数"""
        from ckanext.advancedfilters import helpers
        return {
            'advancedfilters_get_operators': helpers.get_operators,
            'advancedfilters_get_operators_for_type': helpers.get_operators_for_type,
            'advancedfilters_get_field_types': helpers.get_field_types,
            'advancedfilters_format_filter_display': helpers.format_filter_display,
        }

    # IActions
    def get_actions(self):
        """注册新的API动作"""
        from ckanext.advancedfilters.logic import action
        return {
            'advanced_datastore_search': action.advanced_datastore_search,
            'get_resource_field_types': action.get_resource_field_types,
        }

    # IValidators
    def get_validators(self):
        """注册验证器"""
        from ckanext.advancedfilters.logic import validators
        return {
            'advanced_filter_validator': validators.advanced_filter_validator,
            'operator_validator': validators.operator_validator,
            'filter_value_validator': validators.filter_value_validator,
        }

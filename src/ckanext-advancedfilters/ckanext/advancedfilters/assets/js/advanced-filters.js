/* 
 * Advanced Filters JavaScript Module
 * 为CKAN DataStore视图添加高级筛选功能
 */

this.ckan.module('advanced-filters', function ($) {
  return {
    options: {
      resourceId: null,
      fieldTypes: {},
      operators: {}
    },

    initialize: function () {
      $.proxyAll(this, /_on/);
      
      this.resourceId = this.options.resourceId;
      this.fieldTypes = this.options.fieldTypes || {};
      this.operators = this.options.operators || {};
      this.filters = [];
      
      // 绑定事件
      this.el.on('click', '.add-filter-btn', this._onAddFilter);
      this.el.on('click', '.remove-filter-btn', this._onRemoveFilter);
      this.el.on('change', '.filter-field-select', this._onFieldChange);
      this.el.on('change', '.filter-operator-select', this._onOperatorChange);
      this.el.on('click', '.apply-filters-btn', this._onApplyFilters);
      this.el.on('click', '.clear-filters-btn', this._onClearFilters);
      
      // 初始化现有筛选条件
      this._loadExistingFilters();
    },

    /* 添加新的筛选条件行 */
    _onAddFilter: function (event) {
      event.preventDefault();
      
      var filterRow = this._createFilterRow();
      this.$('.filters-container').append(filterRow);
      
      // 初始化第一个字段的操作符选项
      var $row = this.$('.filter-row:last');
      var fieldName = $row.find('.filter-field-select').val();
      if (fieldName) {
        this._updateOperatorOptions($row, fieldName);
      }
    },

    /* 移除筛选条件行 */
    _onRemoveFilter: function (event) {
      event.preventDefault();
      $(event.target).closest('.filter-row').remove();
    },

    /* 字段选择变化时更新操作符选项 */
    _onFieldChange: function (event) {
      var $row = $(event.target).closest('.filter-row');
      var fieldName = $(event.target).val();
      
      if (fieldName) {
        this._updateOperatorOptions($row, fieldName);
        this._updateValueInput($row, fieldName, 'eq');
      }
    },

    /* 操作符变化时更新值输入框 */
    _onOperatorChange: function (event) {
      var $row = $(event.target).closest('.filter-row');
      var fieldName = $row.find('.filter-field-select').val();
      var operator = $(event.target).val();
      
      if (fieldName && operator) {
        this._updateValueInput($row, fieldName, operator);
      }
    },

    /* 应用筛选条件 */
    _onApplyFilters: function (event) {
      event.preventDefault();
      
      var filters = this._collectFilters();
      
      if (Object.keys(filters).length === 0) {
        this._showMessage('请至少添加一个筛选条件', 'warning');
        return;
      }
      
      // 验证筛选条件
      var validation = this._validateFilters(filters);
      if (!validation.valid) {
        this._showMessage('筛选条件错误: ' + validation.message, 'error');
        return;
      }
      
      // 将筛选条件编码到URL
      var filtersJson = JSON.stringify(filters);
      var currentUrl = window.location.href.split('?')[0];
      var newUrl = currentUrl + '?advanced_filters=' + encodeURIComponent(filtersJson);
      
      // 重新加载页面应用筛选
      window.location.href = newUrl;
    },

    /* 清除所有筛选条件 */
    _onClearFilters: function (event) {
      event.preventDefault();
      
      this.$('.filters-container').empty();
      
      // 移除URL中的筛选参数
      var currentUrl = window.location.href.split('?')[0];
      window.location.href = currentUrl;
    },

    /* 创建筛选条件行HTML */
    _createFilterRow: function () {
      var fields = Object.keys(this.fieldTypes);
      
      var html = '<div class="filter-row form-inline" style="margin-bottom: 10px;">' +
                 '  <select class="filter-field-select form-control" style="width: 200px; margin-right: 10px;">' +
                 '    <option value="">选择字段...</option>';
      
      fields.forEach(function(fieldName) {
        html += '    <option value="' + fieldName + '">' + fieldName + '</option>';
      });
      
      html += '  </select>' +
              '  <select class="filter-operator-select form-control" style="width: 150px; margin-right: 10px;">' +
              '    <option value="">选择操作符...</option>' +
              '  </select>' +
              '  <span class="filter-value-container" style="display: inline-block; margin-right: 10px;"></span>' +
              '  <button class="remove-filter-btn btn btn-danger btn-sm">' +
              '    <i class="fa fa-times"></i> 移除' +
              '  </button>' +
              '</div>';
      
      return $(html);
    },

    /* 更新操作符下拉选项 */
    _updateOperatorOptions: function ($row, fieldName) {
      var fieldInfo = this.fieldTypes[fieldName];
      if (!fieldInfo) return;
      
      var fieldType = fieldInfo.type;
      var $operatorSelect = $row.find('.filter-operator-select');
      
      // 清空现有选项
      $operatorSelect.empty();
      $operatorSelect.append('<option value="">选择操作符...</option>');
      
      // 根据字段类型添加可用操作符
      for (var opKey in this.operators) {
        var opInfo = this.operators[opKey];
        if (opInfo.types.indexOf(fieldType) !== -1) {
          $operatorSelect.append(
            '<option value="' + opKey + '">' + opInfo.label + '</option>'
          );
        }
      }
      
      // 默认选择第一个操作符
      $operatorSelect.val('eq');
      this._updateValueInput($row, fieldName, 'eq');
    },

    /* 更新值输入框 */
    _updateValueInput: function ($row, fieldName, operator) {
      var fieldInfo = this.fieldTypes[fieldName];
      if (!fieldInfo) return;
      
      var fieldType = fieldInfo.type;
      var $container = $row.find('.filter-value-container');
      
      $container.empty();
      
      // 根据操作符类型创建不同的输入框
      if (operator === 'between') {
        // 范围输入：两个输入框
        var inputType = fieldType === 'date' ? 'date' : 'number';
        var step = fieldType === 'numeric' ? '0.01' : '1';
        
        $container.append(
          '<input type="' + inputType + '" class="filter-value-min form-control" ' +
          'style="width: 120px; display: inline-block;" ' +
          'step="' + step + '" placeholder="最小值"> ' +
          '<span style="margin: 0 5px;">至</span> ' +
          '<input type="' + inputType + '" class="filter-value-max form-control" ' +
          'style="width: 120px; display: inline-block;" ' +
          'step="' + step + '" placeholder="最大值">'
        );
      } else if (operator === 'in') {
        // 多值输入
        $container.append(
          '<input type="text" class="filter-value form-control" ' +
          'style="width: 300px;" ' +
          'placeholder="输入多个值，用逗号分隔">'
        );
      } else {
        // 单值输入
        var inputType = 'text';
        var step = '1';
        
        if (fieldType === 'numeric') {
          inputType = 'number';
          step = '0.01';
        } else if (fieldType === 'date') {
          inputType = 'date';
        }
        
        $container.append(
          '<input type="' + inputType + '" class="filter-value form-control" ' +
          'style="width: 250px;" ' +
          'step="' + step + '" placeholder="输入值">'
        );
      }
    },

    /* 收集所有筛选条件 */
    _collectFilters: function () {
      var filters = {};
      var self = this;
      
      this.$('.filter-row').each(function () {
        var $row = $(this);
        var fieldName = $row.find('.filter-field-select').val();
        var operator = $row.find('.filter-operator-select').val();
        
        if (!fieldName || !operator) return;
        
        var value;
        
        if (operator === 'between') {
          var minVal = $row.find('.filter-value-min').val();
          var maxVal = $row.find('.filter-value-max').val();
          if (!minVal || !maxVal) return;
          value = [minVal, maxVal];
        } else if (operator === 'in') {
          var inputVal = $row.find('.filter-value').val();
          if (!inputVal) return;
          value = inputVal.split(',').map(function(v) { return v.trim(); });
        } else {
          value = $row.find('.filter-value').val();
          if (!value) return;
        }
        
        filters[fieldName] = {
          operator: operator,
          value: value
        };
      });
      
      return filters;
    },

    /* 验证筛选条件 */
    _validateFilters: function (filters) {
      for (var fieldName in filters) {
        var filter = filters[fieldName];
        var fieldInfo = this.fieldTypes[fieldName];
        
        if (!fieldInfo) {
          return {valid: false, message: '字段 ' + fieldName + ' 不存在'};
        }
        
        var operator = filter.operator;
        var value = filter.value;
        
        // 验证操作符
        if (!this.operators[operator]) {
          return {valid: false, message: '无效的操作符: ' + operator};
        }
        
        // 验证值
        if (operator === 'between') {
          if (!Array.isArray(value) || value.length !== 2) {
            return {valid: false, message: '范围筛选需要两个值'};
          }
        } else if (operator === 'in') {
          if (!Array.isArray(value) || value.length === 0) {
            return {valid: false, message: '多值筛选至少需要一个值'};
          }
        }
      }
      
      return {valid: true};
    },

    /* 从URL加载现有筛选条件 */
    _loadExistingFilters: function () {
      var urlParams = new URLSearchParams(window.location.search);
      var filtersJson = urlParams.get('advanced_filters');
      
      if (!filtersJson) return;
      
      try {
        var filters = JSON.parse(decodeURIComponent(filtersJson));
        
        for (var fieldName in filters) {
          var filter = filters[fieldName];
          this._addExistingFilterRow(fieldName, filter.operator, filter.value);
        }
      } catch (e) {
        console.error('加载筛选条件失败:', e);
      }
    },

    /* 添加现有的筛选条件行 */
    _addExistingFilterRow: function (fieldName, operator, value) {
      var $row = this._createFilterRow();
      this.$('.filters-container').append($row);
      
      // 设置字段
      $row.find('.filter-field-select').val(fieldName);
      this._updateOperatorOptions($row, fieldName);
      
      // 设置操作符
      $row.find('.filter-operator-select').val(operator);
      this._updateValueInput($row, fieldName, operator);
      
      // 设置值
      if (operator === 'between' && Array.isArray(value)) {
        $row.find('.filter-value-min').val(value[0]);
        $row.find('.filter-value-max').val(value[1]);
      } else if (operator === 'in' && Array.isArray(value)) {
        $row.find('.filter-value').val(value.join(', '));
      } else {
        $row.find('.filter-value').val(value);
      }
    },

    /* 显示消息 */
    _showMessage: function (message, type) {
      var alertClass = 'alert-info';
      if (type === 'error') alertClass = 'alert-danger';
      else if (type === 'warning') alertClass = 'alert-warning';
      else if (type === 'success') alertClass = 'alert-success';
      
      var $alert = $(
        '<div class="alert ' + alertClass + ' alert-dismissible fade in" role="alert">' +
        '  <button type="button" class="close" data-dismiss="alert">&times;</button>' +
        '  ' + message +
        '</div>'
      );
      
      this.el.prepend($alert);
      
      setTimeout(function() {
        $alert.alert('close');
      }, 5000);
    }
  };
});

#!/bin/bash
# 一键启用 ckanext-advancedfilters 插件（生产环境）

echo "================================================"
echo "  🚀 启用 ckanext-advancedfilters 插件"
echo "================================================"
echo ""
echo "环境信息："
echo "  - CKAN地址: https://localhost:8443/"
echo "  - 部署模式: 生产环境"
echo "  - 容器名称: filter-ckan-1"
echo ""

# 检查容器是否运行
echo "✓ 检查容器状态..."
if ! docker ps | grep -q filter-ckan-1; then
    echo "❌ 错误: filter-ckan-1 容器未运行"
    echo "   请先启动服务: docker-compose up -d"
    exit 1
fi
echo "  ✅ 容器运行正常"
echo ""

# 检查插件是否已安装
echo "✓ 检查插件安装..."
if ! docker exec filter-ckan-1 pip list | grep -q advancedfilters; then
    echo "❌ 错误: 插件未安装"
    echo "   正在安装插件..."
    docker exec -u root filter-ckan-1 bash -c \
      "cd /srv/app/src_extensions/ckanext-advancedfilters && pip install -e ."
    if [ $? -ne 0 ]; then
        echo "❌ 安装失败"
        exit 1
    fi
fi
echo "  ✅ 插件已安装"
echo ""

# 配置插件
echo "✓ 配置插件到 ckan.ini..."
docker exec -u root filter-ckan-1 bash -c \
  "ckan config-tool /srv/app/ckan.ini \
  'ckan.plugins = image_view text_view datatables_view video_view audio_view webpage_view resource_proxy datastore datapusher envvars advancedfilters'"

if [ $? -eq 0 ]; then
    echo "  ✅ 配置成功"
else
    echo "  ❌ 配置失败"
    exit 1
fi
echo ""

# 重启CKAN服务
echo "✓ 重启CKAN服务..."
docker-compose restart ckan

if [ $? -eq 0 ]; then
    echo "  ✅ 重启成功"
else
    echo "  ❌ 重启失败"
    exit 1
fi
echo ""

# 等待服务启动
echo "✓ 等待服务完全启动（15秒）..."
for i in {15..1}; do
    echo -ne "  ⏳ 倒计时: $i 秒\r"
    sleep 1
done
echo "  ✅ 启动完成                    "
echo ""

# 验证插件加载
echo "✓ 验证插件加载状态..."
if docker logs filter-ckan-1 2>&1 | tail -50 | grep -q "advancedfilters"; then
    echo "  ✅ 插件加载成功！"
else
    echo "  ⚠️  警告: 未在日志中发现插件加载信息"
    echo "     请手动检查: docker logs filter-ckan-1"
fi
echo ""

echo "================================================"
echo "  ✅ 插件启用完成！"
echo "================================================"
echo ""
echo "📱 下一步操作："
echo ""
echo "1. 访问CKAN:"
echo "   👉 https://localhost:8443/"
echo ""
echo "2. 打开数据集:"
echo "   - 进入 spotify_analysis_dataset"
echo "   - 点击资源名称"
echo ""
echo "3. 使用高级筛选:"
echo "   - 点击 'Table' 视图"
echo "   - 在表格上方找到 '高级筛选条件' 面板"
echo "   - 点击 '添加筛选条件' 开始使用"
echo ""
echo "📚 查看完整文档:"
echo "   cat 安装使用指南.md"
echo ""
echo "🐛 遇到问题？"
echo "   docker logs filter-ckan-1 | tail -50"
echo ""
echo "================================================"
echo "  🎉 祝使用愉快！"
echo "================================================"

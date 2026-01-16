#!/bin/bash
# 启用ckanext-advancedfilters插件的脚本

echo "========================================="
echo "  启用 ckanext-advancedfilters 插件"
echo "========================================="
echo ""

echo "步骤1: 在容器中配置插件..."
docker exec -u root filter-ckan-dev-1 bash -c "ckan config-tool /srv/app/ckan.ini 'ckan.plugins = image_view text_view datatables_view video_view audio_view webpage_view resource_proxy datastore datapusher envvars advancedfilters'"

if [ $? -eq 0 ]; then
    echo "✅ 配置成功！"
else
    echo "❌ 配置失败，请检查容器是否运行"
    exit 1
fi

echo ""
echo "步骤2: 重启CKAN服务..."
docker-compose -f docker-compose.dev.yml restart ckan-dev

if [ $? -eq 0 ]; then
    echo "✅ 重启成功！"
else
    echo "❌ 重启失败"
    exit 1
fi

echo ""
echo "步骤3: 等待服务启动（15秒）..."
sleep 15

echo ""
echo "步骤4: 验证插件加载..."
docker logs filter-ckan-dev-1 2>&1 | tail -20 | grep -i "Loading the following plugins"

echo ""
echo "========================================="
echo "  ✅ 插件启用完成！"
echo "========================================="
echo ""
echo "下一步："
echo "1. 访问: https://localhost:8443"
echo "2. 打开任意已推送到DataStore的资源"
echo "3. 点击 'Table' 视图"
echo "4. 在表格上方应该能看到 '高级筛选条件' 面板"
echo ""
echo "查看详细文档:"
echo "- 快速开始: cat QUICK_START.md"
echo "- 完整指南: cat DEPLOYMENT_GUIDE.md"
echo ""

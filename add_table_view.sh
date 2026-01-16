#!/bin/bash
#
# 为CKAN资源添加DataTables视图
# 使用方法: ./add_table_view.sh <resource_id>
#

RESOURCE_ID="$1"

if [ -z "$RESOURCE_ID" ]; then
    echo "用法: $0 <resource_id>"
    echo "示例: $0 abc123def-456-789-ghi"
    exit 1
fi

echo "为资源 $RESOURCE_ID 创建 Table 视图..."

docker exec filter-ckan-1 bash -c "
ckan -c /srv/app/ckan.ini user token add admin add_view_token 2>/dev/null | grep -oP 'eyJ[^\"]*' > /tmp/token.txt
TOKEN=\$(cat /tmp/token.txt)

curl -X POST 'http://localhost:5000/api/3/action/resource_view_create' \\
  -H 'Authorization: '\$TOKEN \\
  -H 'Content-Type: application/json' \\
  -d '{
    \"resource_id\": \"$RESOURCE_ID\",
    \"title\": \"Table\",
    \"view_type\": \"datatables_view\",
    \"filterable\": true,
    \"responsive\": false,
    \"ellipsis_length\": 100
  }' | python3 -m json.tool

rm /tmp/token.txt
"

echo "完成！"

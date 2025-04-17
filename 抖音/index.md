# 抖音订单接入

## 接入流程

1. 申请开通抖音小店
2. 获取开放平台权限
3. 创建应用并获取相关参数
4. 进行应用开发对接

## 应用开发

### 1. 获取 access_token

请求地址：`https://open.douyin.com/oauth/client_token/`

请求方式：GET

参数说明：
- client_key：应用唯一标识
- client_secret：应用唯一密钥
- grant_type：固定值 client_credential

响应示例：
```json
{
    "data": {
        "access_token": "access_token",
        "expires_in": 7200
    },
    "message": "success"
}
```
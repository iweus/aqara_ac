# [https://github.com/iweus/aqara_ac](https://github.com/iweus/aqara_ac)
Aqara空调红外控制插件

该插件允许您通过Aqara开放平台控制红外控制的空调。请按照以下步骤进行安装和配置。

## 1. 安装准备
1.1 注册Aqara开放平台账号，并创建一个项目并通过审核（https://developer.aqara.com/ ↗）。
1.2 在Aqara智能家居App中绑定红外控制的空调。
1.3 在Aqara开放平台中，进入项目管理 > 设备管理，搜索出空调设备的did（可以通过账户ID或者Aqara账号进行搜索）。
1.4 在Aqara开放平台中，进入项目管理 > 授权管理，进行Aqara账号授权，以获取accessToken和refreshToken。
1.5 在Aqara开放平台中，进入项目管理 > 概况> Appid&密钥（点击底部展开找到中国服务），以获取appid、appkey和keyid
1.5 将 `aqara_ac` 文件夹放入 `custom_components` 目录中。
1.6 在 `/config/tmp/aqara_token.json` 文件中，添加accessToken和refreshToken信息
```json
{"accessToken": "xxxxx", "refreshToken": "xxxxxxxx"}
```

## 2. homeassistant配置方法

在 configuration.yaml 文件中添加以下配置：

```yaml
climate:
  - platform: aqara_ac
    did: ir.xxxxxxxxxxxxxx
    accesstoken: xxxxxxx
    refreshtoken: xxxxxxxxxxxx
    appkey: xxxxxxxxxxxxx
    keyid: K.xxxxxxxxxxxxxx
    appid: xxxxxxxx
```

请注意，Aqara开放平台请求需要accessToken并且会过期，因此插件会每6天刷新一次token。刷新后的token将被存储在 /config/tmp/aqara_token.json 文件中。插件将优先从该文件中获取token，如果找不到则会从Home Assistant的配置文件中获取token。因此，如果您重启了Home Assistant，则需要同时配置Home Assistant中的token和 /config/tmp/aqara_token.json 文件中的token。
# [https://github.com/iweus/aqara_ac](https://github.com/iweus/aqara_ac)
aqara空调红外插件
## 1. 安装准备
把 `aqara_ac` 放入 `custom_components`；
新建json文件 `/config/tmp/aqara_token.json`

## 2. 配置方法

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
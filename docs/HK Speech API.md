# 港会通语音转录服务API

## 域名

dev环境: `openspeech.hkgai.net`

## API接口

### 1. 语音识别

#### 接口相关信息

- **请求方法**: `POST`
- **请求路径**: `/api/v1/speech_recognize`
- **请求头**:

| 参数名        | 类型   | 必填 | 说明            |
| ------------- | ------ | ---- | --------------- |
| Authorization | string | 是   | 权限认证api key |

- **请求参数**:

| 参数名        | 类型                | 必填 | 说明                                                         |
| ------------- | ------------------- | ---- | ------------------------------------------------------------ |
| request_id    | string              | 是   | 用于提交和查询任务的任务ID, 推荐传入随机生成的UUID, 例如 `23ae89ba-7d50-4c24-fvd7-acfols349qls` |
| resource.type | Audio Resource Type | 是   | 资源类型 (1:URL 2:BYTES)                                     |
| resource.url  | string              | 否   | 音频URL (type为1时必填)                                      |
| resource.data | bytes               | 否   | 音频数据 (type为2时必填)                                     |

- **响应参数**:

| 参数名      | 类型       | 说明           |
| ----------- | ---------- | -------------- |
| code        | int        | 请求状态码     |
| msg         | string     | 请求状态码信息 |
| result      | string     | 识别结果       |
| status_desc | string     | 状态描述       |
| status_code | StatusCode | 业务状态码     |
| request_id  | string     | 请求ID         |

- **枚举类型说明**

  **AudioResourceType**

| 枚举值                  | 说明     |
| ----------------------- | -------- |
| `RESOURCE_TYPE_UNKNOWN` | 未知类型 |
| `RESOURCE_TYPE_URL`     | URL类型  |
| `RESOURCE_TYPE_BYTES`   | 字节类型 |

- **状态码说明**

  **Code**

| 状态码 | 说明         |
| ------ | ------------ |
| 200    | 成功         |
| 400    | 参数错误     |
| 401    | 认证错误     |
| 500    | 服务内部错误 |

#### 请求体示例

1. **url**

```json
{
  "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
  "resource": {
    "type": 1,
    "url": "" // 音频文件地址
  }
}
```

1. **Bytes**

```json
{
  "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
  "resource": {
    "type": 2,
    "data": "" // 字节流
  }
}
```

#### 返回体示例

```json
{
  "code": 200,
  "data": {
    "msg": "SUCCESS",
    "result": "You're listening to a podcast from the brookings institution, we are con convenienting for what has become an annual eventa, joint brookings taian, mediaconference on the economic developments in chinawe've, sometimes added the united states to this year, we are focusing especially on the.",
    "status_desc": "STATUS_OK",
    "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls"
  }
}
```
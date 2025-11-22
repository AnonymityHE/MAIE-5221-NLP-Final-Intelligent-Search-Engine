# HKGAI语音开放平台服务

## 1.1 会议转录（区分说话人）

### 域名

dev环境：openspeech.hkgai.net

### API接口

#### 会议转录接口相关信息

- 请求方法：POST
- 请求路径：/api/v1/transcription
- 请求头：

| 参数名        | 类型   | 必填 | 说明            |
| ------------- | ------ | ---- | --------------- |
| Authorization | string | 是   | 权限认证api key |

Key: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY

- 请求参数：

| 参数名        | 类型              | 必填 | 说明                                                         |
| ------------- | ----------------- | ---- | ------------------------------------------------------------ |
| request_id    | string            | 是   | 用于提交和查询任务的任务ID，推荐传入随机生成的UUID，例如23ae89ba-7d50-4c24-fvd7-acfols349qls |
| resource.type | AudioResourceType | 是   | 资源类型（1:URL 2:BYTES）                                    |
| resource.url  | string            | 否   | 音频URL（type为1时必填）                                     |
| resource.data | bytes             | 否   | 音频数据（type为2时必填）                                    |

- 响应参数：

| 参数名      | 类型       | 说明       |
| ----------- | ---------- | ---------- |
| code        | int        | 状态码     |
| msg         | string     | 状态码描述 |
|             |            |            |
| messages    | []object   | 识别结果   |
| time_range  | object     | 时间区间   |
| - start     | int        | 开始       |
| - end       | int        | 结束       |
| speaker     | object     | 说话人     |
| -name       | string     | 说话人标识 |
| content     | string     | 识别内容   |
| language    | string     | 语言       |
| status_desc | string     | 状态描述   |
| status_code | StatusCode | 业务状态码 |
| request_id  | string     | 请求ID     |

- 枚举类型说明

AudioResourceType

| 枚举值                | 说明     |
| --------------------- | -------- |
| RESOURCE_TYPE_UNKNOWN | 未知类型 |
| RESOURCE_TYPE_URL     | URL类型  |
| RESOURCE_TYPE_BYTES   | 字节类型 |

- 状态码说明

Code

| 状态码 | 说明         |
| ------ | ------------ |
| 200    | 成功         |
| 400    | 参数错误     |
| 401    | 认证错误     |
| 500    | 服务内部错误 |

#### 请求体示例

1. url

```JSON
{
    "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
    "resource":{
        "type": 1,
        "url": ""//音频文件地址
    }
}
```

2. Bytes

```JSON
{
    "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
    "resource":{
        "type": 2,
        "data": //字节流
    }
}
```

#### 返回体示例

```JSON
{
    "code": 200,
    "msg": "SUCCESS",
    "data": {
        "messages": [
            {
                "time_range": {
                    "start": 739,
                    "end": 96842
                },
                "speaker": {
                    "name": "Speaker-1"
                },
                "content": "You're listening to a podcast from the brookings institution we are con convenienting for what has becoming an annual event, a joint brookings taian media conference on the economic developments in China, we've sometimes added the united states to this year, we are focusing as especially on the Chinese side, but looking at the coming five years or so with two panels this afternoon, the 1st is on new dynamics in China state society relations before I introduce the panelists, I want to introduce the head of seian media hu shuli, who is enormously well known in China and abroad, has gotten a list of awards, most of which say one of the top 100 most important thinkers in the world or one of the top ten thinkers in asia, and so for so surely delighted to have you here, yes, we will be moderating our 2nd panel, but I just wanted to introduce her at the start of our program for our 1st panel, we have three speakers I will introduce all of them now, so I don't keep interrupting as each one finishes when all three are done will then have a substantial amount of time for qa from the audience when we turn to qa from the audience. We'll have roving mics, so I'll ask you to please.",
                "language": "en"
            },
            {
                "time_range": {
                    "start": 96842,
                    "end": 188891
                },
                "speaker": {
                    "name": "Speaker-1"
                },
                "content": "Identify yourself by name and affiliation, and then feel free to directed question to a particular speaker or to the panel as a whole our 1st speaker is ambassador joe wazhong ambassador joe's last foreign ministry posting was as ambassador to the united states, he now is the head of the bo al forum in China, he is also vice president of the China us people's friendship association, he had a long and distinguished foreign ministry career, diplomatic career at times serving as ambassador to australia and early in his career as ambassador to barbados and to antiu and barbuda I've never heard of bar forgive my ignorance, but anyway, but anyway, really a pleasure to have you here, mr ambassador 2nd speaker will be vikram neru, who is now a senior associated in the asia program at thenegi endowment, but he spent 30 years at the world bank, where he had a variety of positions, his research overall has focused on economic, political and strategic security issues involving asia, and then our 3rd speaker is professor of finance at the yale school of management, professor chunjer wo, he spent a good part of his career, focused on overall financial theory and global financial issues, but in the last decade.",
                "language": "en"
            }
        ],
        "status_desc": "STATUS_OK",
        "request_id": "sadwdadwdadsdawdawsda"
    }
}
```

# 1.2 语音识别（无说话人）

### 域名

dev环境：openspeech.hkgai.net

### API接口

#### 接口相关信息

- 请求方法：POST
- 请求路径：/api/v1/speech_recognize
- 请求头：

| 参数名        | 类型   | 必填 | 说明            |
| ------------- | ------ | ---- | --------------- |
| Authorization | string | 是   | 权限认证api key |

Key: TzmW5eWvGWphlubmavEIRtG5U6OwS9wF02AwtEHWx0stLvtqZWpz5LK2q7lRQhDY

- 请求参数：

| 参数名        | 类型              | 必填 | 说明                                                         |
| ------------- | ----------------- | ---- | ------------------------------------------------------------ |
| request_id    | string            | 是   | 用于提交和查询任务的任务ID，推荐传入随机生成的UUID，例如23ae89ba-7d50-4c24-fvd7-acfols349qls |
| resource.type | AudioResourceType | 是   | 资源类型（1:URL 2:BYTES）                                    |
| resource.url  | string            | 否   | 音频URL（type为1时必填）                                     |
| resource.data | bytes             | 否   | 音频数据（type为2时必填）                                    |

- 响应参数：

| 参数名      | 类型       | 说明           |
| ----------- | ---------- | -------------- |
| code        | int        | 请求状态码     |
| msg         | string     | 请求状态码信息 |
|             |            |                |
| result      | string     | 识别结果       |
| status_desc | string     | 状态描述       |
| status_code | StatusCode | 业务状态码     |
| request_id  | string     | 请求ID         |

- 枚举类型说明

AudioResourceType

| 枚举值                | 说明     |
| --------------------- | -------- |
| RESOURCE_TYPE_UNKNOWN | 未知类型 |
| RESOURCE_TYPE_URL     | URL类型  |
| RESOURCE_TYPE_BYTES   | 字节类型 |

- 状态码说明

Code

| 状态码 | 说明         |
| ------ | ------------ |
| 200    | 成功         |
| 400    | 参数错误     |
| 401    | 认证错误     |
| 500    | 服务内部错误 |

#### 请求体示例

1. url

```JSON
{
    "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
    "resource":{
        "type": 1,
        "url": ""//音频文件地址
    }
}
```

2. Bytes

```JSON
{
    "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls",
    "resource":{
        "type": 2,
        "data": //字节流
    }
}
```

#### 返回体示例

```JSON
{
    "code": 200,
    "msg": "SUCCESS",
    "data": {
        "result": "You're listening to a podcast from the brookings institution, we are con convenienting for what has become an annual eventa, joint brookings taian, mediaconference on the economic developments in chinawe've, sometimes added the united states to this year, we are focusing especially on the.",
        "status_desc": "STATUS_OK",
        "request_id": "23ae89ba-7d50-4c24-fvd7-acfols349qls"
    }
}
```

## 3 语音合成

### API 接口说明

### 请求地址

`GET`` ``https://openspeech.hkgai.net/server_proxy/api/tts`

- 请求头：

| 参数名        | 类型   | 必填 | 说明            |
| ------------- | ------ | ---- | --------------- |
| Authorization | string | 是   | 权限认证api key |

### 请求参数

| 参数名   | 类型   | 描述                                                         |
| -------- | ------ | ------------------------------------------------------------ |
| text     | string | 待合成的文本                                                 |
| language | string | 语言，可选：mandarin（普通话）、cantonese（粤语），默认 mandarin |
| voice    | string | 音色，可选：female（女声）、male（男声），默认female         |
| type     | string | 可选:file（文件输出）, stream（pcm raw音频流），默认file     |

### 响应

- 返回pcm raw音频流，或直接输出到文件
- 状态码说明

Code

| 状态码 | 说明         |
| ------ | ------------ |
| 200    | 成功         |
| 400    | 参数错误     |
| 401    | 认证错误     |
| 500    | 服务内部错误 |

### 命令行示例（以输出到文件为例）

```SQL
curl 'https://openspeech.hkgai.net/server_proxy/api/tts?text=%E4%B8%80%E4%BA%8C%E4%B8%89%E4%B8%89%E4%BA%8C%E4%B8%80&voice=female&language=cantonese' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJ0MSIsInJvbGUiOiJ1c2VyIiwicGF0aHMiOlsiL3NlcnZlcl9wcm94eS9hcGkvZ2VuIiwiL3NlcnZlcl9wcm94eS9hcGkvdHRzIl0sImF0dHJzIjp7InR0c19hbGwiOmZhbHNlLCJ0dHNfdm9pY2VzIjpbInpoX2ZlbWFsZV8xIiwiZW5fbWFsZV8yIl19LCJzdWIiOiJ1c2VyLTEiLCJleHAiOjEwNDAzMjY1NDYxLCJpYXQiOjE3NjMzNTE4NjF9.gQ9aBrApIUZljjqp-vRJnpCkFAoykgNaz-f_QHhcDOEotCilkQn1aahvSCixCn3ISvj6D2q7sbx0lj4JppApHCm7d8iEPAEkd4_wZENLTvYSjTr-wCmdu5RcH_KuxyPG_vWzkN6OT8gkbQLNbdV8Oa2tQqE5gWfVTzgv5rOW6bCqm2mjYVIkcm2-eKdlMz5-EcZPRflL_FqghseiC9S7jn_gn6k_tvQpVJxSq6A5OftZ-BVszdR1Rf8bIyZd082AxaCu1LyQG9TOcwcjbwQHqe7A--OASa54DmUZiG-AsxaGCIO4Jgcf5Ek5Qvh6EuS2XFW1B5LXS9gcTKJ7CW5fdg" > demo.wav
```
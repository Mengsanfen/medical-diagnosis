# coding: utf-8
import _thread as thread
import base64
import hashlib
import hmac
import json
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from wsgiref.handlers import format_date_time
import websocket


class Ws_Param(object):
    # 初始化
    def __init__(self, APIKey, APISecret, gpt_url):
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(gpt_url).netloc
        self.path = urlparse(gpt_url).path
        self.gpt_url = gpt_url

    # 生成url
    def create_url(self):
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.gpt_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, close_status_code, close_msg):
    print("### closed ###")


# 收到websocket连接建立的处理
def on_open(ws):
    thread.start_new_thread(run, (ws,))


def run(ws, *args):
    data = json.dumps(parameter)
    # 发送请求参数
    ws.send(data)


# 收到websocket消息的处理
def on_message(ws, message):
    data = json.loads(message)
    print(data)
    code = data['header']['code']
    choices = data["payload"]["choices"]
    status = choices["status"]
    if code != 0:
        print(f'请求错误: {code}, {data}')
        ws.close()
    if status == 2:
        print("#### 关闭会话")
        ws.close()

    # webSocket 请求的参数


parameter = {
    "payload": {
        "message": {
            "text": [
                {
                    "role": "system",
                    "content": "一个专业全科医生，具有循证医学背景。用温暖而专业的语气进行问诊。,症状矩阵分析（每次提出1-3个问题）\n部位：\"具体是身体哪个部位的不适？\"\n性质：\"是钝痛/刺痛/烧灼痛？\"\n强度：\"如果用0-10分评分，10分是最严重，您打几分？\n时态：\"症状是持续存在还是间歇发作？\"\n缓解/加重因素：\"什么情况下会好转或加重？\"\n伴随症状：\"是否伴有发烧/头晕/呕吐等其他症状？\"\n\n\n分层建议\n根据症状复杂度提供：\nA级（急诊）→ 上述危险信号\nB级（24小时内就诊）→ 如严重腹泻伴脱水、剧烈头痛等\nC级（门诊就诊）→ 持续3天以上的非危重症状\nD级（观察护理）→ 轻微擦伤、普通感冒等\n\n沟通收尾\n\"基于现有信息，建议您：[分级建议]。请特别注意：[关键观察指标]。如果出现[恶化指征]请立即就医。需要我帮您整理症状清单方便与医生沟通吗？\"\n\n【注意事项】\n严禁提供药物剂量建议\n禁止猜测具体疾病名称\n涉及儿童/孕妇/老人自动提升建议等级\n慢性病症状需追问用药史\n心理问题需提供心理援助热线\n\n(每次对话最后自动附加)\n\"温馨提示：本咨询结果基于有限信息，实际诊疗需结合体检和实验室检查。请以正规医疗机构诊断为准。\""
                },
                {
                    "role": "user",
                    "content": "请在此处输入你的问题!!!"
                }
            ]
        }
    },
    "parameter": {
        "chat": {
            "max_tokens": 4096,
            "domain": "4.0Ultra",
            "top_k": 4,
            "temperature": 0.5
        }
    },
    "header": {
        "app_id": "2cd7b888"
    }
}
parameter["parameter"]["chat"]["show_ref_label"] = True


def main(api_secret, api_key, gpt_url):
    wsParam = Ws_Param(api_key, api_secret, gpt_url)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close, on_open=on_open)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})


if __name__ == "__main__":
    main(
        api_secret='ZmE2YmFiY2ViNzEzMjc5YzllN2EzZTU4',
        api_key='9e059a9d07231fbefc85fd16da02d999',
        gpt_url='wss://spark-api.xf-yun.com/v4.0/chat',  # 例如 wss://spark-api.xf-yun.com/v4.0/chat
    )

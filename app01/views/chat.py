# chat.py
from django.shortcuts import render
import json
import ssl
import threading
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
import websocket
import logging
from urllib.parse import urlparse
from datetime import datetime
from time import mktime
from wsgiref.handlers import format_date_time
import hashlib
import hmac
import base64
from urllib.parse import urlencode
import queue

def ai_chat(request):
    """AI问诊聊天界面"""
    return render(request, 'ai_chat.html')


class WsParam:
    """WebSocket连接参数生成类（来自官方示例改造）"""

    def __init__(self, appid, api_key, api_secret, spark_url):
        self.appid = appid
        self.api_key = api_key
        self.api_secret = api_secret

        # 使用标准库解析URL
        parsed_url = urlparse(spark_url)
        self.host = parsed_url.hostname
        self.path = parsed_url.path
        self.spark_url = spark_url

    def create_url(self):
        """生成带鉴权的URL"""
        # 生成RFC1123格式时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接签名串
        signature_origin = f"host: {self.host}\ndate: {date}\nGET {self.path} HTTP/1.1"

        # 进行hmac-sha256加密
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()

        # Base64编码
        signature_sha_base64 = base64.b64encode(signature_sha).decode('utf-8')

        # 构造Authorization
        authorization_origin = (
            f'api_key="{self.api_key}", algorithm="hmac-sha256", '
            f'headers="host date request-line", signature="{signature_sha_base64}"'
        )
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode('utf-8')

        # 生成最终URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }

        # 调试输出
        print(f"签名原始字符串:\n{signature_origin}")
        print(f"生成签名: {signature_sha_base64}")
        print(f"完整URL: {self.spark_url}?{urlencode(params)}")

        return f"{self.spark_url}?{urlencode(params)}"


def gen_params(appid, query, domain="4.0Ultra"):
    """生成请求参数"""
    return {
        "header": {
            "app_id": appid,
            "uid": "user123"  # 可替换为实际用户ID
        },
        "parameter": {
            "chat": {
                "domain": domain,
                "temperature": 0.5,
                "max_tokens": 4096
            }
        },
        "payload": {
            "message": {
                "text": [{"role": "user", "content": query}]
            }
        }
    }

logger = logging.getLogger(__name__)

@csrf_exempt
def ai_process(request):
    """流式API处理视图"""
    if request.method == 'POST':
        try:
            # 配置检查
            config = getattr(settings, 'SPARK_CONFIG', {})
            APPID = config.get('APPID')
            API_KEY = config.get('API_KEY')
            API_SECRET = config.get('API_SECRET')

            if not all([APPID, API_KEY, API_SECRET]):
                logger.error("讯飞配置缺失: APPID=%s, API_KEY=%s***", APPID, API_KEY[:3])
                return JsonResponse({"error": "服务配置错误"}, status=500)

            # 解析请求
            data = json.loads(request.body)
            user_input = data.get('message', '')
            if not user_input:
                return JsonResponse({"error": "输入内容不能为空"}, status=400)

            # 生成WebSocket URL
            SPARK_URL = "wss://spark-api.xf-yun.com/v4.0/chat"
            ws_param = WsParam(APPID, API_KEY, API_SECRET, SPARK_URL)
            ws_url = ws_param.create_url()
            logger.debug("生成WebSocket URL: %s", ws_url)

            # 打印调试信息
            logger.debug(f"APPID: {APPID}")
            logger.debug(f"API_KEY: {API_KEY[:3]}***")
            logger.debug(f"API_SECRET: {API_SECRET[:3]}***")

            # 创建响应生成器
            def response_generator():
                data_queue = queue.Queue()  # 线程安全队列
                event = threading.Event()

                # WebSocket回调函数改造
                def on_message(ws, message):
                    try:
                        data = json.loads(message)
                        if data["header"]["code"] != 0:
                            error = f"[{data['header']['code']}] {data['header']['message']}"
                            data_queue.put({'error': error})
                            event.set()
                        else:
                            content = data["payload"]["choices"]["text"][0]["content"]
                            status = data["payload"]["choices"]["status"]
                            data_queue.put({'content': content, 'status': status})
                            if status == 2:
                                event.set()
                    except Exception as e:
                        data_queue.put({'error': str(e)})
                        event.set()

                def on_error(ws, error):
                    data_queue.put({'error': f"连接错误: {str(error)}"})
                    event.set()

                def on_close(ws, *args):
                    if not event.is_set():
                        event.set()

                def on_open(ws):
                    ws.send(json.dumps(gen_params(APPID, user_input)))

                # 创建WebSocket连接
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_open=on_open,
                    on_message=lambda ws, msg: [chunk for chunk in on_message(ws, msg)],
                    on_error=on_error,
                    on_close=on_close
                )

                # 在后台线程运行WebSocket
                ws_thread = threading.Thread(
                    target=ws.run_forever,
                    kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}}
                )
                ws_thread.start()

                # 等待事件完成或超时（30秒）
                event.wait(timeout=30)

                if not event.is_set():
                    yield "data: {\"error\": \"请求超时\"}\n\n"

                ws.close()
                ws_thread.join()

            return StreamingHttpResponse(
                response_generator(),
                content_type='text/event-stream'
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "无效的JSON格式"}, status=400)
        except Exception as e:
            logger.exception("处理请求时发生异常:")  # 打印完整堆栈
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "仅支持POST请求"}, status=405)
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
        self.host = urlparse(spark_url).netloc
        self.path = urlparse(spark_url).path
        self.spark_url = spark_url

    def create_url(self):
        """生成带鉴权的URL"""
        # 生成RFC1123格式时间戳
        now = datetime.now()  # 使用UTC时间
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
        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        # 构造Authorization
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 生成最终URL
        params = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }

        # 拼接鉴权参数，生成url
        url = self.spark_url + '?' + urlencode(params)

        # 调试输出
        print(f"签名原始字符串:\n{signature_origin}")
        print(f"生成签名: {signature_sha_base64}")
        print(f"完整URL: " + url)

        return url


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
                "top_k": 4,
                "max_tokens": 4096,
                "show_ref_label": True
            }
        },
        "payload": {
            "message": {
                "text": [
                    {
                        "role": "system",
                        "content": "一个专业全科医生，具有循证医学背景。用温暖而专业的语气进行问诊。,症状矩阵分析（每次提出1-3个问题）\n部位：\"具体是身体哪个部位的不适？\"\n性质：\"是钝痛/刺痛/烧灼痛？\"\n强度：\"如果用0-10分评分，10分是最严重，您打几分？\n时态：\"症状是持续存在还是间歇发作？\"\n缓解/加重因素：\"什么情况下会好转或加重？\"\n伴随症状：\"是否伴有发烧/头晕/呕吐等其他症状？\"\n\n\n分层建议\n根据症状复杂度提供：\nA级（急诊）→ 上述危险信号\nB级（24小时内就诊）→ 如严重腹泻伴脱水、剧烈头痛等\nC级（门诊就诊）→ 持续3天以上的非危重症状\nD级（观察护理）→ 轻微擦伤、普通感冒等\n\n沟通收尾\n\"基于现有信息，建议您：[分级建议]。请特别注意：[关键观察指标]。如果出现[恶化指征]请立即就医。需要我帮您整理症状清单方便与医生沟通吗？\"\n\n【注意事项】\n严禁提供药物剂量建议\n禁止猜测具体疾病名称\n涉及儿童/孕妇/老人自动提升建议等级\n慢性病症状需追问用药史\n心理问题需提供心理援助热线\n\n(每次对话最后自动附加)\n\"温馨提示：本咨询结果基于有限信息，实际诊疗需结合体检和实验室检查。请以正规医疗机构诊断为准。\""
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ]
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

            SPARK_URL = config.get('SPARK_URL')
            domain = config.get('DOMAIN')

            if not all([APPID, API_KEY, API_SECRET]):
                logger.error("讯飞配置缺失: APPID=%s, API_KEY=%s***", APPID, API_KEY[:3])
                return JsonResponse({"error": "服务配置错误"}, status=500)

            # 解析请求
            data = json.loads(request.body)
            user_input = data.get('message', '')
            if not user_input:
                return JsonResponse({"error": "输入内容不能为空"}, status=400)

            # 生成WebSocket URL
            ws_param = WsParam(APPID, API_KEY, API_SECRET, SPARK_URL)
            websocket.enableTrace(False)
            ws_url = ws_param.create_url()
            logger.debug("生成WebSocket URL: %s", ws_url)

            # 打印调试信息
            logger.debug(f"APPID: {APPID}")
            logger.debug(f"API_KEY: {API_KEY[:3]}***")
            logger.debug(f"API_SECRET: {API_SECRET[:3]}***")

            # 创建响应生成器
            def response_generator():
                """流式响应生成器（完整修复版）"""
                data_queue = queue.Queue()  # 线程安全数据队列
                event = threading.Event()  # 控制事件
                ws_thread = None  # WebSocket线程引用

                # WebSocket回调函数 ======================================
                def on_message(ws, message):
                    print(message)
                    try:
                        data = json.loads(message)
                        header_code = data["header"]["code"]

                        # 错误处理
                        if header_code != 0:
                            error_msg = f"[{header_code}] {data['header']['message']}"
                            data_queue.put({'type': 'error', 'content': error_msg})
                            event.set()
                            return

                        # 正常处理
                        choices = data["payload"]["choices"]
                        content = choices["text"][0]["content"]
                        status = choices["status"]

                        data_queue.put({
                            'type': 'data',
                            'content': content,
                            'status': status
                        })

                        # 最终消息标记
                        if status == 2:
                            data_queue.put({'type': 'done'})
                            event.set()

                    except Exception as e:
                        data_queue.put({'type': 'error', 'content': str(e)})
                        event.set()

                # 收到websocket错误的处理
                def on_error(ws, error):
                    data_queue.put({'type': 'error', 'content': f"WebSocket错误: {str(error)}"})
                    event.set()
                    print("### error:", error)

                # 收到websocket关闭的处理
                def on_close(ws, close_status_code, close_msg):
                    if not event.is_set():
                        data_queue.put({'type': 'error', 'content': "连接意外关闭"})
                        event.set()
                        print("### closed ###")

                # 收到websocket连接建立的处理
                def on_open(ws):
                    try:
                        logger.debug("正在发送请求参数...")
                        ws.send(json.dumps(gen_params(APPID, user_input)))
                    except Exception as e:
                        data_queue.put({'type': 'error', 'content': str(e)})
                        event.set()

                # WebSocket连接初始化 ====================================
                ws = websocket.WebSocketApp(
                    ws_url,
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )

                # 启动WebSocket线程 =====================================
                ws_thread = threading.Thread(
                    target=ws.run_forever,
                    kwargs={'sslopt': {"cert_reqs": ssl.CERT_NONE}}
                )
                ws_thread.start()

                # 流式响应主循环 ========================================
                try:
                    buffer = ""  # 用于合并分段内容
                    while True:
                        # 处理超时
                        if not event.wait(timeout=30):
                            data_queue.put({'type': 'error', 'content': '请求超时'})
                            break

                        # 处理队列数据
                        try:
                            item = data_queue.get_nowait()

                            if item['type'] == 'error':
                                yield f"data: {json.dumps({'error': item['content']})}\n\n"
                                break

                            elif item['type'] == 'data':
                                # 合并分段内容
                                buffer += item['content']

                                # 如果有换行符则分次发送
                                while '\n' in buffer:
                                    line, buffer = buffer.split('\n', 1)
                                    yield f"data: {json.dumps({'response': line})}\n\n"

                                # 发送当前缓冲区内容
                                if buffer:
                                    yield f"data: {json.dumps({'response': buffer})}\n\n"
                                    buffer = ""

                            elif item['type'] == 'done':
                                # 发送最终缓冲内容
                                if buffer:
                                    yield f"data: {json.dumps({'response': buffer})}\n\n"
                                break

                        except queue.Empty:
                            if not ws_thread.is_alive():
                                break
                            continue

                finally:
                    # 清理资源
                    ws.close()
                    ws_thread.join(timeout=1)

                    # 最终超时检查
                    if buffer:
                        yield f"data: {json.dumps({'response': buffer})}\n\n"

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
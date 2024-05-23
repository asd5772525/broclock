import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
import tempfile  
import logging  
from urllib.parse import urlparse  
import os  
from datetime import datetime  

URL = "https://xiaoapi.cn/API/zs_zdbs.php"        #https://xiaoapi.cn/?action=doc&id=57





@plugins.register(name="broclock",
                  desc="报时",
                  version="1.0",
                  author="Haru",
                  desire_priority=100)




class broclock(Plugin):

    content = None
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"发送【报时】获得语音报时"
        return help_text


    def on_handle_context(self, e_context: EventContext):
        # 只处理文本消息
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()
        
        if self.content.startswith("报时") :
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            result = self.broclock()
            if result != None:
                reply.type = ReplyType.FILE
                reply.content = result
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等Haru修复"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS



    def broclock(self): 
        if self.content.startswith("报时"):
            url = URL
            now = datetime.now()  
            hour = now.hour  
        params = {"h": hour}   

        try:
            # 主接口
            response = requests.get(url=url, params=params)
            if isinstance(response.json(), dict) :
                json_data = response.json()
                if json_data['mp3']:
                    url = json_data['mp3']
                    logger.info(json_data)

                    response = requests.get(url)  
                    # 确保请求成功  
                    if response.status_code == 200:  
                        parsed_url = urlparse(url)  
                        file_name, file_ext = os.path.splitext(os.path.basename(parsed_url.path))      
                        with tempfile.NamedTemporaryFile(  
                            prefix=json_data['msg'] + ".", suffix=file_ext, delete=False) as f:  
                            f.write(response.content)  
                            temp_file_path = f.name  
                        logger.info(f"文件已保存到临时文件: {temp_file_path}")  

                        return temp_file_path
                    else:  
                        logger.info(f"请求失败，状态码: {response.status_code}")
                    return

                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
                
        logger.error("所有接口都挂了,无法获取")
        return None



import os
import subprocess
from astrbot.api.event import filter, EventContext
from astrbot.api.star import Context, Star, register
from astrbot.api.model import MessageChain

@register("sega_manager", "YourName", "SEGA 数据管理插件", "1.0.0")
class SegaPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.base_path = "/root/SDGB"

    # 功能 1: /sega get - 读取文件内容
    @filter.command("sega")
    async def sega_handler(self, event: EventContext):
        # 这里处理子命令，也可以直接用 @filter.command("sega get")
        pass

    @filter.command("sega")
    async def sega_get(self, event: EventContext, sub_cmd: str):
        if sub_cmd == "get":
            file_path = os.path.join(self.base_path, "get.txt")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                yield event.plain_result(content)
            else:
                yield event.plain_result("错误：未找到 get.txt 文件")

        # 功能 2: /sega update - 运行脚本并读取版本
        elif sub_cmd == "update":
            python_exe = "/root/SDGB/sdgb/bin/python3"
            script_path = os.path.join(self.base_path, "download.py")
            version_path = os.path.join(self.base_path, "option/last_version.txt")

            try:
                # 运行更新脚本
                subprocess.run([python_exe, script_path], check=True)
                
                # 读取最新版本号
                with open(version_path, "r", encoding="utf-8") as f:
                    version = f.read().strip()
                
                yield event.plain_result(f"更新指示书成功，目前最新opt为{version}")
            except Exception as e:
                yield event.plain_result(f"更新失败: {str(e)}")

        # 功能 3: /sega download - 发送 ZIP 文件
        elif sub_cmd == "download":
            temp_dir = os.path.join(self.base_path, "temp")
            if not os.path.exists(temp_dir):
                yield event.plain_result("错误：temp 文件夹不存在")
                return

            files = [f for f in os.listdir(temp_dir) if f.endswith(".zip")]
            
            if len(files) == 0:
                yield event.plain_result("错误：temp 文件夹中没有 ZIP 文件")
            elif len(files) > 1:
                yield event.plain_result(f"错误：存在多个 ZIP 文件 ({', '.join(files)})，请手动清理")
            else:
                zip_path = os.path.abspath(os.path.join(temp_dir, files[0]))
                # 使用 AstrBot 的文件发送接口
                chain = MessageChain().file(zip_path)
                yield event.chain_result(chain)
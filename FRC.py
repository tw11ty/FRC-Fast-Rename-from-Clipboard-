import idaapi
import idc
import pyperclip  # 读取剪贴板

class FastRename(idaapi.plugin_t):
    flags = idaapi.PLUGIN_UNL
    comment = "Fast Rename from Clipboard Plugin"
    help = "This plugin allows you to rename functions based on clipboard contents"
    wanted_name = "Fast_Rename_Clipboard"
    wanted_hotkey = "Shift+V"

    def __init__(self):
        self.copied_name = ""
        self.rename_method = None
        self.operand_index = 1  # 操作数索引 默认为1

    def init(self):
        print("[FRC] Plugin initialized. Waiting for Shift+V to trigger functionality.")
        return idaapi.PLUGIN_OK

    def term(self):
        print("[FRC] Plugin terminated.")
        pass

    def run(self, arg):
        self.show_method_selection_dialog()
        
    def String_customization(self, strName):
        suffix_map = {
            ".cgi": "CGI",
            ".htm": "HTM",
            ".asp": "ASP",
            ".html": "HTML"
        }

        for old_suffix, new_suffix in suffix_map.items():
            if strName.lower().endswith(old_suffix):
                strName = strName[:-len(old_suffix)] + new_suffix
                break
        
        new_name = strName.replace('.', '_').replace('/', '_').replace('?', '_')
        
        return new_name

    def show_method_selection_dialog(self):
        # 重命名方法
        choice = idaapi.ask_yn(1, "Choose renaming method:\n\n1. Address-based renaming\n2. Mouse selection-based renaming\n\nPress Yes for Address-based, No for Mouse selection-based.")
        
        if choice == 1:  # 基于逻辑地址修改函数名(不推荐)
            self.rename_method = "address_based"
            idaapi.msg("Selected: Address-based renaming.\n")
        elif choice == 0: # 基于操作数修改函数名(推荐)
            self.rename_method = "mouse_selection_based"
            idaapi.msg("Selected: Mouse selection-based renaming.\n")
            
            # 让用户指定操作数的索引（默认为1）
            operand_index_str = idaapi.ask_str(str(self.operand_index), 0, "Enter the operand index for renaming:")
            try:
                self.operand_index = int(operand_index_str) if operand_index_str else 1
            except ValueError:
                idaapi.msg("[FRC] Invalid input. Using default operand index 1.\n")
            
        else:
            idaapi.msg("Operation cancelled.\n")
            return

        if self.rename_method == "address_based":
            idaapi.add_hotkey("Shift+V", self.rename_function_address_based)
        elif self.rename_method == "mouse_selection_based":
            idaapi.add_hotkey("Shift+V", self.rename_function_mouse_selection_based)

    def rename_function_address_based(self):
        # 获取剪贴板内容
        clipboard_name = pyperclip.paste()

        # 如果剪贴板为空
        if not clipboard_name:
            idaapi.msg("[FRC] No name copied. Please copy a function name first.\n")
            return

        # 获取当前选中的地址
        ea = idc.get_screen_ea()
        
        ## 获取该地址处的函数名
        #func_name = idc.get_func_name(ea)

        #if not func_name:
        #    idaapi.msg("[FRC] No function found at the cursor location.\n")
        #    return

        # 处理复制的名称，替换掉不合法的字符
        new_name = self.String_customization(clipboard_name)

        # 检查新的名称是否已经存在于程序中
        if idc.get_name_ea_simple(new_name) != idc.BADADDR:
            idaapi.msg(f"[FRC] Name '{new_name}' already exists. Adding suffix.\n")
            # 如果名称已存在，添加后缀
            i = 1
            while idc.get_name_ea_simple(f"{new_name}_{i}") != idc.BADADDR:
                i += 1
            new_name = f"{new_name}_{i}"

        # 重命名操作
        if idc.set_name(ea, new_name):
            idaapi.msg(f"[FRC] Renamed function at 0x{ea:X} to {new_name}\n")
        else:
            idaapi.msg(f"[FRC] Failed to rename function at 0x{ea:X}\n")

    def rename_function_mouse_selection_based(self):
        clipboard_name = pyperclip.paste()  # 获取剪贴板中的内容

        if not clipboard_name:  # 剪贴板为空
            idaapi.msg("[FRC] No name copied. Please copy a function name first.\n")
            return

        ea = idc.get_screen_ea()  # 获取当前光标所在的地址

        operand_value = idc.get_operand_value(ea, self.operand_index)  # 获取当前指令的操作数（由用户定义的操作数索引）

        if operand_value == idc.BADADDR:
            idaapi.msg(f"[FRC] No valid pointer found in the instruction at operand index {self.operand_index}.\n")
            return

        #func_name = idc.get_func_name(operand_value)  # 获取该地址处的函数名

        #if not func_name:
        #    idaapi.msg(f"[FRC] No function found at the pointer address (operand index {self.operand_index}).\n")
        #    return

        # 处理复制的名称，替换掉不合法的字符
        new_name = self.String_customization(clipboard_name)

        # 后缀已存在，添加后缀
        if idc.get_name_ea_simple(new_name) != idc.BADADDR:
            idaapi.msg(f"[FRC] Name '{new_name}' already exists. Adding suffix.\n")
            i = 1
            while idc.get_name_ea_simple(f"{new_name}_{i}") != idc.BADADDR:
                i += 1
            new_name = f"{new_name}_{i}"

        # set_name 重命名ea所在函数地址
        if idc.set_name(operand_value, new_name):
            idaapi.msg(f"[FRC] Renamed function at 0x{operand_value:X} to {new_name}\n")
        else:
            idaapi.msg(f"[FRC] Failed to rename function at 0x{operand_value:X}\n")

def PLUGIN_ENTRY():
    plugin = FastRename()
    return plugin

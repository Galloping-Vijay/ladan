import urllib.request
import urllib.parse
import http.cookiejar
import json
import re
import time
import sys
import ssl

def safe_decode_content(content, headers):
    """
    安全地解码内容，处理gzip压缩
    """
    # 检查是否是gzip压缩
    if headers.get('Content-Encoding') == 'gzip':
        try:
            import gzip
            import io
            # 确保content是bytes类型
            if isinstance(content, str):
                content = content.encode('utf-8')
            
            buf = io.BytesIO(content)
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
        except Exception as e:
            print(f"解压gzip内容失败: {e}")
            return content
    
    # 解码为字符串
    if isinstance(content, bytes):
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return content.decode('gbk')
            except UnicodeDecodeError:
                return content.decode('utf-8', errors='ignore')
    
    return content

class VVICOrderPayment:
    def __init__(self):
        # 创建cookie处理器
        self.cookiejar = http.cookiejar.CookieJar()
        self.handler = urllib.request.HTTPCookieProcessor(self.cookiejar)
        self.opener = urllib.request.build_opener(self.handler)
        
        # 设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # SSL上下文
        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

    def visit_login_page(self):
        """
        访问登录页面
        """
        print("正在访问登录页面...")
        
        login_url = "https://www.vvic.com/login.html"
        req = urllib.request.Request(login_url, headers=self.headers)
        
        try:
            # 发送请求
            response = self.opener.open(req, timeout=10, context=self.context)
            
            # 读取响应内容
            login_page_content = response.read()
            
            # 安全地解码内容
            login_page_content = safe_decode_content(login_page_content, response.headers)
            print(f"成功访问登录页面，状态码: {response.getcode()}")
            return login_page_content
        except Exception as e:
            print(f"访问登录页面失败: {e}")
            # 尝试不使用SSL上下文
            try:
                print("尝试不使用SSL上下文...")
                response = self.opener.open(req, timeout=10)
                login_page_content = response.read()
                login_page_content = safe_decode_content(login_page_content, response.headers)
                print(f"成功访问登录页面，状态码: {response.getcode()}")
                return login_page_content
            except Exception as e2:
                print(f"再次尝试也失败了: {e2}")
                return None

    def login(self, username, password):
        """
        登录账户
        """
        # 首先访问登录页面获取隐藏字段
        login_page_content = self.visit_login_page()
        if not login_page_content:
            return False
            
        # 提取隐藏字段
        hidden_fields = {}
        hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', login_page_content)
        for input_tag in hidden_inputs:
            name_match = re.search(r'name=["\']([^"\']+)["\']', input_tag)
            value_match = re.search(r'value=["\']([^"\']*)["\']', input_tag)
            if name_match:
                name = name_match.group(1)
                value = value_match.group(1) if value_match else ""
                hidden_fields[name] = value
        
        print(f"发现隐藏字段: {hidden_fields}")
        
        # 准备登录数据
        login_data = {
            'username': username,
            'password': password,
            **hidden_fields  # 合并隐藏字段
        }
        
        print("准备登录...")
        print(f"登录数据: {login_data}")
        
        # 尝试不同的登录接口URL
        login_endpoints = [
            "https://www.vvic.com/login",
            "https://www.vvic.com/user/login",
            "https://www.vvic.com/auth/login"
        ]
        
        # 将登录数据编码为POST数据
        post_data = urllib.parse.urlencode(login_data).encode('utf-8')
        
        for endpoint in login_endpoints:
            try:
                print(f"尝试登录接口: {endpoint}")
                req = urllib.request.Request(endpoint, data=post_data, headers=self.headers)
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
                
                # 发送登录请求
                response = self.opener.open(req, timeout=10, context=self.context)
                
                # 读取响应内容
                response_content = response.read()
                # 安全地解码内容
                response_content = safe_decode_content(response_content, response.headers)
                print(f"登录响应状态码: {response.getcode()}")
                
                # 检查是否登录成功
                if response.getcode() in [200, 302, 301]:
                    if "验证码" not in response_content and "密码错误" not in response_content:
                        print("登录成功")
                        # 保存响应内容供分析
                        with open('login_response.html', 'w', encoding='utf-8') as f:
                            f.write(response_content)
                        return True
                    else:
                        print("登录失败，需要验证码或密码错误")
            except Exception as e:
                print(f"登录失败: {e}")
        
        return False

    def visit_home_page(self):
        """
        访问首页确认登录状态
        """
        print("\n正在访问首页确认登录状态...")
        try:
            req = urllib.request.Request("https://www.vvic.com/", headers=self.headers)
            response = self.opener.open(req, timeout=10, context=self.context)
            
            home_content = response.read()
            # 安全地解码内容
            home_content = safe_decode_content(home_content, response.headers)
            print(f"首页访问状态码: {response.getcode()}")
            
            # 简单判断是否登录成功
            if "登录" not in home_content[:200] or "退出" in home_content:
                print("登录状态确认成功")
                return True
            else:
                print("可能未登录成功")
                return False
        except Exception as e:
            print(f"访问首页失败: {e}")
            return False

    def visit_pending_payment_orders(self):
        """
        访问待付款订单页面
        """
        print("\n正在访问待付款订单页面...")
        # 尝试访问待付款订单页面
        order_urls = [
            "https://www.vvic.com/user/order/list.html?status=1",  # 假设status=1表示待付款
            "https://www.vvic.com/user/order/list.html?type=payment",  # 另一种可能的URL
            "https://www.vvic.com/user/order/list.html",
            "https://www.vvic.com/user/order"
        ]
        
        for order_url in order_urls:
            try:
                req = urllib.request.Request(order_url, headers=self.headers)
                response = self.opener.open(req, timeout=10, context=self.context)
                
                order_content = response.read()
                # 安全地解码内容
                order_content = safe_decode_content(order_content, response.headers)
                print(f"访问 {order_url} 状态码: {response.getcode()}")
                
                # 检查是否成功访问订单页面
                if response.getcode() == 200 and ("订单" in order_content or "order" in order_content.lower()):
                    # 保存订单页面内容
                    filename = f'pending_payment_orders_{int(time.time())}.html'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(order_content)
                    print(f"待付款订单页面已保存到 {filename}")
                    
                    # 解析待付款订单
                    self.parse_pending_orders(order_content)
                    return True
                elif response.getcode() == 200:
                    # 即使不确定也保存页面供分析
                    filename = f'possible_order_page_{int(time.time())}.html'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(order_content)
                    print(f"可能的订单页面已保存到 {filename}")
            except Exception as e:
                print(f"访问 {order_url} 失败: {e}")
        
        return False

    def parse_pending_orders(self, order_content):
        """
        解析待付款订单
        """
        print("\n正在解析待付款订单...")
        # 这里需要根据实际页面结构来解析订单信息
        # 由于我们无法直接查看网站结构，这里提供一个通用的解析方法
        
        # 查找订单相关的HTML元素
        order_patterns = [
            r'<div[^>]*class=["\'][^"\']*order[^"\']*["\'][^>]*>.*?</div>',
            r'<tr[^>]*class=["\'][^"\']*order[^"\']*["\'][^>]*>.*?</tr>',
            r'<li[^>]*class=["\'][^"\']*order[^"\']*["\'][^>]*>.*?</li>'
        ]
        
        orders = []
        for pattern in order_patterns:
            matches = re.findall(pattern, order_content, re.DOTALL | re.IGNORECASE)
            if matches:
                orders.extend(matches)
        
        if orders:
            print(f"找到 {len(orders)} 个订单相关元素")
            # 保存解析结果
            with open('parsed_orders.json', 'w', encoding='utf-8') as f:
                json.dump([order[:200] for order in orders], f, ensure_ascii=False, indent=2)
            print("订单解析结果已保存到 parsed_orders.json")
        else:
            print("未找到订单相关元素")
            
        # 尝试查找支付按钮
        pay_buttons = re.findall(r'<a[^>]*href=[^>]*pay[^>]*>.*?</a>', order_content, re.IGNORECASE)
        pay_buttons.extend(re.findall(r'<button[^>]*pay[^>]*>.*?</button>', order_content, re.IGNORECASE))
        
        if pay_buttons:
            print(f"找到 {len(pay_buttons)} 个支付相关按钮")
            # 保存支付按钮信息
            with open('pay_buttons.json', 'w', encoding='utf-8') as f:
                json.dump(pay_buttons, f, ensure_ascii=False, indent=2)
            print("支付按钮信息已保存到 pay_buttons.json")
            
            # 尝试点击第一个支付按钮
            if pay_buttons:
                self.click_payment_button(pay_buttons[0])
        else:
            print("未找到支付相关按钮")

    def click_payment_button(self, button_html):
        """
        点击支付按钮
        """
        print("\n正在尝试点击支付按钮...")
        # 从按钮HTML中提取href属性
        href_match = re.search(r'href=["\']([^"\']+)["\']', button_html)
        if href_match:
            payment_url = href_match.group(1)
            print(f"支付链接: {payment_url}")
            
            # 如果是相对路径，转换为绝对路径
            if payment_url.startswith('/'):
                payment_url = "https://www.vvic.com" + payment_url
            
            # 访问支付页面
            try:
                req = urllib.request.Request(payment_url, headers=self.headers)
                response = self.opener.open(req, timeout=10, context=self.context)
                
                payment_content = response.read()
                # 安全地解码内容
                payment_content = safe_decode_content(payment_content, response.headers)
                print(f"访问支付页面状态码: {response.getcode()}")
                
                # 保存支付页面
                filename = f'payment_page_{int(time.time())}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(payment_content)
                print(f"支付页面已保存到 {filename}")
                
                # 检查是否是支付宝支付页面
                if "alipay" in payment_content.lower():
                    print("检测到支付宝支付页面")
                    self.handle_alipay_payment(payment_content)
                elif "微信" in payment_content:
                    print("检测到微信支付页面")
                else:
                    print("未识别支付方式")
                    
            except Exception as e:
                print(f"访问支付页面失败: {e}")
        else:
            print("未找到支付链接")

    def handle_alipay_payment(self, payment_content):
        """
        处理支付宝支付
        """
        print("\n正在处理支付宝支付...")
        # 查找支付宝表单
        form_match = re.search(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>', payment_content, re.DOTALL | re.IGNORECASE)
        if form_match:
            action_url = form_match.group(1)
            form_content = form_match.group(2)
            print(f"支付宝表单action: {action_url}")
            
            # 保存支付宝表单信息
            alipay_info = {
                "action": action_url,
                "form_content": form_content[:500]  # 只保存前500个字符
            }
            
            with open('alipay_info.json', 'w', encoding='utf-8') as f:
                json.dump(alipay_info, f, ensure_ascii=False, indent=2)
            print("支付宝信息已保存到 alipay_info.json")
            
            # 如果之前创建的支付宝跳转页面脚本存在，可以结合使用
            print("如果需要完成支付，请使用之前创建的支付宝跳转页面")
        else:
            print("未找到支付宝表单")

    def save_cookies(self):
        """
        保存Cookie信息
        """
        print("\n正在保存Cookie信息...")
        cookies_dict = {}
        for cookie in self.cookiejar:
            cookies_dict[cookie.name] = cookie.value
        
        with open('vvic_cookies.json', 'w', encoding='utf-8') as f:
            json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
        print("Cookie信息已保存到 vvic_cookies.json")

    def load_cookies(self):
        """
        加载Cookie信息
        """
        print("\n正在加载Cookie信息...")
        try:
            with open('vvic_cookies.json', 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
            
            print("Cookie加载完成")
            return True
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return False

    def run(self):
        """
        运行完整流程
        """
        print("=== 搜款网自动支付系统 ===")
        print(f"Python版本: {sys.version}")
        
        # 登录信息
        username = "18202857285"
        password = "sange888"
        
        # 1. 登录
        if not self.login(username, password):
            print("登录失败，程序退出")
            return
        
        # 2. 保存Cookie
        self.save_cookies()
        
        # 3. 验证登录状态
        if not self.visit_home_page():
            print("登录状态验证失败")
            return
        
        # 4. 访问待付款订单
        if not self.visit_pending_payment_orders():
            print("访问待付款订单失败")
            return
        
        print("\n所有步骤已完成!")

def main():
    """
    主函数
    """
    payment_system = VVICOrderPayment()
    
    print("选择操作:")
    print("1. 完整流程 - 登录并处理待付款订单")
    print("2. 仅登录")
    print("3. 使用已保存的Cookie访问待付款订单")
    
    try:
        choice = input("请输入选项 (1/2/3): ").strip()
    except:
        choice = "1"  # 默认选择完整流程
    
    if choice == "1":
        payment_system.run()
    elif choice == "2":
        username = "18202857285"
        password = "sange888"
        if payment_system.login(username, password):
            payment_system.save_cookies()
            print("登录成功")
        else:
            print("登录失败")
    elif choice == "3":
        if payment_system.load_cookies():
            payment_system.visit_pending_payment_orders()
        else:
            print("加载Cookie失败")
    else:
        print("无效选项，执行默认操作：完整流程")
        payment_system.run()

if __name__ == "__main__":
    main()
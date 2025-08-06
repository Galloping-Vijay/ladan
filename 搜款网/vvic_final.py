import urllib.request
import urllib.parse
import http.cookiejar
import json
import re
import time
import sys

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

def vvic_login_with_requests():
    # 检查Python版本
    print(f"当前Python版本: {sys.version}")
    
    # 创建cookie处理器
    cookiejar = http.cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cookiejar)
    opener = urllib.request.build_opener(handler)
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    print("正在访问登录页面...")
    
    # 1. 访问登录页面
    login_url = "https://www.vvic.com/login.html"
    req = urllib.request.Request(login_url, headers=headers)
    
    try:
        # 发送请求（不使用SSL上下文以避免Python 3.8中的问题）
        response = opener.open(req, timeout=10)
        
        # 读取响应内容
        login_page_content = response.read()
        
        # 安全地解码内容
        login_page_content = safe_decode_content(login_page_content, response.headers)
        print(f"成功访问登录页面，状态码: {response.getcode()}")
    except Exception as e:
        print(f"访问登录页面失败: {e}")
        return
    
    # 2. 尝试从页面中提取可能的隐藏字段
    hidden_fields = {}
    # 查找<input type="hidden">标签
    hidden_inputs = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*>', login_page_content)
    for input_tag in hidden_inputs:
        name_match = re.search(r'name=["\']([^"\']+)["\']', input_tag)
        value_match = re.search(r'value=["\']([^"\']*)["\']', input_tag)
        if name_match:
            name = name_match.group(1)
            value = value_match.group(1) if value_match else ""
            hidden_fields[name] = value
    
    print(f"发现隐藏字段: {hidden_fields}")
    
    # 3. 准备登录数据
    login_data = {
        'username': '18202857285',
        'password': 'sange888',
        **hidden_fields  # 合并隐藏字段
    }
    
    print("准备登录...")
    print(f"登录数据: {login_data}")
    
    # 4. 尝试不同的登录接口URL
    login_endpoints = [
        "https://www.vvic.com/login",
        "https://www.vvic.com/user/login",
        "https://www.vvic.com/auth/login"
    ]
    
    # 将登录数据编码为POST数据
    post_data = urllib.parse.urlencode(login_data).encode('utf-8')
    
    login_success = False
    for endpoint in login_endpoints:
        try:
            print(f"尝试登录接口: {endpoint}")
            req = urllib.request.Request(endpoint, data=post_data, headers=headers)
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            
            # 发送登录请求（不使用SSL上下文以避免Python 3.8中的问题）
            response = opener.open(req, timeout=10)
            
            # 读取响应内容
            response_content = response.read()
            # 安全地解码内容
            response_content = safe_decode_content(response_content, response.headers)
            print(f"登录响应状态码: {response.getcode()}")
            
            # 检查是否登录成功
            if response.getcode() in [200, 302, 301]:
                if "验证码" not in response_content and "密码错误" not in response_content:
                    print("登录可能成功")
                    login_success = True
                    # 保存响应内容供分析
                    with open('login_response.html', 'w', encoding='utf-8') as f:
                        f.write(response_content)
                    break
                else:
                    print("登录可能失败，需要验证码或密码错误")
        except Exception as e:
            print(f"登录失败: {e}")
    
    if not login_success:
        print("所有登录尝试均失败")
        return
    
    # 5. 显示当前会话的Cookie
    print("\n当前会话的Cookie:")
    cookies_dict = {}
    for cookie in cookiejar:
        print(f"{cookie.name}: {cookie.value}")
        cookies_dict[cookie.name] = cookie.value
    
    # 6. 保存Cookie信息
    with open('requests_cookies.json', 'w', encoding='utf-8') as f:
        json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
    print("\nCookie信息已保存到 requests_cookies.json")
    
    # 7. 尝试访问首页确认登录状态
    print("\n正在访问首页确认登录状态...")
    try:
        req = urllib.request.Request("https://www.vvic.com/", headers=headers)
        response = opener.open(req, timeout=10)
        
        home_content = response.read()
        # 安全地解码内容
        home_content = safe_decode_content(home_content, response.headers)
        print(f"首页访问状态码: {response.getcode()}")
        
        # 简单判断是否登录成功
        if "登录" not in home_content[:200] or "退出" in home_content:
            print("登录状态确认成功")
        else:
            print("可能未登录成功")
    except Exception as e:
        print(f"访问首页失败: {e}")
    
    # 8. 尝试访问我的订单页面
    print("\n正在访问我的订单页面...")
    order_urls = [
        "https://www.vvic.com/user/order/list.html",
        "https://www.vvic.com/user/order"
    ]
    
    order_page_found = False
    for order_url in order_urls:
        try:
            req = urllib.request.Request(order_url, headers=headers)
            response = opener.open(req, timeout=10)
            
            order_content = response.read()
            # 安全地解码内容
            order_content = safe_decode_content(order_content, response.headers)
            print(f"访问 {order_url} 状态码: {response.getcode()}")
            
            # 检查是否成功访问订单页面
            if response.getcode() == 200 and ("订单" in order_content or "order" in order_content.lower()):
                # 保存订单页面内容
                filename = f'orders_page_requests_{int(time.time())}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(order_content)
                print(f"订单页面已保存到 {filename}")
                order_page_found = True
                break
            elif response.getcode() == 200:
                # 即使不确定也保存页面供分析
                filename = f'possible_order_page_{int(time.time())}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(order_content)
                print(f"可能的订单页面已保存到 {filename}")
        except Exception as e:
            print(f"访问 {order_url} 失败: {e}")
    
    if not order_page_found:
        print("未找到明确的订单页面")
    
    print("\n所有步骤完成!")

def load_cookies_and_access_orders():
    """
    使用已保存的Cookie访问订单页面
    """
    # 创建cookie处理器
    cookiejar = http.cookiejar.CookieJar()
    handler = urllib.request.HTTPCookieProcessor(cookiejar)
    opener = urllib.request.build_opener(handler)
    
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # 加载Cookie
    try:
        with open('requests_cookies.json', 'r', encoding='utf-8') as f:
            cookies_dict = json.load(f)
        
        # 注意：urllib不支持直接设置cookiejar中的cookie，这种方式有限制
        print("Cookie加载完成（注意：urllib的cookie处理有限制）")
    except Exception as e:
        print(f"加载Cookie失败: {e}")
        return
    
    # 访问订单页面
    order_urls = [
        "https://www.vvic.com/user/order/list.html",
        "https://www.vvic.com/user/order"
    ]
    
    for order_url in order_urls:
        try:
            req = urllib.request.Request(order_url, headers=headers)
            response = opener.open(req, timeout=10)
            
            order_content = response.read()
            # 安全地解码内容
            order_content = safe_decode_content(order_content, response.headers)
            print(f"访问 {order_url} 状态码: {response.getcode()}")
            
            if response.getcode() == 200:
                filename = f'orders_with_cookies_{int(time.time())}.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(order_content)
                print(f"使用Cookie访问的订单页面已保存到 {filename}")
                break
        except Exception as e:
            print(f"访问 {order_url} 失败: {e}")

if __name__ == "__main__":
    print("选择操作:")
    print("1. 登录并获取订单信息")
    print("2. 使用已保存的Cookie访问订单信息")
    
    try:
        choice = input("请输入选项 (1 或 2): ").strip()
    except:
        choice = "1"  # 默认选择登录
    
    if choice == "1":
        vvic_login_with_requests()
    elif choice == "2":
        load_cookies_and_access_orders()
    else:
        print("无效选项，执行默认操作：登录并获取订单信息")
        vvic_login_with_requests()
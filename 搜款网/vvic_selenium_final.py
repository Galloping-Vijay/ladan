from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json

def vvic_automation_with_selenium():
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 如果需要无头模式（不显示浏览器窗口），取消下一行注释
    # chrome_options.add_argument("--headless")
    
    # 启动浏览器
    print("正在启动浏览器...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        # 执行JavaScript来隐藏webdriver属性
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"启动浏览器失败: {e}")
        print("请确保已安装Chrome浏览器和ChromeDriver")
        return
    
    try:
        # 1. 访问登录页面
        print("正在访问登录页面...")
        driver.get("https://www.vvic.com/login.html")
        
        # 等待页面加载
        wait = WebDriverWait(driver, 10)
        
        # 2. 输入账号和密码
        print("正在输入账号和密码...")
        # 等待用户名输入框出现并输入用户名
        username_input = wait.until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_input.clear()
        username_input.send_keys("18202857285")
        
        # 查找密码输入框并输入密码
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys("sange888")
        
        # 3. 点击登录按钮
        print("正在点击登录按钮...")
        # 尝试几种可能的登录按钮选择器
        login_button_selectors = [
            (By.XPATH, '//button[@type="submit"]'),
            (By.CLASS_NAME, 'login-btn'),
            (By.XPATH, '//input[@type="submit"]'),
            (By.ID, 'login-button'),
            (By.XPATH, '//a[contains(@class, "login") and contains(@class, "btn")]')
        ]
        
        login_button = None
        for selector_type, selector_value in login_button_selectors:
            try:
                login_button = driver.find_element(selector_type, selector_value)
                if login_button.is_displayed() and login_button.is_enabled():
                    break
            except NoSuchElementException:
                continue
        
        if login_button:
            # 滚动到元素并点击
            driver.execute_script("arguments[0].scrollIntoView();", login_button)
            time.sleep(1)
            login_button.click()
        else:
            # 如果找不到特定的登录按钮，尝试点击页面上的第一个提交按钮
            submit_buttons = driver.find_elements(By.XPATH, '//button[@type="submit"] | //input[@type="submit"]')
            if submit_buttons:
                submit_buttons[0].click()
            else:
                print("未找到登录按钮，尝试按回车键...")
                password_input.send_keys(u'\ue007')  # Enter键
        
        # 4. 等待登录完成
        print("等待登录完成...")
        time.sleep(5)
        
        # 检查是否登录成功
        current_url = driver.current_url
        page_source = driver.page_source
        
        # 判断登录是否成功（检查页面是否有"退出"或没有"登录"字样）
        if "退出" in page_source or "个人中心" in page_source or "user" in current_url:
            print("登录成功!")
        else:
            print("可能登录失败，请检查账号密码是否正确")
        
        # 5. 获取Cookie
        print("正在获取Cookie...")
        cookies = driver.get_cookies()
        
        # 保存Cookie到文件
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']
        
        with open('selenium_vvic_cookies.json', 'w', encoding='utf-8') as f:
            json.dump(cookies_dict, f, ensure_ascii=False, indent=2)
        
        print("Cookie已保存到 selenium_vvic_cookies.json")
        
        # 6. 访问待付款订单页面
        print("正在访问待付款订单页面...")
        try:
            # 尝试直接访问待付款订单页面
            driver.get("https://www.vvic.com/user/order/list.html?status=1")
            time.sleep(3)
            
            # 保存页面源码
            filename = f"pending_payment_orders_selenium_{int(time.time())}.html"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            print(f"待付款订单页面已保存到 {filename}")
            
            # 查找支付按钮
            try:
                # 查找包含"付款"或"支付"字样的按钮
                pay_buttons = driver.find_elements(By.XPATH, '//a[contains(text(), "付款")] | //a[contains(text(), "支付")] | //button[contains(text(), "付款")] | //button[contains(text(), "支付")]')
                
                if pay_buttons:
                    print(f"找到 {len(pay_buttons)} 个支付按钮")
                    # 点击第一个支付按钮
                    pay_buttons[0].click()
                    print("已点击第一个支付按钮")
                    time.sleep(3)
                    
                    # 保存支付页面
                    pay_filename = f"payment_page_selenium_{int(time.time())}.html"
                    with open(pay_filename, 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print(f"支付页面已保存到 {pay_filename}")
                else:
                    print("未找到支付按钮")
            except Exception as e:
                print(f"查找或点击支付按钮时出错: {e}")
                
        except Exception as e:
            print(f"访问待付款订单页面失败: {e}")
        
        # 保持浏览器打开一段时间以便观察
        print("任务完成，浏览器将在10秒后关闭...")
        time.sleep(10)
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        # 保存错误时的页面内容用于调试
        with open('error_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("错误页面已保存到 error_page.html")
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

def load_cookies_and_access_orders():
    """
    使用已保存的Cookie访问订单页面
    """
    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # 如果需要无头模式（不显示浏览器窗口），取消下一行注释
    # chrome_options.add_argument("--headless")
    
    # 启动浏览器
    print("正在启动浏览器...")
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    except Exception as e:
        print(f"启动浏览器失败: {e}")
        print("请确保已安装Chrome浏览器和ChromeDriver")
        return
    
    try:
        # 访问首页以初始化域名
        driver.get("https://www.vvic.com/")
        time.sleep(2)
        
        # 加载并添加Cookie
        print("正在加载Cookie...")
        try:
            with open('selenium_vvic_cookies.json', 'r', encoding='utf-8') as f:
                cookies_dict = json.load(f)
            
            for name, value in cookies_dict.items():
                driver.add_cookie({
                    'name': name,
                    'value': value,
                    'domain': '.vvic.com',  # 设置正确的域名
                    'path': '/'
                })
            
            print("Cookie加载成功")
        except Exception as e:
            print(f"加载Cookie失败: {e}")
            return
        
        # 刷新页面使Cookie生效
        driver.refresh()
        time.sleep(2)
        
        # 访问待付款订单页面
        print("正在访问待付款订单页面...")
        driver.get("https://www.vvic.com/user/order/list.html?status=1")
        time.sleep(3)
        
        # 保存页面源码
        filename = f"pending_payment_orders_with_cookies_{int(time.time())}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        
        print(f"使用Cookie访问的待付款订单页面已保存到 {filename}")
        
        # 查找并点击支付按钮
        try:
            pay_buttons = driver.find_elements(By.XPATH, '//a[contains(text(), "付款")] | //a[contains(text(), "支付")] | //button[contains(text(), "付款")] | //button[contains(text(), "支付")]')
            
            if pay_buttons:
                print(f"找到 {len(pay_buttons)} 个支付按钮")
                # 点击第一个支付按钮
                pay_buttons[0].click()
                print("已点击第一个支付按钮")
                time.sleep(3)
                
                # 保存支付页面
                pay_filename = f"payment_page_with_cookies_{int(time.time())}.html"
                with open(pay_filename, 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"支付页面已保存到 {pay_filename}")
            else:
                print("未找到支付按钮")
        except Exception as e:
            print(f"查找或点击支付按钮时出错: {e}")
        
        # 保持浏览器打开一段时间以便观察
        print("任务完成，浏览器将在10秒后关闭...")
        time.sleep(10)
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    print("搜款网自动化系统 (Selenium版本)")
    print("=" * 40)
    print("请选择操作:")
    print("1. 完整流程 - 登录并处理待付款订单")
    print("2. 使用已保存的Cookie访问待付款订单")
    
    try:
        choice = input("请输入选项 (1 或 2): ").strip()
    except:
        choice = "1"  # 默认选择完整流程
    
    if choice == "1":
        vvic_automation_with_selenium()
    elif choice == "2":
        load_cookies_and_access_orders()
    else:
        print("无效选项，执行默认操作：完整流程")
        vvic_automation_with_selenium()
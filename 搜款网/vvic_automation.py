import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class VVICAutomation:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.login_url = "https://www.vvic.com/login.html"
        self.orders_url = "https://www.vvic.com/user/orders.html?q=&t=0"
        self.username = "18202857285"
        self.password = "sange888"
        
    def setup_driver(self):
        """初始化浏览器驱动"""
        try:
            print("正在初始化浏览器驱动...")
            
            chrome_options = Options()
            # 可选：无头模式
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--remote-debugging-port=9222')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--allow-running-insecure-content')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # 设置用户代理
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # 指定chromedriver路径
            service = Service('D:\\Program\\chromedriver-win64\\chromedriver.exe')
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 设置窗口大小
            self.driver.set_window_size(1920, 1080)
            
            # 隐藏webdriver特征
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            
            self.wait = WebDriverWait(self.driver, 15)
            print("浏览器驱动初始化完成")
            
        except Exception as e:
            print(f"初始化浏览器驱动失败: {str(e)}")
            print("请确保ChromeDriver路径正确且Chrome浏览器已安装")
            raise e
        
    def login(self):
        """登录搜款网"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 检查浏览器会话是否有效
                try:
                    self.driver.current_url
                except:
                    print(f"浏览器会话无效，尝试重新初始化 (尝试 {attempt + 1}/{max_retries})")
                    if not self.setup_driver():
                        continue
                
                print("正在打开登录页面...")
                self.driver.get(self.login_url)
                time.sleep(3)
                
                # 等待页面加载完成
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                print("登录页面加载完成")
                
                # 第一步：确保切换到账号密码登录tab
                print("正在切换到账号密码登录模式...")
                try:
                    # 直接通过ID定位账号密码登录tab
                    account_tab = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "account"))
                    )
                    
                    # 检查是否已经是激活状态
                    if "active" not in account_tab.get_attribute("class"):
                        print("点击切换到账号密码登录tab")
                        self.driver.execute_script("arguments[0].click();", account_tab)
                        time.sleep(2)
                    else:
                        print("已经是账号密码登录模式")
                        
                except Exception as e:
                    print(f"切换登录模式时发生错误: {str(e)}")
                
                # 第二步：等待账号密码登录区域显示
                print("等待账号密码登录区域显示...")
                try:
                    pwd_login_area = self.wait.until(
                        EC.visibility_of_element_located((By.ID, "pwd-login"))
                    )
                    print("账号密码登录区域已显示")
                except Exception as e:
                    print(f"等待登录区域显示失败: {str(e)}")
                
                # 第三步：输入用户名
                print("正在输入用户名...")
                try:
                    username_input = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "username"))
                    )
                    
                    # 滚动到元素位置并输入
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", username_input)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", username_input)
                    self.driver.execute_script("arguments[0].value = '';", username_input)
                    self.driver.execute_script("arguments[0].value = arguments[1];", username_input, self.username)
                    # 触发input事件
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", username_input)
                    print(f"用户名输入完成: {self.username}")
                    
                except Exception as e:
                    print(f"用户名输入失败: {str(e)}")
                    continue
                
                # 第四步：输入密码
                print("正在输入密码...")
                try:
                    password_input = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "password"))
                    )
                    
                    # 滚动到元素位置并输入
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", password_input)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", password_input)
                    self.driver.execute_script("arguments[0].value = '';", password_input)
                    self.driver.execute_script("arguments[0].value = arguments[1];", password_input, self.password)
                    # 触发input事件
                    self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_input)
                    print("密码输入完成")
                    
                except Exception as e:
                    print(f"密码输入失败: {str(e)}")
                    continue
                
                # 第五步：点击登录按钮
                print("正在点击登录按钮...")
                try:
                    login_button = self.wait.until(
                        EC.element_to_be_clickable((By.ID, "submit"))
                    )
                    
                    # 滚动到按钮位置并点击
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", login_button)
                    print("已点击登录按钮")
                    
                except Exception as e:
                    print(f"点击登录按钮失败: {str(e)}")
                    continue
                
                # 第六步：等待登录结果
                print("等待登录结果...")
                time.sleep(5)
                
                current_url = self.driver.current_url
                print(f"登录后当前URL: {current_url}")
                
                # 检查是否登录成功
                if "login" not in current_url.lower():
                    print("登录成功！")
                    return True
                else:
                    print("登录可能失败，仍在登录页面")
                    
                    # 检查错误信息
                    try:
                        error_element = self.driver.find_element(By.CLASS_NAME, "j-error")
                        if error_element.is_displayed() and error_element.text.strip():
                            print(f"登录错误信息: {error_element.text}")
                    except:
                        pass
                    
                    # 检查是否需要验证码
                    try:
                        captcha_elements = self.driver.find_elements(By.XPATH, 
                            "//div[contains(@id, 'captcha')] | //div[contains(@class, 'captcha')] | //div[contains(text(), '验证码')]"
                        )
                        for captcha_element in captcha_elements:
                            if captcha_element.is_displayed():
                                print("检测到验证码，需要手动处理")
                                break
                    except:
                        pass
                    
                    if attempt < max_retries - 1:
                        print(f"登录失败，准备重试 (尝试 {attempt + 2}/{max_retries})")
                        time.sleep(3)
                        continue
                    else:
                        return False
                        
            except TimeoutException:
                print(f"登录过程中发生超时错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return False
            except Exception as e:
                print(f"登录过程中发生错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
                return False
        
        return False
    
    def navigate_to_orders(self):
        """导航到我的订单页面"""
        try:
            print("正在导航到订单页面...")
            
            # 直接访问订单页面URL
            self.driver.get(self.orders_url)
            time.sleep(3)
            
            # 检查是否成功进入订单页面
            current_url = self.driver.current_url
            if "orders" in current_url:
                print("已成功进入订单页面")
                return True
            else:
                print(f"可能未成功进入订单页面，当前URL: {current_url}")
                return False
            
        except Exception as e:
            print(f"导航到订单页面时发生错误: {str(e)}")
            return False
    
    def click_pending_payment_tab(self):
        """点击待付款标签页"""
        try:
            print("正在查找并点击待付款标签...")
            time.sleep(2)
            
            # 查找待付款标签 - 使用多种选择器
            pending_selectors = [
                "//a[contains(text(), '待付款')]",
                "//span[contains(text(), '待付款')]",
                "//div[contains(text(), '待付款')]",
                "//li[contains(text(), '待付款')]",
                "//button[contains(text(), '待付款')]",
                "//a[contains(@href, 't=0')]",  # 根据URL参数查找
                "//tab[contains(text(), '待付款')]"
            ]
            
            pending_tab = None
            for selector in pending_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements and elements[0].is_displayed():
                        pending_tab = elements[0]
                        print(f"找到待付款标签，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if pending_tab:
                # 使用JavaScript点击
                self.driver.execute_script("arguments[0].click();", pending_tab)
                time.sleep(3)
                print("已点击待付款标签")
                return True
            else:
                print("未找到待付款标签")
                # 打印页面内容用于调试
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text[:1000]
                    print(f"页面内容片段: {page_text}")
                except:
                    pass
                return False
            
        except Exception as e:
            print(f"点击待付款标签时发生错误: {str(e)}")
            return False
    
    def find_pending_orders_and_payment_links(self):
        """查找待付款订单并点击立即支付按钮"""
        try:
            print("正在查找待付款订单...")
            
            # 等待订单列表加载
            time.sleep(3)
            
            # 根据提供的HTML结构，查找订单行
            order_selectors = [
                "//tr[contains(@class, 'tr-tb') and contains(@class, 'j-order')]",
                "//tr[@class='tr-tb j-order']",
                "//tr[contains(@class, 'j-order')]"
            ]
            
            orders = []
            for selector in order_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        orders = elements
                        print(f"找到 {len(orders)} 个订单，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if not orders:
                print("未找到任何订单")
                return []
            
            payment_links = []
            
            # 处理第一个待付款订单
            if orders:
                first_order = orders[0]
                print("正在处理第一个待付款订单...")
                
                try:
                    # 根据HTML结构查找"立即支付"按钮
                    pay_button_selectors = [
                        ".//a[contains(@class, 'pay-btn') and contains(text(), '立即支付')]",
                        ".//a[@class='btn btn-primary pay-btn']",
                        ".//a[contains(@class, 'btn') and contains(@class, 'primary') and contains(@class, 'pay-btn')]",
                        ".//a[contains(text(), '立即支付')]",
                        ".//a[contains(@href, '/user/pay.html')]"
                    ]
                    
                    pay_button = None
                    for selector in pay_button_selectors:
                        try:
                            elements = first_order.find_elements(By.XPATH, selector)
                            if elements and elements[0].is_displayed():
                                pay_button = elements[0]
                                print(f"找到支付按钮，使用选择器: {selector}")
                                break
                        except:
                            continue
                    
                    if pay_button:
                        # 获取支付链接
                        payment_url = pay_button.get_attribute('href')
                        if payment_url:
                            print(f"找到支付链接: {payment_url}")
                            
                            # 直接导航到支付页面，而不是点击按钮
                            print("直接导航到支付页面...")
                            self.driver.get(payment_url)
                            
                            # 等待页面加载
                            time.sleep(3)
                            
                            # 检查是否成功跳转到支付页面
                            current_url = self.driver.current_url
                            print(f"当前页面URL: {current_url}")
                            
                            if '/user/pay.html' in current_url:
                                print("成功跳转到支付页面")
                                payment_links.append({
                                    'order_index': 1,
                                    'payment_url': payment_url,
                                    'current_url': current_url,
                                    'element_text': pay_button.text
                                })
                                return payment_links
                            else:
                                print(f"跳转失败，当前URL: {current_url}")
                                
                                # 如果直接导航失败，尝试点击方式
                                print("尝试点击方式...")
                                # 先回到订单页面
                                self.driver.back()
                                time.sleep(2)
                                
                                # 重新找到按钮
                                try:
                                    pay_button = first_order.find_element(By.XPATH, ".//a[contains(@href, '/user/pay.html')]")
                                    
                                    # 滚动到按钮位置
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", pay_button)
                                    time.sleep(1)
                                    
                                    # 尝试不同的点击方式
                                    try:
                                        # 方式1：模拟鼠标点击
                                        from selenium.webdriver.common.action_chains import ActionChains
                                        actions = ActionChains(self.driver)
                                        actions.move_to_element(pay_button).click().perform()
                                        print("已点击立即支付按钮（ActionChains）")
                                    except:
                                        try:
                                            # 方式2：JavaScript点击
                                            self.driver.execute_script("arguments[0].click();", pay_button)
                                            print("已点击立即支付按钮（JavaScript）")
                                        except:
                                            # 方式3：直接点击
                                            pay_button.click()
                                            print("已点击立即支付按钮（直接点击）")
                                    
                                    # 等待页面跳转
                                    time.sleep(3)
                                    
                                    # 再次检查URL
                                    current_url = self.driver.current_url
                                    print(f"点击后的页面URL: {current_url}")
                                    
                                    if '/user/pay.html' in current_url:
                                        print("成功跳转到支付页面")
                                        payment_links.append({
                                            'order_index': 1,
                                            'payment_url': payment_url,
                                            'current_url': current_url,
                                            'element_text': pay_button.text
                                        })
                                        return payment_links
                                        
                                except Exception as e:
                                    print(f"重新点击时发生错误: {str(e)}")
                        else:
                            print("支付按钮没有href属性")
                    else:
                        print("未找到立即支付按钮")
                        # 打印订单内容用于调试
                        try:
                            order_text = first_order.text[:300]
                            print(f"订单内容片段: {order_text}")
                        except:
                            pass
                            
                except Exception as e:
                    print(f"处理第一个订单时发生错误: {str(e)}")
            
            return payment_links
            
        except Exception as e:
            print(f"查找待付款订单时发生错误: {str(e)}")
            return []
    
    def run(self):
        """运行主流程"""
        try:
            print("开始执行搜款网自动化脚本...")
            
            # 初始化浏览器
            self.setup_driver()
            
            # 登录
            if not self.login():
                print("登录失败，脚本终止")
                return
            
            # 导航到订单页面
            if not self.navigate_to_orders():
                print("导航到订单页面失败，脚本终止")
                return
            
            # 点击待付款标签
            if not self.click_pending_payment_tab():
                print("点击待付款标签失败，脚本终止")
                return
            
            # 查找待付款订单和支付链接
            payment_links = self.find_pending_orders_and_payment_links()
            
            if payment_links:
                print("\n=== 找到支付链接，正在处理支付页面 ===")
                
                # 处理支付页面
                if self.handle_payment_page():
                    print("支付页面处理成功")
                else:
                    print("支付页面处理失败")
            else:
                print("未找到待付款订单或支付链接")
            
            # 保持浏览器打开一段时间，方便查看结果
            print("\n脚本执行完成，浏览器将保持打开状态...")
            input("按回车键关闭浏览器...")
            
        except Exception as e:
            print(f"脚本执行过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
                print("浏览器已关闭")

if __name__ == "__main__":
    automation = VVICAutomation()
    automation.run()


def handle_payment_page(self):
    """处理支付页面的操作"""
    try:
        print("正在处理支付页面...")
        
        # 等待支付页面加载
        time.sleep(3)
        
        # 检查是否在支付页面
        if '/user/pay.html' not in self.driver.current_url:
            print("当前不在支付页面")
            return False
        
        print(f"当前支付页面URL: {self.driver.current_url}")
        
        # 1. 处理验证码
        try:
            # 查找验证码输入框
            verification_code_input = None
            verification_selectors = [
                "//input[@id='secCode']",
                "//input[@name='secCode']",
                "//input[contains(@placeholder, '验证码')]"
            ]
            
            for selector in verification_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        verification_code_input = element
                        break
                except:
                    continue
            
            if verification_code_input:
                print("找到验证码输入框")
                # 这里需要用户手动输入验证码，或者使用OCR识别
                print("请手动查看验证码图片并输入验证码...")
                
                # 等待用户输入验证码（可以添加OCR识别功能）
                input("请在浏览器中输入验证码，然后按回车继续...")
            
        except Exception as e:
            print(f"处理验证码时发生错误: {str(e)}")
        
        # 2. 获取短信验证码
        try:
            # 查找获取短信验证码按钮
            sms_button_selectors = [
                "//span[@id='getSms']",
                "//span[contains(@class, 'btn') and contains(text(), '获取短信验证码')]",
                "//button[contains(text(), '获取短信验证码')]"
            ]
            
            sms_button = None
            for selector in sms_button_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed():
                        sms_button = element
                        break
                except:
                    continue
            
            if sms_button:
                print("找到获取短信验证码按钮")
                # 滚动到按钮位置
                self.driver.execute_script("arguments[0].scrollIntoView(true);", sms_button)
                time.sleep(1)
                
                # 点击获取短信验证码
                self.driver.execute_script("arguments[0].click();", sms_button)
                print("已点击获取短信验证码按钮")
                time.sleep(2)
                
                # 等待用户输入短信验证码
                print("请查看手机短信并输入短信验证码...")
                input("请在浏览器中输入短信验证码，然后按回车继续...")
            
        except Exception as e:
            print(f"获取短信验证码时发生错误: {str(e)}")
        
        # 3. 查找并点击立即付款按钮
        try:
            # 等待一下确保所有信息都已填写
            time.sleep(2)
            
            # 查找立即付款按钮
            pay_button_selectors = [
                "//button[contains(text(), '立即付款')]",
                "//a[contains(text(), '立即付款')]",
                "//span[contains(text(), '立即付款')]",
                "//div[contains(@class, 'btn') and contains(text(), '立即付款')]",
                "//input[@type='submit' and contains(@value, '立即付款')]",
                "//button[contains(@class, 'pay-btn')]",
                "//button[contains(@class, 'btn-primary')]"
            ]
            
            pay_button = None
            for selector in pay_button_selectors:
                try:
                    element = self.driver.find_element(By.XPATH, selector)
                    if element.is_displayed() and element.is_enabled():
                        pay_button = element
                        print(f"找到立即付款按钮，使用选择器: {selector}")
                        break
                except:
                    continue
            
            if pay_button:
                # 滚动到按钮位置
                self.driver.execute_script("arguments[0].scrollIntoView(true);", pay_button)
                time.sleep(1)
                
                # 点击立即付款按钮
                try:
                    self.driver.execute_script("arguments[0].click();", pay_button)
                    print("已点击立即付款按钮（JavaScript）")
                except:
                    pay_button.click()
                    print("已点击立即付款按钮（直接点击）")
                
                # 等待页面响应
                time.sleep(3)
                
                # 检查是否跳转到支付宝或其他支付页面
                current_url = self.driver.current_url
                print(f"点击后的页面URL: {current_url}")
                
                if 'alipay' in current_url.lower() or 'pay' in current_url.lower():
                    print("成功跳转到支付页面")
                    return True
                else:
                    print("可能需要检查页面状态或错误信息")
                    # 检查是否有错误提示
                    try:
                        error_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error')] | //span[contains(@class, 'err')] | //div[contains(@class, 'alert')]")
                        for error_element in error_elements:
                            if error_element.is_displayed() and error_element.text.strip():
                                print(f"发现错误信息: {error_element.text}")
                    except:
                        pass
                    return False
            else:
                print("未找到立即付款按钮")
                # 打印页面内容用于调试
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
                    print(f"页面内容片段: {page_text}")
                except:
                    pass
                return False
                
        except Exception as e:
            print(f"点击立即付款按钮时发生错误: {str(e)}")
            return False
        
    except Exception as e:
        print(f"处理支付页面时发生错误: {str(e)}")
        return False
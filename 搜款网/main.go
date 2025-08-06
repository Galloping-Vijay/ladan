package main

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"net/url"
	"os"
	"regexp"
	"strings"
)

// 支付宝表单数据结构
type AlipayFormData struct {
	Charset   string
	Method    string
	Sign      string
	ReturnUrl string
	NotifyUrl string
	SignType  string
	Timestamp string
	Version   string
	AppId     string
	Format    string
	Action    string
}

func main() {
	// Step 1: 访问网站并获取响应
	fmt.Println("正在访问网站并获取支付信息...")
	responseContent, err := visitWebsite()
	if err != nil {
		fmt.Printf("访问网站失败: %v\n", err)
		return
	}

	// 保存响应内容到文件，便于调试
	err = ioutil.WriteFile("response.txt", []byte(responseContent), 0644)
	if err != nil {
		fmt.Printf("保存响应内容失败: %v\n", err)
	}

	// Step 2: 解析支付宝表单数据
	fmt.Println("解析支付表单数据...")
	formData := parseAlipayFormData(responseContent)

	// Step 3: 生成HTML跳转页面
	fmt.Println("生成HTML跳转页面...")
	err = generateHTMLPage(formData)
	if err != nil {
		fmt.Printf("生成HTML页面失败: %v\n", err)
		return
	}

	fmt.Println("成功生成跳转页面: alipay_redirect.html")
	fmt.Println("请在浏览器中打开该文件并点击按钮完成支付跳转")
}

func visitWebsite() (string, error) {
	// 目标URL
	targetURL := "http://www.vvic.com/user/payment/page/submit.html?payCode=alipay&xy=2&orderId=538202072850497537&payNo=null&totalAmount=62.5&balanceAmount=0&channelAmount=62.5&type=0"

	// 创建HTTP请求
	req, err := http.NewRequest("GET", targetURL, nil)
	if err != nil {
		return "", err
	}

	// 设置Cookie
	cookie := `HWWAFSESTIME=1754484522249; HWWAFSESID=fac027cabf6833d0ca; sajssdk_2015_cross_new_user=1; cu=9411F002F2D4A5C2E45ED4DC7E02AF8F; countlyIp=110.87.7.76; _ga=GA1.2.1730275170.1754484551; _gid=GA1.2.654351018.1754484551; _uab_collina=175448457630986671313176; _countlyIp=110.87.7.76; DEVICE_INFO=%7B%22device_id%22%3A%229411F002F2D4A5C2E45ED4DC7E02AF8F%22%2C%22device_channel%22%3A1%2C%22device_type%22%3A1%2C%22device_model%22%3A%22Windows%22%2C%22device_os%22%3A%22Windows%2010%22%2C%22device_lang%22%3A%22zh-CN%22%2C%22device_size%22%3A%221536*864%22%2C%22device_net%22%3A%220%22%2C%22device_lon%22%3A%22%22%2C%22device_lat%22%3A%22%22%2C%22device_address%22%3A%22%22%2C%22browser_type%22%3A%22Chrome%22%2C%22browser_version%22%3A%22138.0.0.0%22%7D; Hm_lvt_fbb512d824c082a8ddae7951feb7e0e5=1754484580; HMACCOUNT=ED9AFACE06EB72AC; Hm_lvt_fdffeb50b7ea8a86ab0c9576372b2b8c=1754484580; _ati=4848660450440; algo4Cu=0; ISSUPPORTPANGGE=true; _c_WBKFRo=lkyMpbaGGIOGOx8bagNge2snzzyJRNyy9VGFjoPv; _nb_ioWEgULi=; userName=vvic2241760892; userLoginAuto=1; hasCityMarket=""; city=gz; lang=cn; currency=CNY; ipCity=110.87.7.76,; itemAlgo=%7B%22algoId%22%3A0%2C%22isLandingPage%22%3A0%7D; algo4Uid=0; hasFocusStall=false; f5d944ea-053f-428f-98a2-fa89c4950dae; ocity=gz; vvic_token=f5d944ea-053f-428f-98a2-fa89c4950dae; _ADDRESSTYPE=add; uid=5193701; ut=0; umc=1; pn=0; defaultShopId=; shopId=; uno=0; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%225193701%22%2C%22first_id%22%3A%221987f6d95456bc-00843fc590e41e1-26011151-1327104-1987f6d9546843%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk4N2Y2ZDk1NDU2YmMtMDA4NDNmYzU5MGU0MWUxLTI2MDExMTUxLTEzMjcxMDQtMTk4N2Y2ZDk1NDY4NDMiLCIkaWRlbnRpdHlfbG9naW5faWQiOiI1MTkzNzAxIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%225193701%22%7D%2C%22%24device_id%22%3A%221987f6d95456bc-00843fc590e41e1-26011151-1327104-1987f6d9546843%22%7D; Hm_lpvt_fdffeb50b7ea8a86ab0c9576372b2b8c=1754486125; Hm_lpvt_fbb512d824c082a8ddae7951feb7e0e5=1754486125`
	req.Header.Set("Cookie", cookie)

	// 设置User-Agent
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// 读取响应内容
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	fmt.Printf("响应状态码: %d\n", resp.StatusCode)
	return string(body), nil
}

func parseAlipayFormData(content string) AlipayFormData {
	formData := AlipayFormData{}

	// 查找表单开始位置
	formStart := strings.Index(content, "<form name=\"punchout_form\"")
	if formStart == -1 {
		// 如果没有找到表单，使用默认数据
		fmt.Println("未找到支付表单，使用默认数据")
		formData.Action = "https://openapi.alipay.com/gateway.do"
		formData.Charset = "utf-8"
		formData.Method = "alipay.trade.page.pay"
		formData.Sign = "nzZLmGFbeiLKxe92t/KcLE9mNnypk7MTuB1vFt6D9QgLfj1QFXcrPxpQ7K3oMI5huGRhDBSrUHftpPkO1PI8lHb+fTNFUsxDScQBFTIfeuJasq0K5IW/0oUUCP4QXBZ1lbhIL3WXay6kggjHf2O5UkVtwQpMRdOCjCkyKA5R410qwrUrAfWQiXn7uIltcZYqJmZtaRRiSfORsIyNwYsa6ynqzZ4E7tKubQugRIGC1K68YNnmZ5sWniGilW8v1dG7nMZ0GHWw8ZFW5qnCKpB87paygeNi3DTeVbbW/AYN4mY5rHKYWChmNFZnyEb12j1W1520T/bfHQIj/a6szdOZ4A=="
		formData.ReturnUrl = "https://pay.vvic.com/payment/callback/pay-gateway/alipay/order-create/return_url"
		formData.NotifyUrl = "https://paygwcb.vvic.com/pay-gateway/channel/v1/alipay-official/page/notify-url"
		formData.SignType = "RSA2"
		formData.Timestamp = "2025-08-06 21:10:58"
		formData.Version = "1.0"
		formData.AppId = "2019011963101126"
		formData.Format = "json"
		return formData
	}

	// 查找表单结束位置
	formEnd := strings.Index(content[formStart:], "</form>")
	if formEnd == -1 {
		formEnd = len(content)
	} else {
		formEnd += formStart + len("</form>")
	}

	// 提取表单内容
	formContent := content[formStart:formEnd]

	// 解析action属性
	actionRe := regexpAction.FindStringSubmatch(formContent)
	if len(actionRe) > 1 {
		actionURL := actionRe[1]
		parsedURL, err := url.Parse(actionURL)
		if err == nil {
			formData.Action = fmt.Sprintf("%s://%s%s", parsedURL.Scheme, parsedURL.Host, parsedURL.Path)

			// 解析查询参数
			params := parsedURL.Query()
			formData.Charset = params.Get("charset")
			formData.Method = params.Get("method")
			formData.Sign = params.Get("sign")
			formData.ReturnUrl = params.Get("return_url")
			formData.NotifyUrl = params.Get("notify_url")
			formData.SignType = params.Get("sign_type")
			formData.Timestamp = params.Get("timestamp")
			formData.Version = params.Get("version")
			formData.AppId = params.Get("app_id")
			formData.Format = params.Get("format")
		}
	}

	return formData
}

// 预编译正则表达式提高性能
var regexpAction = regexp.MustCompile(`action="([^"]+)"`)

func generateHTMLPage(formData AlipayFormData) error {
	// 定义HTML模板
	htmlTemplate := `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>跳转到支付宝支付页面</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background-color: #f5f5f5;
        }
        .container {
            text-align: center;
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .button {
            background-color: #00a3ee;
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #008cd4;
        }
        .info {
            margin-bottom: 20px;
            color: #666;
        }
        .params {
            text-align: left;
            background-color: #f8f8f8;
            padding: 15px;
            border-radius: 4px;
            margin-top: 20px;
            font-size: 14px;
        }
        .param-item {
            margin-bottom: 8px;
        }
        .param-name {
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>支付跳转页面</h1>
        <div class="info">
            <p>点击下面的按钮将跳转到支付宝支付页面</p>
        </div>
        <button class="button" onclick="submitForm()">跳转到支付宝支付</button>

        <!-- 隐藏的表单 -->
        <form id="redirectForm" name="punchout_form" method="post" action="{{.Action}}">
            <input type="hidden" name="charset" value="{{.Charset}}">
            <input type="hidden" name="method" value="{{.Method}}">
            <input type="hidden" name="sign" value="{{.Sign}}">
            <input type="hidden" name="return_url" value="{{.ReturnUrl}}">
            <input type="hidden" name="notify_url" value="{{.NotifyUrl}}">
            <input type="hidden" name="sign_type" value="{{.SignType}}">
            <input type="hidden" name="timestamp" value="{{.Timestamp}}">
            <input type="hidden" name="version" value="{{.Version}}">
            <input type="hidden" name="app_id" value="{{.AppId}}">
            <input type="hidden" name="format" value="{{.Format}}">
        </form>

        <div class="params">
            <h3>支付参数信息:</h3>
            <div class="param-item"><span class="param-name">Charset:</span> {{.Charset}}</div>
            <div class="param-item"><span class="param-name">Method:</span> {{.Method}}</div>
            <div class="param-item"><span class="param-name">Sign Type:</span> {{.SignType}}</div>
            <div class="param-item"><span class="param-name">Timestamp:</span> {{.Timestamp}}</div>
            <div class="param-item"><span class="param-name">Version:</span> {{.Version}}</div>
            <div class="param-item"><span class="param-name">App ID:</span> {{.AppId}}</div>
            <div class="param-item"><span class="param-name">Format:</span> {{.Format}}</div>
        </div>

        <script>
            function submitForm() {
                document.getElementById('redirectForm').submit();
            }
            
            // 页面加载完成后可选择是否自动跳转
            window.onload = function() {
                // 如果需要自动跳转，取消下面这行的注释
                // submitForm();
            }
        </script>
    </div>
</body>
</html>`

	// 解析模板
	tmpl, err := template.New("alipay").Parse(htmlTemplate)
	if err != nil {
		return err
	}

	// 创建输出文件
	file, err := os.Create("alipay_redirect.html")
	if err != nil {
		return err
	}
	defer file.Close()

	// 执行模板并写入文件
	err = tmpl.Execute(file, formData)
	if err != nil {
		return err
	}

	return nil
}

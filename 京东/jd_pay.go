package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// 京东支付接口示例
func main() {
	//jdPay()
	// 示例使用
	payId := "0143073184024874ad3a9b12f71afceb"
	eid := "225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQ"

	resp, err := CreateJDPay(payId, eid)
	if err != nil {
		fmt.Printf("创建支付失败: %v\n", err)
		return
	}
	fmt.Printf("支付响应: %+v\n", resp)
	fmt.Printf("微信支付链接: %s\n", resp.PayInfo.MwebURL)
}

func jdPay() {
	// 请求URL
	apiURL := "https://api.m.jd.com/client.action?functionId=platWapWXPay&appid=mcashier&scval=mpay"

	// 构建请求体
	data := url.Values{}
	data.Set("body", `{"appId":"m_kSqlzBic","payId":"0143073184024874ad3a9b12f71afceb","eid":"225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQ","source":"mcashier","origin":"h5","mcashierTraceId":1744890532781}`)
	data.Set("x-api-eid-token", "jdd03225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQAAAAMWIOKDY6IAAAAACCTHY4I7MV7VBAX")
	data.Set("h5st", "20250417195452280;9144993414603527;303a7;tk03w87ab1b2018nLEF5wAKuGLrTpRWSR8LzLYFd1OinDhbEq-9v5wUHJAAtiQin2oM3e80AEzfw031PX88ZJwScD4go;1577540b2f6e694339155e802984cfc86a0bfbaed2f9af5afdf4b17cf025c92d;3.1;1744890892280;62f4d401ae05799f14989d31956d3c5ff9d35894c0cddd9a08e2fe40b8bf72210a5aa1465bc1dd53091b529144bf5e400aedfae6101bc11e79cf6183417750665c6c14ee231b1730ba326ada6d6fbdaa759e23c42eac85a22e7e0dd559740d70b2d90e143289aa082f5efbec2999832a")

	// 创建请求
	req, err := http.NewRequest("POST", apiURL, strings.NewReader(data.Encode()))
	if err != nil {
		fmt.Printf("创建请求失败: %v\n", err)
		return
	}

	// 设置请求头
	req.Header.Set("Host", "api.m.jd.com")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36 EdgA/135.0.0.0")
	req.Header.Set("Origin", "https://mpay.m.jd.com")
	req.Header.Set("Referer", "https://mpay.m.jd.com/")
	req.Header.Set("x-referer-page", "https://mpay.m.jd.com/mpay.f129e5329c5358dbb38b.html")
	req.Header.Set("x-rp-client", "h5_1.0.0")

	// 设置Cookie（这里只设置了几个关键Cookie）
	cookies := []string{
		"pt_key=AAJoAN4zADBfHNDU2e2RzpF633dvty6VKlKsbQ3aHI_747ywhqN1vtHWMn7qiq84ayuo90-aZb8",
		"pt_pin=wjf19940211",
		"pt_token=3t0ivuah",
	}
	req.Header.Set("Cookie", strings.Join(cookies, "; "))

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("请求失败: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("读取响应失败: %v\n", err)
		return
	}

	fmt.Printf("响应状态码: %d\n", resp.StatusCode)
	fmt.Printf("响应内容: %s\n", string(body))
}

// PayRequest 支付请求参数
type PayRequest struct {
	AppID           string `json:"appId"`
	PayID           string `json:"payId"`
	EID             string `json:"eid"`
	Source          string `json:"source"`
	Origin          string `json:"origin"`
	McashierTraceId int64  `json:"mcashierTraceId"`
}

// PayResponse 支付响应结构
type PayResponse struct {
	Code    string `json:"code"`
	PayID   string `json:"payId"`
	PayInfo struct {
		PayEnum  string `json:"payEnum"`
		MwebURL  string `json:"mweb_url"`
		PrepayId string `json:"prepayId"`
		PayId    string `json:"payId"`
	} `json:"payInfo"`
	PayScene string `json:"payScene"`
}

func CreateJDPay(payId string, eid string) (*PayResponse, error) {
	// 构建请求参数
	payReq := PayRequest{
		AppID:           "m_kSqlzBic",
		PayID:           payId,
		EID:             eid,
		Source:          "mcashier",
		Origin:          "h5",
		McashierTraceId: time.Now().UnixMilli(),
	}

	// 序列化请求体
	bodyBytes, err := json.Marshal(payReq)
	if err != nil {
		return nil, fmt.Errorf("序列化请求参数失败: %v", err)
	}

	// 构建表单数据
	data := url.Values{}
	data.Set("body", string(bodyBytes))
	data.Set("x-api-eid-token", eid)
	// h5st参数需要根据实际情况生成
	data.Set("h5st", "这里需要实现h5st的生成算法")

	// 创建请求
	apiURL := "https://api.m.jd.com/client.action?functionId=platWapWXPay&appid=mcashier&scval=mpay"
	req, err := http.NewRequest("POST", apiURL, strings.NewReader(data.Encode()))
	if err != nil {
		return nil, fmt.Errorf("创建请求失败: %v", err)
	}

	// 设置请求头
	req.Header.Set("Host", "api.m.jd.com")
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36 EdgA/135.0.0.0")
	req.Header.Set("Origin", "https://mpay.m.jd.com")
	req.Header.Set("Referer", "https://mpay.m.jd.com/")
	req.Header.Set("x-referer-page", "https://mpay.m.jd.com/mpay.f129e5329c5358dbb38b.html")
	req.Header.Set("x-rp-client", "h5_1.0.0")

	// 设置Cookie
	cookies := []string{
		"pt_key=你的pt_key",
		"pt_pin=你的pt_pin",
		"pt_token=你的pt_token",
	}
	req.Header.Set("Cookie", strings.Join(cookies, "; "))

	// 发送请求
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("请求失败: %v", err)
	}
	defer resp.Body.Close()

	// 读取响应
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("读取响应失败: %v", err)
	}

	// 解析响应
	var payResp PayResponse
	if err := json.Unmarshal(body, &payResp); err != nil {
		return nil, fmt.Errorf("解析响应失败: %v", err)
	}

	return &payResp, nil
}

package main

import (
	"compress/gzip"
	"fmt"
	"io"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"

	"github.com/andybalholm/brotli"
)

// 京东支付接口示例
func main() {
	jdPay() // 取消注释，启用支付接口测试
	// getCurrentOrder()
}

func jdPay() {
	// 请求URL
	apiURL := "https://api.m.jd.com/client.action?functionId=platWapWXPay&appid=mcashier&scval=mpay"

	// 构建请求体
	data := url.Values{}
	data.Set("body", `{"appId":"m_kSqlzBic","payId":"5e62a75649a24c14b5f55158cbb03003","eid":"225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQ","source":"mcashier","origin":"h5","mcashierTraceId":1744903907236}`)
	data.Set("x-api-eid-token", "jdd03225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQAAAAMWIRQKSRYAAAAADULPHIDC4PCT3IX")
	data.Set("h5st", "20250417233156601;9144993414603527;303a7;tk03w87ab1b2018nLEF5wAKuGLrTpRWSR8LzLYFd1OinDhbEq-9v5wUHJAAtiQin2oM3e80AEzfw031PX88ZJwScD4go;f747f565489867bb2666cbabc969de239709893dd462a5ddde6ec7d59edf7b52;3.1;1744903916601;62f4d401ae05799f14989d31956d3c5ff9d35894c0cddd9a08e2fe40b8bf72210a5aa1465bc1dd53091b529144bf5e400aedfae6101bc11e79cf6183417750665c6c14ee231b1730ba326ada6d6fbdaa759e23c42eac85a22e7e0dd559740d70b2d90e143289aa082f5efbec2999832a")

	// 创建请求
	req, err := http.NewRequest("POST", apiURL, strings.NewReader(data.Encode()))
	if err != nil {
		fmt.Printf("创建请求失败: %v\n", err)
		return
	}

	// 设置请求头
	req.Header.Set("Host", "api.m.jd.com")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("sec-ch-ua-platform", "Android")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36 EdgA/135.0.0.0")
	req.Header.Set("sec-ch-ua", `"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"`)
	req.Header.Set("accept", "application/json, text/plain, */*")
	req.Header.Set("x-referer-page", "https://mpay.m.jd.com/mpay.f129e5329c5358dbb38b.html")
	req.Header.Set("content-type", "application/x-www-form-urlencoded")
	req.Header.Set("x-rp-client", "h5_1.0.0")
	req.Header.Set("sec-ch-ua-mobile", "?1")
	req.Header.Set("Origin", "https://mpay.m.jd.com")
	req.Header.Set("Sec-Fetch-Site", "same-site")
	req.Header.Set("Sec-Fetch-Mode", "cors")
	req.Header.Set("Sec-Fetch-Dest", "empty")
	req.Header.Set("Referer", "https://mpay.m.jd.com/")
	req.Header.Set("Accept-Encoding", "gzip, deflate, br, zstd")
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6")

	// 设置完整的Cookie
	cookies := []string{
		"unpl=JF8EAKRnNSttUE9dV0xWHxBAH1UGW15YQ0cCaGYBUlldQgZWGQobERN7XlVdWRRKFR9vbxRVVFNJVQ4ZCisSF3teVV1eCE8VAGhgNWRtW0tkBCsCHRcTSVhRXVgJTRYHb28HV1VRT1MCEzIaIhdLVGReXwxIFwNoZjVkXGhKZAQrVHUSEUpcVV9YDEwQTm9hAFdfXU5XABoEGhYQQ19XVlQMTBALX2Y1Vw",
		"mba_muid=17423442407051932985669",
		"retina=1",
		"cid=9",
		"webp=1",
		"visitkey=8236189737561370883",
		"sc_width=360",
		"pt_key=AAJoAN4zADBfHNDU2e2RzpF633dvty6VKlKsbQ3aHI_747ywhqN1vtHWMn7qiq84ayuo90-aZb8",
		"pt_pin=wjf19940211",
		"pt_token=3t0ivuah",
		"pwdt_id=wjf19940211",
		"sdtoken=AAbEsBpEIOVjqTAKCQtvQu176s6p0Zeh9_k-MHlpaFQBYJtEaH-kW1qjSbn69KkuX6uaVfw_BX8n5dQdDRbFyq7rqnQ3PJU4_GB0I44--zQJGXmVukcN3YM7RnwQCfibNua6d2Wy7-JsGZ1Z7pMRBiS1Rg",
		"__jd_ref_cls=MCashierNew_ConfirmPayment",
	}
	req.Header.Set("Cookie", strings.Join(cookies, "; "))

	// 修改 http.Client，添加自动处理压缩的传输
	client := &http.Client{
		Transport: &http.Transport{
			DisableCompression: false,
		},
	}

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("请求失败: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// 根据 Content-Encoding 处理响应
	var reader io.Reader
	switch resp.Header.Get("Content-Encoding") {
	case "gzip":
		reader, err = gzip.NewReader(resp.Body)
		if err != nil {
			fmt.Printf("创建 gzip reader 失败: %v\n", err)
			return
		}
		defer reader.(*gzip.Reader).Close()
	case "br":
		reader = brotli.NewReader(resp.Body)
	default:
		reader = resp.Body
	}

	// 读取响应
	body, err := ioutil.ReadAll(reader)
	if err != nil {
		fmt.Printf("读取响应失败: %v\n", err)
		return
	}

	fmt.Printf("响应状态码: %d\n", resp.StatusCode)
	fmt.Printf("响应内容: %s\n", string(body))
}

// 新增订单查询函数
func getCurrentOrder() {
	apiURL := "https://api.m.jd.com/client.action"

	data := url.Values{}
	data.Set("client", "Linux armv81")
	data.Set("clientVersion", "2.5.2")
	data.Set("osVersion", "other")
	data.Set("screen", "360*780")
	data.Set("networkType", "false")
	data.Set("d_brand", "")
	data.Set("d_model", "")
	data.Set("lang", "zh-CN")
	data.Set("sdkVersion", "2.5.2")
	data.Set("appid", "m_core")
	data.Set("openudid", "")
	data.Set("x-api-eid-token", "jdd03225EAZ7YH3TNTBALAKUIVIKTE5TAOKR5CZJGFFEMPAXD3RK3YKNNQELZ3REJJIGIITKRIV5KLYVKRQURU4HQJ7CWFQ")
	data.Set("functionId", "balance_getCurrentOrder_m")
	data.Set("uuid", "17423442407051932985669")
	data.Set("loginType", "2")
	data.Set("t", fmt.Sprintf("%d", time.Now().UnixMilli()))
	data.Set("scval", "845197")
	data.Set("xAPIScval3", "unknown")

	// 构建请求体
	bodyStr := `{"deviceUUID":"8236189737561370883","appId":"wxae3e8056daea8727","appVersion":"2.5.2","tenantCode":"jgm","bizModelCode":"3","bizModeClientType":"M","token":"3852b12f8c4d869b7ed3e2b3c68c9436","externalLoginType":1,"referer":"https://item.m.jd.com/","resetGsd":true,"useBestCoupon":"1","locationId":"1-72-2819-0","packageStyle":true,"sceneval":"2","balanceCommonOrderForm":{"supportTransport":false,"action":1,"overseaMerge":false,"international":false,"netBuySourceType":0,"appVersion":"2.5.2","tradeShort":false},"balanceDeviceInfo":{"resolution":"360*780","networkType":"wifi"},"cartParam":{"skuItem":{"skuId":"845197","num":"1","orderCashBack":false,"extFlag":{}}}}`
	data.Set("body", bodyStr)

	// h5st参数需要根据实际情况生成
	data.Set("h5st", "20250417231506648;xx3pzpwg3mpqjj09;bd265;tk03w7d631bc718ng81EQYO7Ev0bF0pBI3_PmLQ8pJEWuzKLLZDNiewtqA-bScoa6W_jvKO45ccBJpFyzyCICS9GeuPl;802bed543028e8e606e75a8daa54b7eb;5.1;1744902905648;t6HsMKriEFYS_54iHRnS0t3i2NHmOGLm_VImOuMsCOrm0mMTLhImOuMsCmMhNVrg_eYg5iLi3aog2qrVJlrV2iLVMZLV6qoi5u7W9msm0msSo94VMZ4RMusmk_MmJhYi7i4i2aoh2SLW7ebWNVbV4SrgLlbgMlIh1qYVMJLmOGLm7pIRAp4WMusmk_siOGLm6aHWMusmk_Mm82ciAaLRPZoTFV4X5OImOGLm4lsmOGujMK7d9qpd8WaT_SqcMuMgM64TK1YW8lsmOGujMqrg45ISNtsQ51YUilsm0mMV_lsmOGujxtsmkmrm0mci9aHWMusmOuMsCKrm0msi9aHWMusmOuMsCObjOGLm8qbRMlsmOusmk_MmjVohDNIiiZbbj1KmOGLmBxoVApISMusmOuMsCurm0msg5lImOusmOGuj_uMgMSbRMlsmOusmk_ciBuMgMWbRMlsmOusmk_siOGLm5aHWMusmOuMsCurm0msh5lImOusmOGuj3irm0m8i5lImOusmOGujMubiAqLj_msm0mci5lImOusmOGuj_uMgMC4RMusmOuMsCqbjOGLm79ImOusmOGuj_uMgM_ImOusmOGuj_uMgMe4RMusmOuMsztMgMeITJdnQJlsmOGujxtsmkmci9mri6Kbg9WIU3lsm0mci_lsmOusmkCnm0msS_lsmOGujMCqmzubiOeYU-lnVApqmzOXRAJobMuMgMqYR7lsmOG_Q;3df5d4621b1b4e48dd964b6bacf3d5cd")

	// 创建请求
	req, err := http.NewRequest("POST", apiURL, strings.NewReader(data.Encode()))
	if err != nil {
		fmt.Printf("创建请求失败: %v\n", err)
		return
	}

	// 设置请求头
	req.Header.Set("Host", "api.m.jd.com")
	req.Header.Set("Connection", "keep-alive")
	req.Header.Set("sec-ch-ua-platform", "Android")
	req.Header.Set("User-Agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Mobile Safari/537.36 EdgA/135.0.0.0")
	req.Header.Set("sec-ch-ua", `"Microsoft Edge";v="135", "Not-A.Brand";v="8", "Chromium";v="135"`)
	req.Header.Set("x-referer-page", "https://trade.m.jd.com/pay")
	req.Header.Set("content-type", "application/x-www-form-urlencoded")
	req.Header.Set("x-rp-client", "h5_1.0.0")
	req.Header.Set("sec-ch-ua-mobile", "?1")
	req.Header.Set("Accept", "*/*")
	req.Header.Set("Origin", "https://trade.m.jd.com")
	req.Header.Set("Sec-Fetch-Site", "same-site")
	req.Header.Set("Sec-Fetch-Mode", "cors")
	req.Header.Set("Sec-Fetch-Dest", "empty")
	req.Header.Set("Referer", "https://trade.m.jd.com/")
	req.Header.Set("Accept-Encoding", "gzip, deflate, br, zstd")
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.9,en-GB;q=0.8,en-US;q=0.7,en;q=0.6")

	// 设置Cookie
	cookies := []string{
		"unpl=JF8EAKRnNSttUE9dV0xWHxBAH1UGW15YQ0cCaGYBUlldQgZWGQobERN7XlVdWRRKFR9vbxRVVFNJVQ4ZCisSF3teVV1eCE8VAGhgNWRtW0tkBCsCHRcTSVhRXVgJTRYHb28HV1VRT1MCEzIaIhdLVGReXwxIFwNoZjVkXGhKZAQrVHUSEUpcVV9YDEwQTm9hAFdfXU5XABoEGhYQQ19XVlQMTBALX2Y1Vw",
		"mba_muid=17423442407051932985669",
		"retina=1",
		"cid=9",
		"webp=1",
		"visitkey=8236189737561370883",
		"sc_width=360",
		"pt_key=AAJoAN4zADBfHNDU2e2RzpF633dvty6VKlKsbQ3aHI_747ywhqN1vtHWMn7qiq84ayuo90-aZb8",
		"pt_pin=wjf19940211",
		"pt_token=3t0ivuah",
	}
	req.Header.Set("Cookie", strings.Join(cookies, "; "))

	// 修改 http.Client，添加自动处理压缩的传输
	client := &http.Client{
		Transport: &http.Transport{
			DisableCompression: false,
		},
	}

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("请求失败: %v\n", err)
		return
	}
	defer resp.Body.Close()

	// 根据 Content-Encoding 处理响应
	var reader io.Reader
	switch resp.Header.Get("Content-Encoding") {
	case "gzip":
		reader, err = gzip.NewReader(resp.Body)
		if err != nil {
			fmt.Printf("创建 gzip reader 失败: %v\n", err)
			return
		}
		defer reader.(*gzip.Reader).Close()
	case "br":
		reader = brotli.NewReader(resp.Body)
	default:
		reader = resp.Body
	}

	// 读取响应
	body, err := ioutil.ReadAll(reader)
	if err != nil {
		fmt.Printf("读取响应失败: %v\n", err)
		return
	}

	fmt.Printf("响应状态码: %d\n", resp.StatusCode)
	fmt.Printf("响应内容: %s\n", string(body))
}

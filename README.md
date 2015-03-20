# 微信APP支付

最近微信支付莫名其妙的进行了升级，在[微信开放平台](https://open.weixin.qq.com/)提交的移动应用开发中微信支付，如果收到的是这样的[邮件](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=3_1)则无法使用在开放平台的移动应用开发的[文档](http://wxpay.weixin.qq.com/doc/download/wx_pay_app.zip)。因为邮件中少了2个关键的KEY：`paySignKey`, `partnerKey`。

一直询问支持，给的都是[支付开发教程（微信商户平台版）
 ](https://mp.weixin.qq.com/paymch/readtemplate?t=mp/business/course3_tmpl)，研究了下，都是公众号的开发。

后面找到了这份[文档](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=8_1)，研究了一番，依旧觉得是公众号的，里面的[统一下单](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_1)需要个openid，这分明是微信公众号的开发。后面看到openid只是在公众号开发的时候才传递，所以决定按照这份文档一试。

按照文档中的[业务流程](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=8_3)，当进行到第三步的时候，文档这样说:
>步骤3：统一下单接口返回正常的prepay_id，再按签名规范重新生成签名后，将数据传输给APP。参与签名的字段名为appId，partnerId，prepayId，nonceStr，timeStamp，package。注意：package的值格式为prepay_id=wx20141009175351724b348a500087751557

但是我我找遍了所有地方，都没有说明这个`package`具体的事例，以及参加签名的字段`partnerId`是老文档中的描述，而且这里的字符串怎么突然有大小写了？后面参考了老文档，成功了。
> 3.5 添加 prepayid 再次签名
获取到 prepayid 后,将参数 appid、appkey、noncestr、package(注意:此处应置为 Sign=WXPay)、partnerid、prepayid、timestamp 签名后返回给 APP,签名方法跟 3.4 节
app_signature 说明一致。得到参数列表如下,通过这些参数即可在客户端调起支付。
{
"appid":"wxd930ea5d5a258f4f", "noncestr":"139042a4157a773f209847829d80894d", "package":"Sign=WXpay";
"partnerid":"1900000109" "prepayid":"1101000000140429eb40476f8896f4c9", "sign":"7ffecb600d7157c5aa49810d2d8f28bc2811827b", "timestamp":"1398746574"
}

总结下开发：
 - 先按照[同一下单请求参数](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=9_1)去获取`prepay_id`
 - 得到`prepay_id`, 参考上面的 **3.5 添加 prepayid 再次签名**


然后再吐槽下微信支付：新接口获取`prepay_id`确实方便了很多，不需要去获取token、packge，请求与接收都有`JSON`换成了`XML`。但接口更新也不正式的声明下，文档也乱写，[DEMO](http://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=11_1)也没用完全开放出来，坑啊！
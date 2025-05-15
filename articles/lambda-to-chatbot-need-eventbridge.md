---
title: AWS LambdaからChatbotでSlack投稿するまで
emoji: 🐼
type: tech
topics:
  - Amazon EventBridge

published: false
---
LambdaからChatbotは直接はいけません。
https://docs.aws.amazon.com/ja_jp/chatbot/latest/adminguide/related-services.html
EventBridgeを経由するのがよさそうです。

EventBridgeからCahtbotも直ではいけません。


EventBridgeルールを作って、カスタムルールを待ち受けるようにします。

## 呼び出せるLambdaに制限をつける
制限したい場合はEventBridgeルールに制限をつけることができます。

もしくはEventBusを経由させて、 EventBusPolicyで制限をつけることもできます。 EventBusPolicyはカスタマーマネージドポリシーをアタッチすることはできず、 その場で書く必要があります。



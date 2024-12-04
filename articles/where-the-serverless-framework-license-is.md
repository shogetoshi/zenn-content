---
title: Serverless Framework V4のライセンス情報の置き場所について考えてみた
emoji: 🐼
type: tech
topics:
  - Serverless Framework
published: true
---
[Serverless Framework](https://www.serverless.com/) V4は有料のライセンスを購入して利用する形となります。

デプロイを行うときにライセンスキー情報が必要となりますが、 最初にデプロイを行おうとすると
```bash
? Serverless Framework V.4 requires an account or a license key. Please login/register or enter your license key. …
❯ Login/Register
  Get A License
  Enter A License Key
  Explain Licensing Basics
```
こんな選択画面が表示されて、ライセンスキーを入力することができます。 （ちなみにこの選択肢の移動に「Ctrl-p,n」のようなキーを入力すると、 表示がおかしくなって目的のものが選べなくなってしまいます。 おとなしく矢印キーで操作するのが良さそうです）

私も初回にこれをやってライセンスキーを登録したのですが、 そのことをすっかり忘れて、 「ライセンスキーを入力していないのに、なぜかデプロイができる！？」 と混乱していました。 自分の操作メモを見てこんな画面で入力したことは思い出せたのですが、 どこにこの情報が保存されているかわからず探し回ることになりました。

そして無事目的のファイルを見つけることができたのですが、 その場所にあることを考えるとライセンス情報の保持の仕方には注意が必要そうなことがわかったので、対策を調べてみました。
## どこにあるか
`~/.serverlessrc`にありました。

中に`accessKeys`という項目があり、組織IDやアクセスキーが記載されていました。
```json
"accessKeys": {
  "orgs": {
    "___org_name___": {
      "accessKey": "XXXX",
      "orgName": "___org_name___",
      "orgId": "XXXX"
    }
  },
  "defaultOrgName": "___org_name___"
}
```
### ファイルの取り扱いに関する注意
このファイルがホームディレクトリ直下に置かれています。 ホームディレクトリにあるということは、 この情報はそのユーザがどのディレクトリにおいても利用される可能性があるということを意味します。 そしてそれは、複数のプロジェクトをまたがって、 別のライセンスを利用してしまう可能性があるということも意味しています！ これは対策が必要そうです。
### 解決策
公式のドキュメントを確認しましょう。
https://www.serverless.com/framework/docs/guides/license-keys
2つの解決策が示されています。
1. 環境変数に設定する
2. AWSのパラメータストア or SecretsManager or HashicorpのVaultを使う

環境変数を使うやり方ではデプロイを行う各ユーザが自分でライセンスキーを管理する必要があり、 キーが漏洩するリスクが高くなります。 ここは2の方法を使うのが良さそうです。

私はAWS環境へのデプロイを目的にServerless Frameworkを利用しているので、 SSMパラメータストアにSecureStringで配置する方法を取ることにしました。
## ライセンス場所の探し方
`~/.serverlessrc`を探した方法としては、 `sls`コマンドに`--debug`オプションつけて実行すればわかりました。
```bash
$ sls --debug
```
とするとその中に
```
s:core:auth:get-authenticated-data: license key found in .serverlessrc
```
という記載があるのを見つけました。 ディレクトリが示されていないのですが、 カレントディレクトリではなくホームディレクトリに存在していました。

なお、このファイルをプロジェクトのディレクトリなどに配置したら、 プロジェクトごとに使い分けができるのではないかと思って試してみましたが、 ホームディレクトリ以外の場所にあっても探してくれないようでした。
## まとめ
Serverless Framework V4のライセンスをどう管理するかについて少し調べてみました。 ライセンスキーは個人のPC環境で管理するリスクが高いものですので、 パラメータストアなどの環境に適切な暗号化設定をした上で保存するのが良さそうです。

以上、誰かの参考になれば幸いです。

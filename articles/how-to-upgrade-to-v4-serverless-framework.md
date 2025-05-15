---
title: 既存のServerless Framework環境をV4に変更する
emoji: 🐼
type: tech
topics:
  - ServerlessFramework
  - npm

published: false
---
yarn前提
## Serverless.yaml
バージョン番号を書き換えて、SSMパラメータストアにおいたライセンスキーを参照するように設定します。
```yaml
frameworkVersion: "4"
licenseKey: ${ssm:/PROJECT_NAME/dev/Serverless/LicenseKey}
```
また、この時確実にパラメータストアのライセンスキーが使われるように、 `~/.serverlessrc`にライセンス情報がないかも確認するのが良いと思います。
https://dev.classmethod.jp/articles/where-the-serverless-framework-license-is/
## node_modules
削除しました。
## package.json
```json:package.json
{
  "dependencies": {
    "serverless": "^3.34.0",
    "serverless-prune-plugin": "^2.0.2",
    "serverless-python-requirements": "^6.0.0"
  }
}
```
のようになっていたので、この部分を削除します。
## yarn-lock.json
削除しました。
## 改めてインストール
```bash
$ npm install serverless serverless-prune-plugin serverless-python-requirements
```
これでv4のServerlessFrameworkがインストールされました。

```json:package.json
{
  "dependencies": {
    "serverless": "^4.4.14",
    "serverless-prune-plugin": "^2.1.0",
    "serverless-python-requirements": "^6.1.1"
  }
}
```
## CodeBuildの対応
`buildspec.yaml`の`nodejs`が16だったので、これを上げる必要がありました。

またそのために、使っていたコンテナイメージを変更しました。
```
前: aws/codebuild/standard:6.0
後: aws/codebuild/standard:7.0
```

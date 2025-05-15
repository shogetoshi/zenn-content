---
title: "[Redshift] テーブルへのアクセス権付与権限について調べてみた"
emoji: 🐼
type: tech
topics:
  - Redshift

published: false
---
DBでは一般に、「あるユーザがあるテーブルにアクセスできる権限」という概念が存在します。 これはまぁ当たり前の話なので特に疑問を持つ人もいないかと思います。

一方で、「あるユーザが、他のユーザがあるテーブルにアクセスできる権限を付与できる権限」という概念が存在することはご存知でしょうか？ はい、私は知りませんでした。

今回はこの「テーブルへのアクセス権を付与できる権限」について調べてみました。 今回はこの概念のことを「アクセス権付与権限」と表記します。 ややこしいです。

:::message
今回はわかりやすさのためにpublicスキーマを利用します。 Redshiftにおいてpublicスキーマは特別なスキーマで、 明示的な権限付与を行わずに全てのユーザがアクセス可能です。 以下の文章で単に「テーブルへのアクセス権を付与」や「テーブルへのアクセス権付与権限を付与」と言った場合には、 public以外のスキーマにおいては、スキーマへの`USAGE`権限についても同様に付与が必要となります。
:::

## アクセス権付与権限を持つか確認
アクセス権付与権限を持つかどうかは以下のようなクエリで調べることができました（以降「アクセス権付与権限確認クエリ」と呼びます）。

```sql
SELECT
  namespace_name AS schema_name,
  relation_name AS table_name,
  privilege_type,
  identity_name,
  identity_type,
  admin_option
FROM SVV_RELATION_PRIVILEGES
;
```
結果はこんな感じです。
```
|schema_name|table_name|privilege_type|identity_name|identity_type|admin_option|
|-----------|----------|--------------|-------------|-------------|------------|
|schema_a   |table_a   |INSERT        |user_a       |user         |false       |
|schema_a   |table_a   |SELECT        |group_a      |group        |false       |
```
### 読み方
カラムが多くて難しいですが、`admin_option`以外全てがキーと考えましょう。 つまり、

「`schema_name.table_name`テーブルに`privilege_type`するための権限について、 `identity_name`（これはタイプとしては`identity_type`である）が アクセス権付与権限を持つかどうか（`admin_option`）。」

という読み方となります。

この結果を見ると、 アクセス権付与権限はuserだけでなくgroupにも付与できることがわかります （この例には出ていませんが、roleも同じです）。 またこの表はRELATION（＝テーブル）についての表ですが、 以下のように、SCHEMAなどについても同じ概念を確認するテーブルが用意されています。
- SVV_DATABASE_PRIVILEGES
- SVV_SCHEMA_PRIVILEGES
- SVV_FUNCTION_PRIVILEGES
- SVV_LANGUAGE_PRIVILEGES
#### 結果テーブルのもう一つの意味
この結果テーブルはアクセス権付与権限があるかないかを表していますが、 実はそれだけでなく「アクセス権があるか」についても読み取ることができます。

というのも、このテーブルの行としてデータが存在するということは 「アクセス権がある」ということを表しているらしく、 そもそもアクセス権がないテーブルについてはアクセス権付与権限の有無という概念が存在しないようです。 「アクセス権はないけどアクセス権付与権限はある」という状態も論理的には存在しうるわけですが、 この表の挙動から推測するに、Redshiftにはそういう状態は存在しないようです。
## アクセス権付与権限の挙動を確認してみる
ざっくりと概要がわかったところで、実際に挙動を確認してみます。
### ユーザ作成
スーパーユーザで3人のユーザを作ります。 デフォルトではテーブルに対して何も権限を持たない無力な3人です。
```sql
-- スーパーユーザで実行
CREATE USER user_a PASSWORD 'Passw0rd';
CREATE USER user_b PASSWORD 'Passw0rd';
CREATE USER user_c PASSWORD 'Passw0rd';
```
### 権限の確認
3人とも同じ権限のはずですので、代表としてuser_aを見てみます。
```sql
-- スーパーユーザで実行
SELECT
  namespace_name AS schema_name,
  relation_name AS table_name,
  privilege_type,
  identity_name,
  identity_type,
  admin_option
FROM SVV_RELATION_PRIVILEGES
where identity_name = 'user_a'
;
```
結果は0行でした。 user_aはどのテーブルも参照することができないので、 1行も結果がないものと考えられます。
### user_aにアクセス権を付与
user_aに「アクセス権」を付与してから権限を確認してみます。
```sql
-- スーパーユーザで実行
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_a;
```
この状態でアクセス権付与権限確認クエリを流すと
```
|schema_name|table_name   |privilege_type|identity_name|identity_type|admin_option|
|-----------|-------------|--------------|-------------|-------------|------------|
|public     |table_a      |SELECT        |user_a       |user         |false       |
```
こんな感じで、table_aに対してSELECT権限が付与されたことが確認できます。 このとき`admin_option`はfalseです。
### user_bにアクセス権付与権限を付与
user_bには「アクセス権付与権限」を付与して確認してみます。
```sql
-- スーパーユーザでJikkou
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_b WITH GRANT OPTION;
```
`WITH GRANT OPTION`がポイントです。

アクセス権付与権限確認クエリの結果は
```
|schema_name|table_name   |privilege_type|identity_name|identity_type|admin_option|
|-----------|-------------|--------------|-------------|-------------|------------|
|public     |table_a      |SELECT        |user_b       |user         |true        |
```
となり、アクセス権付与権限が付与されたことがわかります。
### user_cに権限付与してみる
user_aはアクセス権付与権限なし、user_bはありという状態になっています。 このときにuser_cへのアクセス権付与の挙動を見てみます。
#### user_aで実施してみる
権限付与権限がないので失敗するはずです。
```sql
-- user_aで実行
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_c;
```
「Warnings: No privileges were granted.」という表示になりました。想定通りですね。

余談ですが、Redshiftでこの黄色のWarningが出るのは珍しい気がします。
![[PastedImage20241220022150.png]]
#### user_bで実施してみる
こちらはうまくいくはずです。
```sql
-- user_bで実行
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_c;
```
アクセス権付与されたので、user_cでSELECTをしてみるとうまくいきました。 アクセス権付与権限確認クエリの結果も想定通りです。
```
|schema_name|table_name   |privilege_type|identity_name|identity_type|admin_option|
|-----------|-------------|--------------|-------------|-------------|------------|
|public     |table_a      |SELECT        |user_c       |user         |false       |
```
## まとめ
GRANT文に`WITH GRANT OPTION`をつけることで 「権限を付与する権限」を付与できることが確認できました。 私はこのような概念があること自体を把握していませんでしたが、 今回その挙動を理解することができスッキリしました。

この挙動をきちんと理解して権限設定をしていくという場面に 今後出くわすことがあるのかわかりませんが、 権限周りについてちょっと詳しくなれたのでよかったです。

以上、誰かの参考になれば幸いです。

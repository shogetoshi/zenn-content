---
title: Jestでテスト
emoji: 🚀
type: tech
topics:
  - TypeScript
  - Jest

published: true
---
TypeScriptの単体テストに[Jest](https://jestjs.io/ja/)を使ってみました。 TypeScriptで作ったプロジェクトにサクッと導入するために必要な必要最低限の手順をまとめておきたいと思います。
## 利用の準備
必要なパッケージをインストールします。
```bash
$ npm install --save-dev jest ts-jest @types/jest
```
`package.json`の`scripts`セクションに`test`の項目を追加します。
```json:package.json
  "scripts": {
    "test": "jest"
  },
```
また`tsconfig.json`の`compilerOptions`にも設定を加えます。
```json:tsconfig.json
{
  "compilerOptions": {
    "types": ["node", "jest"]
  }
} 
```
次にJestの設定ファイルを下記のように記述します。
```javascript:jest.config.js
module.exports = {
    preset: "ts-jest",
    testEnvironment: "node",
    transform: {
        "^.+\\.tsx?$": "ts-jest",
    },
    moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
};
```
以上で準備は完了です。
## テストしてみる
テスト対象ファイルを準備します。 テストは別ファイルに記述するので関数は`export`する必要があります。
```typescript:calc.ts
export const add = (a: number, b: number): number => {
  return a + b;
};
```
テストファイルを準備します。
```typescript:calc.test.ts
import { add } from "./calc"

test('adds 2 and 3 to equal 5', () => {
    expect(add(2, 3)).toBe(5);
});
```
テストを実行してみます。
```bash
$ npm test

> test
> jest

 PASS  ./calc.test.ts
  ✓ adds 2 and 3 to equal 5 (1 ms)

Test Suites: 1 passed, 1 total
Tests:       1 passed, 1 total
Snapshots:   0 total
Time:        0.524 s, estimated 1 s
Ran all test suites.
```
きちんとテストがPASSしましたのでOKです！
## まとめ
Jestでとりあえず最初のテストを作るところまでできました。 思ったよりも色々なところに設定を加える必要がありますが、 単体テストを書く方が結果的に早く開発が進むということを実感してしまったので、 これでサクッとテストを書いていけます。

以上、誰かの参考になれば幸いです。

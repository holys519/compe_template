# Repository instructions

このリポジトリでは、会話履歴ではなくファイルから実験の現在地を判断する。

最初に次を実行する。

```bash
python3 scripts/status.py
```

実験を追加・変更するときは以下を守る。

1. `spec.toml` に仮説、ベース実験、変更点、成功条件を実行前に記載する。
2. 1つの実験では主因子を1つだけ変える。
3. Macでの検証は `m_experiments/`、RTX 3090での実験は `l_experiments/`、GPUクラスタ・クラウドでの実験は `g_experiments/` に置く。
4. 環境を移す場合は `scripts/promote_experiment.py` を使い、同じ `expNNN` を保つ。
5. すべての実行は `scripts/run_experiment.py` 経由にし、`metrics.json` を必ず生成する。
6. 実験結果を見た後で成功条件を書き換えない。条件を変える場合は新しい実験にする。
7. `data/` を書き換える処理と、学習・推論処理を分ける。元データは不変として扱う。
8. checkpointやキャッシュなどの重量物をGitへ追加しない。
9. Kaggleへの提出や外部へのpushは自動実行しない（スキルや自律ループの「push」はこの方針の下で行う: 認可された運用でのみ、他セッションの差分を含めずに）。

共有化するのは2つ以上の実験で安定したコードだけとし、それまでは各 `expNNN/` 内で完結させる。

## 対戦・シミュレーション系コンペで追加する規則（kaggriculture 2026-09 の教訓）
10. 評価は `docs/evaluation-protocol.md` に従う: seed 台帳に事前登録、同 seed 両席、1 回だけ見る（640-800 seed）、screen は証拠にしない。
11. 最初の 2 日で順位指標を分解した得点表を作り、ローカル指標と本番の相関を確認する。上位の試合は自分で眺める（`docs/experiment-workflow.md`、`.claude/skills/replay-cards`）。
12. 無言のフォールバック（例外→PASS）を禁止し、telemetry と構造ガードを必須にする。新しいランナーは同一性確認から。
13. 複数セッションは `docs/multi-session-coordination.md` に従う（自動追記ファイルの分離、他セッションの差分を add しない、提出は承認制で有効ペアを確認）。
14. 自律ループは `docs/autonomous-loops.md` の基準（SE を測ってから閾値、ラウンド間で分布を引き継ぐ、α=0.005）。他人の agent に層を積むときは `docs/layering-on-foreign-agents.md` の前提を先に確認する。

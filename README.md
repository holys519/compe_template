# Competition experiment template

Kaggle コンペで、Macの軽量検証、RTX 3090の本実験、GPUクラスタ／クラウド実験へ同じ実験番号を引き継ぐためのテンプレートです。
RSNA リポジトリの「仮説を先に書く」「実験ごとに設定と結果を残す」「`metrics.json` を結果の契約にする」という運用を、小さく再利用できる形にしています。

## 対戦・シミュレーション系コンペ向けの追加ガイド（2026-10 追加）

- [評価プロトコル](docs/evaluation-protocol.md)（seed 台帳・事前登録・one look・screen の偽陽性・無言失敗）
- [複数セッションの協調](docs/multi-session-coordination.md)、[日次ループ](docs/daily-loop.md)、[自律ループの設計基準](docs/autonomous-loops.md)、[他人の agent に層を積む前提](docs/layering-on-foreign-agents.md)
- Claude Code skills: `.claude/skills/{paired-eval,daily-loop,review-loop,replay-cards}`
- 実例: kaggriculture リポジトリの `docs/report/kaggriculture_report_20260930.html`、`docs/research/retrospective_mac_20261002.md`

## 環境の使い分け

| ディレクトリ | 環境 | 主な用途 |
|---|---|---|
| `m_experiments/` | Mac（CPU / MPS） | EDA、前処理、単体テスト、少量データでの smoke test |
| `l_experiments/` | RTX 3090（CUDA） | 学習、全データ・全 Fold、速度とVRAMの検証 |
| `g_experiments/` | GPUクラスタ／クラウド | 複数GPU、大規模モデル、長時間実行、Kaggle GPU |

1つの仮説には1つの `expNNN` を割り当てます。Macで成立した `m_experiments/exp001` は、番号を変えずに `l_experiments/exp001`、さらに `g_experiments/exp001` へ昇格します。環境差を新しい実験として数えないためです。

## 最初の5分

Python 3.11 以上だけで実験管理ツールとサンプル実験を動かせます。

```bash
cd compe_template
python3 scripts/new_experiment.py m "baseline" \
  --hypothesis "最小構成のパイプラインがMac上で再現可能に完走する"
python3 scripts/run_experiment.py m exp001
python3 scripts/status.py
python3 -m unittest discover -s tests -v
```

作られた `m_experiments/exp001/` の `config.toml`、`run.py`、`README.md` を編集します。Macで検証できたら3090環境へ昇格します。

```bash
python3 scripts/promote_experiment.py exp001
python3 scripts/run_experiment.py l exp001
python3 scripts/promote_experiment.py exp001 --from l
python3 scripts/run_experiment.py g exp001
python3 scripts/report.py
```

`EXPERIMENT_REPORT.md` に一覧が生成されます。

## ディレクトリ構成

```text
compe_template/
├── configs/                    # 実験をまたいで共有する設定
├── data/                       # Git管理しないデータ置き場
│   ├── raw/
│   ├── interim/
│   └── processed/
├── docs/                       # EDA、CV設計、判断基準
├── m_experiments/              # Mac向けの軽量実験
├── l_experiments/              # RTX 3090向けの本実験
├── g_experiments/              # GPUクラスタ／クラウド向け実験
├── runs/                       # 実行結果。JSONは管理し、重量物は除外
│   ├── m/expNNN/<run_id>/
│   ├── l/expNNN/<run_id>/
│   └── g/expNNN/<run_id>/
├── scripts/                    # 作成、昇格、実行、一覧生成
├── src/compe/                  # 実験間で共有する安定コード
├── templates/experiment/       # 新規実験の雛形
└── tests/
```

## 実験の原則

- 実行前に `spec.toml` の仮説・変更点・成功条件を書く。
- 1実験で変える主因子は1つにする。
- Macでは小さいデータ・短いepochでコードと評価方法を検証する。
- 3090では同じコードと設定キーを使い、データ量・Fold・batch sizeなど計算資源に関わる値だけを変える。
- GPUクラスタ／クラウドでは、同じ実験番号を保ったままGPU数やschedulerなど環境固有の設定を追加する。
- 実行結果は必ず `runs/<env>/<exp>/<run_id>/metrics.json` に書く。
- checkpointなどの重量物は各runの `artifacts/` に置く。Gitには入らない。
- 失敗や不採用も消さず、実験READMEに結論を残す。

詳しい手順は [docs/experiment-workflow.md](docs/experiment-workflow.md) を参照してください。

## コンペ開始時に変更するもの

1. `pyproject.toml` のプロジェクト名と依存関係
2. `configs/default.toml` のデータパスと共通設定
3. `docs/competition.md` の評価指標、提出形式、CV設計
4. `templates/experiment/run.py` を最初のベースラインに合わせる
5. 必要なら `src/compe/` にdataset、model、metricを追加する

データへの絶対パスはコードに書かず、`COMPE_DATA_DIR` または `configs/default.toml` で切り替えます。

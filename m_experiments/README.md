# m_experiments — Mac実験

CPUまたはApple SiliconのMPSで、軽量な実験と検証を行う。

- 少量データ、1 Fold、1〜2 epochを基本にする。
- EDA、前処理、CV分割、metric、データリーク、推論コードを確認する。
- CUDA固有の挙動や最終速度の判断には使わない。
- 成立した実験は `python3 scripts/promote_experiment.py expNNN` で3090へ昇格する。

新規作成:

```bash
python3 scripts/new_experiment.py m "title" --hypothesis "検証する仮説"
```

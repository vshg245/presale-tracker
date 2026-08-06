# 来龙餐馆预售票房追踪

每小时自动从猫眼专业版获取《欢迎来龙餐馆》预售票房数据。

## 数据文件

- `latest.json` — 最新一次获取的数据
- `history.json` — 历史数据记录（追加写入）

## 数据来源

猫眼专业版：https://piaofang.maoyan.com/i/imovie/1462628/premiere

## 运行方式

GitHub Actions 每小时整点自动执行，也可在 Actions 页面手动触发。

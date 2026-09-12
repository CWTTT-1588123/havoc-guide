# start_crawl.ps1 —— 拉起单条 BFS 爬虫线（2026-09-09 起唯一的爬虫拉起方式）
# 由 AI 在【托管后台任务】里调用（run_in_background=true, workdir=E:\Deepseek Harness\wegame-capture）：
#   单账号（2 线）：-Worker 1 / -Worker 2（凭证留空自动取最新）
#   双账号（4 线，2026-09-10 起支持）：账号A 用 -Worker 1/2 -CredFile <A凭证>；账号B 用 -Worker 3/4 -CredFile <B凭证>
#   补丁版本：-Patch 16.18（默认；旧版本用 -Patch 16.17）——数据共存，extract 按版本过滤
# 注意：绝不要用 Start-Process / DETACHED_PROCESS 拉爬虫（沙箱回收、用户关窗也会回收 → 爬虫静默死，见 ds_brain 08）。
param(
    [int]$Worker = 1,          # 1~4（艾欧尼亚分片；1/2 与 3/4 建议分属两个账号，各自 2 线不超各自风控档）
    [string]$CredFile = "",    # 凭证文件名（captured\ 下相对名，如 REQ_GetBattleDetail_xxx.json）；留空=自动取最新
    [string]$Patch = "16.18",  # 只收该补丁的对局（2026-09-13 起服务端为 16.18）
    [string]$PatchStartMs = "1789056000000"   # 补丁起点(ms)=2026-09-11 00:00 安全下界；补旧补丁数据传 0 关闭
)

$ErrorActionPreference = "Stop"
Set-Location "E:\Deepseek Harness\wegame-capture"

if ($Worker -lt 1 -or $Worker -gt 4) { throw "Worker 只能是 1~4" }

if (-not $CredFile) {
    $CredFile = Get-ChildItem "captured\REQ_GetBattleDetail_*.json" |
        Sort-Object LastWriteTime | Select-Object -Last 1 -ExpandProperty Name
    if (-not $CredFile) { throw "captured\ 里没有任何 REQ_GetBattleDetail 凭证，先让用户跑 recap_on/off" }
}

# 当前策略参数：只爬艾欧尼亚，0.3s，低页数深挖近期；PATCH_VERSION 由 -Patch 指定
$env:PATCH_VERSION = $Patch
$env:REQ_FILE = $CredFile
$env:SEED_FROM_GAMES = "0"
$env:MAX_PAGES_PER_PLAYER = "30"
$env:DELAY = "0.3"
$env:MAX_GAMES = "50000"
$env:MAX_PLAYERS = "100000"
$env:AREA = "1"
$env:WORKER = "$Worker"
# 补丁起点（毫秒）：翻页遇到"整页都早于该时间"就停 → 不为旧版本对局浪费请求。
# 16.18 实测起点 2026-09-11 21:50；这里取 09-11 00:00 作安全下界。要补旧补丁数据就传 -PatchStart 0。
$env:PATCH_START_MS = "$PatchStartMs"

Write-Output ("[launcher] worker={0} patch={1} patch_start={2} auth={3} -> crawl_a1_w{0}.log" -f $Worker, $Patch, $PatchStartMs, $CredFile)
& ".\.venv\Scripts\python.exe" ".\bfscrawl.py" *> "crawl_a1_w$Worker.log"

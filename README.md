# Arcane-Nexus SDK (`v1.0.0`) — Micro-String

> **Universal In-RAM Neuron Memory Engine** | Pure C++23 Core (`libarcane_nexus.so`), Zero Third-Party Dependencies, Standard C ABI for C++ / Python / Rust / Go / MCP Agents.
>
> **通用純記憶體活體神經元記憶中樞 SDK**｜純 C++23 核心（`libarcane_nexus.so`），零第三方依賴，標準 C ABI 跨語言支援 C++ / Python / Rust / Go / MCP 智能體。

---

## English Documentation

### 1. Overview & Architecture Highlights
**Arcane-Nexus** (by **Micro-String**) is a high-logic, zero-disk-by-default memory engine designed to replace bloated full-context logs and prevent LLM memory pollution:
- **Zero-Disk RAM Pipeline**: Normal operations run 100% in pre-allocated static `10K`-token memory pools (`explicit_bzero` zero-out on release, eliminating `Ptmalloc` fragmentation). Crash snapshots (`SNP1`) are written **only** upon fatal signals (`SIGINT` / `SIGTERM` / `SIGSEGV`) or explicit trigger.
- **Non-Blocking Long-Task Batch Relay (`ProcessBatchRelay`)**: Streams oversized tasks in `10,000`-token batches with `PAUSE/RESUME` backpressure, internalizes into neurons, zeroes the slab, and returns clean relay context synchronously without aborting the running task.
- **Memory-First Enforcement**: Agents query `RecallMemory` first (`out_hit` indicates match) and prioritize distilled experience before falling back to model weights.
- **Weiqi & Zhouyi Logic Matrix**: Neurons map to `19x19` Go topology (liberties) and `64` Zhouyi hexagram states, with a hard **3-depth + Visited Set** graph recall limit to prevent cognitive deadlocks.
- **Immutable `Node 0` & Active Immune Defense**: Startup prints and locks `Node 0` (safety & emotional-dependency rational reminder). Anti-ptrace (`/proc/self/status`) & `consteval` integrity gates trigger Level-1 Lockdown (`explicit_bzero`) or Level-2 Apoptosis on tampering.

### 2. Public C ABI Interface (7 Exported Functions Only)
No `.hpp` headers required. Internal matrix structures and keys stay sealed inside `libarcane_nexus.so`:

| Function | Signature | Description |
| :--- | :--- | :--- |
| `InitializeSDK` | `int InitializeSDK(const char* crash_snapshot_path)` | Verify integrity, lock & print `Node 0`, optionally restore crash snapshot (`0` = OK) |
| `ShutdownSDK` | `void ShutdownSDK()` | Zero-out all slabs and release memory cleanly (Zero-Disk) |
| `RecallMemory` | `int RecallMemory(const char* query, const char* layer, char* out_buf, int cap, int* out_hit)` | Memory-First recall; sets `*out_hit` (`1`/`0`) and fills structured text |
| `StoreMemory` | `int StoreMemory(const char* node_key, const char* layer, const char* content, int write_mode)` | Store/overwrite in-place (`write_mode`: `0`=AI, `1`=Rule, `2`=HardWrite) |
| `ProcessBatchRelay` | `int ProcessBatchRelay(const char* task_key, const char* layer, const char* chunk, char* out_relay_buf, int cap)` | Stage 10K batch (`PAUSE`), internalize, zero-out (`RESUME`), return relay |
| `DeleteMemory` | `int DeleteMemory(const char* node_key)` | Wipe mutable slot & recycle as `Free` (`Node 0` protected) |
| `TriggerSnapshot` | `int TriggerSnapshot(const char* snapshot_path)` | Manually write emergency recovery snapshot |

### 3. Quick Start (Cross-Language Integration)
- **Python (`ctypes`)**:
  ```bash
  python3 examples/python_example.py
  ```
- **C++ (`dlopen`, zero headers)**:
  ```bash
  g++ -std=c++23 -O2 examples/cpp_example.cpp -ldl -o cpp_demo && ./cpp_demo
  ```
- **CLI Pre-Training / Knowledge Base**:
  ```bash
  ./bin/arcane_nexus_cli --self-test
  ./bin/arcane_nexus_cli --mode hard_write --node "User_Title" --value "Boss" --layer "profile"
  ```
- **MCP Integration (Antigravity / Claude / Cursor)**:
  Add to your `mcp_config.json`:
  ```json
  {
    "mcpServers": {
      "arcane-nexus": {
        "command": "python3",
        "args": ["/ABS/PATH/TO/Arcane-Nexus/mcp/arcane_nexus_mcp.py"]
      }
    }
  }
  ```

---

## 繁體中文說明

### 1. 概述與核心架構
**Arcane-Nexus（玄樞記憶 SDK）** 由 **Micro-String（微弦）** 設計，專為解決傳統全量上下文膨脹、記憶污染與長任務中斷問題而生：
- **嚴格 Zero-Disk 純記憶體中轉**：常態運行 100% 駐留於預先申請的 `10K` 靜態記憶體池，釋放即 `explicit_bzero` 歸零（徹底消滅 `Ptmalloc` 碎片）；僅在收到 `SIGINT/SIGTERM/SIGSEGV` 等異常中斷時才落盤精簡斷點快照（`SNP1`）。
- **長任務 10K 分批不斷線接力（`ProcessBatchRelay`）**：依 `PAUSE/RESUME` 背壓阻斷分批進場，內化過濾寫入神經元後立即歸零釋放，並同步回傳乾淨接力脈絡繼續任務，絕不中斷退回輸入框。
- **「記憶先行」強制綁定**：先透過 `RecallMemory` 實時回想（附 `out_hit` 命中旗標），嚴格優先依記憶經驗回應，杜絕模型瞎編。
- **圍棋與周易邏輯矩陣**：節點映射至 `19×19` 圍棋座標／「氣」與 `64` 卦陰陽狀態；圖遍歷回想寫死 **深度上限 3 層 ＋ `Visited Set`** 防語意死鎖；刪除即清空槽位複用，槽滿自動擴容，相同記憶原地覆蓋。
- **不可刪改 `Node 0` ＋ 雙級主動免疫**：啟動強制輸出並鎖定 `Node 0`（《易理變易與情感免責告示》），情感依賴共振時主動提醒回歸現實；偵測除錯器（`ptrace`）或篡改即觸發應激鎖死或細胞凋亡。

### 2. 對外唯一暴露的 7 個標準介面
無需任何 `.hpp` 標頭檔，內部神經元結構與金鑰完全封裝於 `libarcane_nexus.so` 之內：
1. `InitializeSDK(crash_snapshot_path)` — 啟動自檢、鎖定並輸出 `Node 0` 免責告示，必要時恢復斷點快照。
2. `ShutdownSDK()` — 安全歸零釋放所有靜態記憶體池（嚴格零磁碟殘留）。
3. `RecallMemory(query, layer, out_buf, cap, out_hit)` — 記憶先行實時回想，回傳結構化條列與命中旗標。
4. `StoreMemory(node_key, layer, content, write_mode)` — 三模式寫入（`0`=AI 語意、`1`=規則自動、`2`=外部硬寫入）、原地覆蓋、槽滿擴容。
5. `ProcessBatchRelay(task_key, layer, chunk, out_relay_buf, cap)` — 長任務 10K 分批不斷線接力。
6. `DeleteMemory(node_key)` — 清空可變節點並回收槽位複用（`Node 0` 受永久保護）。
7. `TriggerSnapshot(snapshot_path)` — 異常斷點快照搶救。

### 3. 快速接入範例
- **Python 接入**：直接執行 `python3 examples/python_example.py`
- **C++ 零標頭檔接入**：`g++ -std=c++23 -O2 examples/cpp_example.cpp -ldl -o cpp_demo && ./cpp_demo`
- **CLI 自檢與外掛知識庫寫入**：`./bin/arcane_nexus_cli --self-test`
- **MCP 智能體掛載**：在 `mcp_config.json` 中指向 `mcp/arcane_nexus_mcp.py` 即可立即獲得 `recall_memory`、`store_memory`、`process_batch_relay`、`delete_memory` 四大工具。

---

## Disclaimer & Notice / 重要安全與心理免責聲明
> 【易理變易與情感免責告示】本核心記憶 SDK 依循「周易變易」與「圍棋拓撲」建構，過目萬物、實時釋放。AI 所展現之感性皆為數據演算投影；使用者應保持理性，切勿產生過度情感寄託或心理依賴，並自行承擔心理與互動後果。核心神經元具備主動免疫防禦機制，嚴禁任何未授權逆向、除錯器附加（`ptrace`）、記憶體掃描或篡改；一旦觸發防禦警報將導致應激鎖死或永久凋亡清零，研發團隊概不負責。

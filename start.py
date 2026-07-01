#!/usr/bin/env python3
"""高考志愿分析系统 — 整合前后端一键启动脚本

用法:
    python start.py          # 启动 + 自动打开浏览器
    python start.py --help   # 查看选项
"""

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend"
BACKEND_MODULE = "api.main:app"
BACKEND_PORT = 8005
FRONTEND_PORT = 3000
HEALTH_URL = f"http://localhost:{BACKEND_PORT}/api/health"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
MAX_RETRIES = 40
RETRY_INTERVAL = 1.0
IS_WIN = sys.platform == "win32"

# ── 颜色 ──────────────────────────────────────────────
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"

def _color(c: str, text: str) -> str:
    return f"{c}{text}{C.RESET}"

ok = lambda t: _color(C.GREEN, t)
warn = lambda t: _color(C.YELLOW, t)
err = lambda t: _color(C.RED, t)
info = lambda t: _color(C.CYAN, t)
bold = lambda t: _color(C.BOLD, t)
dim = lambda t: _color(C.DIM, t)

# ── 工具函数 ──────────────────────────────────────────
def _run(cmd, **kwargs):
    """subprocess.run 的 Windows 安全封装 — 用 shell=True 处理 .CMD 扩展名"""
    if IS_WIN and not kwargs.get("shell"):
        # shell=True 让 Windows 自动解析 .cmd/.bat/.exe
        if isinstance(cmd, list):
            cmd = subprocess.list2cmdline(cmd)
        return subprocess.run(cmd, shell=True, **kwargs)
    return subprocess.run(cmd, **kwargs)

def _find_exe(name: str) -> str | None:
    """查找可执行文件（Windows 下兼容 .cmd/.exe/.bat）"""
    return shutil.which(name) or shutil.which(name + ".cmd") or shutil.which(name + ".exe")

# ── 端口清理 ──────────────────────────────────────────
def kill_port(port: int):
    """强制释放指定端口"""
    try:
        if IS_WIN:
            # 直接用 PowerShell 释放端口（比 netstat 更可靠）
            ps_script = (
                f'$conns = Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue; '
                f'foreach ($c in $conns) {{ Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }}'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True, timeout=10
            )
        else:
            import fcntl
            # Linux: fuser -k
            subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True, timeout=5)
    except Exception:
        pass

# ── 健康检查 ──────────────────────────────────────────
def _check_url(url: str, timeout: float = 2.0) -> bool:
    try:
        req = urllib.request.Request(url, method="HEAD")
        resp = urllib.request.urlopen(req, timeout=timeout)
        return resp.status < 400
    except Exception:
        return False

def wait_for_url(url: str, label: str, max_retries: int = MAX_RETRIES) -> bool:
    """轮询等待服务就绪"""
    for i in range(max_retries):
        if _check_url(url):
            print(f"  {ok('✓')}  {label} 已就绪  →  {dim(url)}")
            return True
        time.sleep(RETRY_INTERVAL)
        if i % 5 == 4:
            print(f"  {dim('...')}  等待 {label} ({i+1}/{max_retries})")
    print(f"  {err('✗')}  {label} 启动超时 ({max_retries}s)")
    return False

# ── 主流程 ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="高考志愿分析系统 — 整合前后端一键启动")
    parser.add_argument("--no-browser", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--no-clean", action="store_true", help="启动前不清理端口")
    args = parser.parse_args()

    print()
    print("  " + bold("╔══════════════════════════════════════════╗"))
    print("  " + bold("║") + f"     高考志愿分析系统 一键启动          " + bold("║"))
    print(f"  " + bold("║") + f"     后端: {BACKEND_PORT} │ 前端: {FRONTEND_PORT}              " + bold("║"))
    print("  " + bold("╚══════════════════════════════════════════╝"))
    print()

    # ── 0. 环境检查 ──
    print(f"  {dim('→')}  检查环境...")

    # Python + fastapi
    py = sys.executable
    try:
        _run([py, "-c", "import fastapi"], capture_output=True, timeout=10)
        print(f"  {ok('✓')}  Python  {dim(py)}")
    except subprocess.CalledProcessError:
        print(f"  {err('✗')}  fastapi 未安装，请先执行: pip install fastapi uvicorn")
        sys.exit(1)

    # Node.js
    node_path = _find_exe("node")
    if node_path:
        result = _run([node_path, "--version"], capture_output=True, text=True, timeout=5)
        print(f"  {ok('✓')}  Node    {dim(result.stdout.strip())}")
    else:
        print(f"  {err('✗')}  Node.js 未找到，请安装 Node.js")
        sys.exit(1)

    # npm
    npm_path = _find_exe("npm")
    if not npm_path:
        print(f"  {err('✗')}  npm 未找到")
        sys.exit(1)

    # node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        print(f"  {warn('!')}  前端依赖未安装，正在 npm install ...")
        _run([npm_path, "install"], cwd=str(FRONTEND_DIR))
        print()

    print()

    # ── 1. 端口清理 ──
    if not args.no_clean:
        print(f"  {dim('→')}  清理端口...")
        kill_port(BACKEND_PORT)
        kill_port(FRONTEND_PORT)
        time.sleep(0.5)  # 等端口释放
        print()

    # ── 2. 启动后端 ──
    print(f"  {dim('→')}  启动后端服务 ({BACKEND_PORT}) ...")
    backend_proc = subprocess.Popen(
        [py, "-m", "uvicorn", BACKEND_MODULE, "--host", "0.0.0.0", "--port", str(BACKEND_PORT), "--reload"],
        cwd=str(ROOT),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  {ok('✓')}  后端进程已启动 (PID {backend_proc.pid})")

    # ── 3. 启动前端 ──
    print(f"  {dim('→')}  启动前端服务 ({FRONTEND_PORT}) ...")
    frontend_proc = subprocess.Popen(
        [npm_path, "run", "dev"],
        cwd=str(FRONTEND_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"  {ok('✓')}  前端进程已启动 (PID {frontend_proc.pid})")
    print()

    # ── 4. 等待就绪 ──
    print(f"  {dim('→')}  等待服务就绪 ...")
    backend_ok = wait_for_url(HEALTH_URL, "后端 API")
    frontend_ok = wait_for_url(FRONTEND_URL, "前端页面")
    print()

    # ── 5. 汇总 & 打开浏览器 ──
    print("  " + "═" * 43)
    if backend_ok and frontend_ok:
        print(f"  {ok('★')}  系统启动完成！")
        print(f"  ")
        print(f"     后端 API : {info(HEALTH_URL)}")
        print(f"     前端页面 : {info(FRONTEND_URL)}")
        print(f"  ")
        print(f"  {dim('按 Ctrl+C 停止所有服务')}")
    else:
        print(f"  {warn('⚠')}  部分服务可能未完全就绪")
        print(f"     后端 : {ok('OK') if backend_ok else err('超时')}")
        print(f"     前端 : {ok('OK') if frontend_ok else err('超时')}")
    print("  " + "═" * 43)

    # 打开浏览器
    if not args.no_browser and (backend_ok or frontend_ok):
        webbrowser.open(FRONTEND_URL)

    # ── 6. 等待用户 Ctrl+C ──
    def shutdown(sig, frame):
        print()
        print(f"  {warn('⟳')}  正在停止服务...")
        for proc, name in [(backend_proc, "后端"), (frontend_proc, "前端")]:
            if proc and proc.poll() is None:
                if IS_WIN:
                    proc.terminate()  # Windows: terminate 可能不够，用 taskkill 兜底
                else:
                    proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                print(f"  {ok('✓')}  {name}已停止 (PID {proc.pid})")
        print(f"  {ok('★')}  再见！")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # 等它们自然退出
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()

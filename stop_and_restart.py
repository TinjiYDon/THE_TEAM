"""停止旧进程并重启服务器"""
import subprocess
import sys
import os
import time

def stop_processes():
    """停止占用端口8000的进程"""
    print("正在查找占用端口8000的进程...")
    
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", ":8000"],
            shell=True,
            capture_output=True,
            text=True
        )
        
        lines = result.stdout.strip().split('\n')
        pids = set()
        
        for line in lines:
            if 'LISTENING' in line:
                parts = line.split()
                if len(parts) > 4:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
        
        if pids:
            print(f"找到 {len(pids)} 个占用端口的进程: {', '.join(pids)}")
            print("\n正在停止这些进程...")
            
            for pid in pids:
                try:
                    subprocess.run(
                        ["taskkill", "/PID", pid, "/F"],
                        capture_output=True,
                        check=False
                    )
                    print(f"  [OK] 已停止进程 {pid}")
                except Exception as e:
                    print(f"  [警告] 停止进程 {pid} 失败: {e}")
            
            print("\n等待2秒让端口释放...")
            time.sleep(2)
        else:
            print("未找到占用端口的进程")
    
    except Exception as e:
        print(f"查找进程失败: {e}")
        print("\n请手动停止进程：")
        print("1. 运行: netstat -ano | findstr :8000")
        print("2. 找到PID后运行: taskkill /PID [PID] /F")

def main():
    """主函数"""
    print("=" * 60)
    print("停止旧进程并准备重启服务器")
    print("=" * 60)
    print()
    
    stop_processes()
    
    print("\n" + "=" * 60)
    print("准备完成")
    print("=" * 60)
    print("\n现在可以重新启动服务器：")
    print("  python run_server.py")
    print("\n或者使用安全启动脚本：")
    print("  python start_server_safe.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()


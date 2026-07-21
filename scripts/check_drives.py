import ctypes

def get_drive_info():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for i in range(26):
        if bitmask & (1 << i):
            letter = chr(65 + i)
            path = letter + ':\\'
            try:
                total = ctypes.c_ulonglong()
                free = ctypes.c_ulonglong()
                if ctypes.windll.kernel32.GetDiskFreeSpaceExW(path, None, ctypes.byref(total), ctypes.byref(free)):
                    total_gb = total.value / (1024**3)
                    free_gb = free.value / (1024**3)
                    used_gb = (total.value - free.value) / (1024**3)
                    pct = (used_gb / total_gb) * 100 if total_gb > 0 else 0
                    if used_gb > 0:
                        print(f'{letter}:  {used_gb:.1f} / {total_gb:.1f} GB used  |  {free_gb:.1f} GB free  ({pct:.1f}%)')
            except:
                pass

if __name__ == '__main__':
    get_drive_info()

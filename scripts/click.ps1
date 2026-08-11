# Fleet click helper - raw user32 SetCursorPos + mouse_event
param([int]$X, [int]$Y, [int]$DelayMs = 300)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class RawClick {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, IntPtr dwExtraInfo);
    public static void Click(int x, int y) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(120);
        mouse_event(0x0002, 0, 0, 0, IntPtr.Zero); // left down
        System.Threading.Thread.Sleep(60);
        mouse_event(0x0004, 0, 0, 0, IntPtr.Zero); // left up
    }
}
"@
[RawClick]::Click($X, $Y)
Start-Sleep -Milliseconds $DelayMs

Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class GovIdle {
    [StructLayout(LayoutKind.Sequential)] struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
    [DllImport("user32.dll")] static extern bool GetLastInputInfo(ref LASTINPUTINFO info);
    public static uint Seconds() {
        LASTINPUTINFO i = new LASTINPUTINFO(); i.cbSize = (uint)Marshal.SizeOf(i);
        if (!GetLastInputInfo(ref i)) { return 4294967295; }
        return ((uint)Environment.TickCount - i.dwTime) / 1000;
    }
}
'@
[GovIdle]::Seconds()

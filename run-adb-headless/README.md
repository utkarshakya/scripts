# Run ADB Headless

A terminal-based Android helper for working with ADB without a desktop UI. It can list connected devices, connect over Wi‑Fi, inspect device details, and restart/reset the ADB service when needed.

## Features

| Menu option | Description |
| --- | --- |
| 1. Auto Connect Device | Restarts ADB and checks for a ready device automatically |
| 2. Manual Connect | Connects to a device using its IP and port |
| 3. Pair Wireless Device | Pairs a device using the wireless debugging code flow |
| 4. Show Connected Devices | Lists attached and wireless devices with details |
| 5. Show Device Information | Displays OS and hardware details for the active device |
| 6. Restart ADB Server | Stops and restarts the ADB daemon |
| 7. Reset ADB | Disconnects devices and restarts ADB |
| 8. Exit | Closes the script |

## Requirements

- Python 3.8+
- Android SDK Platform Tools installed and `adb` available on your `PATH`
- Android 11+ for wireless debugging features

## Running the Script

From the project directory:

```bash
python adb_manager.py
```

If `adb` is not installed or not on `PATH`, the script will print the missing setup instructions and exit.

## Typical Wireless Debugging Flow

1. Enable Wireless debugging on the device.
2. Select the pairing option from the script menu.
3. Enter the device IP, pairing port, and pairing code.
4. Use the normal connection option with the device's connect address and port.
5. Use the auto-connect option later if the device is already authorized.

## Logging

The script writes readable activity logs to `adb_manager.log` in the working directory. Entries mirror messages such as `[INFO]`, `[SUCCESS]`, `[WARNING]`, and `[ERROR]` and are kept out of version control by `.gitignore`.

## PowerShell Alias Example

To run it from anywhere in PowerShell, add this to your profile:

```powershell
function Invoke-AdbManager {
    python "C:\path\to\run_adb_headless\adb_manager.py" @args
}
Set-Alias adbmenu Invoke-AdbManager
```

Then call:

```powershell
adbmenu
```

## Notes

- The script is most useful when your Android device is connected to the same network.
- Wireless debugging requires pairing once before normal `adb connect` works reliably.
- Device details are pulled using `adb shell` commands and platform outputs.

# SEEs Detector Quick Start Guide - WINDOWS EDITION

**SEEs** - Solar Energetic Events Detector Payload for AERIS Mission

Interactive command console for the SiPM particle detector.

**THIS GUIDE ASSUMES YOU'RE STARTING FROM SCRATCH ON WINDOWS 10 OR 11**

---

## Table of Contents
1. [Quick Reference Card](#quick-reference-card) ⭐ START HERE!
2. [Software Installation](#software-installation)
3. [Hardware Setup](#hardware-setup)
4. [Building and Uploading Firmware](#building-and-uploading-firmware)
5. [Connecting to the Device](#connecting-to-the-device)
6. [Taking Measurements](#taking-measurements)
7. [Data Capture](#data-capture)
8. [Troubleshooting](#troubleshooting)
9. [One-Page Cheat Sheet](#one-page-cheat-sheet-print-this) 📄 PRINT THIS!

---

## Quick Reference Card

**⭐ COMPLETE BEGINNER? Read this entire section first, then follow the detailed steps below!**

### What You're Going to Do (The Big Picture)

1. **Install software** on your computer (Python, Visual Studio Code, Git)
2. **Download the code** from the internet (called "cloning")
3. **Build the code** (turn it into a program the Teensy can run)
4. **Upload the program** to the Teensy (via USB cable)
5. **Run a simple program** called SEEs.bat to connect to the Teensy
6. **Type commands** to make the detector take measurements
7. **Find your data** in folders on your computer

### What is what?

- **Teensy 4.1**: A small circuit board (microcontroller) that controls the detector
- **detector**: The scientific instrument that measures light
- **USB Cable**: Connects the Teensy to your computer (you need a micro-USB cable)
- **COM Port**: How Windows identifies USB devices (like COM3, COM4, etc.)
- **PowerShell**: A blue window where you type commands (it's built into Windows)
- **SEEs.bat**: A simple program that connects to the Teensy and shows you a console
- **CSV File**: A spreadsheet file with your measurement data that you can open in Excel

### The Absolute Minimum You Need to Know

**To install everything (ONE TIME ONLY):**
1. Install Python → Download from python.org, CHECK "Add Python to PATH"
2. Install Visual Studio Code → Download from code.visualstudio.com
3. Install PlatformIO extension inside Visual Studio Code
4. Install Git → Download from git-scm.com
5. Clone the repository using Visual Studio Code (Ctrl+Shift+P, type "git clone")

**To upload firmware to the Teensy (EVERY TIME YOU GET A NEW TEENSY, or want to update):**
1. Open the `SEEsDriver` folder in Visual Studio Code
2. Plug in the Teensy via USB
3. Click the checkmark ✓ at the bottom (Build)
4. Wait for SUCCESS
5. Click the arrow → at the bottom (Upload)
6. Wait for SUCCESS

**To use the device (EVERY TIME YOU WANT TO TAKE MEASUREMENTS):**
1. Plug in the Teensy via USB
2. Open File Explorer, go to `aeris-sees-software\SEEsDriver`
3. Click in the address bar, type `powershell`, press Enter
4. Type `.\SEEs.bat` and press Enter
5. Type `measure` to take a measurement
6. Type `auto 60` to take measurements every 60 seconds
7. Type `stop` to stop automatic measurements
8. Your data is saved in folders like `session_2025-11-13_...`

### Common Terms You'll See

- **Repository**: A folder with all the code, stored on the internet (GitHub)
- **Clone**: Download a copy of the repository to your computer
- **Build**: Convert human-readable code into machine code the Teensy can run
- **Upload**: Send the built program to the Teensy
- **Firmware**: The program that runs on the Teensy
- **Serial Console**: A text-based window where you type commands
- **Baud Rate**: Speed of communication (always use 115200)
- **PATH**: A Windows setting that tells it where to find programs like Python

### Keyboard Keys Reference (For Complete Beginners)

**If you've never used keyboard shortcuts before:**

- **Windows Key**: The key with the Windows logo (⊞) on your keyboard, usually between Ctrl and Alt
- **Ctrl Key**: Says "Ctrl" on it, usually in the bottom-left corner of your keyboard
- **Shift Key**: The key with an up arrow (⇧), above the Ctrl key
- **Enter Key**: The large key on the right side of your keyboard, might say "Enter" or "Return" or have a ↵ symbol
- **Plus (+) in shortcuts**: Means hold down the first key, THEN press the second key
  - Example: `Ctrl + Shift + P` means: Hold Ctrl, hold Shift, press P, then release all

**When we say "press Windows Key + X":**
1. Find the Windows key (⊞) on your keyboard
2. Hold it down
3. While holding it, press the X key
4. Release both keys
5. A menu appears!

---

## Software Installation

### Step 1: Install Python (Required for data capture)

**Part A: Download Python**

1. **Find your web browser icon** on your desktop or taskbar
   - It might be called "Google Chrome" (colorful circle), "Microsoft Edge" (blue wave), or "Firefox" (orange fox)
2. **Click once** on the browser icon to open it
3. **Click in the address bar** at the top of the browser window (where web addresses go)
4. **Type exactly**: `python.org/downloads`
5. **Press the Enter key** on your keyboard (the large key on the right side)
6. **Wait** for the page to load (2-5 seconds)
7. **Look for** a big yellow button that says "Download Python 3.12.x" (the numbers might be different)
8. **Click once** on that yellow button
9. **Wait** for the download to start
   - You might see a small window appear asking "Save file?" - if so, click "Save"
   - Look at the bottom of your browser - you should see a file downloading
10. **Wait** for the download to finish (30 seconds to 2 minutes depending on your internet)
    - When done, the file will stop showing a progress bar

**Part B: Install Python**

11. **Look at the bottom** of your browser window - you should see the downloaded file
    - It's named something like `python-3.12.5-amd64.exe`
12. **Click once** on that downloaded file
    - OR: Click the folder icon on your taskbar, click "Downloads" on the left, find the Python file, and double-click it
13. A window will appear asking "Do you want to allow this app to make changes?" - **Click "Yes"**

**THIS NEXT STEP IS CRITICAL - DO NOT SKIP!**

14. You'll see a window that says "Install Python 3.x.x"
15. **LOOK AT THE BOTTOM** of this window
16. You'll see a checkbox that says "Add python.exe to PATH"
17. **Click in that checkbox** so it has a checkmark (✓)
    - This is VERY IMPORTANT - without this, nothing will work!
18. Now **click** the button that says "Install Now" (near the top)
19. **Wait** while Python installs (1-3 minutes)
    - You'll see a progress bar filling up
    - It will say things like "Installing..." and show files being copied
20. When you see "Setup was successful" at the top, **click "Close"**

**Part C: Verify Python Works**

21. **Press and hold** the Windows key (the key with ⊞ symbol, between Ctrl and Alt)
22. **While holding Windows key**, press the letter **R**
23. **Release both keys**
24. A small window appears called "Run" - **wait for it to appear**
25. **Click in the white box** in this window
26. **Type exactly**: `cmd`
27. **Press Enter** (or click the OK button)
28. A **black window** appears - this is called "Command Prompt"
29. **Click anywhere** inside the black window
30. **Type exactly**: `python --version`
    - That's two dashes before "version"
    - Make sure to include the space after "python"
31. **Press Enter**
32. **Look at the black window** - you should see text that says `Python 3.12.x`
    - If you see this, SUCCESS! Python is installed correctly!
    - If you see "python is not recognized" - GO BACK TO STEP 14 and make sure you checked the PATH box!
33. **Type exactly**: `exit`
34. **Press Enter**
35. The black window closes

### Step 2: Install Visual Studio Code

**Part A: Download VS Code**

1. **If your browser is closed**, open it again (click the browser icon)
2. **Click in the address bar** at the top
3. **Type exactly**: `code.visualstudio.com/download`
4. **Press Enter**
5. **Wait** for the page to load
6. **Look for** a big blue button that says "Download for Windows"
   - It might also show a version number like "Windows 10, 11"
7. **Click once** on that blue button
8. **Wait** for the download
   - Look at the bottom of your browser for the downloading file
9. **Wait** for the download to complete (1-3 minutes)
   - The file is about 90 MB in size

**Part B: Install VS Code**

10. **Look at the bottom** of your browser - find the downloaded file
    - It's named something like `VSCodeUserSetup-x64-1.85.2.exe`
11. **Click once** on that file to open it
    - OR: Open File Explorer (folder icon), click Downloads, double-click the VS Code file
12. A window asks "Do you want to allow this app to make changes?" - **Click "Yes"**
13. A setup window appears with a license agreement
14. **Click the circle** next to "I accept the agreement"
15. **Click** the "Next" button at the bottom
16. **Click** "Next" again (the location is fine as default)
17. **Click** "Next" again (the start menu folder is fine)
18. You'll see "Select Additional Tasks" - **just click "Next"** (defaults are fine)
19. You'll see "Ready to Install" - **click "Install"**
20. **Wait** while VS Code installs (1-2 minutes)
    - You'll see a progress bar
21. When done, you'll see "Completing the Visual Studio Code Setup Wizard"
22. **Click** the "Finish" button
23. Visual Studio Code will open automatically - **this is normal, leave it open**

### Step 3: Install PlatformIO Extension

1. **Make sure Visual Studio Code is open**
   - If you just finished Step 2, it should already be open
   - If not: Click the Windows Start button (⊞ in bottom-left), type "visual studio code", click on it
2. **Look at the left side** of the Visual Studio Code window
   - You'll see a vertical column of icons (like a toolbar on the side)
3. **Count down from the top** of these icons
   - 1st icon: Files (looks like two sheets of paper)
   - 2nd icon: Search (looks like a magnifying glass)
   - 3rd icon: Source Control (looks like a branching diagram)
   - 4th icon: Run and Debug (looks like a play button with a bug)
   - 5th icon: **Extensions (looks like four squares)** ← THIS ONE!
4. **Click once** on the Extensions icon (the four squares)
5. The left side panel changes to show "EXTENSIONS"
6. **Look at the top** of this panel - there's a search box that says "Search Extensions in Marketplace"
7. **Click once** in that search box
8. **Type exactly**: `platformio`
9. **Press Enter** or wait a moment
10. **Look at the results** - the first one should say "PlatformIO IDE"
    - It will have a description that mentions "Arduino" and "Embedded"
    - It might show a small icon with "PIO" on it
11. **Click once** on "PlatformIO IDE" to see more details
12. **Look for** a blue or green button that says "Install"
13. **Click once** on the "Install" button
14. **WAIT PATIENTLY** - this takes 2-5 minutes!
    - You'll see "Installing" with a spinning icon
    - The bottom-right of VS Code might show progress messages
    - DO NOT close VS Code during this time
15. **Watch for** one of these to happen:
    - A button appears saying "Reload Required" - if you see this, **click it**
    - OR VS Code might reload automatically
    - OR the Install button changes to say "Installed" or shows a gear icon
16. **After reload**, look at the left sidebar again
    - You should now see a new icon that looks like an alien head or home icon (PlatformIO)
17. **SUCCESS!** PlatformIO is installed

### Step 4: Install Git (for cloning the repository)

**Part A: Download Git**

1. **Open your web browser** (if it's not already open)
2. **Click in the address bar** at the top
3. **Type exactly**: `git-scm.com/download/win`
4. **Press Enter**
5. **Wait** for the page to load (2-3 seconds)
6. **The download should start AUTOMATICALLY**
   - Look at the bottom of your browser - a file should start downloading
   - The file is named something like `Git-2.43.0-64-bit.exe`
7. **If nothing downloads automatically**:
   - Look for a link that says "Click here to download manually"
   - Click on that link
8. **Wait** for the download to complete (30 seconds to 2 minutes)

**Part B: Install Git**

9. **Look at the bottom** of your browser - find the Git file you just downloaded
10. **Click once** on that file
    - OR: Open File Explorer, go to Downloads, find the Git file, double-click it
11. A window asks "Do you want to allow this app to make changes?" - **Click "Yes"**
12. You'll see "GNU General Public License" - **Click "Next"**
13. You'll see "Select Destination Location" - **Click "Next"** (default is fine)
14. You'll see "Select Components" - **Click "Next"** (defaults are fine)
15. You'll see "Select Start Menu Folder" - **Click "Next"**
16. You'll see "Choosing the default editor" - **Click "Next"** (default is fine)
17. You'll see several more screens - **just keep clicking "Next"** for all of them
    - "Adjusting your PATH environment" - **Click "Next"**
    - "Choosing HTTPS transport backend" - **Click "Next"**
    - "Configuring the line ending conversions" - **Click "Next"**
    - "Configuring the terminal emulator" - **Click "Next"**
    - "Choose the default behavior of git pull" - **Click "Next"**
    - "Choose a credential helper" - **Click "Next"**
    - "Configuring extra options" - **Click "Next"**
    - "Configuring experimental options" - **Click "Next"** (leave checkboxes UNCHECKED)
18. Finally, you'll see "Installing" with a progress bar - **wait patiently** (1-2 minutes)
19. When you see "Completing the Git Setup Wizard" - **Click "Finish"**

### Step 5: Clone the Repository (Download the Code)

1. **Make sure Visual Studio Code is open**
   - If it's not: Click Start button (⊞), type "visual studio code", click it
2. **Press and hold** the **Ctrl** key (bottom-left of keyboard)
3. **While holding Ctrl**, press and hold the **Shift** key (just above Ctrl)
4. **While holding both**, press the letter **P** key
5. **Release all three keys**
6. **LOOK AT THE TOP-CENTER** of the Visual Studio Code window
   - A text box appears with a ">" symbol
   - This is called the "Command Palette"
7. **Click in that text box** (if it's not already active)
8. **Type exactly**: `git clone`
   - Type it slowly and carefully
   - As you type, you'll see suggestions appear below
9. **Look at the suggestions** below the text box
   - One should say **"Git: Clone"** (with a little Git icon)
10. **Click once** on **"Git: Clone"**
11. **Another text box appears** at the top, asking for a repository URL
12. **Click in this text box**
13. **Type exactly** (or copy and paste): `https://github.com/hsfl/aeris-sees-software.git`
    - Make sure you include the ".git" at the end
    - Make sure there are no extra spaces
14. **Press Enter**
15. **A file browser window opens** asking where to save the repository
16. **Choose a location** - we recommend:
    - **Click** on "Documents" in the left sidebar
    - OR **Click** on "Desktop" in the left sidebar
    - Choose whichever one you prefer - just remember where you put it!
17. **Click** the **"Select Repository Location"** button (or "Select Folder" button)
18. **WAIT** while the code downloads (30 seconds to 2 minutes)
    - You might see a progress bar in the bottom-right
    - You might see messages about "Cloning into..."
19. **A notification appears** in the bottom-right asking "Would you like to open the cloned repository?"
20. **Click** the **"Open"** button in that notification
    - If you missed the notification, that's okay - we'll open it later
21. **SUCCESS!** You've downloaded the code

**Did the notification disappear before you clicked it?** No problem:
- Click "File" at the top
- Click "Open Folder"
- Navigate to where you saved it (Documents or Desktop)
- Find and click on the folder named "aeris-sees-software"
- Click "Select Folder"

### Step 6: Install Python Libraries (Required for SEEs.bat)

This step installs a special add-on (library) that lets Python talk to the Teensy.

1. **Press and hold** the **Windows key** (⊞ symbol, between Ctrl and Alt)
2. **While holding it**, press the letter **R** key
3. **Release both keys**
4. A small "Run" window appears
5. **Click in the white text box** (if not already selected)
6. **Type exactly**: `cmd`
7. **Press Enter** (or click the "OK" button)
8. **A black window appears** - this is "Command Prompt"
   - Don't be scared of the black window - it's just a text interface
9. **Click anywhere inside the black window** to make sure it's active
10. **Type exactly**: `pip install pyserial`
    - Make sure to include the spaces between words
11. **Press Enter**
12. **WAIT and WATCH** the black window
    - You'll see text scrolling
    - It might say "Collecting pyserial"
    - It might say "Downloading..."
    - This takes 10-30 seconds
13. **Look for** this text: `Successfully installed pyserial`
    - When you see this, the installation worked!
    - If you see "Requirement already satisfied" - that's also fine, it means it's already installed
14. **Type exactly**: `exit`
15. **Press Enter**
16. The black window closes
17. **SUCCESS!** The Python library is installed

---

## Hardware Setup

### Required Components
- Teensy 4.1 microcontroller
- SiPM particle detector
- USB cable (spliced for USB Host connection)
- Micro-USB cable (for serial console - connects Teensy to computer)
- SD card (optional, but recommended for data logging)

### Physical Connections

```
Computer ←─ micro-USB ─→ Teensy 4.1 ←─ USB Host Pads ─→ AvaSpec
    (Serial Console)      🟥🟩⬜⬛ spliced     (USB-A spliced)
                          5V D+ D– GND
```

**USB Host Wiring** (already done, but for reference):
- 🟥 Red (5V) → Teensy 5V Host Pad
- 🟩 Green (D+) → Teensy D+ Host Pad
- ⬜ White (D–) → Teensy D– Host Pad
- ⬛ Black (GND) → Teensy GND Host Pad

**What you need to do:**
1. Connect the **micro-USB cable** from your computer to the Teensy 4.1
2. The detector should already be connected to the Teensy via USB Host pads
3. Insert an **SD card** into the Teensy if you want to save data

---

## Building and Uploading Firmware

This section teaches you how to turn the code into a program and put it on the Teensy.

### Step 1: Open the Project

1. **Make sure Visual Studio Code is open**
   - If not: Click Windows Start (⊞), type "visual studio code", press Enter
2. **Look at the very top** of the Visual Studio Code window
   - You'll see a menu bar with: File, Edit, Selection, View, Go, Run, Terminal, Help
3. **Click once** on **"File"**
   - A dropdown menu appears
4. **Click once** on **"Open Folder..."** (near the top of the dropdown)
5. **A file browser window opens**
6. **Navigate to where you saved the repository**:
   - If you saved it in Documents:
     - **Click** "Documents" in the left sidebar
     - **Double-click** the folder named "aeris-sees-software"
   - If you saved it on Desktop:
     - **Click** "Desktop" in the left sidebar
     - **Double-click** the folder named "aeris-sees-software"
7. **You're now inside the aeris-sees-software folder**
8. **Look for** a folder named **"SEEsDriver"**
9. **Click once** on "SEEsDriver" to select it (it highlights in blue)
10. **Look at the bottom-right** of the file browser window
11. **Click** the button that says **"Select Folder"**
12. **WAIT PATIENTLY** (10-30 seconds)
    - PlatformIO is loading the project
    - You might see progress messages at the bottom of VS Code
    - The left sidebar will show the project files
13. **Look at the bottom** of VS Code - you should see a blue bar with icons
    - If you see this blue bar, PlatformIO is ready!
14. **SUCCESS!** The project is open

### Step 2: Build the Firmware

"Building" means converting the code into a program the Teensy can understand.

1. **Look at the VERY BOTTOM** of the Visual Studio Code window
   - There's a colored bar (usually blue or purple) all the way across the bottom
   - This is called the "status bar"
2. **Look at the LEFT SIDE** of this bottom bar
   - You'll see several small icons
3. **Find the CHECKMARK icon** (✓)
   - It might be the first or second icon
   - If you move your mouse over it, a tooltip appears saying "PlatformIO: Build"
4. **Click once** on the **checkmark icon** (✓)
5. **IMMEDIATELY** look at the bottom of the window
   - A panel opens showing a black terminal window with text
   - This is the build process starting
6. **WAIT PATIENTLY** and watch the text scroll
   - First time: This takes 1-3 minutes (it downloads tools)
   - Later times: This takes 30-60 seconds
   - You'll see lots of text like "Compiling...", "Linking...", etc.
   - DO NOT close Visual Studio Code during this time
7. **WATCH FOR THE RESULT**:
   - **If successful**: You'll see `[SUCCESS]` in **GREEN** text at the end
   - **If failed**: You'll see `[FAILED]` in **RED** text
8. **If you see `[SUCCESS]`**:
   - **GREAT!** The build worked!
   - Move on to Step 3
9. **If you see `[FAILED]`**:
   - See [Troubleshooting - Build Failed](#problem-build-failed-in-platformio)
   - You'll need to fix the error before continuing

### Step 3: Upload to Teensy

"Uploading" means sending the program from your computer to the Teensy.

**FIRST: Connect the Teensy**

1. **Find** your Teensy 4.1 device (the small circuit board)
2. **Find** a micro-USB cable
   - This is a small USB cable (smaller than a phone charger)
   - One end is micro-USB (small rectangular), other end is regular USB
3. **Plug the micro-USB end** into the Teensy
   - There's a micro-USB port on the Teensy board
4. **Plug the other end** into your computer's USB port
5. **WAIT** 5-10 seconds for Windows to recognize the device
   - You might hear a "ding" sound from Windows
   - You might see a notification in the bottom-right

**NOW: Upload the Program**

6. **Look at the bottom** of Visual Studio Code again
7. **Find the RIGHT ARROW icon** (→)
   - It's next to the checkmark you clicked before
   - Move your mouse over it - tooltip says "PlatformIO: Upload"
8. **Click once** on the **right arrow** icon (→)
9. **WATCH the terminal** at the bottom
   - You'll see text scrolling
   - It might rebuild the code first (that's normal)
   - You'll see "Uploading..."
10. **A NEW WINDOW might appear** called "Teensy"
    - This is the Teensy Loader program
    - This is NORMAL - don't close it
    - It shows a progress bar
11. **WATCH for the upload to complete**:
    - The Teensy window (if it appeared) will show "Reboot OK"
    - The Teensy will automatically restart
    - The terminal in VS Code will show `[SUCCESS]` in **GREEN**
12. **If you see `[SUCCESS]`**:
    - **EXCELLENT!** The firmware is now on the Teensy!
    - The Teensy has restarted and is running your program
    - You can close the Teensy Loader window if it appeared (click the X)
13. **If you see `[FAILED]`**:
    - See [Troubleshooting - Upload Failed](#problem-upload-failed--teensy-not-found)
    - Make sure the Teensy is plugged in
    - Try pressing the white button on the Teensy, then click Upload again

---

## Connecting to the Device

### Step 1: Find the COM Port

The "COM port" is how Windows identifies the Teensy. We need to find out what number it is.

1. **Make sure the Teensy is plugged into your computer** via micro-USB
   - If not, plug it in now
   - Wait 10 seconds after plugging it in
2. **Press and hold** the **Windows key** (⊞)
3. **While holding it**, press the letter **X** key
4. **Release both keys**
5. **A menu appears** in the bottom-left corner of your screen
   - This is the "Quick Link menu"
6. **Look through the menu** for an item that says **"Device Manager"**
   - It's usually about halfway down the list
7. **Click once** on **"Device Manager"**
8. **A new window opens** called "Device Manager"
   - This window shows all the hardware connected to your computer
9. **Look for** an item in the list called **"Ports (COM & LPT)"**
   - You may need to scroll down to find it
   - It has a little arrow or triangle next to it
10. **Click once** on the arrow/triangle next to "Ports (COM & LPT)"
    - The list expands to show devices underneath
11. **Look for** an entry that says one of these:
    - "USB Serial Device (COM3)"
    - "Teensy USB Serial (COM4)"
    - "Serial Port (COM5)"
    - The number might be different - could be COM3, COM4, COM5, COM6, etc.
12. **WRITE DOWN** the COM number
    - Example: If it says "USB Serial Device (COM4)", write down: **COM4**
    - You'll need this number in the next steps
13. **Close** the Device Manager window (click the X in the top-right)

**Can't find any COM ports?**
- **Unplug** the Teensy from your computer
- **Wait** 5 seconds
- **Plug it back in**
- **Wait** 10 seconds
- Try the steps above again
- Still nothing? See [Troubleshooting - No COM Port](#problem-no-com-port-shows-up-in-device-manager)

### Step 2: Open PowerShell in the Right Folder

PowerShell is a program where you type commands. We need to open it in the SEEsDriver folder.

**Method 1 - EASIEST Way (Using File Explorer):**

1. **Find** the folder icon on your taskbar (bottom of screen)
   - It looks like a yellow folder
   - It might say "File Explorer" when you hover over it
2. **Click once** on the folder icon
3. **File Explorer opens** - this shows your files and folders
4. **Navigate to where you saved the repository**:

   **If you saved it in Documents:**
   - **Click** "Documents" in the left sidebar
   - **Double-click** the folder named "aeris-sees-software"
   - **Double-click** the folder named "SEEsDriver"

   **If you saved it on Desktop:**
   - **Click** "Desktop" in the left sidebar
   - **Double-click** the folder named "aeris-sees-software"
   - **Double-click** the folder named "SEEsDriver"

5. **You should now see** files like:
   - SEEs.bat
   - platformio.ini
   - Several folders (src, lib, include, etc.)
6. **Look at the very top** of the File Explorer window
   - There's an address bar showing the folder path
   - It says something like: `This PC > Documents > aeris-sees-software > SEEsDriver`
7. **Click once INSIDE the address bar** (on the text itself)
   - The text becomes highlighted in blue
   - You can now type in this bar
8. **Type exactly**: `powershell`
9. **Press Enter**
10. **A BLUE WINDOW appears** - this is PowerShell!
    - It says "Windows PowerShell" at the top
    - You'll see text ending with something like `PS C:\...\SEEsDriver>`
    - This is the PowerShell prompt
11. **SUCCESS!** PowerShell is open in the correct folder

### Step 3: Run the VIA Console

SEEs.bat is a program that connects to the Teensy and lets you control it.

1. **Make sure the blue PowerShell window is still open**
   - If you closed it, go back to Step 2
2. **Look at the PowerShell window**
   - There should be a prompt that ends with `>`
   - The cursor is blinking, waiting for you to type
3. **Remember the COM port number** you wrote down in Step 1
   - Was it COM3? COM4? COM5?

**If your COM port is COM3:**

4. **Type exactly**: `.\SEEs.bat`
   - Don't forget the period and backslash at the start!
5. **Press Enter**
6. **Go to step 7 below**

**If your COM port is NOT COM3 (it's COM4, COM5, etc.):**

4. **Type exactly**: `.\SEEs.bat COM4`
   - Replace `COM4` with YOUR actual COM port number
   - Example: If yours is COM5, type: `.\SEEs.bat COM5`
   - Make sure there's a SPACE between SEEs.bat and the COM number
5. **Press Enter**
6. **Continue to step 7 below**

**NOW WATCH WHAT HAPPENS:**

7. **The PowerShell window fills with text**
   - You'll see a welcome message
   - You'll see information about connecting
   - This takes 2-5 seconds
8. **LOOK FOR** a prompt that says: `>`
   - When you see this, the program is ready!
   - The cursor will be blinking after `>`
9. **SUCCESS!** You're connected to the Teensy!

**What if it doesn't work?**
- See [Troubleshooting - SEEs.bat closes immediately](#problem-viabat-opens-and-immediately-closes)
- Or see [Troubleshooting - Python not found](#problem-python-is-not-recognized-as-a-command)

### Step 4: Test the Connection

Let's make sure everything is working by asking for help.

1. **Look at the PowerShell window** with the `>` prompt
2. **Click anywhere in the PowerShell window** to make sure it's active
3. **Type exactly**: `help`
   - All lowercase is fine
4. **Press Enter**
5. **WATCH the screen** - text should appear immediately!
6. **You should see** a list of available commands appear, like this:

```
Available Commands:
  help      - Show this help message
  measure   - Take single measurement
  identify  - Query device identification
  auto      - Start auto mode (auto [seconds])
  stop      - Stop auto mode
  status    - Show system status
  sd-on     - Enable SD card logging
  sd-off    - Disable SD card logging
```

7. **After the commands**, you'll see the `>` prompt again
8. **If you see this list**:
   - **PERFECT!** Everything is working!
   - You're ready to take measurements!
9. **If nothing happens or you see an error**:
   - See [Troubleshooting - No output](#problem-no-output-in-putty--console-is-blank)
   - Or see [Troubleshooting - Commands don't work](#problem-commands-dont-work--nothing-happens)

---

## Taking Measurements

Now the fun part - actually using the detector to collect data!

### Single Measurement

Let's take ONE measurement.

1. **Make sure** you see the `>` prompt in the PowerShell window
2. **Type exactly**: `measure`
3. **Press Enter**
4. **WATCH THE SCREEN** - lots of text will appear!
5. **BE PATIENT** - this takes about 15 seconds
6. **You'll see** progress messages like:
   - "Starting Measurement #1"
   - "Querying device identification..."
   - "Preparing measurement parameters..."
   - "Starting measurement..."
   - "Acquiring data..."
   - Lots of CSV data (numbers separated by commas)
   - "Measurement Complete!"
7. **After** all this text, you'll see the `>` prompt again
8. **SUCCESS!** You just took your first measurement!
9. **Your data is automatically saved** in the SEEsDriver folder

### Automatic Mode (Take Measurements Repeatedly)

Want the detector to take measurements automatically every minute? Here's how:

1. **At the `>` prompt**, type: `auto 60`
   - That's the word "auto", a space, then the number "60"
   - The "60" means "every 60 seconds" (1 minute)
2. **Press Enter**
3. **You'll see**: `Auto-measurement mode STARTED`
4. **The system will now take a measurement every 60 seconds**
   - You'll see all the measurement text appear
   - Then it waits 60 seconds
   - Then takes another measurement
   - This repeats forever until you stop it
5. **To STOP automatic mode**:
   - **Type**: `stop`
   - **Press Enter**
   - You'll see: `Auto-measurement mode STOPPED`

**Want a different interval?**
- Type `auto 30` for every 30 seconds
- Type `auto 120` for every 2 minutes (120 seconds)
- Type `auto 300` for every 5 minutes (300 seconds)

### Check System Status

Want to see what's happening?

1. **Type**: `status`
2. **Press Enter**
3. **You'll see information like**:
   - SD Card Logging: ENABLED or DISABLED
   - Auto Mode: RUNNING or STOPPED
   - Auto Interval: How many seconds between measurements
   - Measurements Taken: Total count
   - Uptime: How long the system has been running
4. **This helps you check**:
   - Is automatic mode running?
   - How many measurements have been taken?
   - Is the SD card working?

### Turn SD Card Logging On/Off

If you have an SD card in the Teensy, you can control whether it saves data.

**To turn ON SD card logging:**
1. **Type**: `sd-on`
2. **Press Enter**
3. You'll see a confirmation message
4. Now all measurements will be saved to the SD card

**To turn OFF SD card logging:**
1. **Type**: `sd-off`
2. **Press Enter**
3. You'll see a confirmation message
4. Measurements will no longer be saved to the SD card (but still saved to your computer via SEEs.bat)

---

## Available Commands

| Command | Description |
|---------|-------------|
| `on` | Start data collection (LED blinks, data streams) |
| `off` | Stop data collection (LED solid, streaming stops) |
| `snap` | Capture ±2.5s window (2.5s before + 2.5s after command) ||| Command | Description |
|---------|-------------|
| `on` | Start data collection (LED blinks, data streams) |
| `off` | Stop data collection (LED solid, streaming stops) |
| `snap` | Capture ±2.5s window (2.5s before + 2.5s after command) ||| Command | Description |
|---------|-------------|
| `on` | Start data collection (LED blinks, data streams) |
| `off` | Stop data collection (LED solid, streaming stops) |
| `snap` | Capture ±2.5s window (2.5s before + 2.5s after command) |-|| Command | Description |
|---------|-------------|
| `on` | Start data collection (LED blinks, data streams) |
| `off` | Stop data collection (LED solid, streaming stops) |
| `snap` | Capture ±2.5s window (2.5s before + 2.5s after command) |

**Examples:**
```
> on              # Single measurement
> on              # Auto mode every 30 seconds
> snap               # Check system status
> off                # Enable logging
> off                 # Stop auto mode
```

---

## Telemetry

### System Status
- **SD Card Status** - ENABLED / DISABLED
- **Auto Mode** - RUNNING / STOPPED
- **Auto Interval** - Seconds between measurements
- **Measurement Count** - Total measurements taken
- **System Uptime** - Time since boot (seconds)

### Spectrum Data
- **Format**: 2048 pixels × 16-bit intensity values
- **Size**: 4,106 bytes raw binary (10-byte header + 4,096 bytes pixel data)
- **Output**: CSV (Serial + SD) and hex dump (SD only)

### Data Files (SD Card)
- `meas_0001.txt` - Raw measurement (hex format, ~12,350 bytes)
- `spectrum_0001.csv` - Spectrum data (Pixel,Intensity format)
- Files increment automatically

---

## Data Capture

**Good News!** When you use `SEEs.bat`, all measurements are **automatically saved** to timestamped session folders in the SEEsDriver directory. You don't need to do anything extra!

**Where to find your data:**
1. Open File Explorer
2. Navigate to: `aeris-sees-software\SEEsDriver\`
3. Look for folders with names like: `sees_outputlogs/YYYYMMDD.HHMM`
4. Inside you'll find all your CSV files

### Method 1: Automatic Logging (Using SEEs.bat - RECOMMENDED)

**This happens automatically when you use SEEs.bat:**
- Every measurement is saved to a CSV file
- Files are organized in timestamped session folders
- You can find them in the `SEEsDriver` folder
- Example: `sees_outputlogs/YYYYMMDD.HHMM\spectrum_0001.csv`

**To take measurements:**
1. Run `SEEs.bat` (as described above)
2. Type `measure` to take a single measurement
3. Or type `auto 60` to take measurements every 60 seconds
4. Your data is automatically saved!

### Method 2: Manual Data Capture (Advanced)

If you want to manually capture data using Python scripts:

**Step 1: Open PowerShell in the SEEsDriver folder** (see previous section)

**Step 2: Capture a live measurement:**
```
python capture_measurement.py COM3 my_spectrum.csv
```
- Replace `COM3` with your actual COM port
- Replace `my_spectrum.csv` with your desired filename
- The script will wait for you to type `measure` in PuTTY/VIA console
- Data will be saved to `my_spectrum.csv`

**Step 3: List files on SD card:**
```
python file_transfer.py COM3 list
```

**Step 4: Download a specific file from SD card:**
```
python file_transfer.py COM3 get spectrum_0001.csv
```

### Method 3: Reading SD Card Directly

**Easiest way to get ALL your data:**
1. **Unplug** the Teensy from your computer
2. **Remove** the SD card from the Teensy
3. **Insert** the SD card into your computer (you may need an SD card reader)
4. **Open** the SD card in File Explorer
5. **Copy** all the files to your computer
6. Files will be named like:
   - `meas_0001.txt` (raw hex data)
   - `spectrum_0001.csv` (CSV format - use this one!)
7. **Safely eject** the SD card
8. **Re-insert** it into the Teensy
9. **Plug** the Teensy back into your computer

---

## Example Session

```
════════════════════════════════════════════════════════
  AERIS SEEs Detector Control System
  Version 3.0 - Command Console Mode
════════════════════════════════════════════════════════

> snap
────────────────────────────────────────────
System Status:
────────────────────────────────────────────
  SD Card Logging:     ENABLED
  Auto Mode:           STOPPED
  Measurements Taken:  0
  Uptime:              5 seconds
────────────────────────────────────────────

> on

════════════════════════════════════════════════════════
Starting Measurement #1
════════════════════════════════════════════════════════
📁 Logging to: /meas_0001.txt
📡 Querying device identification...
⚙️  Preparing measurement parameters...
🔬 Starting measurement...
⏳ Acquiring data...
✅ Data acquisition complete
📝 Acknowledging measurement...
💾 Data logged to SD card
════════════════════════════════════════════════════════
Measurement Complete!
════════════════════════════════════════════════════════

> on
🔄 Auto-measurement mode STARTED
   Interval: 30 seconds

> off
⏹  Auto-measurement mode STOPPED
```

---

## Troubleshooting

### Problem: "Python is not recognized as a command"

**This means Python is not installed or not in your PATH.**

**Solution:**
1. Go back to [Step 1: Install Python](#step-1-install-python-required-for-data-capture)
2. **Make sure** you check "Add Python to PATH" during installation
3. If you already installed Python without checking that box:
   - Uninstall Python (Settings → Apps → Python → Uninstall)
   - Re-install Python and CHECK the "Add Python to PATH" box

**To verify Python is working:**
1. Open a NEW PowerShell window (close old ones)
2. Type: `python --version`
3. Press Enter
4. You should see: `Python 3.x.x`

### Problem: "SEEs.bat is not recognized" or "cannot find SEEs.bat"

**You're not in the right folder.**

**Solution:**
1. Open File Explorer
2. Navigate to the `SEEsDriver` folder
3. You should SEE `SEEs.bat` in the file list
4. Click in the address bar at the top
5. Type `powershell` and press Enter
6. NOW try `.\SEEs.bat`

**Alternative:**
1. Open PowerShell from the Start menu
2. Type: `cd "C:\Path\To\Your\aeris-sees-software\SEEsDriver"`
   - Replace with the actual path where you saved it
3. Press Enter
4. Type: `.\SEEs.bat`

### Problem: No COM Port Shows Up in Device Manager

**The Teensy isn't being detected by Windows.**

**Solution:**
1. **Unplug** the Teensy and **plug it back in**
2. Try a **different USB cable** (some cables are charge-only, not data)
3. Try a **different USB port** on your computer
4. **Restart** your computer
5. Check if Windows Update has any driver updates:
   - Go to Settings → Update & Security → Windows Update
   - Click "Check for updates"
6. Install Teensy drivers manually:
   - Go to: `https://www.pjrc.com/teensy/td_download.html`
   - Download and install "Teensyduino"
   - This includes the USB drivers

### Problem: SEEs.bat opens and immediately closes

**There's an error with the Python script or COM port.**

**Solution 1 - Check if Python is working:**
1. Open PowerShell in the SEEsDriver folder
2. Type: `python --version`
3. If you see an error, Python isn't installed correctly

**Solution 2 - Try with the correct COM port:**
1. Check your COM port in Device Manager (see [Step 1: Find the COM Port](#step-1-find-the-com-port))
2. Run: `.\SEEs.bat COM4` (use your actual COM port number)

**Solution 3 - Check for Python dependencies:**
1. Open PowerShell in the SEEsDriver folder
2. Type: `pip install pyserial`
3. Press Enter
4. Wait for installation
5. Try running `.\SEEs.bat` again

### Problem: Build Failed in PlatformIO

**There's a compilation error.**

**Solution:**
1. **Close Visual Studio Code** completely
2. **Re-open** Visual Studio Code
3. **File → Open Folder** → Select `aeris-sees-software\SEEsDriver`
4. **Wait** for PlatformIO to initialize (watch the bottom bar)
5. Try building again (click the ✓ icon)

**If it still fails:**
1. Look at the error message in red text at the bottom
2. Take a screenshot or copy the error
3. Check if it says "missing library" or "dependency"
4. Try: **Delete** the `.pio` folder in the SEEsDriver directory
5. Try building again (PlatformIO will re-download everything)

### Problem: Upload Failed / Teensy Not Found

**PlatformIO can't find the Teensy.**

**Solution:**
1. **Make sure** the Teensy is plugged in via USB
2. **Check** Device Manager to confirm the COM port exists
3. **Try pressing** the white button on the Teensy (this puts it in programming mode)
4. **Immediately after** pressing the button, click Upload (→) again
5. **Try a different USB cable**
6. **Try a different USB port**

### Problem: No output in PuTTY / Console is blank

**The connection isn't working, or the firmware isn't running.**

**Solution:**
1. **Check baud rate** is 115200 in PuTTY
2. **Close PuTTY** completely
3. **Unplug** the Teensy and **plug it back in**
4. **Re-open** PuTTY with the correct settings
5. Press **Enter** a few times - you should see the `>` prompt
6. Type `help` and press Enter

**If using SEEs.bat:**
1. Close the console
2. Unplug the Teensy
3. Plug it back in
4. Run `.\SEEs.bat` again

### Problem: detector Not Detected / Enumeration Failed

**The detector isn't communicating with the Teensy.**

**Solution:**
1. **Check** that the detector's USB cable is properly connected to the Teensy USB Host pads
2. **Verify** the color-coded wires:
   - Red (5V) → 5V pad
   - Green (D+) → D+ pad
   - White (D–) → D– pad
   - Black (GND) → GND pad
3. **Unplug** the detector's USB cable from the Teensy and **plug it back in**
4. **Check** for continuity with a multimeter if you have one
5. Look at the Serial console for enumeration messages - it should say when it detects the device

### Problem: SD Card Not Working / SD Card Errors

**The SD card isn't being detected or can't be written to.**

**Solution:**
1. **Remove** the SD card
2. **Check** that the write-protect tab is NOT locked (slide it up)
3. **Format** the SD card on your computer:
   - Insert SD card into your computer
   - Open File Explorer
   - Right-click on the SD card drive
   - Select "Format..."
   - File System: **FAT32** (very important!)
   - Click "Start"
4. **Re-insert** the SD card into the Teensy
5. Try the `sd-on` command in the console

**If SD card still doesn't work:**
- Try a different SD card (some cards are incompatible)
- Max supported size is usually 32GB for FAT32
- Use a reputable brand (SanDisk, Samsung, Kingston, etc.)

### Problem: Commands Don't Work / Nothing Happens

**The firmware isn't responding to commands.**

**Solution:**
1. Make sure you press **Enter** after typing each command
2. Commands are **case-insensitive** (you can type `MEASURE` or `measure`)
3. Try typing `help` to see if ANY response comes back
4. Check that your baud rate is **115200**
5. Make sure the firmware uploaded successfully (look for `[SUCCESS]`)
6. Try re-uploading the firmware

### Problem: "Access Denied" when opening COM port

**Another program is using the COM port.**

**Solution:**
1. **Close** any other serial terminal programs (PuTTY, Arduino Serial Monitor, etc.)
2. **Close** any other instances of SEEs.bat
3. **Unplug** the Teensy and **plug it back in**
4. Try connecting again

### Problem: Python Script Says "Module not found: serial"

**The PySerial library isn't installed.**

**Solution:**
1. Open PowerShell
2. Type: `pip install pyserial`
3. Press Enter
4. Wait for installation to complete
5. Try running the script again

### Problem: I accidentally closed the PowerShell/VIA window

**No problem! Just open it again.**

**Solution:**
1. Follow steps in [Step 2: Open PowerShell](#step-2-open-powershell)
2. Run `.\SEEs.bat` again
3. Continue where you left off
4. Your previous measurements are still saved in the session folders

**Note:** Each time you run SEEs.bat, it creates a NEW session folder with a timestamp.

### Problem: Where did my CSV files go?

**They're in the SEEsDriver folder in timestamped session folders.**

**Solution:**
1. Open File Explorer (Windows Key + E)
2. Navigate to where you cloned the repository
3. Go to: `aeris-sees-software\SEEsDriver\`
4. Look for folders named like: `sees_outputlogs/YYYYMMDD.HHMM`
5. Open the folder - your CSV files are inside!
6. You can open CSV files with Excel or any text editor

**Tip:** The folders are named with the date and time you started SEEs.bat

### Problem: Excel won't open my CSV file correctly

**Excel might be misinterpreting the comma-separated format.**

**Solution:**
1. Open Excel
2. Go to File → Open
3. Select "Text Files" or "All Files" from the file type dropdown
4. Navigate to your CSV file
5. Select it and click Open
6. Excel will start the "Text Import Wizard"
7. Choose "Delimited"
8. Click Next
9. Check "Comma" as the delimiter
10. Click Finish

**Alternative:** Right-click the CSV file → Open With → Notepad to see the raw data

### Still Having Problems?

**Check these common issues:**
- ✓ Is the Teensy actually plugged in? (Check for a blinking LED)
- ✓ Is the detector powered? (Should see a light on it)
- ✓ Did you upload the firmware successfully?
- ✓ Is Python installed and in your PATH?
- ✓ Are you in the correct folder (SEEsDriver)?
- ✓ Is your antivirus blocking the Python scripts?

**If nothing works:**
1. Take a screenshot of the error
2. Note exactly what step you're stuck on
3. Note your COM port number
4. Check the GitHub repository issues page for similar problems

---

## Data Budget

**Current system (ASCII hex format):**
- File size: ~12,355 bytes per measurement

**Future optimization (raw binary):**
- File size: ~4,110 bytes per measurement (67% smaller)
- Same data, just not human-readable
- Requires conversion script for viewing

---

## One-Page Cheat Sheet (Print This!)

### Daily Use - Taking Measurements

**1. Plug in Teensy** (micro-USB to computer)

**2. Open PowerShell in SEEsDriver folder:**
   - Open File Explorer
   - Navigate to `aeris-sees-software\SEEsDriver`
   - Click address bar, type `powershell`, press Enter

**3. Run SEEs.bat:**
   - Type: `.\SEEs.bat`
   - Or if not COM3: `.\SEEs.bat COM4` (use your port)

**4. Commands:**
   - `help` - Show all commands
   - `status` - Check system status
   - `measure` - Take ONE measurement (~15 seconds)
   - `auto 60` - Take measurements every 60 seconds
   - `stop` - Stop automatic measurements
   - `sd-on` / `sd-off` - Enable/disable SD card

**5. Find your data:**
   - Open `SEEsDriver` folder
   - Look for `session_2025-XX-XX_...` folders
   - CSV files are inside!

### Finding Your COM Port

1. Press `Windows Key + X`
2. Click "Device Manager"
3. Expand "Ports (COM & LPT)"
4. Look for "USB Serial Device (COMX)" - note the number

### Common Problems Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| Python not found | Reinstall Python, CHECK "Add to PATH" |
| SEEs.bat not found | Make sure you're in SEEsDriver folder |
| COM port error | Check Device Manager, unplug/replug Teensy |
| Script closes immediately | Try: `pip install pyserial` |
| No measurements | Check Teensy is plugged in, try `help` command |
| Can't find data | Look in SEEsDriver for `session_...` folders |

### Keyboard Shortcuts

- `Windows Key + R` = Run dialog
- `Windows Key + X` = Quick menu (Device Manager)
- `Windows Key + E` = File Explorer
- `Ctrl + C` in PowerShell = STOP/Cancel
- `Ctrl + Shift + P` in VS Code = Command Palette

### Important Websites

- Python: `https://www.python.org/downloads/`
- VS Code: `https://code.visualstudio.com/`
- Git: `https://git-scm.com/download/win`
- Repository: `https://github.com/hsfl/aeris-sees-software`

---

**AERIS VIA Payload Team** - 2025

\# Advanced Sound Recorder \& Editor – v1.4



\*\*Release Date:\*\* 2025-09-24  



Welcome to the ultimate command-line sound recorder and editor for power users. Yes, this thing actually works now. No more mysterious crashes, no more typing long flags like a caveman, and yes, it even supports MP3 and FLAC. Buckle up.  



---



\## 🐞 Bug Fixes (a.k.a. things we actually fixed so your PC stops screaming at you)



\- \*\*Python 3.13+ compatibility\*\*: Install `audioop-lts` (`pip install audioop-lts`) if you don’t want weird crashes.  

\- \*\*list\_devices AttributeError\*\*: Devices now show up instead of ghosting you.  

\- \*\*Filename NoneType\*\*: Forgot to enter a filename? No problem. We now handle it gracefully.  

\- \*\*General robustness improvements\*\*: Sneezing on your keyboard won’t kill the program anymore.  



---



\## ✨ New Features



\- \*\*Interactive mode prompt\*\*: Stop remembering `--interactive`. The program now politely asks if you want it.  

\- \*\*Recording shortcuts\*\*:  

&nbsp; - `p` → pause/resume recording  

&nbsp; - `s` → check status during recording  

\- \*\*Edit menu\*\*: trim, merge, fade in/out, normalize, auto-list files. Basically, fix your mistakes without headaches.  

\- \*\*Dynamic filenames\*\*: `{timestamp}`, `{date}`, `{time}`, `{counter}`. Never overwrite another file by accident again.  

\- \*\*Multi-format recording\*\*: WAV, MP3, FLAC. Choose your poison.  



---



\## 🛠 Installation (yes, this actually matters)



To avoid the lovely tracebacks and crashes:



1\. \*\*Clone this repo\*\* or download the source:



```bash

git clone https://github.com/yourusername/advanced-sound-recorder.git

cd advanced-sound-recorder

2\. 

Install dependencies:

bash

Copy

pip install pyaudio pydub keyboard audioop-lts

Windows users: You will need FFmpeg for MP3/FLAC support. Download it from https://ffmpeg.org/download.html and add the bin directory to your PATH. Otherwise, enjoy WAV-only recordings and endless warnings.

3\. 

Run it:

bash

Copy

python sound\_recorder.py

If you’re feeling lazy, you’ll be asked whether you want interactive mode. Say yes.

&nbsp;

⚡ Usage

• 

Interactive recording:

bash

Copy

python sound\_recorder.py --I --R

• 

Edit menu:

bash

Copy

python sound\_recorder.py --E

• 

Recording shortcuts during recording:

• 

p → pause/resume

• 

s → status check

• 

Dynamic filenames example:

bash

Copy

python sound\_recorder.py --I --R --filename "podcast\_{timestamp}"

Note: {timestamp} → YYYYMMDD\_HHMMSS

&nbsp;

🎉 Devices

• 

Lists all available audio input devices.

• 

Select a specific device or default to system input.

• 

Graceful fallback if the device is unavailable.

&nbsp;

👏 Thank Yous

To all the anonymous bug reporters: your suffering was not in vain. Thanks to you, this version is slightly less terrible.

&nbsp;

TL;DR

It works, doesn’t explode, supports multiple formats, has a proper edit menu, is interactive, and has dynamic filenames. Basically, it’s now usable, and even your mother could use it if she really tried.


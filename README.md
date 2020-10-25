The [Elgato Cam Link 4K](https://www.elgato.com/en/gaming/cam-link-4k) is a USB device to capture HDMI video, intended for use with mirrorless or DSLR cameras that can output clean HDMI.

It appears as a USB Video Class (UVC) device, and so is natively supported under Linux. Unfortunately, as [Mike Walters](https://assortedhackery.com/patching-cam-link-to-play-nicer-on-linux/) clearly documented, there is a bug in the firmware causing it to declare it supports video formats that it in fact does not. This causes most (but not all) apps on Linux to fail to open it as a webcam.

Fortunately, it is possible to workaround this by creating a virtual ("loopback") video device, and using `ffmpeg` to convert from a format the Cam Link actually supports to a format that all Linux apps will support. [johanhalse](https://ubuntuforums.org/showthread.php?t=2444854) documented this workaround -- but it requires manually running a script. Moreover, the appropriate parameters will vary depending on the video stream being captured.

The Python script in this repository can run in the background, so can be started in `.xinitrc` or a similar startup script. It auto-detects which device the Cam Link is connected to, the resolution and the frame rate and runs the appropriate `ffmpeg` command. If `ffmpeg` fails (for example, the resolution of the connected device changes) then it will repeat this process.

To run this script, you will need:
  - Python3
  - ffmpeg
  - v4l2loopback

On Ubuntu, `sudo apt-get install v4l2loopback-utils v4l2loopback-dkms ffmpeg` should suffice to install the dependencies.

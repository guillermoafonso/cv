# Setup: Counting Game for Child User

The counting game runs automatically when a "child" user logs in.
The child must complete the game before they can use the desktop.
Your own user account is not affected.

## Setup Steps

### 1. Create the child user

```bash
sudo adduser child
```

Pick a simple password (or one the child knows). When it asks for
Full Name etc., you can just press Enter to skip.

### 2. Clone the game into the child's home folder

```bash
sudo cp -r ~/cv /home/child/cv
sudo chown -R child:child /home/child/cv
```

### 3. Set up autostart for the child user

```bash
sudo mkdir -p /home/child/.config/autostart
sudo cp ~/cv/counting-game-autostart.desktop /home/child/.config/autostart/
sudo chown -R child:child /home/child/.config
```

### 4. Test it

Log out of your account, and log in as `child`. The counting game
should appear fullscreen after a couple of seconds. After completing
it, the desktop is usable.

## How It Works

- When `child` logs in, the desktop starts normally
- The autostart entry launches the counting game fullscreen
- The game locks the screen (no quit button, hidden cursor)
- After getting the required correct answers, the game exits
- The child can then use the desktop

Your own account is completely unaffected.

## How to Disable

Delete the autostart file:

```bash
sudo rm /home/child/.config/autostart/counting-game-autostart.desktop
```

## Removing the Old systemd Service

If you set up the systemd service from before, disable it:

```bash
sudo systemctl disable counting-game.service
sudo rm /etc/systemd/system/counting-game.service
sudo systemctl daemon-reload
```

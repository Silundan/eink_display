# e-ink Display project
Small scripts to display weather details and random images with raspberry pi and inky 7 color eink display from Pimoroni.

This is a just-for-fun and practice project for myself as I am learning python and linux, and I wanted an e-ink meme display, and sometimes showing the weather. As this is a hobby project and I am no professional programmer, the codes are a bit speghatti, hopefully I will be improving on the codes later in my journey of programming. :)

And i still have a button unused, will be expanding on it later if I have some more idea to make a good use of it. And the refresh rate of the panel is \~30 secs for a full refersh, using it as a clock is kinda pointless...

Weather icon font is made by [Alessio Atzeni](https://www.alessioatzeni.com/), you can check the original file [here](https://www.alessioatzeni.com/meteocons/).

## Hardware list
- Raspberry Pi (Any model with 40-pin GPIO is fine)
- Inky Impression 5.7" (7 colour ePaper/eInk HAT) from [Pimoroni](https://shop.pimoroni.com/products/inky-impression-5-7)

## Default settings

Currently the top button (Button A) is showing weather summary for the cities you configured in `./weather/config.ini`.

The second button (Button B) is unused, only producing messages on console.

The third button (Button C) is clear function from the [inky library](https://github.com/pimoroni/inky/blob/master/examples/7color/clear.py).

The bottom button (Button D) is the random photo display function (picking photos from `./img/` by default).

## Installation
_You can copy and paste the following commands to install the packages needed._

Enable I2C and SPI with raspberry pi config: `sudo raspi-config`

Installing python library for Inky (instruction from their [GitHub](https://github.com/pimoroni/inky))
```
curl https://get.pimoroni.com/inky | bash
```

**Installing aiohttp:**
```
pip3 install aiohttp
```

**Install git on your system:**

```
sudo apt update
sudo apt install git
```

And download the files here with: 
```
git clone https://github.com/Silundan/eink_display.git
```

After that, go to the `project/weather` folder, and edit the content of `config.ini`.
In most cases it can be done with the following command:
```
cd /home/pi/eink_display/weather
nano config.ini
```
You will have to get a free API key from [Open Weather Map](https://openweathermap.org/).

And pick 3 cities you want to track the weather (possibly adjustable in the future), for city/locations that with a space in between, it is safe to put it as is (eg. Hong Kong). The cities are seperated with `;` not a space, considering the fact that some places (like Hong Kong) contain spaces in between and with in the usage of the OWM API.

Finally adjust the project folder if you needed, and remember to change the config loading in display.py and weather.py if needed too.

This should be all you need.

## Setting up cron job to go full auto

If you don't want to ssh into your pi and start the scripts manually, you can setting up your system to run the script automatically with cronjob. But first you will need to make the python scripts executable:

```
sudo chmod +x /home/pi/eink_display/display.py
sudo chmod +x /home/pi/eink_display/weather/get_weather.py
```

Setting up cron job by typing `crontab -e` in the console, if this is your first time, you will have to pick an editor (I am using nano). Assuming you are pulling the repo in `/home/pi/`, you can set up a cron job to fetch the weather data from OWM every 15 mins _(00/15/30/45)_ with this entry:
```
*/15 * * * * /home/pi/eink_display/weather/get_weather.py
```
And starting the main display script on reboot:
```
@reboot sleep 60 && /home/pi/eink_display/display.py
```

After that press **Control + S**, and **Control + X** to save the changes and exit nano.

Then type in `sudo reboot` (for SSH, if you aren't connecting via SSH then `reboot`), and the scripts should be starting automatically on boot.

## Suggestions / Feedback
Please feel free to send me your ideas and suggestions on GitHub, and if you have a better idea and/or bug fixes please don't be shy to make a Pull Request. :)

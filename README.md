APK with android app located in the APK folder and named 'app-release-unsigned.apk'.
Android application code locate in the 'MyApplication' folder.
Autotest script located in the 'TestTaskLeadsdoit' > 'TestTask.py'.

Setup environment:
1. Install NodeJS
2. Install Python
3. Install Appium
4. Install UIautomator2 driver
5. Install Java
6. Install Android Studio
7. Add variables for Java and Android SDK
8. In project install requests and appium-python-client

Test script setupped to start test case using emulator Pixel 6 Pro and Android API 34 via Appium

You can change launch parameters in the code by changing info in the 'desired_caps':
desired_caps = {
    'platformName': 'Android', - platform
    'platformVersion': '12.0', - version of android
    'app': '/Users/vlad/AndroidStudioProjects/MyApplication/app/build/outputs/apk/release/app-release-unsigned.apk', - APK location
    'avd': 'Pixel_6_Pro_API_34', - emulated device name
    'chromedriverExecutable': '/usr/local/Caskroom/chromedriver/chromedriver_mac64/chromedriver', - Chromedriver location
}


To start test case you should:
1. Start Appium v2.0.0-rc.3 server on the local host. (to instal last appium perform command 'npm i -g appium@next').
2. Start android emulator.
3. Then you can open folder with downloaded 'TestTask.py' in the command line using 'cd <way to folder with file>'.
4. And finaly enter command 'python TestTask.py'. Also you can use command 'python TestTask.py --log' to see logs in the console.


What test can do:
1. Log results to .txt
2. Log results to console
3. Create video recording of the test execution 
4. You can set retries (in case if script execution will be failed it will check MAX_RETRY_COUNT and perform it again if curent run number < value that set in MAX_RETRY_COUNT





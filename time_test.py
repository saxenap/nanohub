import os, time
print(time.strftime('%X %x %Z'))
os.environ['TZ'] = 'Europe/London'
time.tzset()
print(time.strftime('%X %x %Z'))
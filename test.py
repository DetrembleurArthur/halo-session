from datetime import *

seconds = 300
timing_str = " ".join([data[0]+data[1] for data in zip(str(timedelta(seconds=seconds)).split(':'), ["h", "m", "s"])])

print(timing_str)

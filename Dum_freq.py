import os 
import random 
import datetime
from datetime import timezone 
import time

def gen_freq_rInt(FREQ):
    CYCLETIME = 1/FREQ
    t0 = time.perf_counter()    # Time ref point in ms
    time_counter = t0           # Will be incremented with CYCLETIME for each iteration
    info = []
    while 1:
        ### Code that will read message bytes from a port
        now = time.perf_counter()
        time_elapsed = now - time_counter
        if time_elapsed < CYCLETIME:
            target_time =  CYCLETIME - time_elapsed
            update_freq = 1/(target_time)
            time.sleep(target_time)
        
        # In the full program we write to a csv but in this simple program we will just print it
        milliseconds_since_epoch = datetime.datetime.now(timezone.utc)
        #print(milliseconds_since_epoch)
        rando = random.randint(0,100)
        print("Freq (Hz):",round(update_freq), "random number: ", rando)
        if rando in (99,100):
            break
        info.append((round(update_freq), rando))
    

        time_counter += CYCLETIME
    return info 

Z = gen_freq_rInt(50)
print(Z)
for i in range(len(Z)):
    print("Freq (Hz):",Z[i][0], "random number: ", Z[i][1])

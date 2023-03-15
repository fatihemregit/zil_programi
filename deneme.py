from pygame import mixer
import time
mixer.init()

ses = mixer.Sound("ogretmen_giris_zili.wav")
key = 0
ses.play()
time.sleep(14)
mixer.music.stop()

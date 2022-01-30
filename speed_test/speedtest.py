import json
import logging
import os
import socket
import sys
import time

logging.basicConfig(filename='/home/pi/speedtest.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

if __name__ == '__main__':
    logging.info('Starting speed test')
    start_time = time.time()
    output = ''
    try:
        stream = os.popen('/home/pi/.local/bin/speedtest-cli --simple')
        output = stream.read()
        logging.debug('Speed test done: %s', output)
    except:
        logging.error('Failed to run speed test: %s', sys.exc_info()[0], exc_info=True)

    output_parts = output.split()
    ping_ms = float(output_parts[1])
    upload_mbs = float(output_parts[7])
    download_mbs = float(output_parts[4])

    gelf_object = dict()

    gelf_object['version'] = '1.1'
    gelf_object['host'] = 'plex'
    gelf_object['short_message'] = output.replace('\n', ' ')
    gelf_object['timestamp'] = time.time()
    gelf_object['level'] = 1
    gelf_object['_speedtest_ping_ms'] = ping_ms
    gelf_object['_speedtest_upload_mbs'] = upload_mbs
    gelf_object['_speedtest_download_mbs'] = download_mbs

    gelf_text = '{}\n'.format(json.dumps(gelf_object))

    logging.debug('Submitting GELF message %s', json.dumps(gelf_object))

    host = '192.168.50.200'
    port = 12201
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(bytes(gelf_text, 'utf-8'))
    s.close()
    logging.debug('GELF message submitted')
    total_time = time.time() - start_time
    logging.info('Speed test complete in %.2f seconds: %.2f Mbit/s up %.2f Mbit/s down', total_time, upload_mbs, download_mbs)

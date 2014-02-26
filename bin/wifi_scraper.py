import math
import os
import subprocess


# This uses the http://en.wikipedia.org/wiki/Free-space_path_loss formula
# to esitmate distance from a wifi signal. Seems to be accurate within ~3ft.
# This can be further tuned w/ knowledge of different radio equipment signatures.
# https://code.google.com/p/wifisigmap/


def to_distance_m(freq, level):
  """ Convert signal strength to meters. """
  return math.pow(10, ((27.55 - (20 * math.log10(freq)) - level)/20))


def scrape_wireless_network(mac, address, chan, freq, qual, level):
  """ freq:mhz, qual:percentage, level:dbm """
  dist = to_distance_m(freq, level)
  print '%s %s/%s: -- DISTANCE: %sm' % (mac, address, chan, dist)


def scrape_wireless_networks():
  """Run iwlist scan and keep track of the networks we see."""
  cmd = ['/sbin/iwlist', 'scan']
  while True:
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    retcode = process.wait()
    if retcode == 0:
      essid = None
      freq = None
      chan = None
      mac = None
      level = None
      qual = None
      for line in process.stdout.readlines():
        line = line.strip()
        if line.startswith('Cell'):
          mac = line[line.rfind(' ')+1:].strip()
        elif line.startswith('ESSID:'):
          essid = line[7:-1]
          if essid:
            essid = essid.strip()
          else:
            essid = 'HIDDEN'
        elif line.startswith('Channel:'):
          chan = int(line[8:].replace('\t ',''))
        elif line.startswith('Frequency:'):
          # Assume GHz
          freq = 1000*float(line[10:line.find(' ')].replace('\t ', ''))
        elif line.startswith('Quality='):
          n = line.find('Signal level=')
          level = int(line[n+13:-4].strip())
          qual = line[8:n].strip()
          numerator = qual[:qual.find('/')]
          denominator = qual[qual.find('/')+1:]
          qual = 100 * float(numerator)/float(denominator)
        elif line.startswith('IE') and mac:
          scrape_wireless_network(mac, essid, chan, freq, qual, level)
          mac = None
      return
    time.sleep(3)


def main():
  while True:
    scrape_wireless_networks()
    break


if __name__ == "__main__":
  main()

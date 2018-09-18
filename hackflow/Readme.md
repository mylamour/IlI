This is just a funny demo for attack chain

Flow: 

Info Gathering -> Scanning Target -> Bypass WAF/IDS -> Reverse(Persist) Shell -> Transfer Data -> Clean History


You can just try it with :

`python main.py --host 127.0.0.1`

But this demo only implment scan module with `os.system('nmap -A {}'.format(host))`, it's look like roughly and ugly. but as i say, this is only demo. and you can customsized the workflow in `lib` folder.


Programing Design pattern:

* Chain Pattern For Attack Steps
* Commands Pattern For Step
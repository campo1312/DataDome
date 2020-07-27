# This tutorial is for informational purposes only. I guess you'll add the code to your scripts, go ahead but quote me, thanks.

# In the "examples" folder i'll load some DataDome html pages, to let you familiarize with it

# How to bypass it?
# Basically you need a cookie called "datadome", to get it you need to solve the captcha on the page (It isn't a reCaptcha like on starcow)
# and send some requests

# Let's start with SlamJam
# keep in mind that SlamJam sometimes got CloudFlare up, this script will help you only with datadome
import requests, json, re

headers = {"authority":"www.slamjam.com","scheme":"https","accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9","accept-language":"it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7","sec-fetch-dest":"document","sec-fetch-mode":"navigate","sec-fetch-site":"none","sec-fetch-user":"?1","upgrade-insecure-requests":"1","user-agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
url = "https://www.slamjam.com/en_IT/cart"

# Store the datadome redirect challenge url as variable
datadome_url = 'https://www.slamjam.com/on/demandware.store/Sites-slamjam-Site/en_IT/DDUser-Challenge'

s = requests.Session()
proxies = your_proxies_in_json_format 
s.proxies.update(proxies)
 
r = s.get(url, headers=headers)

if r.url != datadome_url:
    print("No needed to solve datadome")
else:
    print('Found datadome challenge')
    
    # Let's extractall the needed info from the page
    dd = json.loads(re.search('var dd=([^"]+)</script>', r.text).group(1).replace("'",'"'))
    initialCid = dd['cid'] 
    hsh = dd['hsh'] 
    t = dd['t']
    host = dd['host']
    cid = s.cookies['datadome'] 
    
    # First post
    first_url = 'https://'+host.replace('&#x2d;','-')+'/captcha/?initialCid={}&hash={}&cid={}&t={}'.format(initialCid, hsh, cid,t)
    first_post = s.get(first_url)

    try:
        data = re.search('getRequest([^"]+)ddCaptcha', first_post.text).group(1)
    except:
        print('Proxy banned')
        # You got the "You have been blocked page", maybe but here a function to handle it and retry with another proxy
        # (You'll see this page if your proxy is banned)

    else:  

        # Get the last needed info to solve the challenge
        useragent = re.search('&ua=([^"]+)&referer=', data).group(1).replace("' + encodeURIComponent('",'').replace("');",'').replace("\n    getRequest += '",'')
        ip = re.search('&x-forwarded-for=([^"]+);', data).group(1).replace("' + encodeURIComponent('",'').replace("')",'')
        # Maybe a rude method, but it works
        
        # We need to generate the "magic number" to pass the challenge
        # I've loaded a js script that do this for us on heroku, send a request like this to generate it
        magic_number = json.loads(requests.get('https://datadome-magic-number-solver.herokuapp.com/datadome?id={}&ua={}'.format(cid, useragent)).text)['id']
        # it will responde with a json like this {"id":169654359} 
        # Number lenght should be 9, else you have probably done something wrong
        
        # SlamJam's datadome page got a captcha, so we need to solve it
        challenge_link = first_post.url
        sitekey = first_post.text.split("'sitekey' : '")[1].split("'")[0]
        response = solvecaptcha(challenge_link, sitekey)
        # Use 2Captcha or some similar services 
        
        second_post = s.get('https://c.captcha-delivery.com/captcha/check?cid={}&icid={}&ccid=null&g-recaptcha-response={}&hash={}&ua={}&referer={}&parent_url={}&x-forwarded-for={}&captchaChallenge={}'.format(cid, initialCid, response, hsh, useragent, datadome_url, datadome_url, ip, magic_number)) 
        if second_post.status_code == 200:
            # If is all good, the server will respond to you with a valid DataDome cookie (the cookie name is datadome), 
            # With it you'll be able to access to the site

            # Example 
            # set-cookie: datadome=Tdx_AVi.VpcPns7JD7n9~EedCazO2jmhdrv_5Hhxmg3ZnUB4iHxn1OE0pum84C2RrSAm_Tnbf7VfF-6.Kfy_XQGeYZBFPwQkbn2~xSmO0J; Max-Age=31536000; Domain=.captcha-delivery.com; Path=/; SameSite=Lax
            
            print('Datadome solved')   
            # Now we got the cookie, you can send the request again and will be all good :)
            # Keep in mind that the cookies are unique for every ip, this cookie will not wotk with another ip
            # Honestly  I don't remember how many time does it last, but you can do some tests 
            # and maybe start harvesting it before a drop 

            # For Courir is the same thing, just rember to save the challenge link as datadome_url
            # for other sites like StarCow, in addition to banning many more proxies as we all know, 
            # it has a different type of captcha, always supported by 2Captcha

        else:
            print("Unexcepted error") 
        
        # Hope i've helped you :)
        
        # If you need other help or work for DataDome, here's my mail 13campo12@gmail.com

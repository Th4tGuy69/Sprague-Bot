import os
import requests

path = os.path.abspath('.')
path = path.replace('\\', '/')
print(path)

def main():
    pens = os.listdir('./Pens')
    for p in pens:
        try:
            htmlFile =  open('./Pens/' + p + '/dist/index.html')
            for line in htmlFile:
                if 'src' in line:
                    if 'http' in line:
                        url = line.replace('<script src=', '')
                        url = url.replace('></script>', '')
                        try:
                            url = url.replace(' ', '')
                            url = url.replace('\'', '')
                            url = url.replace('\"', '')
                        except:
                            pass

                        fname = url.split('/')[-1]

                        # TODO: If cloudflare then download manually

                        print(fname)
                        print(url)
            htmlFile.close()
            return 0
        except:
            pass
        try: 
            dist = os.listdir('./Pens/' + p + '/dist')
            for d in dist:
                if d.endswith('.js'):
                    pass
                    #print(d)
        except: 
            pass
        try: 
            js = os.listdir('./Pens/' + p + '/dist/js')
            for j in js:
                if j.endswith('.js'):
                    pass
                    #print(j)
        except: 
            pass



main()

import sys
import json
import requests

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Referer': 'https://www.google.com/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'If-None-Match': 'W/"5af8185c-3691"',
    'If-Modified-Since': 'Sun, 13 May 2018 10:50:04 GMT',
}

def getJoblists():
    url = "https://job.freebuf.com/index/jobStatusList/"
    response = requests.request("GET", url,headers=headers)
    JobTitles = []
    if response.status_code == 200:
        for cate in json.loads(response.text)['data']:
            for jobtitle in json.loads(response.text)['data'][cate]:
                try:
                    JobTitles.append(jobtitle['name'])
                except Exception as e:
                    # print(e,jobtitle)
                    JobTitles.append(jobtitle)
        return list(set(JobTitles))
    else:
        print(response.status_code)
        sys.exit(1)


def searchJob(jobTitle,currentPage=1):
    url = "https://job.freebuf.com/job/searchJob/"
    querystring = {"flag":"1","city":"","posType":"","salary":"","edu":"","exp":"","financing":"","content":jobTitle,"page":currentPage}
    response = requests.request("GET", url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = json.loads(response.text)

        if currentPage < data['data']['totalPage']:
            nextPage = currentPage+1
            return searchJob(jobTitle,nextPage)
        else:   
            return data['data']['list']

def getJobDetails(jobID):
    url = "https://job.freebuf.com/job/jobDetail/"

    querystring = {"id":jobID}
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        jobInfo = data['data']['position']
        companyInfo = data['data']['company']
        return jobInfo,companyInfo


def main():

    jobTitles = getJoblists()
    for jobTitle in jobTitles:

        try:

            print("Searching.....",jobTitle,end="")
            jobs = searchJob(jobTitle)
            print(":.",len(jobs))

            with open("./alljobs.list","a",encoding='utf-8') as out:
                for job in jobs:
                    jobId = job['url'].split('=')[-1]
                    jobInfo, companyInfo = getJobDetails(jobId)
                    job['jobinfo'] = jobInfo
                    job['companyInfo'] = companyInfo

                    out.writelines(json.dumps(job,ensure_ascii=False))
                    out.write('\n')

        except Exception as e:
            print(e)
            pass

if __name__ == '__main__':
    main()
    

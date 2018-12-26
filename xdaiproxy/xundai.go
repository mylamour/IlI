package main

import (
	"bufio"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strings"
	"syscall"
	"time"
)

type ProxysOrder struct {
	spiderId string
	orderId string
	disabled bool
}

const ALLUESED  = "All Used"
const BUSYING = "System Busy"

func main() {

	authFile := flag.String("authfile", "", "Your proxy auth file, format it to spiderId:orderId")
	outFile := flag.String("output", "xundaliproxys.txt", "Your proxys")

	flag.Parse()

	if *authFile == "" {
		flag.PrintDefaults()
		os.Exit(1)
	}
	var count = 0
	var urls []ProxysOrder
	var urlsqueue = &urls
	urlsqueue = readProxyAuthFile(*authFile, urlsqueue)

	for{

		if count == len(*urlsqueue){
			fmt.Println("All auth was disabled, we would uniq file and exit this program")
			syscall.Exit(0)
		}

		for i, auth := range *urlsqueue {

			if !auth.disabled {
				url := fmt.Sprintf("http://api.xdaili.cn/xdaili-api/greatRecharge/getGreatIp?spiderId=%s&orderno=%s&returnType=1&count=20",auth.spiderId,auth.orderId)
				fmt.Println("+++++: Crawling from ", url)
				res := getProxy(url)

				if res == ALLUESED {
					urls[i].disabled = true
					continue
				}

				if res == BUSYING {
					time.Sleep(3*time.Second)
					continue
				}

				status := writeToFile(*outFile,res)

				if status {
					fmt.Println("✔️: 写入成功")
				}

			}else{

				fmt.Printf("----: spider id: %s was disabled\n",auth.spiderId)
				count += 1
			}
		}

		time.Sleep(10*time.Second)
	}
}

func readProxyAuthFile(filename string, urlsqueue *[]ProxysOrder) *[]ProxysOrder{

	file, err := os.Open(filename)
	if err != nil {
		log.Fatal(err)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		s := strings.Split(scanner.Text(), ":")
		spiderip, orderid := s[0], s[1]

		xundaili := ProxysOrder{spiderip,orderid, false}

		*urlsqueue = append(*urlsqueue, xundaili)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	return urlsqueue
}

func getProxy(url string) string {

	var client http.Client
	resp, err := client.Get(url)
	if err != nil {
		fmt.Println(err)
	}

	defer resp.Body.Close()

	if resp.StatusCode == http.StatusOK {
		bodyBytes, _ := ioutil.ReadAll(resp.Body)
		bodyString := string(bodyBytes)
		if strings.Contains(bodyString, "ERRORCODE"){
			fmt.Println(bodyString)
			if strings.Contains(bodyString, "提取数量已用完") || strings.Contains(bodyString,"今日提取已达上限"){
				return ALLUESED
			}
			if strings.Contains(bodyString,"10063"){
				//spiderID is uncrrect
				fmt.Println("10063",ALLUESED)

				return ALLUESED
			}

			fmt.Println("....",BUSYING)

			return BUSYING
		}

		return bodyString

	} else {
		return BUSYING
	}

}

func writeToFile(filename string, content string) bool {
	if _, err := os.Stat(filename); os.IsNotExist(err) {
		file, err := os.Create(filename)
		if err != nil {
			log.Fatal("Cannot create file", err)
			return false
		}
		defer file.Close()
		fmt.Fprintln(file, content)

	}else {
		f, err := os.OpenFile(filename, os.O_APPEND|os.O_WRONLY, 0600)
		if err != nil {
			panic(err)
		}

		defer f.Close()
		fmt.Fprintln(f, content)
	}

	return true
}
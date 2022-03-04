import datetime
import glob
import os, platform, time, pymysql
import re
import socket
import threading

# import pyautogui as pyautogui
import selenium.common.exceptions
import xlsxwriter
from requests import get
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC, expected_conditions

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
# from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
# from win10toast import ToastNotifier

email = ""
pswrd = ""
link = "https://employers.indeed.com/j#jobs"
mainFolder = "indeedScrapingFile-YassineBaghdadi.com"
data = {}
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']) if platform.system().lower() == "windows" else os.path.expanduser('~'), 'Desktop')
cvPaths = os.path.join(desktop, "IndeBotResumes")
os.mkdir(cvPaths) if not os.path.exists(cvPaths) else print("cvPath exists")

startPage = 0
endPage = 0

def chromDriver():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", cvPaths)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    return webdriver.Firefox(executable_path=GeckoDriverManager().install(), firefox_profile=profile)


def cnn():
    return pymysql.connect(host="127.0.0.1", user="user", password="user", port=3306, database="indebot")

def log(note):
    try:
        cnx = cnn()
        cur = cnx.cursor()
        qr = f'''insert into log(thedate, pubIP, privIP, hostname, note) values("{datetime.datetime.now().strftime("%d-%m-%Y, %H:%M:%S")}", "{get('https://api.ipify.org').content.decode('utf8')}", "{socket.gethostbyname(socket.gethostname())}", "{socket.gethostname()}", "{note.replace('"', "'")}")'''
        print(qr)
        cur.execute(qr)
        cnx.commit()
        cnx.close()

    except Exception as e :
        print(f"Error faced log : {e}")

class Main:
    def __init__(self):

        QTS = """{1} ==> scrap for specific page \n{2} ==> scrap for a range of pages \n{3} ==> scrap for specific offer \n{4} ==> Extraction"""
        print(QTS)
        ansr = input("Enter a Choice (1 to 4) : ")
        while ansr not in [str(i) for i in range(1, 5)]:
            ansr = input("Enter a Choice (1 to 4) : ")

        if ansr == "1":
            # try:
                page = input("input the page number : ")

                # chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--disable-extensions')
                # chrome_options.add_argument('--no-sandbox')
                # chrome_options.add_argument('--disable-dev-shm-usage')
                # self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
                self.browser = chromDriver()
                # if platform.system().lower() == "windows":
                #     self.browser = webdriver.Chrome(executable_path="chromedriver.exe")
                # else:
                self.login()
                self.scrapPage(page)
            # except Exception as e:
            #     print(f"Something Wrong : {e}")

        elif ansr == "2":
            # try:
                pages = input("enter start and end pages separet by '-' ex.(1-4) : ")
                # chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--disable-extensions')
                # chrome_options.add_argument('--no-sandbox')
                # self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
                self.browser = chromDriver()
                # if platform.system().lower() == "windows":
                #     self.browser = webdriver.Chrome(executable_path="chromedriver.exe")
                # else:
                #     self.browser = webdriver.Chrome(ChromeDriverManager().install())
                self.login()
                for i in range(int(pages.split("-")[0]), int(pages.split("-")[1])):

                    self.scrapPage(i)
            # except Exception as e:
            #     print(f"Something Wrong : {e}")
        elif ansr == "3":
            # try:
                offer = input("Enter the link of the offer that you want to scrap : ")
                # chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--disable-extensions')
                # chrome_options.add_argument('--no-sandbox')
                # self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
                self.browser = chromDriver()
                # if platform.system().lower() == "windows":
                #     self.browser = webdriver.Chrome(executable_path="chromedriver.exe", chrome_options=chrome_options)
                # else:
                self.login()
                self.scrapOffer(offer)
            # except Exception as e:
            #     print(f"Something Wrong : {e}")
        elif ansr == "4":
            extractedData = [[i for i in "ID.Full Name.City.Phone Number.E-mail.Applied Date.Offer Name.Link.Cover Letter.Cv Link".split(".")]]
            columns = [i for i in "ID.Full Name.City.Phone Number.E-mail.Applied Date.Offer Name.Link.Cover Letter.Cv Link".split(".")]
            if not os.path.exists(os.path.join(desktop, "IndeBot")):
                 os.mkdir(os.path.join(desktop, "IndeBot"))

            extPath = os.path.join(desktop, "IndeBot", f'IndeBotExtraction{datetime.datetime.now().strftime("%d-%m-%Y, %H_%M_%S")}.xlsx')
            print("{1} ==> Full Extraction \n{2} ==> Extraction with Filter \n")
            o = ''
            while o not in [str(i) for i in range(1, 3)]:
                o = input("Enter a choice (1 to 2) : ")
            if o == "1":
                cnx = cnn()
                cur = cnx.cursor()

                cur.execute("select * from fiche;")
                data = cur.fetchall()
                if data:
                    print("Extracting data ...")
                    [extractedData.append(i) for i in data]
                    workbook = xlsxwriter.Workbook(extPath)
                    worksheet = workbook.add_worksheet()
                    for rind, rv in enumerate(extractedData):
                        for cind, cvl in enumerate(rv):
                            worksheet.write(rind, cind, cvl)
                    workbook.close()
                    print(f"{len(extractedData)-1} records found so far .")
                    print(f"extracted file save to : {extPath}")

                else:
                    print("Sorry There are no Data to Extract ...")


                cnx.close()
            elif o == "2":
                print("what you prefer to filter with : \n{1} ==> city\n{2} ==> Offer Name\n")
                oo = ""
                while oo not in [str(i) for i in range(1, 3)]:
                    oo = input("Make a choice ... (1, 2): ")

                cnx = cnn()
                cur = cnx.cursor()
                key = ""
                if oo == "1":
                    key = "city"
                elif oo == "2":
                    key = "offerName"




                cities_counter = {}
                cur.execute(f"select {key} from fiche")
                cities = cur.fetchall()
                if cities:
                    cities = set([i[0] for i in cities])
                    for c in cities:
                            cur.execute(f'select count({key}) from fiche where {key} like "{c}" or city like "{c.upper}"')
                            cities_counter[c.upper()] = cur.fetchone()

                citt = [i for i in cities_counter.keys()]
                for i, v in enumerate( citt):
                        print(f"{i+1} ==> {v if v else 'No Name '} ({cities_counter[v][0] } fiches)")

                print("")
                cc = ""
                while cc not in [str(i) for i in range(1, len(citt)+1)]:
                        cc = input(f"Please choose the {key} to filter with ... : ")
                cur.execute(f'select * from fiche where {key} like "{cities_counter[citt[int(cc)-1]]}"')
                dt = cur.fetchall()
                if dt:
                    [extractedData.append([x for x in i]) for i in dt]
                print(f'extracting data filtred by {key} ({citt[int(cc)-1]})')

                workbook = xlsxwriter.Workbook(extPath)
                worksheet = workbook.add_worksheet()
                print(f"{len(extractedData)-1} records found so far .")
                for rind, rv in enumerate(extractedData):
                    for cind, cvl in enumerate(rv):
                            worksheet.write(rind, cind, cvl)
                workbook.close()
                print(f"extracted file save to : {extPath}")





                cnx.close()







    def login(self):
        self.browser.get(link)
        self.browser.maximize_window()
        # self.login()

        input("After you complete the log in please click Enter to continue  ...")

        # WebDriverWait(self.browser, 40).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-v5kln7')))
        # print("page 1 loaded ...")
        # print(self.browser.find_elements_by_class_name("css-n96g1e"))
        # print(self.browser.find_element_by_class_name("css-n96g1e")[-1].text)

    def scrapPage(self, page):
        print(f"Scraping for Page : {page}")
        self.counter = 0
        self.browser.get(f"{link}?p={page}")
        time.sleep(.2)
        # WebDriverWait(self.browser, 40).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-v5kln7')))
        WebDriverWait(self.browser, 40).until(EC.presence_of_element_located((By.CLASS_NAME, 'css-143ova3')))
        cndedatsLink = self.browser.find_elements_by_class_name("css-7kslf9")
        # print(f'cndedatsLink ==> {len(cndedatsLink)}')

        cndslinks = []

        for i in cndedatsLink:
            e1 = i.find_element_by_class_name("e37uo190").find_elements_by_class_name("eu4oa1w0")
            if e1[0].text != "0":
                cndslinks.append(e1[1].find_element_by_class_name("e1wnkr790").find_element_by_tag_name("a").get_attribute("href"))

        # print(cndslinks)
        # cndslinks = [i for i in set([cnd.find_element_by_class_name("jmcm-candidate-total css-lfiz4n e37uo190").find_elements_by_class_name("css-16vu25q eu4oa1w0")[1].find_element_by_class_name("css-56s3dp e1wnkr790").find_element_by_class_name("css-16tlhnx emf9s7v0").get_attribute("href") for cnd in cndedatsLink])]
        for cnd in cndslinks:
            # self.browser.get(cnd)
            self.scrapOffer(cnd)


            time.sleep(.3)
        print(f"{self.counter} fiches found in page {page}")


    def scrapOffer(self, offerlink):
        cnx = cnn()
        cur = cnx.cursor()
        agentData = {}

        # self.browser.delete_all_cookies()
        self.browser.get(offerlink)
        # try:
        #     self.browser.get(offerlink)
        # except selenium.common.exceptions.InvalidSessionIdException:
        #     toast = ToastNotifier()
        #     toast.show_toast(
        #         "The driver restarted",
        #         "Please relog because the driver has been restarted with an error",
        #         duration=20,
        #         icon_path="",
        #         threaded=True,
        #     )
        #     # chrome_options = webdriver.ChromeOptions()
        #     # chrome_options.add_argument('--disable-extensions')
        #     # chrome_options.add_argument('--no-sandbox')
        #     # self.browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        #     self.browser = chromDriver()
        #     self.login()
        #     self.browser.get(offerlink)

        time.sleep(.2)
        WebDriverWait(self.browser, 100).until(EC.presence_of_element_located((By.CLASS_NAME, 'search-input')))

        condidatsRow = []
        ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        WebDriverWait(self.browser, 100, ignored_exceptions=ignored_exceptions) \
            .until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "cpqap-CandidateCell-name-text")))
        for i in self.browser.find_elements_by_class_name("cpqap-CandidateCell-name-text"):
            condidatsRow.append(i.get_attribute("href"))

        for i in condidatsRow:
            try:
                ##scrap for offer

                cur.execute(
                    f"""select count(id) from fiche where link like "{i}";""")

                if cur.fetchone()[0]:
                    cur.execute(f"""select id from fiche where link like "{i}";""")
                    print(f"duplicated found and ignored ==> fiche Id : {cur.fetchone()[0]}")
                    continue

                self.browser.get(i)
                time.sleep(.2)
                WebDriverWait(self.browser, 40).until(EC.presence_of_element_located((By.ID, 'plugin_container_ResumePanel')))

                detailsPanelElement = self.browser.find_element_by_id("candidateDetailsPanel")
                try:
                    name = detailsPanelElement.find_elements_by_class_name("hanselNamePlate")[0].find_element_by_class_name(
                        "eu4oa1w0").find_element_by_tag_name("h1").text
                except:
                    name = ""

                agentData["name"] = name
                try:
                    applied_date = self.browser.find_element_by_class_name("noteDate").text
                except:
                    applied_date = ""
                agentData["AppliedDate"] = applied_date
                try:
                    offerName = self.browser.find_element_by_id("primaryFilterDescription").text
                except:
                    offerName = ""

                agentData["Offer"] = offerName.replace("'", " ").replace('"', " ")

                try:
                    email = self.browser.find_element_by_css_selector("""#candidateDetailsPanel > div.hanselNamePlate > div.hanselNamePlate-leftPanel.css-qz21kw.eu4oa1w0 > div:nth-child(3) > small > div:nth-child(1) > span > a""").text
                except selenium.common.exceptions.NoSuchElementException:
                    # email = self.browser.find_element_by_css_selector("""#candidateDetailsPanel > div.hanselNamePlate > div.hanselNamePlate-leftPanel.css-qz21kw.eu4oa1w0 > div > small > div:nth-child(1) > span:nth-child(1) > a""").text
                    email = self.browser.find_element_by_class_name("hanselNamePlate-leftPanel-additional").find_element_by_tag_name("a").text
                    #hanselNamePlate-leftPanel-additional
                else:
                    email = ""
                agentData["email"] = email
                try:
                    city = detailsPanelElement.find_element_by_class_name("hanselNamePlate-leftPanel-location").text
                except:
                    city = ""
                agentData["city"] = city.upper().replace('"', " ").replace("'", " ").replace(",", " ")
                try:
                    coverLeter = detailsPanelElement.find_element_by_class_name("hansel-cover-letter-container").text
                except:
                    coverLeter = ""
                agentData["coverLatter"] = coverLeter.replace("'", " ").replace('"', " ")
                #
                # if not os.path.exists(os.path.join(desktop, mainFolder)):
                #     os.mkdir(os.path.join(desktop, mainFolder))
                #
                # offerPath = os.path.join(desktop, mainFolder, offerName)
                # if not os.path.exists(offerPath):
                #     os.mkdir(offerPath)

                # offerPath = offerPath.replace("é", "e").replace("É", "E").replace("'", " ").replace("’", " ")
                # self.browser.set_preference("download.default_directory", "path/")
                # cvPath = os.path.join(offerPath, f"""{name.replace(' ', '').replace("é", "e").replace("É", "E").replace("'", " ").replace("’", " ")}.pdf""")
                # print(f'cvPath ==> {cvPath}')

                # params = {'behavior': 'allow', 'downloadPath': offerPath}
                # self.browser.execute_cdp_cmd('Page.setDownloadBehavior', params)



                # while True:
                #     list_of_files = glob.glob(os.path.join(offerPath, "*"))
                #     latest_file = max(list_of_files, key=os.path.getctime)
                #     print(latest_file)
                #     if latest_file.split(".")[-1] == "pdf" or latest_file.split(".")[-1] == "doc" or \
                #             latest_file.split(".")[-1] == "docx":
                #         break

                # cvPath = latest_file

                # pyautogui.typewrite(cvPath)
                # time.sleep(.5)
                # pyautogui.hotkey('enter')

                # try:
                #
                #
                #     if not os.path.exists(os.path.join(desktop, mainFolder)):
                #         os.mkdir(os.path.join(desktop, mainFolder))
                #
                #
                #     offerPath = os.path.join(desktop, mainFolder, offerName)
                #     if not os.path.exists(offerPath):
                #         os.mkdir(offerPath)
                #
                #     offerPath = offerPath.replace("é", "e").replace("É", "E").replace("'", " ").replace("’", " ")
                #     # self.browser.set_preference("download.default_directory", "path/")
                #     # cvPath = os.path.join(offerPath, f"""{name.replace(' ', '').replace("é", "e").replace("É", "E").replace("'", " ").replace("’", " ")}.pdf""")
                #     # print(f'cvPath ==> {cvPath}')
                #
                #     params = {'behavior': 'allow', 'downloadPath': offerPath}
                #     self.browser.execute_cdp_cmd('Page.setDownloadBehavior', params['params'])
                #
                #     self.browser.find_element_by_css_selector(
                #         "#plugin_container_ResumePanel > div > div > div > div > div.header.css-vhzuyw.eu4oa1w0 > div > button.css-mbvrx6.e8ju0x51").click()
                #
                #     while True:
                #         list_of_files = glob.glob(os.path.join(offerPath, "*"))
                #         latest_file = max(list_of_files, key=os.path.getctime)
                #         print(latest_file)
                #         if latest_file.split(".")[-1] == "pdf" or  latest_file.split(".")[-1] == "doc" or latest_file.split(".")[-1] == "docx":
                #             break
                #
                #     cvPath = latest_file
                #
                #     # pyautogui.typewrite(cvPath)
                #     # time.sleep(.5)
                #     # pyautogui.hotkey('enter')
                # except:
                #     cvPath = "NoNe"

                time.sleep(2)
                cvPath = f"https://employers.indeed.com/c/resume?id={i.split('id=')[1].split('&')[0]}&ctx=&isPDFView=false&asText=false"
                agentData[
                    "cv"] = cvPath
                agentData["link"] = offerlink

                try:
                    detailsPanelElement.find_element_by_id("showNumberButton").click()
                    WebDriverWait(self.browser, 40).until(EC.presence_of_element_located((By.ID, 'dockedMessagingContainer')))
                    phoneNum = self.browser.find_element_by_id("dockedMessagingContainer").find_element_by_class_name(
                    "PostCallSurveyBody-header").find_element_by_tag_name("div").text
                # try:
                #     phoneNum = self.browser.find_element_by_class_name("PostCallSurveyBody-header").find_element_by_class_name("PostCallSurveyBody-header").text
                # except:
                #     phoneNum = ""
                    agentData["phone"] = phoneNum

                # self.browser.find_element_by_id("hanselRightSectionContainer").find_element_by_class_name("DesktopMessagingHeader-toggle css-11p1dam e8ju0x51").click()
                    time.sleep(.5)
                except :
                    agentData["phone"] = ""

                # agentData = {"name":name,"city":city,"email":email,"coverLatter":coverLeter,"phone":phoneNum, "AppliedDate":applied_date, "Offer":offerName,"cv":cvPath}
                # threading.Thread(target=lambda : self.browser.get(cvPath)).start()

                # self.browser.get(cvPath)

                # detailsPanelElement.find_element_by_id("hanselInformationSection").find_element_by_id("tabContent").find_element_by_class_name\
                #     ("tabContent-wrapper").find_element_by_id("plugin_container_ResumePanel").\
                #     find_element_by_class_name("plugin-emocan-ph").find_element_by_tag_name("div").find_element_by_class_name("hansel-resume-panel-wrapper hansel-application-section").\
                #     find_element_by_class_name("hanselApplicationTabInformationPanel").find_element_by_class_name("header css-1pc2oh2 eu4oa1w0").\
                #     find_element_by_class_name("css-1m9rfm6 eu4oa1w0").find_element_by_id("download-resume-button").click()



                # agentData["cvPath"] = str(os.path.join(cvPaths, f"Resume{name.replace(' ', '')}.pdf"))

                # data[offerName.replace("’", " ").replace("é", "e").replace("É", "e")]["condidats"][name] = agentData
                # data[offerName] = {}
                # data[offerName]["condidats"] = {}
                #
                # data[offerName]["condidats"][name] = agentData

                time.sleep(2)
                cur.execute(f"""select count(id) from fiche where phone like "{agentData["phone"]}" and offerName like "{agentData["Offer"]}";""")
                if not cur.fetchone()[0]:

                    try:
                        self.browser.find_element_by_css_selector(
                            "#plugin_container_ResumePanel > div > div > div > div > div.header.css-vhzuyw.eu4oa1w0 > div > button.css-mbvrx6.e8ju0x51").click()
                        agentData["cvPath"] = str(os.path.join(cvPaths, f"Resume{name.replace(' ', '')}.pdf"))
                    except selenium.common.exceptions.NoSuchElementException:
                        try:
                            self.browser.find_element_by_css_selector(
                                "#plugin_container_ResumePanel > div > div > div > div > div.header.css-1pc2oh2.eu4oa1w0 > div > button").click()
                            agentData["cvPath"] = str(os.path.join(cvPaths, f"Resume{name.replace(' ', '')}.pdf"))

                        except selenium.common.exceptions.NoSuchElementException:
                            agentData["cvPath"] = "ERROR"


                    print(agentData)
                    cmd = f"""insert into fiche(fullName, city, phone, email, appliedDate, offerName, link, coverlettre, cvLink, cvPath) values("{name}", "{agentData["city"]}", "{agentData["phone"]}", "{email}", "{applied_date}", "{agentData["Offer"]}", "{i}", "{agentData["coverLatter"]}", "{cvPath}", "{re.escape(agentData["cvPath"])}")"""
                    # cmd = f"""insert into fiche(fullName, city, phone, email, appliedDate, offerName, link, coverlettre, cvLink) values("{name}", "{city}", "{agentData["phone"]}", "{email}", "{applied_date}", "{agentData["Offer"]}", "{i}", "{agentData["coverLatter"]}", "{cvPath}")"""
                    print(cmd)
                    cur.execute(cmd)
                    cnx.commit()
                    self.counter += 1
                    print("saved ...")
                else:
                    cur.execute(f"""select id, cvPath from fiche where phone like "{agentData["phone"]}" and offerName like "{agentData["Offer"]}";""")
                    cc = [i for i in cur.fetchone()]
                    if cc[1] == '' or cc[1] == "ERROR":
                        cvp = "ERROR"
                        try:
                            self.browser.find_element_by_css_selector(
                                "#plugin_container_ResumePanel > div > div > div > div > div.header.css-vhzuyw.eu4oa1w0 > div > button.css-mbvrx6.e8ju0x51").click()
                            cvp = str(os.path.join(cvPaths, f"Resume{name.replace(' ', '')}.pdf"))
                        except selenium.common.exceptions.NoSuchElementException:
                            try:
                                self.browser.find_element_by_css_selector(
                                    "#plugin_container_ResumePanel > div > div > div > div > div.header.css-1pc2oh2.eu4oa1w0 > div > button").click()
                                cvp = str(os.path.join(cvPaths, f"Resume{name.replace(' ', '')}.pdf"))

                            except selenium.common.exceptions.NoSuchElementException:
                                cvp = "ERROR"

                        cmd = f"""update fiche set cvPath = '{re.escape(cvp)}' where id = {cc[0]}"""
                        print(cmd)
                        cur.execute(cmd)


                    print("duplicated found and ignored ")
                time.sleep(.2)
            except Exception as e:
                print(f"ERROR : {e}")
                log(f"""ERROR : {str(e).replace("'", ' ')}\nLINK :\n{i}""")


        cnx.close()
    #
    # def login(self):
    #     self.browser.find_element_by_xpath('//*[@id="ifl-InputFormField-3" and @name="__email"]').send_keys(email)
    #     time.sleep(.5)
    #     self.browser.find_element_by_class_name("css-rhczsh").click()
    #     pswrd_inp = self.browser.find_element_by_xpath('//*[@id="ifl-InputFormField-21" and @name="__password"]')
    #     WebDriverWait(self.browser, 60).until(
    #         EC.presence_of_element_located(pswrd_inp))
    #     pswrd_inp.send_keys(pswrd)
    #     time.sleep(.5)
    #     self.browser.find_element_by_xpath('//*[@id="loginform"]/button').click()




if __name__ == "__main__":
    Main()
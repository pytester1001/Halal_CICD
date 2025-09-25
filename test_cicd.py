from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pytest , time , os , random , allure , re
from selenium.webdriver import ActionChains


# 清真Halal
# 測試案例3-1 廠商-新增案件成功
# 測試案例3-2 協會-匯款審核成功
# 測試案例3-3 協會-收件確認-確認收件
# 測試案例3-4 協會-收件確認-紙本文件確認
# 測試案例3-5 協會-收件確認-初審前置確認
# 測試案例3-6 協會-案件指派成功
# 測試案例3-7 協會-我的文件初審審核成功
# 測試案例3-8 協會-我的文件複審審核成功
# 測試案例3-9 協會-勘廠審查成功
# 測試案例3-10 協會-內部審議成功
# 測試案例3-11 協會-核發證書成功


# 設置 Browser 環境
@pytest.fixture
def driver(scope="function"):

    # 設置遠端Selenium Server環境
    driver = webdriver.Remote(
    command_executor="http://localhost:4444/wd/hub",
    options=webdriver.ChromeOptions()
    )
    
    # 設置 Chrome 環境
    # options = ChromeOptions()
    # service = ChromeService("/usr/local/bin/chromedriver")
    # driver = webdriver.Chrome(service=service, options=options)

    # 設置 Firefox 環境
    # options = FirefoxOptions()
    # options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"
    # service = FirefoxService("/usr/local/bin/geckodriver")
    # driver = webdriver.Firefox(service=service, options=options)

    # 設置 Safari 環境
    # driver = webdriver.Safari()
    # driver.set_window_rect(0, 0, 1200, 800)

    # 無頭測試
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1920,1080")

    yield driver
    driver.quit()

# 設置元素等待條件
def wait_for_element_clickable(driver, locator, timeout=10, screenshot_name="screenshot"):
    wait = WebDriverWait(driver, timeout)
    try:
        element = wait.until(EC.element_to_be_clickable(locator))
        return element
    except TimeoutException:
        capture_screenshot(driver, screenshot_name)
        return None

# 設置截圖路徑/名稱
def capture_screenshot(driver, filename="screenshot.png"):
    directory = 'screenshots'
    if not os.path.exists(directory):
        os.makedirs(directory)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filepath = os.path.join(directory, f"{filename}_{timestamp}.png")
    driver.save_screenshot(filepath)

# 獲取當前時間
current_datetime1 = datetime.now().strftime('%Y%m%d%H%M%S')
random_name = f'{current_datetime1}'

# 登入'協會'後台
@pytest.fixture(scope="function")
def login_association(driver):
    driver.get('https://halal-dev-is.intersense.cloud/halal-association')
    account = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="account"]'))
    assert account is not None, "未找到account"
    account.send_keys('admin@test.com')
    password = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="8-16 位數密碼，請區分大小寫"]'))
    assert password is not None, "未找到password"
    password.send_keys('Test1234')
    login = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"登入")]'))
    assert login is not None, "未找到login"
    login.click()
    WebDriverWait(driver, 10).until(EC.url_changes('https://halal-dev-is.intersense.cloud/halal-association/account-management/employee'))
    return driver

account_or_unified_number = "88888888"
manufacturer_password = "Test1234"

# 登入'廠商'後台
@pytest.fixture(scope="function")
def login_manufactor(driver):
    # 廠商登入頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-manufactor')
    # 統編/信箱
    unified_number = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="account"]'))
    assert unified_number is not None, "未找到統編/信箱"
    unified_number.send_keys(account_or_unified_number)
    # 密碼
    password = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="8-16 位數密碼，請區分大小寫"]'))
    assert password is not None, "未找到密碼"
    password.send_keys(manufacturer_password)
    # 登入
    login = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"登入")]'))
    assert login is not None, "未找到登入"
    login.click()
    WebDriverWait(driver, 10).until(EC.url_changes('https://halal-dev-is.intersense.cloud/halal-manufactor/setting-management'))
    return driver

# ===== 全域共享 order_id ===== #
@pytest.fixture(scope="session")
def order_id():
    return {"value": None}

# 測試案例3-1 廠商-新增案件成功
@allure.feature("廠商前台-我的案件")
@allure.story("TC3-1廠商-新增案件成功")
def test_add_new_case_successfully(driver,login_manufactor,order_id):
    driver = login_manufactor
    time.sleep(1.5)

    # 確保載入'我的案件'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-manufactor/case-management')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-manufactor/case-management"))
    time.sleep(1.5)

    # 0.我的案件頁面
    with allure.step("0.建立訂單"):
        # 新增申請案件
        add_case = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增申請案件")]'))
        assert add_case is not None, "未找到新增申請案件"
        add_case.click()
        # 選擇'飲料食品'類別
        drink_and_food = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="ApplyType_1"]'))
        assert drink_and_food is not None, "未找到飲料食品"
        drink_and_food.click()
        time.sleep(0.5)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        # 確認按鈕
        check_button = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確認")]'))
        assert check_button is not None, "未找到確認"
        check_button.click()
        time.sleep(0.5)
        # 彈窗確認
        check_alert = wait_for_element_clickable(driver, (By.XPATH, '/html/body/div[3]/div/div[6]/button[1]'))
        assert check_alert is not None, "未找到彈窗確認"
        check_alert.click()
        time.sleep(1.5)

        # 取得目前網址
        current_url = driver.current_url
        print(f"當前網址：{current_url}")
        match = re.search(r'/case/(\d+)', current_url)
        assert match, "未找到訂單號碼"
        order_id["value"] = match.group(1)
        print(f"訂單號碼：{order_id['value']}")

    # 1.基本資料tag
    with allure.step("1.基本資料Tag"):
        # 滾動頁面至底部-填入聯絡人資訊
        def scroll_down(driver, pixels=500):
            driver.execute_script(f"window.scrollBy(0, {pixels});")
        scroll_down(driver, pixels=1600)
        time.sleep(1)
        # 聯絡人資訊表單
        # 聯絡人姓名
        name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
        assert name is not None, "未找到聯絡人姓名"
        name.clear()
        name.send_keys('張哈利')
        # 公司電話(區碼+號碼)
        companyTel = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='companyTel']"))
        assert companyTel is not None, "未找到公司電話(區碼+號碼)"
        companyTel.clear()
        companyTel.send_keys('(02)22223333')
        # 分機
        extensionNumber = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='extensionNumber']"))
        assert extensionNumber is not None, "未找到分機"
        extensionNumber.clear()
        extensionNumber.send_keys('1234')
        # 手機
        phone = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='phone']"))
        assert phone is not None, "未找到手機"
        phone.clear()
        phone.send_keys('0912345678')
        # 電子郵件
        email = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='email']"))
        assert email is not None, "未找到電子郵件"
        email.clear()
        email.send_keys('harry.chang@intersense.com.tw')
        # 預期要銷售的國家
        saleCountries = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='saleCountries']"))
        assert saleCountries is not None, "未找到預期要銷售的國家"
        saleCountries.clear()
        saleCountries.send_keys('台灣')
        time.sleep(0.5)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        # 填寫完畢準備進入'工廠資訊'頁面
        # 下一步
        next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
        assert next_step is not None, "未找到下一步"
        next_step.click()
        time.sleep(1)

    # 2.工廠資訊tag
    with allure.step("2.工廠資訊Tag"):
        # 工廠資訊-新增工廠
        for i in range(1):
            # 新增工廠
            add_factory = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增工廠")]'))
            assert add_factory is not None, "未找到新增工廠"
            add_factory.click()
            # 開啟新增工廠彈窗
            # 工廠登記編號
            factoryNo = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='no']"))
            assert factoryNo is not None, "未找到工廠登記編號"
            factoryNo.clear()
            factoryNo.send_keys("09000241")
            # 工廠名稱
            factoryName = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert factoryName is not None, "未找到工廠名稱"
            factoryName.clear()
            factoryName.send_keys("瑞春醬油有限公司福田廠")
            # 工廠地址
            factoryAddress = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='address']"))
            assert factoryAddress is not None, "未找到工廠地址"
            factoryAddress.clear()
            factoryAddress.send_keys('雲林縣西螺鎮福田里社口68-31號')
            # 電話
            factoryTel = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='tel']"))
            assert factoryTel is not None, "未找到電話"
            factoryTel.clear()
            factoryTel.send_keys('05-5882288')
            # 網址
            factoryURL = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='website']"))
            assert factoryURL is not None, "未找到網址"
            factoryURL.clear()
            factoryURL.send_keys('https://www.rueichun.com.tw/')
            # 代工廠核取方塊
            foundry_checkbox = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='isFoundry']"))
            assert foundry_checkbox is not None, "未找到代工廠核取方塊"
            foundry_checkbox.click()
            # 生產設備核取方塊
            production_equipment = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='isEquipment']"))
            assert production_equipment is not None, "未找到生產設備核取方塊"
            production_equipment.click()
            # 設備/生產線/產品描述
            attachment_description = wait_for_element_clickable(driver, (By.XPATH, "//textarea[@id='equipmentDescription']"))
            assert attachment_description is not None, "未找到設備/生產線/產品描述"
            attachment_description.clear()
            attachment_description.send_keys('讓工作更輕鬆、生活更有序 —— 我們的智能任務管理工具結合直覺式設計與強大功能，專為追求效率與靈活性的你打造。不論是團隊協作還是個人規劃，只需一個平台就能輕鬆掌握所有待辦事項、專案進度與日常提醒，讓你不再被瑣事打亂節奏，專注完成真正重要的事。')
            # 滾動頁面至底部
            def scroll_down(driver, pixels=500):
                driver.execute_script(f"window.scrollBy(0, {pixels});")
            scroll_down(driver, pixels=1600)
            time.sleep(0.5)
            # 各廠衛接及半成品運送方式描述
            shipping_method = wait_for_element_clickable(driver, (By.XPATH, "//textarea[@id='transportation']"))
            assert shipping_method is not None, "未找到各廠衛接及半成品運送方式描述"
            shipping_method.clear()
            shipping_method.send_keys('我們提供多元且彈性的運送選項，讓您的商品能快速、安全地送達指定地點。標準配送服務預計於下單後 2～5 個工作天內送達，另提供快速到貨（24 小時內出貨）與宅配代收服務，滿足不同時效與便利性的需求。所有包裹均可透過追蹤編號即時查詢配送狀態，確保每一筆訂單皆準時無誤地送到您手中。')
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 新增
            add_factory = wait_for_element_clickable(driver, (By.XPATH, '//button[@aria-label="新增"]'))
            assert add_factory is not None, "未找到新增"
            add_factory.click()
            # 彈窗確認
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到彈窗確認"
            alert_check.click()

            # 工廠附件
            def upload_file(filetype_text, file_path):
                driver.find_element(By.CLASS_NAME, "css-dk3iff-control").click()
                time.sleep(0.5)
                for el in driver.find_elements(By.XPATH, f"//div[text()='{filetype_text}']"):
                    if el.is_displayed():
                        el.click()
                        break
                upload_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'attachments'))
                )
                upload_input.send_keys(file_path)
                file_type_text = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//td[text()='{filetype_text}']"))
                )
                assert file_type_text.text == filetype_text, f"列表中找不到『{filetype_text}』"

                # 點擊彈出視窗的「確定」按鈕
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'確定')]"))
                )
                confirm_button.click()
                time.sleep(0.5)

            # 上傳文件
            upload_file('產品製程圖', 'assets/dog.jpg')
            upload_file('工廠登記核准相關文件', 'assets/dog.jpg')
            upload_file('工廠平面配置圖', 'assets/dog.jpg')
            upload_file('生產設備 清潔/消毒 之作業 方式/程序(含清潔劑、消毒劑)', 'assets/dog.jpg')
            upload_file('其它(檔名請清楚描述檔案用途)', 'assets/dog.jpg')

            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            
            # 滾動頁面至頂部
            def scroll_to_top(driver):
                driver.execute_script("window.scrollTo(0, 0);")
            scroll_to_top(driver)
            time.sleep(0.5)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 填寫完畢準備進入'申請產品'頁面
            # 下一步
            next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
            assert next_step is not None, "未找到下一步"
            next_step.click()
            time.sleep(1)
            # 滾動頁面至頂部
            def scroll_to_top(driver):
                driver.execute_script("window.scrollTo(0, 0);")
            scroll_to_top(driver)
            time.sleep(0.5)
 
    # 3.申請產品tag
    with allure.step("3.申請產品Tag"):
        # 產品分類清單-新增分類
        category_names = []
        for i in range(1):
            # 新增分類
            add_category = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增分類')]"))
            assert add_category is not None, "未找到新增分類"
            add_category.click()
            # 開啟新增分類彈窗
            # 分類中文名稱
            categoryCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert categoryCN is not None, "未找到分類中文名稱"
            categoryCN.clear()
            categoryCN.send_keys("調味料")
            # 分類英文名稱
            categoryEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert categoryEN is not None, "未找到分類英文名稱"
            categoryEN.clear()
            categoryEN.send_keys("Seasonings")
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到新增"
            add_button.click()
            # 彈窗確認
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到彈窗確認"
            alert_check.click()
            time.sleep(0.5)
        # 滾動頁面至底部
        def scroll_down(driver, pixels=500):
            driver.execute_script(f"window.scrollBy(0, {pixels});")
        scroll_down(driver, pixels=1600)
        time.sleep(0.5)

        # 申請產品清單-新增產品(第一筆)
        for i in range(1): 
            # 新增產品
            add_product = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增產品')]"))
            assert add_product is not None, "未找到新增產品"
            add_product.click()
            # 開啟新增產品彈窗
            # 中文名稱
            nameCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert nameCN is not None, "未找到中文名稱"
            nameCN.clear()
            nameCN.send_keys("瑞春醬油素瓜仔肉（純素）")
            # 英文名稱
            nameEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert nameEN is not None, "未找到英文名稱"
            nameEN.clear()
            nameEN.send_keys("Vegetarian meat")
            # 產品分類下拉選單
            productType = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div"))
            assert productType is not None, "未找到產品分類"
            productType.click()
            time.sleep(1)
            # 選擇「調味料」分類
            productType_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='調味料']"))
            assert productType_option is not None, "未找到產品分類項目-調味料"
            productType_option.click()
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 含藥化妝品核取方塊
            # medicated_cosmetics_checkbox = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='isContainsCosmetic']"))
            # assert medicated_cosmetics_checkbox is not None, "未找到含藥化妝品核取方塊"
            # medicated_cosmetics_checkbox.click()
            # 衛生署許可證-上傳檔案(PDF)
            # upload_input = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//input[@id='file' and @type='file']"))
            # )
            # upload_input.send_keys('assets/dog.jpg')
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到新增"
            add_button.click()
            # 彈窗確認
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到彈窗確認"
            alert_check.click()


            # 製程圖綁定
            process_diagram_binding = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-tooltip-content="製程圖綁定"]'))
            assert process_diagram_binding is not None, "未找到綁定製成圖"
            process_diagram_binding.click()
            # 工廠名稱下拉選單
            factoryName = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div[1]/div/div"))
            assert factoryName is not None, "未找到工廠名稱下拉選單"
            factoryName.click()
            time.sleep(1)
            # 選擇「瑞春醬油」
            factoryName_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='瑞春醬油有限公司福田廠']"))
            assert factoryName_option is not None, "未找到工廠選項-瑞春醬油有限公司福田廠"
            factoryName_option.click()
            # 製程圖下拉選單
            processImage = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div[2]/div/div"))
            assert processImage is not None, "未找到製程圖下拉選單"
            processImage.click()
            time.sleep(1)
            # 選擇「產品製程圖」
            processImage_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='產品製程圖.jpg']"))
            assert processImage_option is not None, "未找到製程圖選項-產品製程圖.jpg"
            processImage_option.click()
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 綁定製程圖
            bind_picture = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定圖片')]"))
            assert bind_picture is not None, "未找到綁定製成圖"
            bind_picture.click()
            # 彈窗確認
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到彈窗確認"
            alert_check.click()
            time.sleep(1)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()


            # 編輯包裝規格
            edit_packaging_specifications = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-tooltip-content="編輯包裝規格"]'))
            assert edit_packaging_specifications is not None, "未找到編輯包裝規格"
            edit_packaging_specifications.click()
            # 中文規格
            spceCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='spec']"))
            assert spceCN is not None, "未找到spceCN"
            spceCN.clear()
            spceCN.send_keys("330克±5％∕罐")
            # 英文規格
            specEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='specEn']"))
            assert specEN is not None, "未找到specEN"
            specEN.clear()
            specEN.send_keys("330g±5％∕Bottle")
            # 規格圖片-上傳圖片
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class,'input_container')]/input[@type='file' and contains(@accept,'.jpg')]"
                ))
            )
            upload_input.send_keys('assets/dog.jpg')
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(1)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()


            # 產品1-新增原料-Halal證明文件
            # 產品原料綁定
            product_raw_material_binding = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-tooltip-content="產品原料綁定"]'))
            assert product_raw_material_binding is not None, "未找到product_raw_material_binding"
            product_raw_material_binding.click()
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("麵筋")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Gluten")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("谷王食品工業股份有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("谷王食品工業股份有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"Halal 證書"
            for option in all_options:
                if option.text.strip() == "Halal 證書":
                    option.click()
                    break
            time.sleep(0.5)
            # 選擇發證單位下拉選單
            cert_issuer_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//label[normalize-space(text())='發證單位']/parent::div//div[contains(@class,'css-dk3iff-control')]"
                ))
            )
            assert cert_issuer_dropdown is not None, "未找到cert_issuer_dropdown"
            cert_issuer_dropdown.click()
            time.sleep(0.5)
            # 獲取下拉選單項目
            cert_issuer_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 點擊第一個項目
            cert_issuer_options[0].click()
            # 有效日期
            valid_date = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇日期']"))
            )
            valid_date.click()
            # 選擇「今天」的日期
            today_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
            )
            today_btn.click()
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 產品1-新增原料-問卷
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("大豆沙拉油")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Soybean Oil")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("泰山企業股份有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("泰山企業股份有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"問卷"
            for option in all_options:
                if option.text.strip() == "問卷":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 產品1-新增原料-COA
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("砂糖")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Sugar")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("PANTALEON, S.A.")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("瓜地馬拉")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("楷群企業有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"COA"
            for option in all_options:
                if option.text.strip() == "COA":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()

            # 產品1-新增原料-MSDS/SDS
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("蔭瓜")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Pickles")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("永發食品廠")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("北勢坑農場")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"MSDS/SDS"
            for option in all_options:
                if option.text.strip() == "MSDS/SDS":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 產品1-新增原料-聲明書
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("香菇")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Mushroom")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("綠園農產")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("綠園農產")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"聲明聲"
            for option in all_options:
                if option.text.strip() == "聲明書":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()

            # 產品1-新增原料-進口報單
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("醬油")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Soy Sauce")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("瑞春醬油有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("瑞春醬油有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"進口報單"
            for option in all_options:
                if option.text.strip() == "進口報單":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 產品1-新增原料-輸入許可證
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("食鹽")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Salt")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("臺鹽實業股份有限公司進口鹽儲運所")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("秀芳行有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"輸入許可證"
            for option in all_options:
                if option.text.strip() == "輸入許可證":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 產品1-新增原料-其他
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("肉精香料")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("SM-819011 Beef Flavor")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("盛美股份有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("盛美股份有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"其他"
            for option in all_options:
                if option.text.strip() == "其他":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()

            
        # 申請產品清單-新增產品(第二筆)
        for i in range(1): 
            # 新增產品
            add_product = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增產品')]"))
            assert add_product is not None, "未找到add_product"
            add_product.click()
            # 開啟新增產品彈窗
            # 中文名稱
            nameCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert nameCN is not None, "未找到nameCN"
            nameCN.clear()
            nameCN.send_keys("瑞春醬油黑豆蔭豆豉（純素）")
            # 英文名稱
            nameEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert nameEN is not None, "未找到nameEN"
            nameEN.clear()
            nameEN.send_keys("Preserved black bean")
            # 產品分類下拉選單
            productType = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[1]/div"))
            assert productType is not None, "未找到productType"
            productType.click()
            time.sleep(1)
            # 選擇「調味料」分類
            productType_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='調味料']"))
            assert productType_option is not None, "未找到productType_option 調味料"
            productType_option.click()
            # 含藥化妝品核取方塊
            # medicated_cosmetics_checkbox = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='isContainsCosmetic']"))
            # assert medicated_cosmetics_checkbox is not None, "未找到medicated_cosmetics_checkbox"
            # medicated_cosmetics_checkbox.click()
            # 衛生署許可證-上傳檔案(PDF)
            # upload_input = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, "//input[@id='file' and @type='file']"))
            # )
            # upload_input.send_keys('assets/dog.jpg')
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()


            # 製程圖綁定
            process_diagram_binding = wait_for_element_clickable(driver, (By.XPATH, '//tbody/tr[2]/td[5]/div[1]/div[3]'))
            assert process_diagram_binding is not None, "未找到process_diagram_binding"
            process_diagram_binding.click()
            # 工廠名稱下拉選單
            factoryName = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div[1]/div/div"))
            assert factoryName is not None, "未找到factoryName"
            factoryName.click()
            time.sleep(1)
            # 選擇「瑞春醬油」
            factoryName_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='瑞春醬油有限公司福田廠']"))
            assert factoryName_option is not None, "未找到factoryName_option 瑞春醬油有限公司福田廠"
            factoryName_option.click()
            # 製程圖下拉選單
            processImage = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div/div/div[2]/div/div"))
            assert processImage is not None, "未找到processImage"
            processImage.click()
            time.sleep(1)
            # 選擇「產品製程圖」
            processImage_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='產品製程圖.jpg']"))
            assert processImage_option is not None, "未找到processImage_option 產品製程圖.jpg"
            processImage_option.click()
            # 綁定製程圖
            bind_picture = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定圖片')]"))
            assert bind_picture is not None, "未找到bind_picture"
            bind_picture.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(1)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()


            # 編輯包裝規格
            edit_packaging_specifications = wait_for_element_clickable(driver, (By.XPATH, '//tbody/tr[2]/td[5]/div[1]/div[4]'))
            assert edit_packaging_specifications is not None, "未找到edit_packaging_specifications"
            edit_packaging_specifications.click()
            # 中文規格
            spceCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='spec']"))
            assert spceCN is not None, "未找到spceCN"
            spceCN.clear()
            spceCN.send_keys("330克±5％∕罐")
            # 英文規格
            specEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='specEn']"))
            assert specEN is not None, "未找到specEN"
            specEN.clear()
            specEN.send_keys("330g±5％∕Bottle")
            # 規格圖片-上傳圖片
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[contains(@class,'input_container')]/input[@type='file' and contains(@accept,'.jpg')]"
                ))
            )
            upload_input.send_keys('assets/dog.jpg')
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(1)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()


            # 產品2-新增原料-Halal證明文件
            # 產品原料綁定
            product_raw_material_binding = wait_for_element_clickable(driver, (By.XPATH, '//tbody/tr[2]/td[5]/div[1]/div[5]'))
            assert product_raw_material_binding is not None, "未找到product_raw_material_binding"
            product_raw_material_binding.click()
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("沙茶醬")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Barbecue Sauce")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("瑞春醬油有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("瑞春醬油有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"Halal 證書"
            for option in all_options:
                if option.text.strip() == "Halal 證書":
                    option.click()
                    break
            time.sleep(0.5)
            # 選擇發證單位下拉選單
            cert_issuer_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//label[normalize-space(text())='發證單位']/parent::div//div[contains(@class,'css-dk3iff-control')]"
                ))
            )
            assert cert_issuer_dropdown is not None, "未找到cert_issuer_dropdown"
            cert_issuer_dropdown.click()
            time.sleep(0.5)
            # 獲取下拉選單項目
            cert_issuer_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 點擊第一個項目
            cert_issuer_options[0].click()
            # 有效日期
            valid_date = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇日期']"))
            )
            valid_date.click()
            # 選擇「今天」的日期
            today_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
            )
            today_btn.click()
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)

            # 產品1-新增原料-問卷
            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("大豆沙拉油")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Soybean Oil")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("泰山企業股份有限公司")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("泰山企業股份有限公司")
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"問卷"
            for option in all_options:
                if option.text.strip() == "問卷":
                    option.click()
                    break
            time.sleep(0.5)
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            time.sleep(0.5)
            # 滾動頁面至底部
            def scroll_down(driver, pixels=500):
                driver.execute_script(f"window.scrollBy(0, {pixels});")
            scroll_down(driver, pixels=1600)
            time.sleep(0.5)
            # 填寫完畢準備進入'不申請產品'頁面
            # 下一步
            next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
            assert next_step is not None, "未找到next_step"
            next_step.click()
            time.sleep(1)
            # 滾動頁面至頂部
            def scroll_to_top(driver):
                driver.execute_script("window.scrollTo(0, 0);")
            scroll_to_top(driver)
            time.sleep(0.5)

    # 4.不申請產品tag
    with allure.step("4.不申請產品Tag"):
        # 產品分類清單-新增不申請產品
        for i in range(1): 
            # 新增產品
            add_product = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增產品')]"))
            assert add_product is not None, "未找到add_product"
            add_product.click()
            # 開啟新增產品彈窗
            # 中文名稱
            nameCN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert nameCN is not None, "未找到nameCN"
            nameCN.clear()
            nameCN.send_keys("正蔭瓜(純素)")
            # 英文名稱
            nameEN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert nameEN is not None, "未找到nameEN"
            nameEN.clear()
            nameEN.send_keys("Preserved Cucumbers")
            # 共線
            collinear = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='isUsingSameLine']"))
            assert collinear is not None, "未找到collinear"
            collinear.click()
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 新增
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)

            # 選擇原料
            choose_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'選擇原料')]"))
            assert choose_raw_materials is not None, "未找到choose_raw_materials"
            choose_raw_materials.click()
            # 新增原料
            add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'新增原料')]"))
            assert add_raw_materials is not None, "未找到add_raw_materials"
            add_raw_materials.click()
            # 原料中文
            raw_materials_CN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='name']"))
            assert raw_materials_CN is not None, "未找到raw_materials_CN"
            raw_materials_CN.clear()
            raw_materials_CN.send_keys("朝天辣椒")
            # 原料英文
            raw_materials_EN = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nameEn']"))
            assert raw_materials_EN is not None, "未找到raw_materials_EN"
            raw_materials_EN.clear()
            raw_materials_EN.send_keys("Chaotian pepper")
            # 原料暱稱
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='nickName']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("原料暱稱")
            # 製造商
            raw_materials_nick_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='manufacturer']"))
            assert raw_materials_nick_name is not None, "未找到raw_materials_nick_name"
            raw_materials_nick_name.clear()
            raw_materials_nick_name.send_keys("何鳳棋")
            # 產地
            raw_materials_origin = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='origin']"))
            assert raw_materials_origin is not None, "未找到raw_materials_origin"
            raw_materials_origin.clear()
            raw_materials_origin.send_keys("台灣")
            # 供應商
            raw_materials_supplier = wait_for_element_clickable(driver, (By.XPATH, "//input[@id='supplier']"))
            assert raw_materials_supplier is not None, "未找到raw_materials_origin"
            raw_materials_supplier.clear()
            raw_materials_supplier.send_keys("何鳳棋")
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 新增按鈕
            add_button = wait_for_element_clickable(driver, (By.XPATH, "//button[@aria-label='新增']"))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            # 選擇文件類型
            file_type_dropdown = wait_for_element_clickable(driver, (
                By.XPATH, "//div[contains(@class,'placeholder') and text()='請選擇文件類型']"
            ))
            assert file_type_dropdown is not None, "未找到file_type_dropdown"
            file_type_dropdown.click()
            time.sleep(0.5)
            # 獲取全部下拉選單項目
            all_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 遍歷所有項目並點擊"Halal 證書"
            for option in all_options:
                if option.text.strip() == "Halal 證書":
                    option.click()
                    break
            time.sleep(0.5)
            # 選擇發證單位下拉選單
            cert_issuer_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH, "//label[normalize-space(text())='發證單位']/parent::div//div[contains(@class,'css-dk3iff-control')]"
                ))
            )
            assert cert_issuer_dropdown is not None, "未找到cert_issuer_dropdown"
            cert_issuer_dropdown.click()
            time.sleep(0.5)
            # 獲取下拉選單項目
            cert_issuer_options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class,'-option')]"))
            )
            # 點擊第一個項目
            cert_issuer_options[0].click()
            # 有效日期
            valid_date = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇日期']"))
            )
            valid_date.click()
            # 選擇「今天」的日期
            today_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
            )
            today_btn.click()
            # 上傳檔案
            upload_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//label[normalize-space(text())='文件檔案']/following-sibling::div//input[@type='file']"
                ))
            )
            upload_input.send_keys("assets/dog.jpg")
            time.sleep(0.5)
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.XPATH, "//body/div[4]/div[1]/div[1]"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            # 勾選項目一
            choose1_button = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
            assert choose1_button is not None, "未找到原料項目一"
            choose1_button.click()
            # 綁定原料
            binding_raw_materials = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'綁定')]"))
            assert binding_raw_materials is not None, "未找到綁定原料"
            binding_raw_materials.click()
            # 彈窗確定
            alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
            assert alert_check is not None, "未找到alert_check"
            alert_check.click()
            time.sleep(0.5)
            # 右上關閉
            close_button = wait_for_element_clickable(driver, (By.ID, "qa-close"))
            assert close_button is not None, "未找到右上關閉"
            close_button.click()
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            time.sleep(0.5)
            # 滾動頁面至底部
            def scroll_down(driver, pixels=500):
                driver.execute_script(f"window.scrollBy(0, {pixels});")
            scroll_down(driver, pixels=1600)
            time.sleep(0.5)
            # 填寫完畢準備進入'原料資訊'頁面
            # 下一步
            next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
            assert next_step is not None, "未找到next_step"
            next_step.click()
            time.sleep(1)
            # 滾動頁面至頂部
            def scroll_to_top(driver):
                driver.execute_script("window.scrollTo(0, 0);")
            scroll_to_top(driver)
            time.sleep(0.5)

    # 5.原料資訊tag
    with allure.step("5.原料資訊Tag"):
        # 滾動頁面至底部
            def scroll_down(driver, pixels=500):
                driver.execute_script(f"window.scrollBy(0, {pixels});")
            scroll_down(driver, pixels=1600)
            time.sleep(0.5)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
            # 填寫完畢準備進入'原料資訊'頁面
            # 下一步
            next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
            assert next_step is not None, "未找到next_step"
            next_step.click()
            time.sleep(1)
            # 滾動頁面至頂部
            def scroll_to_top(driver):
                driver.execute_script("window.scrollTo(0, 0);")
            scroll_to_top(driver)
            time.sleep(0.5)

    # 6.其他附件tag
    with allure.step("6.其他附件Tag"):
        # 檔案1
        file_name = wait_for_element_clickable(driver, (By.XPATH, "//input[@placeholder='請輸入檔案說明']"))
        assert file_name is not None, "未找到file_name"
        file_name.clear()
        file_name.send_keys("file_1")
        # 上傳檔案
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )
        upload_input.send_keys("assets/dog.jpg")
        time.sleep(0.5)
        # 彈窗確定
        alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert alert_check is not None, "未找到alert_check"
        alert_check.click()
        # 檔案2
        file_name.clear()
        file_name.send_keys("file_2")
        # 上傳檔案
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )
        upload_input.send_keys("assets/dog.jpg")
        time.sleep(0.5)
        # 彈窗確定
        alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert alert_check is not None, "未找到alert_check"
        alert_check.click()
        # 檔案3
        file_name.clear()
        file_name.send_keys("file_3")
        # 上傳檔案
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
        )
        upload_input.send_keys("assets/dog.jpg")
        time.sleep(0.5)
        # 彈窗確定
        alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert alert_check is not None, "未找到alert_check"
        alert_check.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        # 滾動頁面至底部
        def scroll_down(driver, pixels=500):
            driver.execute_script(f"window.scrollBy(0, {pixels});")
        scroll_down(driver, pixels=1600)
        time.sleep(0.5)
        # 填寫完畢準備進入'原料資訊'頁面
        # 下一步
        next_step = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'下一步')]"))
        assert next_step is not None, "未找到next_step"
        next_step.click()
        time.sleep(1)
        # 滾動頁面至頂部
        def scroll_to_top(driver):
            driver.execute_script("window.scrollTo(0, 0);")
        scroll_to_top(driver)
        time.sleep(0.5)

    # 7.文審費tag
    with allure.step("7.文審費Tag"):
        # 滾動頁面至底部
        def scroll_down(driver, pixels=500):
            driver.execute_script(f"window.scrollBy(0, {pixels});")
        scroll_down(driver, pixels=1600)
        time.sleep(0.5)
        # 繳款資訊
        # 付款帳號末五碼
        account_number = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='paidCode']"))
        assert account_number is not None, "未找到account_number"
        account_number.send_keys('12345')
        # 付款日期
        payment_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇日期']"))
        )
        payment_input.click()
        # 選擇「今天」的日期
        today_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
        )
        today_btn.click()
        # 匯款單據-上傳檔案
        upload_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "paidFile"))
        )
        upload_input.send_keys("assets/dog.jpg")
        # 送出申請
        send_application = wait_for_element_clickable(driver, (By.XPATH, "//button[contains(text(),'送出申請')]"))
        assert send_application is not None, "未找到send_application"
        send_application.click()
        # 等待彈窗並驗證文字
        swal_title = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "swal2-title"))
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        assert swal_title.text.strip() == "建立成功", f"彈窗標題錯誤，實際為: {swal_title.text}"
        print('#測試案例3-1 廠商新增案件成功')

# 測試案例3-2 協會-匯款審核成功
@allure.feature("協會後台-匯款審核")
@allure.story("TC3-2協會-匯款審核成功")
def test_remittance_review_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(1.5)

    # 確保載入'匯款審核'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/review-remit')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/review-remit"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id["value"]) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊檢視內容"):
        # 檢視內容
        view_content = wait_for_element_clickable(driver, (By.XPATH, '//tbody/tr[1]/td[6]/div[1]/button[1]'))
        assert view_content is not None, "未找到view_content"
        view_content.click()

    with allure.step("點擊審核通過"):
        # 審核通過
        review_pass = wait_for_element_clickable(driver, (By.XPATH, '//button[@aria-label="通過"]'))
        assert review_pass is not None, "未找到review_pass"
        review_pass.click()

    with allure.step("彈窗確認"):
        # 彈窗確認
        edit_alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert edit_alert_check is not None, "未找到彈窗確認"
        edit_alert_check.click()

    with allure.step("彈窗確認"):
        # 彈窗確認
        alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert alert_check is not None, "未找到彈窗確認"
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        alert_check.click()

    with allure.step("驗證匯款審核狀態"):
        status_tag = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//span[text()="通過"]'))
        )
        assert status_tag.text.strip() == "通過", f"匯款審核狀態錯誤，實際為：{status_tag.text}"
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        print("# 測試案例3-2 協會-匯款審核成功")

# 測試案例3-3 協會-收件確認-確認收件成功
@allure.feature("協會後台-收件確認")
@allure.story("TC3-3協會-確認收件成功")
def test_confirm_receipt_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(1.5)

    # 確保載入'收件確認'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊確認收件"):
        # 確認收件
        confirm_receipt = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[1]'))
        assert confirm_receipt is not None, "未找到confirm_receipt"
        confirm_receipt.click()

    with allure.step("彈窗確認"):
        # 彈窗確認
        edit_alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert edit_alert_check is not None, "未找到彈窗確認"
        edit_alert_check.click()

    with allure.step("彈窗確認"):
        # 彈窗確認
        alert_check = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"確定")]'))
        assert alert_check is not None, "未找到彈窗確認"
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        alert_check.click()
        time.sleep(1)

    with allure.step("打印收件狀態時間"):
        paper_collection_time = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr/td[8]'))
        )
        text_value = paper_collection_time.text.strip()
        print(f"# 收件確認-收件時間：{text_value}")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        print("# 測試案例3-3 協會-收件確認-確認收件成功")

# 測試案例3-4 協會-收件確認-紙本文件成功
# @allure.feature("協會後台-收件確認")
# @allure.story("TC3-4協會-紙本文件確認成功")
# def test_paper_document_confirmation_successfully(driver,login_association,order_id):
    # assert order_id["value"] is not None, "order_id 尚未建立"
    # print(f"使用訂單編號：{order_id['value']}")

    # driver = login_association
    # time.sleep(2)

    # # 確保載入'收件確認'頁面
    # driver.get('https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm')
    # WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm"))
    # time.sleep(1)

    # with allure.step("搜尋訂單編號"):
    #     # 搜尋訂單編號
    #     search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
    #     assert search_order_id is not None, "未找到search_order_id"
    #     search_order_id.clear()
    #     search_order_id.send_keys(order_id['value']) # 帶入 order_id

    # with allure.step("點擊搜尋"):
    #     # 搜尋
    #     search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
    #     assert search is not None, "未找到search"
    #     search.click()
    #     time.sleep(1)
    #     allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    # with allure.step("點擊紙本文件確認"):
    #     # 紙本文件確認
    #     paper_document_confirmation = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[1]'))
    #     assert paper_document_confirmation is not None, "未找到paper_document_confirmation"
    #     paper_document_confirmation.click()
    #     time.sleep(1)
    #     # 刷新頁面
    #     driver.refresh()
    #     time.sleep(1)

    # with allure.step("1.申請書-收到紙本"):
    #     paper_document_confirmation_1 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[2]'))
    #     assert paper_document_confirmation_1 is not None, "未找到paper_document_confirmation_1"
    #     paper_document_confirmation_1.click()

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # with allure.step("2.附件一：申請驗證產品及原料表-收到紙本"):
    #     paper_document_confirmation_2 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[5]'))
    #     assert paper_document_confirmation_2 is not None, "未找到paper_document_confirmation_2"
    #     paper_document_confirmation_2.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # with allure.step("3.附件二：所有不申請驗證產品及原料表-收到紙本"):
    #     paper_document_confirmation_3 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[8]'))
    #     assert paper_document_confirmation_3 is not None, "未找到paper_document_confirmation_3"
    #     paper_document_confirmation_3.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
        
    # with allure.step("4.附件三：原料明細表-收到紙本"):
    #     paper_document_confirmation_4 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[11]'))
    #     assert paper_document_confirmation_4 is not None, "未找到paper_document_confirmation_4"
    #     paper_document_confirmation_4.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # with allure.step("5.承諾遵守驗證方案及工廠稽核聲明書-收到紙本"):
    #     paper_document_confirmation_5 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[14]'))
    #     assert paper_document_confirmation_5 is not None, "未找到paper_document_confirmation_5"
    #     paper_document_confirmation_5.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # with allure.step("6.包裝標示切結書-收到紙本"):
    #     paper_document_confirmation_6 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[17]'))
    #     assert paper_document_confirmation_6 is not None, "未找到paper_document_confirmation_6"
    #     paper_document_confirmation_6.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # with allure.step("7.附錄：導致結案或拒絕受理之事項-收到紙本"):
    #     paper_document_confirmation_7 = wait_for_element_clickable(driver, (By.XPATH, '(//button[@type="button"])[20]'))
    #     assert paper_document_confirmation_7 is not None, "未找到paper_document_confirmation_7"
    #     paper_document_confirmation_7.click()
    #     time.sleep(1)

    #     # 等下拉觸發點可點擊
    #     dropdown_trigger = WebDriverWait(driver, 10).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[contains(@class,"css-dk3iff-control")]'))
    #     )
    #     dropdown_trigger.click()

    #     # 等 option 出現（這才是等 list-versions API 的「結果」）
    #     WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"-option")]'))
    #     )

    #     # 點第一個版本
    #     driver.find_element(By.XPATH, '//div[contains(@class,"-option")]').click()

    #     # 填寫備註
    #     note_area = driver.find_element(By.XPATH, '//textarea[@placeholder="請輸入內部備註"]')
    #     assert note_area is not None, "未找到note_area"
    #     note_area.send_keys("測試通過")

    #     # 點擊通過
    #     approve_button = driver.find_element(By.XPATH, '//button[contains(text(),"通過")]')
    #     assert approve_button is not None, "未找到approve_button"
    #     approve_button.click()

    #     # 確認彈窗
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()
    #     WebDriverWait(driver, 5).until(
    #         EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
    #     ).click()

    # # 確保載入'收件確認'頁面
    # driver.get('https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm')
    # WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm"))
    # time.sleep(1)

    # with allure.step("搜尋訂單編號"):
    #     # 搜尋訂單編號
    #     search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
    #     assert search_order_id is not None, "未找到search_order_id"
    #     search_order_id.clear()
    #     search_order_id.send_keys(order_id['value']) # 帶入 order_id

    # with allure.step("點擊搜尋"):
    #     # 搜尋
    #     search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
    #     assert search is not None, "未找到search"
    #     search.click()
    #     time.sleep(1)
    #     allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
    
    # with allure.step("驗證紙本狀態是否為已完成"):
    #     status_tag = WebDriverWait(driver, 5).until(
    #         EC.presence_of_element_located(
    #             (By.XPATH, '//span[contains(@class, "table_approved__") and contains(text(), "已完成")]')
    #         )
    #     )
    #     allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
    #     assert status_tag is not None, "未找到狀態標籤"
    #     assert status_tag.text.strip() == "已完成", f"紙本狀態錯誤，實際為：{status_tag.text}"
    #     print("# 測試案例3-4 協會-收件確認-紙本文件成功")

# 測試案例3-5 協會-收件確認-初審前置確認成功
@allure.feature("協會後台-收件確認")
@allure.story("TC3-5協會-初審前置確認成功")
def test_preliminary_confirmation_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'收件確認'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊初審前置確認"):
        # 初審前置確認
        paper_document_confirmation = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[2]'))
        assert paper_document_confirmation is not None, "未找到paper_document_confirmation"
        paper_document_confirmation.click()
        time.sleep(1)

    with allure.step("點擊完成審核"):
        # 完成審核
        complete_review = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"整件審核")]'))
        assert complete_review is not None, "未找到complete_review"
        complete_review.click()
        # 確認彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        time.sleep(1)
    
    # 確保載入'收件確認'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/receipt-confirm"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("驗證初審前置狀態是否為已完成"):
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[6]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "已完成", f"初審前置狀態錯誤，實際為：{status_text}"
        print("測試案例3-5 協會-收件確認-初審前置確認成功")

# 測試案例3-6 協會-案件指派-案件指派成功
@allure.feature("協會後台-案件指派")
@allure.story("TC3-6協會-案件指派成功")
def test_case_assignment_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'案件指派'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/assing-case')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/assing-case"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊指派人員"):
        # 指派人員
        designate_personnel = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/div/div/div[1]/table/tbody/tr/td[7]/div/button'))
        assert designate_personnel is not None, "未找到designate_personnel"
        designate_personnel.click()
        time.sleep(1)

    with allure.step("指派初審人員"):
        # 點開初審人員下拉式選單
        preliminary_reviewer = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[1]/div/div"))
        assert preliminary_reviewer is not None, "未找到preliminary_reviewer"
        preliminary_reviewer.click()
        time.sleep(0.5)
        # 點選 Harry
        harry_option = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class,'menu')]//div[text()='Harry']"
            ))
        )
        harry_option.click()
        time.sleep(0.5)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("指派複審人員"):
        # 點開複審人員下拉式選單
        reviewer = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[2]/div/div"))
        assert reviewer is not None, "未找到reviewer"
        reviewer.click()
        time.sleep(0.5)
        # 點選 Harry
        harry_option = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class,'menu')]//div[text()='Harry']"
            ))
        )
        harry_option.click()
        time.sleep(0.5)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊送出"):
        # 送出
        submit_button = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
        assert submit_button is not None, "未找到submit_button"
        submit_button.click()

        # 確認彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    # 驗證初審人員
    with allure.step("驗證初審人員是否為 Harry"):
        initial_reviewer_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[5]')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        initial_text = initial_reviewer_td.text.strip()
        assert initial_text == "Harry", f"初審人員錯誤，實際為：{initial_text}"
        print("測試案例3-6 協會-案件指派-初審人員指派成功")

    # 驗證複審人員
    with allure.step("驗證複審人員是否為 Harry"):
        final_reviewer_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[6]')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        final_text = final_reviewer_td.text.strip()
        assert final_text == "Harry", f"複審人員錯誤，實際為：{final_text}"
        print("測試案例3-6 協會-案件指派-複審人員指派成功")

# 測試案例3-7 協會-我的文件初審-初審審核成功
@allure.feature("協會後台-我的文件初審")
@allure.story("TC3-7協會-我的文件初審審核成功")
def test_my_file_initial_review_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'我的文件初審'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/preaudit-case')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/preaudit-case"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊檢視案件"):
        # 檢視案件
        view_case = wait_for_element_clickable(driver, (By.XPATH, '//tbody/tr[1]/td[8]/div[1]/button[1]/div[1]'))
        assert view_case is not None, "未找到view_case"
        view_case.click()
        time.sleep(2)

    with allure.step("點擊完成審核"):
        # 完成審核
        complete_review = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"整件審核")]'))
        assert complete_review is not None, "未找到complete_review"
        complete_review.click()
        # 確認彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        time.sleep(1)

    # 確保載入'我的文件初審'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/preaudit-case')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/preaudit-case"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("驗證我的文件初審狀態是否為已完成"):
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[6]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "已完成", f"我的文件初審狀態錯誤，實際為：{status_text}"
        print("測試案例3-7 協會-我的文件初審-初審審核成功")

# 測試案例3-8 協會-我的文件複審-複審審核成功
@allure.feature("協會後台-我的文件複審")
@allure.story("TC3-8協會-我的文件複審審核成功")
def test_my_document_review_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'我的文件複審'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/reaudit-case')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/reaudit-case"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊複審審核"):
        # 複審審核
        review_review = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[2]'))
        assert review_review is not None, "未找到review_review"
        review_review.click()
        time.sleep(1)

    with allure.step("填入詳細類別名稱"):
        # 詳細類別名稱
        detailed_category_name = wait_for_element_clickable(driver, (By.XPATH, "//body[1]/div[1]/div[1]/div[2]/div[1]/div[2]/form[1]/div[4]/div[1]/div[1]/div[1]/div[1]"))
        assert detailed_category_name is not None, "未找到detailed_category_name"
        detailed_category_name.clear()
        detailed_category_name.send_keys("本產品屬於食品類別，依規定分類並管理。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("填入不申請認證產品是否有交叉汙染風險"):
        # 不申請認證產品是否有交叉汙染風險
        cross_contamination = wait_for_element_clickable(driver, (By.XPATH, "//div[@data-placeholder='交叉污染風險說明（非必填）']"))
        assert cross_contamination is not None, "未找到cross_contamination"
        cross_contamination.clear()
        cross_contamination.send_keys("經評估，未申請認證之產品無交叉汙染風險。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入製程說明"):
        # 製程說明
        process_description = wait_for_element_clickable(driver, (By.XPATH, "//div[@data-placeholder='製程說明（必填）']"))
        assert process_description is not None, "未找到process_description"
        process_description.clear()
        process_description.send_keys("製程包括原料檢驗、配料、混合、成型、包裝與檢驗，全程依SOP作業。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入設備清洗"):
        # 設備清洗
        equipment_cleaning = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='root']/div/div[2]/div/div[2]/form/div[12]/div/div/div/div"))
        assert equipment_cleaning is not None, "未找到equipment_cleaning"
        equipment_cleaning.clear()
        equipment_cleaning.send_keys("所有生產設備依規定SOP進行清洗，確保衛生與無殘留。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入清潔劑"):
        # 清潔劑
        detergent = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='root']/div/div[2]/div/div[2]/form/div[14]/div/div/div/div"))
        assert detergent is not None, "未找到detergent"
        detergent.clear()
        detergent.send_keys("使用食品級安全清潔劑，符合相關規範，並經確認無殘留風險。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入消毒劑"):
        # 消毒劑
        disinfectant = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='root']/div/div[2]/div/div[2]/form/div[16]/div/div/div/div"))
        assert disinfectant is not None, "未找到disinfectant"
        disinfectant.clear()
        disinfectant.send_keys("使用經核可之食品級消毒劑，並依規範濃度及程序操作。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入消毒用酒精"):
        # 消毒用酒精
        disinfectant_alcohol = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='root']/div/div[2]/div/div[2]/form/div[18]/div/div/div/div"))
        assert disinfectant_alcohol is not None, "未找到disinfectant_alcohol"
        disinfectant_alcohol.clear()
        disinfectant_alcohol.send_keys("使用75%食品級酒精進行表面消毒，確保衛生環境。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("選擇原料成分"):
        # 新增原料
        add_raw_materials = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增原料")]'))
        assert add_raw_materials is not None, "未找到add_raw_materials"
        add_raw_materials.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        # 選取原料1
        raw_material_1 = wait_for_element_clickable(driver, (By.XPATH, "//tbody/tr[1]/td[1]/input[1]"))
        assert raw_material_1 is not None, "未找到raw_material_1"
        raw_material_1.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        # 新增
        add_button = wait_for_element_clickable(driver, (By.XPATH, '//button[@aria-label="新增"]'))
        assert add_button is not None, "未找到add_button"
        add_button.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入包裝是否符合規定"):
        # 包裝是否符合規定
        packaging_instructions = wait_for_element_clickable(driver, (By.XPATH, "//div[@data-placeholder='包裝說明（非必填）']"))
        assert packaging_instructions is not None, "未找到packaging_instructions"
        packaging_instructions.clear()
        packaging_instructions.send_keys("產品包裝材質及標示均符合相關法規及標準。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入備註"):
        # 備註
        remark = wait_for_element_clickable(driver, (By.XPATH, "//div[@class='ql-editor ql-blank']"))
        assert remark is not None, "未找到remark"
        remark.clear()
        remark.send_keys("此項產品無需填入備註事項。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入文件審核摘要"):
        # 文件審核摘要
        document_review_summary = wait_for_element_clickable(driver, (By.XPATH, "//*[@id='root']/div/div[2]/div/div[2]/form/div[26]/div/div/div[2]/div[1]"))
        assert document_review_summary is not None, "未找到document_review_summary"
        document_review_summary.clear()
        document_review_summary.send_keys("經文件審核，所有流程、清潔紀錄及檢驗報告均符合規範，無異常情事。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊審核通過"):
        # 審核通過
        approved = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"審核通過")]'))
        assert approved is not None, "未找到approved"
        approved.click()

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    # 確保載入'我的文件複審'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/reaudit-case')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/reaudit-case"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("驗證我的文件複審狀態是否為已完成"):
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[7]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "已完成", f"我的文件初審狀態錯誤，實際為：{status_text}"
        print("測試案例3-8 協會-我的文件複審-複審審核成功")

# 測試案例3-9 協會-勘廠審查-審查成功
@allure.feature("協會後台-勘廠審查")
@allure.story("TC3-9協會-勘廠審查成功")
def test_my_factory_review_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'勘廠審查'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/factory-inspection-review')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/factory-inspection-review"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊勘廠審查"):
        # 勘廠審查
        review_review = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[3]'))
        assert review_review is not None, "未找到review_review"
        review_review.click()
        time.sleep(1)

    with allure.step("勘廠基本資訊"):
        with allure.step("選擇勘廠時間"):
            # 勘廠時間
            factory_survey_time = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇勘場時間']"))
            )
            factory_survey_time.click()
            time.sleep(0.5)
            # 選擇「今天」的日期
            today_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
            )
            today_btn.click()
            time.sleep(0.5)

    with allure.step("勘廠審查人"):
        with allure.step("新增審查人員"):
            # 新增審查人員
            add_new_reviewer = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增審查人員")]'))
            assert add_new_reviewer is not None, "未找到add_new_reviewer"
            add_new_reviewer.click()

        with allure.step("指派人員"):
            # 指派人員
            designate_personnel = wait_for_element_clickable(driver, (By.XPATH, "/html/body/div[2]/div/div[2]/div[1]/div[1]/div/div"))
            assert designate_personnel is not None, "未找到designate_personnel"
            designate_personnel.click()
            time.sleep(0.5)
            # 點選 Harry
            harry_option = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.XPATH, "//div[contains(@class,'menu')]//div[text()='Harry']"
                ))
            )
            harry_option.click()
            time.sleep(0.5)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

        with allure.step("點擊新增"):
            # 新增
            add_button = wait_for_element_clickable(driver, (By.XPATH, '//button[@aria-label="新增"]'))
            assert add_button is not None, "未找到add_button"
            add_button.click()

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()

        with allure.step("編輯審查人簽名"):
            # 編輯簽名
            edit_signature = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-tooltip-content="編輯審查人簽名"]'))
            assert edit_signature is not None, "未找到edit_signature"
            edit_signature.click()

            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)
        
        with allure.step("點擊送出"):
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send is not None, "未找到send"
            send.click()
        
        with allure.step("點擊更新"):
            # 更新
            update = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"更新")]'))
            assert update is not None, "未找到update"
            update.click()

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()

    with allure.step("廠商陪同勘廠人員"):
        with allure.step("新增陪同人員"):
            # 新增陪同人員
            add_accompanying_personnel = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增陪同人員")]'))
            assert add_accompanying_personnel is not None, "未找到add_accompanying_personnel"
            add_accompanying_personnel.click()

        with allure.step("選擇工廠"):
            # 1. 等待並點擊下拉箭頭（避免直接點 div）
            dropdown_arrow = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.css-1xc3v61-indicatorContainer"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_arrow)
            dropdown_arrow.click()
            time.sleep(0.5)

            # 2. 等待選項出現並點擊「瑞春醬油有限公司福田廠(代工廠)」
            factory_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'option') and text()='瑞春醬油有限公司福田廠(代工廠)']"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", factory_option)
            driver.execute_script("arguments[0].click();", factory_option)

        with allure.step("填入姓名"):
            # 姓名
            name = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="請輸入姓名"]'))
            assert name is not None, "未找到name"
            name.clear()
            name.send_keys("金城武")

        with allure.step("填入職務"):
            # 職務
            position = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="請輸入職務"]'))
            assert position is not None, "未找到position"
            position.clear()
            position.send_keys("勘廠助理")

        with allure.step("點擊請簽名"):
            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)

        with allure.step("點擊送出"):
            # 送出
            send_button = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send_button is not None, "未找到send_button"
            send_button.click()

        with allure.step("點擊新增"):
            # 新增
            add_button = wait_for_element_clickable(driver, (By.XPATH, '//button[@aria-label="新增"]'))
            assert add_button is not None, "未找到add_button"
            add_button.click()
            time.sleep(1)

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()

    with allure.step("複審要求注意事項"):
        with allure.step("無其他不申請驗證產品-勘廠注意事項"):
            # 無其他不申請驗證產品-勘廠注意事項
            no_other_products = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[10]/div[2]/div[1]/div/div[3]/div/div/div/div'))
            assert no_other_products is not None, "未找到no_other_products"
            no_other_products.clear()
            no_other_products.send_keys("現場確認僅有申請驗證之產品生產，無未申請驗證產品存在。")
        
        with allure.step("比對原料-勘廠注意事項"):
            # 比對原料-勘廠注意事項
            compare_raw_materials = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[10]/div[2]/div[2]/div/div[3]/div/div/div/div'))
            assert compare_raw_materials is not None, "未找到compare_raw_materials"
            compare_raw_materials.clear()
            compare_raw_materials.send_keys("現場確認僅有申請驗證之產品生產，無未申請驗證產品存在。")

        with allure.step("清潔劑-勘廠注意事項"):
            # 清潔劑-勘廠注意事項
            detergent = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[10]/div[2]/div[3]/div/div[3]/div/div/div/div'))
            assert detergent is not None, "未找到detergent"
            detergent.clear()
            detergent.send_keys("現場使用之清潔劑符合食品級規範，經查驗確認無殘留風險。")

        with allure.step("消毒劑-勘廠注意事項"):
            # 消毒劑-勘廠注意事項
            disinfectant = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[10]/div[2]/div[4]/div/div[3]/div/div/div/div'))
            assert disinfectant is not None, "未找到disinfectant"
            disinfectant.clear()
            disinfectant.send_keys("現場使用之消毒劑為核可食品級產品，操作依規定濃度及程序進行，無異常。")

        with allure.step("消毒用酒精-勘廠注意事項"):
            # 消毒用酒精-勘廠注意事項
            disinfectant_alcohol = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[10]/div[2]/div[5]/div/div[3]/div/div/div/div'))
            assert disinfectant_alcohol is not None, "未找到disinfectant_alcohol"
            disinfectant_alcohol.clear()
            disinfectant_alcohol.send_keys("現場使用75%食品級酒精進行表面消毒，環境衛生良好，無異常。")

    with allure.step("現場勘查項目"):
        with allure.step("1. 該廠產製產品分類"):
            # 1. 該廠產製產品分類
            product_classification = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[13]/div[2]/div/div/div/div'))
            assert product_classification is not None, "未找到product_classification"
            product_classification.clear()
            product_classification.send_keys("產品分類")

        with allure.step("2. 該廠是否承接代工(ODM/OEM)業務"):
            # 2. 該廠是否承接代工(ODM/OEM)業務
            oem_odm_business = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[14]/div[2]/div/div/div/div'))
            assert oem_odm_business is not None, "未找到oem_odm_business"
            oem_odm_business.clear()
            oem_odm_business.send_keys("是")

        with allure.step("3. 生產驗證產品是否使用清真專線(設備/車間)"):
            # 3. 生產驗證產品是否使用清真專線(設備/車間)
            halal_production_line = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[15]/div[2]/div/div/div/div'))
            assert halal_production_line is not None, "未找到halal_production_line"
            halal_production_line.clear()
            halal_production_line.send_keys("是")

        with allure.step("4. 承上，如無清真專線，是否有交叉污染之虞"):
            # 4. 承上，如無清真專線，是否有交叉污染之虞
            cross_contamination_risk = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[16]/div[2]/div/div/div/div'))
            assert cross_contamination_risk is not None, "未找到cross_contamination_risk"
            cross_contamination_risk.clear()
            cross_contamination_risk.send_keys("無")
        
        with allure.step("5. 工作人員進入生產線前是否有清潔消毒防護"):
            # 5. 工作人員進入生產線前是否有清潔消毒防護
            staff_cleaning_protection = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[17]/div[3]/div/div/div/div'))
            assert staff_cleaning_protection is not None, "未找到staff_cleaning_protection"
            staff_cleaning_protection.clear()
            staff_cleaning_protection.send_keys("是")

        with allure.step("6. 勘廠時申請驗證之產品正在生產中"):
            # 6. 勘廠時申請驗證之產品正在生產中
            product_production = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[18]/div[2]/div/div/div/div'))
            assert product_production is not None, "未找到product_production"
            product_production.clear()
            product_production.send_keys("是")

        with allure.step("7. （承上）若否，已勘查相同生產流程之其他產品"):
            # 7. （承上）若否，已勘查相同生產流程之其他產品
            other_products = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[19]/div[2]/div/div/div/div'))
            assert other_products is not None, "未找到other_products"
            other_products.clear()
            other_products.send_keys("無")

        with allure.step("8. 實際生產流程與提報文件之生產流程圖相符；如不符，請說明差異"):
            # 8. 實際生產流程與提報文件之生產流程圖相符；如不符，請說明差異
            production_process = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[20]/div[2]/div/div/div/div'))
            assert production_process is not None, "未找到production_process"
            production_process.clear()
            production_process.send_keys("實際生產流程與提報文件一致，無差異。")

        with allure.step("9. 生產前/後進行機器設備之清洗消毒"):
            # 9. 生產前/後進行機器設備之清洗消毒
            equipment_cleaning = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[21]/div[2]/div/div/div/div'))
            assert equipment_cleaning is not None, "未找到equipment_cleaning"
            equipment_cleaning.clear()
            equipment_cleaning.send_keys("是")

        with allure.step("10. 生產線週圍無祭祀設施"):
            # 10. 生產線週圍無祭祀設施
            no_worship_facilities = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[22]/div[2]/div/div/div/div'))
            assert no_worship_facilities is not None, "未找到no_worship_facilities"
            no_worship_facilities.clear()
            no_worship_facilities.send_keys("是")

        with allure.step("11. 勘廠前廠方是否已先行盤點原料"):
            # 11. 勘廠前廠方是否已先行盤點原料
            raw_material_inventory = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[23]/div[2]/div/div/div/div'))
            assert raw_material_inventory is not None, "未找到raw_material_inventory"
            raw_material_inventory.clear()
            raw_material_inventory.send_keys("是")

        with allure.step("12. 進料是否有拍照存檔備查"):
            # 12. 進料是否有拍照存檔備查
            raw_material_photos = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[24]/div[2]/div/div/div/div'))
            assert raw_material_photos is not None, "未找到raw_material_photos"
            raw_material_photos.clear()
            raw_material_photos.send_keys("是")

        with allure.step("13. 原料是否標示附件三序號？並依序擺放"):
            # 13. 原料是否標示附件三序號？並依序擺放
            raw_material_serial_number = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[25]/div[2]/div/div/div/div'))
            assert raw_material_serial_number is not None, "未找到raw_material_serial_number"
            raw_material_serial_number.clear()
            raw_material_serial_number.send_keys("是")
        
        with allure.step("14. 原料三要素比對：原廠標示與附件三所記並無不符？（依文審人員指示應確認之原料）"):
            # 14. 原料三要素比對：原廠標示與附件三所記並無不符？（依文審人員指示應確認之原料）
            raw_material_three_elements = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[26]/div[2]/div/div/div/div'))
            assert raw_material_three_elements is not None, "未找到raw_material_three_elements"
            raw_material_three_elements.clear()
            raw_material_three_elements.send_keys("是")

        with allure.step("15. 原料是否使用編碼？若否，如何追溯原料"):
            # 15. 原料是否使用編碼？若否，如何追溯原料
            raw_material_coding = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[27]/div[2]/div/div/div/div'))
            assert raw_material_coding is not None, "未找到raw_material_coding"
            raw_material_coding.clear()
            raw_material_coding.send_keys("是")

        with allure.step("16. 原料倉儲是否有清真專用倉/室/儲位"):
            # 16. 原料倉儲是否有清真專用倉/室/儲位
            halal_storage = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[28]/div[2]/div/div/div/div'))
            assert halal_storage is not None, "未找到halal_storage"
            halal_storage.clear()
            halal_storage.send_keys("是")

        with allure.step("17. 整體而言，原料倉儲無交叉污染混淆之虞"):
            # 17. 整體而言，原料倉儲無交叉污染混淆之虞
            no_cross_contamination = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[29]/div[2]/div/div/div/div'))
            assert no_cross_contamination is not None, "未找到no_cross_contamination"
            no_cross_contamination.clear()
            no_cross_contamination.send_keys("是")

        with allure.step("18. 成品倉儲是否有清真專用倉/室/儲位"):
            # 18. 成品倉儲是否有清真專用倉/室/儲位
            halal_product_storage = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[30]/div[2]/div/div/div/div'))
            assert halal_product_storage is not None, "未找到halal_product_storage"
            halal_product_storage.clear()
            halal_product_storage.send_keys("是")

        with allure.step("19. 整體而言，成品倉儲無交叉污染混淆之虞？"):
            # 19. 整體而言，成品倉儲無交叉污染混淆之虞？
            no_cross_contamination_product = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[31]/div[2]/div/div/div/div'))
            assert no_cross_contamination_product is not None, "未找到no_cross_contamination_product"
            no_cross_contamination_product.clear()
            no_cross_contamination_product.send_keys("是")

        with allure.step("20. 成品包裝外觀無伊斯蘭不宜之圖文標示"):
            # 20. 成品包裝外觀無伊斯蘭不宜之圖文標示
            no_islamic_inappropriate_labeling = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[32]/div[2]/div/div/div/div'))
            assert no_islamic_inappropriate_labeling is not None, "未找到no_islamic_inappropriate_labeling"
            no_islamic_inappropriate_labeling.clear()
            no_islamic_inappropriate_labeling.send_keys("是")

        with allure.step("21. 是否有生產記錄？若否，如何追查產品流向"):
            # 21. 是否有生產記錄？若否，如何追查產品流向
            production_record = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[33]/div[2]/div/div/div/div'))
            assert production_record is not None, "未找到production_record"
            production_record.clear()
            production_record.send_keys("是")

        with allure.step("22. 整體而言，無不合教法物料汙染之虞或引起汙染之風險"):
            # 22. 整體而言，無不合教法物料汙染之虞或引起汙染之風險
            no_haram_materials = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[34]/div[2]/div/div/div/div'))
            assert no_haram_materials is not None, "未找到no_haram_materials"
            no_haram_materials.clear()
            no_haram_materials.send_keys("是")

        with allure.step("23. 該廠具有相關認證"):
            # 23. 該廠具有相關認證
            relevant_certification = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[35]/div[3]/div/div/div/div'))
            assert relevant_certification is not None, "未找到relevant_certification"
            relevant_certification.clear()
            relevant_certification.send_keys("是")

        with allure.step("24. 是否已建立清真品保系統"):
            # 24. 是否已建立清真品保系統
            halal_quality_system = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[36]/div[2]/div/div/div/div'))
            assert halal_quality_system is not None, "未找到halal_quality_system"
            halal_quality_system.clear()
            halal_quality_system.send_keys("是")

        with allure.step("25. 是否按時實施HAS內訓"):
            # 25. 是否按時實施HAS內訓
            has_internal_training = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[37]/div[2]/div/div/div/div'))
            assert has_internal_training is not None, "未找到has_internal_training"
            has_internal_training.clear()
            has_internal_training.send_keys("是")

        with allure.step("26. 是否按時核備HAS內稽報告"):
            # 26. 是否按時核備HAS內稽報告
            has_internal_audit_report = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[38]/div[2]/div/div/div/div'))
            assert has_internal_audit_report is not None, "未找到has_internal_audit_report"
            has_internal_audit_report.clear()
            has_internal_audit_report.send_keys("是")

        with allure.step("27. HAS相關紀錄文件是否詳實"):
            # 27. HAS相關紀錄文件是否詳實
            has_related_records = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[39]/div[2]/div/div/div/div'))
            assert has_related_records is not None, "未找到has_related_records"
            has_related_records.clear()
            has_related_records.send_keys("是")

        with allure.step("填入勘場摘要"):
            # 勘場摘要
            survey_summary = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫勘場摘要"]'))
            assert survey_summary is not None, "未找到survey_summary"
            survey_summary.clear()
            survey_summary.send_keys("勘廠確認該廠符合清真認證要求，無異常情事。")

        with allure.step("日後稽核重點"):
            # 日後稽核重點
            future_audit_focus = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫日後稽核重點"]'))
            assert future_audit_focus is not None, "未找到future_audit_focus"
            future_audit_focus.clear()
            future_audit_focus.send_keys("日後稽核重點包括原料來源確認、清潔消毒程序執行、產品標示符合規範。")

    with allure.step("點擊儲存"):
        # 儲存
        save_button = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"儲存")]'))
        assert save_button is not None, "未找到save_button"
        save_button.click()

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
    
    with allure.step("點擊審核通過"):
        # 審核通過
        approved = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"審核通過")]'))
        assert approved is not None, "未找到approved"
        approved.click()

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    # 確保載入'勘廠審查'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/factory-inspection-review')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/factory-inspection-review"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("驗證勘廠審查狀態是否為已完成"):
        # 驗證勘廠審查狀態是否為已完成
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[6]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "已完成", f"勘廠審查狀態錯誤，實際為：{status_text}"
        print("測試案例3-9 協會-勘廠審查-審查成功")
        
# 測試案例3-10 協會-內部審議-審議成功
@allure.feature("協會後台-內部審議")
@allure.story("TC3-10協會-內部審議成功")
def test_internal_review_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'內部審議'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/inner-audit')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/inner-audit"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊進入內部審議"):
        # 內部審議
        internal_review = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[4]'))
        assert internal_review is not None, "未找到internal_review"
        internal_review.click()
        time.sleep(1)

    with allure.step("選擇會議日期"):
        # 會議日期
        meeting_date = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇會議日期']"))
        )
        meeting_date.click()
        time.sleep(0.5)
        # 選擇「今天」的日期
        today_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
        )
        today_btn.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        time.sleep(0.5)

    with allure.step("填入建議分類-類別"):
        # 類別
        suggested_classification = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="請輸入類別"]'))
        assert suggested_classification is not None, "未找到suggested_classification"
        suggested_classification.send_keys('最終審查結論')
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入建議分類-項目"):
        # 項目
        suggested_classification = wait_for_element_clickable(driver, (By.XPATH, '//input[@placeholder="請輸入項目"]'))
        assert suggested_classification is not None, "未找到suggested_classification"
        suggested_classification.send_keys('5')
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("選擇風險等級-低"):
        # 風險等級
        risk_level = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="riskLevel_1"]'))
        assert risk_level is not None, "未找到risk_level"
        risk_level.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("選擇提供續約優惠-否"):
        # 提供續約優惠折扣
        offer_renewal_discounts = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="isRenewalDiscount_2"]'))
        assert offer_renewal_discounts is not None, "未找到offer_renewal_discounts"
        offer_renewal_discounts.click()

    with allure.step("選擇審議委員意見-1年"):
        # 審議委員意見
        opinions_of_review_committee_members = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="committeeOpinionYear_1"]'))
        assert opinions_of_review_committee_members is not None, "未找到opinions_of_review_committee_members"
        opinions_of_review_committee_members.click()

    with allure.step("新增出席人員"):
        with allure.step("新增案件審查召集人"):
            # 案件審查會議出席人員-新增人員
            add_new_personnel = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增人員")]'))
            assert add_new_personnel is not None, "未找到add_new_personnel"
            add_new_personnel.click()
            time.sleep(0.5)
            
            # 姓名
            name = wait_for_element_clickable(driver, (By.XPATH, '//textarea[@placeholder="請填寫姓名"]'))
            assert name is not None, "未找到name"
            name.send_keys("案件審查召集人哈利")

            # 角色-案件審查召集人
            # 打開下拉
            role_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class,'css-dk3iff-control')][.//div[contains(@class,'placeholder') and normalize-space()='請選擇角色']]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", role_dropdown)
            role_dropdown.click()

            # 點選「案件審查召集人」
            target_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space()='案件審查召集人']"))
            )
            target_option.click()

            # 送出
            submit = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert submit is not None, "未找到submit"
            submit.click()

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()

        with allure.step("新增審議委員代表"):
            # 案件審查會議出席人員-新增人員
            add_new_personnel = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"新增人員")]'))
            assert add_new_personnel is not None, "未找到add_new_personnel"
            add_new_personnel.click()
            time.sleep(0.5)
            
            # 姓名
            name = wait_for_element_clickable(driver, (By.XPATH, '//textarea[@placeholder="請填寫姓名"]'))
            assert name is not None, "未找到name"
            name.send_keys("審議委員代表哈利")

            # 角色-審議委員代表
            # 打開下拉
            role_dropdown = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class,'css-dk3iff-control')][.//div[contains(@class,'placeholder') and normalize-space()='請選擇角色']]"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", role_dropdown)
            role_dropdown.click()

            # 點選「審議委員代表」
            target_option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='option' and normalize-space()='審議委員代表']"))
            )
            target_option.click()

            # 送出
            submit = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert submit is not None, "未找到submit"
            submit.click()

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()

    with allure.step("編輯出席人員簽名"):
        with allure.step("案件審查召集人-編輯簽名"):
            # 編輯
            edit_sign = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[12]/div[2]/div[1]/div/div[4]/div/div[2]'))
            assert edit_sign is not None, "未找到edit_sign"
            edit_sign.click()

            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '/html/body/div[3]/div/form/div[2]/div[2]/button'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()
        
        with allure.step("文件審查員-編輯簽名"):
            # 編輯
            edit_sign = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[12]/div[2]/div[2]/div/div[4]/div/div'))
            assert edit_sign is not None, "未找到edit_sign"
            edit_sign.click()

            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '/html/body/div[3]/div/form/div[2]/div[2]/button'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()
        
        with allure.step("勘廠稽核員-編輯簽名"):
            # 編輯
            edit_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[3]//div[1]//div[4]//div[1]//div[1]'))
            assert edit_sign is not None, "未找到edit_sign"
            edit_sign.click()

            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '/html/body/div[3]/div/form/div[2]/div[2]/button'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()
        
        with allure.step("審議委員代表-編輯簽名"):
            # 編輯
            edit_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[4]//div[1]//div[4]//div[1]//div[2]'))
            assert edit_sign is not None, "未找到edit_sign"
            edit_sign.click()

            # 點擊「請簽名」
            please_sign = wait_for_element_clickable(driver, (By.XPATH, '//div[contains(text(),"請簽名")]'))
            assert please_sign is not None, "未找到please_sign"
            please_sign.click()

            # 簽名板
            sigCanvas = wait_for_element_clickable(driver, (By.XPATH, '//canvas[@class="sigCanvas"]'))
            assert sigCanvas is not None, "未找到簽名板"

            draw_script = """
            const canvas = arguments[0];
            const ctx = canvas.getContext('2d');
            const rect = canvas.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const size = rect.height / 3;
            const gap = 50;               // 字母間距
            const jitter = 1.5;           // 抖動幅度 (px)

            function jitterValue(val) {
                return val + (Math.random() - 0.5) * jitter * 2;
            }

            function drawJitteredLine(x1, y1, x2, y2, steps=15) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(x1), jitterValue(y1));
                for (let i = 1; i <= steps; i++) {
                    const t = i / steps;
                    const x = x1 + (x2 - x1) * t;
                    const y = y1 + (y2 - y1) * t;
                    ctx.lineTo(jitterValue(x), jitterValue(y));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            function drawJitteredCurve(points) {
                ctx.beginPath();
                ctx.moveTo(jitterValue(points[0][0]), jitterValue(points[0][1]));
                for (let i = 1; i < points.length; i++) {
                    ctx.lineTo(jitterValue(points[i][0]), jitterValue(points[i][1]));
                }
                ctx.lineWidth = 2;
                ctx.stroke();
            }

            // 清空畫布
            ctx.clearRect(0, 0, rect.width, rect.height);

            // 計算每個字母中心位置
            const letters = ['T', 'E', 'S', 'T'];
            const totalWidth = (letters.length - 1) * gap;
            const startX = centerX - totalWidth / 2;

            // === 畫 T ===
            let x = startX;
            let topY = centerY - size/2;
            let bottomY = centerY + size/2;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫

            // === 畫 E ===
            x += gap;
            drawJitteredLine(x-8, topY, x-8, bottomY);                 // 垂直
            drawJitteredLine(x-8, topY, x+10, topY);                   // 上橫
            drawJitteredLine(x-8, centerY, x+8, centerY);              // 中橫
            drawJitteredLine(x-8, bottomY, x+10, bottomY);             // 下橫

            // === 畫 S ===
            x += gap;
            drawJitteredCurve([
                [x+15, topY],
                [x-15, centerY - size/4],
                [x+15, centerY]
            ]);
            drawJitteredCurve([
                [x+15, centerY],
                [x-15, centerY + size/4],
                [x+15, bottomY]
            ]);

            // === 畫 T (最後一個) ===
            x += gap;
            drawJitteredLine(x, topY, x, bottomY);                     // 垂直
            drawJitteredLine(x-15, topY, x+15, topY);                  // 上橫
            """
            driver.execute_script(draw_script, sigCanvas)
            allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '/html/body/div[3]/div/form/div[2]/div[2]/button'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)
        
            # 送出
            send = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"送出")]'))
            assert send is not None, "未找到send"
            send.click()
            time.sleep(0.5)

            # 確定彈窗
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
            ).click()
        
    with allure.step("決議-通過"):
        # 決議-通過
        resolution_passed = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="resolution_1"]'))
        assert resolution_passed is not None, "未找到resolution_passed"
        resolution_passed.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("填入附註"):
        # 附註
        remarks = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="root"]/div/div[2]/div/div[2]/form/div[15]/div/div/div[2]/div[1]'))
        assert remarks is not None, "未找到remarks"
        remarks.send_keys("各審查人員需對分工項目提出具體意見，不得僅簽核無意見。")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
    
    with allure.step("點擊儲存"):
        # 儲存
        save = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"儲存")]'))
        assert save is not None, "未找到save"
        save.click()

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    with allure.step("點擊審核通過"):
        # 審核通過
        approved = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"審核通過")]'))
        assert approved is not None, "未找到approved"
        approved.click()

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
            
    # 確保載入'內部審議'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/inner-audit')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/inner-audit"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("驗證內部審議狀態是否為已完成"):
        # 驗證勘廠審查狀態是否為已完成
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[7]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "已完成", f"勘廠審查狀態錯誤，實際為：{status_text}"
        print("測試案例3-10 協會-內部審議-審議成功")

# 測試案例3-11 協會-證書管理-發證成功
@allure.feature("協會後台-證書管理")
@allure.story("TC3-11協會-發證成功")
def test_certificate_management_and_issuance_successfully(driver,login_association,order_id):
    assert order_id["value"] is not None, "order_id 尚未建立"
    print(f"使用訂單編號：{order_id['value']}")

    driver = login_association
    time.sleep(2)

    # 確保載入'證書管理'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/manage-certification')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/manage-certification"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊進入確認合約/證書關鍵內容"):
        # 確認合約/證書關鍵內容
        confirm_contract = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[2]'))
        assert confirm_contract is not None, "未找到confirm_contract"
        confirm_contract.click()
        time.sleep(1)

    with allure.step("填入證書編號"):
        # 證書編號
        certificate_number = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫證書編號"]'))
        assert certificate_number is not None, "未找到certificate_number"
        certificate_number.clear()
        certificate_number.send_keys("HALAL",random_name)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("選擇合約開始日"):
        # 合約開始日
        contract_start_date = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇合約開始日']"))
        )
        contract_start_date.click()
        time.sleep(0.5)
        # 選擇「今天」的日期
        today_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
        )
        today_btn.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        time.sleep(0.5)

    with allure.step("勾選添加HAS補充說明"):
        # HAS補充說明
        valid_more_than_one_year = wait_for_element_clickable(driver, (By.XPATH, '//input[@type="checkbox"]'))
        assert valid_more_than_one_year is not None, "未找到valid_more_than_one_year"
        valid_more_than_one_year.click()

    with allure.step("證書類別勾選有附件"):
        # 證書類別-有附件
        certificate_type_with_attachment = wait_for_element_clickable(driver, (By.XPATH, '//*[@id="certificationType_1"]'))
        assert certificate_type_with_attachment is not None, "未找到certificate_type_with_attachment"
        certificate_type_with_attachment.click()
        time.sleep(1)

    with allure.step("填入公司英文地址"):
        # 公司英文地址
        company_english_address = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫公司英文地址"]'))
        assert company_english_address is not None, "未找到company_english_address"
        company_english_address.clear()
        company_english_address.send_keys("No. 888 ,Taichung City")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        time.sleep(1)

    with allure.step("填入工廠英文地址"):
        # 工廠英文地址
        factory_english_address = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫工廠英文地址"]'))
        assert factory_english_address is not None, "未找到factory_english_address"
        factory_english_address.clear()
        factory_english_address.send_keys("No. 205, Sec. 3, Beixin Rd., Xindian Dist., New Taipei City 231, Taiwan (R.O.C.)")

    with allure.step("填入合約負責人"):
        # 合約負責人
        contract_person_in_charge = wait_for_element_clickable(driver, (By.XPATH, '//div[@data-placeholder="請填寫合約負責人"]'))
        assert contract_person_in_charge is not None, "未找到contract_person_in_charge"
        contract_person_in_charge.send_keys("Halal哈利")
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("選擇合約發信日"):
        # 合約發信日
        contract_signing_date = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇合約發信日']"))
        )
        contract_signing_date.click()
        time.sleep(0.5)
        # 選擇「今天」的日期
        today_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
        )
        today_btn.click()
        time.sleep(0.5)

    with allure.step("選擇簽約日"):
        # 簽約日
        signing_date = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='請選擇簽約日']"))
        )
        signing_date.click()
        time.sleep(0.5)
        # 選擇「今天」的日期
        today_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".react-datepicker__day--today"))
        )
        today_btn.click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        time.sleep(0.5)

    with allure.step("點選儲存"):
        # 儲存
        save = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"儲存")]'))
        assert save is not None, "未找到save"
        save.click()
        time.sleep(0.5)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    # 確保載入'證書管理'頁面
    driver.get('https://halal-dev-is.intersense.cloud/halal-association/manage-certification')
    WebDriverWait(driver, 10).until(EC.url_to_be("https://halal-dev-is.intersense.cloud/halal-association/manage-certification"))
    time.sleep(1)

    with allure.step("搜尋訂單編號"):
        # 搜尋訂單編號
        search_order_id = wait_for_element_clickable(driver, (By.XPATH, '//input[@id="displayId"]'))
        assert search_order_id is not None, "未找到search_order_id"
        search_order_id.clear()
        search_order_id.send_keys(order_id['value']) # 帶入 order_id

    with allure.step("點擊搜尋"):
        # 搜尋
        search = wait_for_element_clickable(driver, (By.XPATH, '//button[contains(text(),"搜尋")]'))
        assert search is not None, "未找到search"
        search.click()
        time.sleep(1)
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

    with allure.step("點擊確定發證"):
        # 確定發證
        confirm_issuance_certificate = wait_for_element_clickable(driver, (By.XPATH, '//tbody//button[5]'))
        assert confirm_issuance_certificate is not None, "未找到confirm_issuance_certificate"
        confirm_issuance_certificate.click()
        time.sleep(1)

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)

        # 確定彈窗
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(),"確定")]'))
        ).click()

    with allure.step("驗證案件類型是否正確"):
        # 驗證案件類型是否正確
        status_td = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.XPATH, '//table//tbody/tr/td[4]//span')
            )
        )
        allure.attach(driver.get_screenshot_as_png(), name="截圖", attachment_type=allure.attachment_type.PNG)
        status_text = status_td.text.strip()
        assert status_text == "有效證書", f"勘廠審查狀態錯誤，實際為：{status_text}"
        print("測試案例3-11 協會-證書管理-發證成功")
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
@pytest.fixture(scope="function")
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=2560,1440")  
    chrome_options.add_argument("--headless=new")         

    # 遠端 Selenium Server
    driver = webdriver.Remote(
        command_executor="http://localhost:4444/wd/hub",
        options=chrome_options
    )

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
            processImage_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='dog.jpg']"))
            assert processImage_option is not None, "未找到製程圖選項-dog.jpg"
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
            time.sleep(1)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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

            time.sleep(1)
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
            processImage_option = wait_for_element_clickable(driver, (By.XPATH, "//div[text()='dog.jpg']"))
            assert processImage_option is not None, "未找到processImage_option dog.jpg"
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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
            # 滾動到可見再點擊
            driver.execute_script("arguments[0].scrollIntoView(true);", file_type_dropdown)
            driver.execute_script("arguments[0].click();", file_type_dropdown)
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


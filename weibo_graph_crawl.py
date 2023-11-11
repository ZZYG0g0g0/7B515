import requests
from faker import Faker
from concurrent.futures import ThreadPoolExecutor
import os
import shutil
import imghdr

fake = Faker(locale='zh_CN')

def page_download(page):
    url = "https://m.weibo.cn/api/container/getIndex?"
    ua = fake.user_agent()
    headers = {
        "User-Agent": ua
    }
    param = {
        "jumpfrom": "weibocom",
        "uid": uid,
        "t": "0",
        "containerid": containerid,
        "page": page
    }
    resp = requests.get(url, headers=headers, params=param).json()
    resp_list = resp.get("data").get("cards")
    for i in range(len(resp_list)):
        src_list = resp_list[i].get("mblog").get("pics")
        if src_list is not None:
            with ThreadPoolExecutor(n2) as t2:
                for j in src_list:
                    t2.submit(img_download, j)

    print(str(page) + "页，下载完毕")

def img_download(url):
    ua = fake.user_agent()
    headers = {
        "User-Agent": ua
    }
    src = url.get("pid")
    img_url = "https://tva1.sinaimg.cn/large/" + src

    img_resp = requests.get(img_url, headers=headers, stream=True)  # 使用stream模式下载

    # 确保响应成功
    if img_resp.status_code == 200:
        # 从Content-Type头部获取文件格式
        content_type = img_resp.headers.get('Content-Type')
        # 若Content-Type头部存在，确定扩展名，否则使用imghdr检测
        if content_type:
            extension = content_type.split('/')[-1]  # 从Content-Type中提取文件格式
        else:
            # 使用imghdr来检测图片类型
            img_resp.raw.decode_content = True
            extension = imghdr.what(None, img_resp.raw.read(2048))  # 读取前2048字节来确定图片类型
            img_resp.raw.seek(0)  # 重置文件指针位置

        if not extension:
            extension = 'jpg'  # 默认使用jpg如果无法确定格式

        # 构造文件完整路径
        file_path = os.path.join(fileName, f"{src}.{extension}")

        # 将图片内容写入文件
        with open(file_path, mode="wb") as f:
            for chunk in img_resp.iter_content(8192):  # 使用迭代器避免大文件占用过多内存
                f.write(chunk)
        print("Finish!", src)
    else:
        print(f"Download failed for {src}, status code: {img_resp.status_code}")


def get_containerid(user_id):
    # 微博用户的移动版页面URL
    url = f'https://m.weibo.cn/api/container/getIndex?type=uid&value={user_id}'

    # 发送HTTP GET请求
    response = requests.get(url)
    # 检查响应是否成功
    if response.status_code == 200:
        # 解析JSON数据
        json_data = response.json()
        if json_data.get('ok') and 'tabsInfo' in json_data.get('data', {}):
            tabs = json_data['data']['tabsInfo']['tabs']
            for tab in tabs:
                if tab['tab_type'] == 'weibo':
                    # 返回containerid
                    return tab['containerid']
        else:
            print("数据获取失败或用户id不存在")
    else:
        print("请求失败，状态码：", response.status_code)

if __name__ == '__main__':
    # 开始页数
    page1 = 1
    # 结束页数
    page2 = 10
    url = "https://weibo.com/u/1241148864"

    # 用户id
    uid = url.split('/')[-1]
    containerid = get_containerid(uid)
    # 文件名
    fileName = "image"
    if os.path.exists(fileName):
        shutil.rmtree(fileName)
    if not os.path.exists(fileName):
        os.makedirs(fileName)
    # 线程数
    n1 = 2
    n2 = 4

    with ThreadPoolExecutor(n1) as t1:
        for page in range(page1, page2):
            t1.submit(page_download, page)

    print(str(page1) + "到" + str(page2) + "页，全部下载完毕")
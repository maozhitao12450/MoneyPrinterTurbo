import os
from app.config import config
from aip import AipImageClassify
from loguru import logger

'''
 整理下载的素材，提取一些关键词，用来筛选和描述相关
'''

client = None

# 创建或者获取client
def get_or_create_client():
    global client
    if client: 
        return client
    """ 你的 APPID AK SK """
    APP_ID = config.baidu.get("APP_ID")
    API_KEY = config.baidu.get("API_KEY")
    SECRET_KEY = config.baidu.get("SECRET_KEY")

    if not APP_ID and not API_KEY and not SECRET_KEY:
        logger.warning("not config baidu")
        return None
    else:
        client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)
    return client
# 判断是否启用
def if_baidu_image_generate_enable():
    if get_or_create_client():
        return True
    return False

# 读取图片 
def get_file_content(filePath):
    filePath = os.path.abspath(filePath)
    with open(filePath, 'rb') as fp:
        return fp.read()

def generate_images_result(result):
    results = []
    for item in result.get("result"):
        keyword = item.get("keyword")
        score = item.get("score")
        if score > 0.3: # 阈值
            results.append(keyword)
    return results

import app.utils.utils as utils
def advanced_general_url(url):
    if url == None:
        return None
    # 将url md5 加密
    path = utils.md5(url)
    save_dir = utils.storage_dir("cache_url_key_word")
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if os.path.exists(save_dir + "/" + path): # 如果已经存在，直接返回
        return utils.read_json(save_dir + "/" + path)
    client =  get_or_create_client()
    if not client:
        return None
    logger.info("advanced general url:" + url)
    result = client.advancedGeneralUrl(url)
    result =  generate_images_result(result=result)
    logger.info("advanced general url result:" + str(result))
    utils.write_json(save_dir + "/" + path, result)
    return result

def advanced_general(path):
    client =  get_or_create_client()
    if not client:
        return None
    image = get_file_content(path)
    """ 带参数调用通用物体和场景识别 """
    result = client.advancedGeneral(image)
    return generate_images_result(result=result)

if __name__ == '__main__':
    # client = advanced_general("../resource/pic/petdog.jpg")
    print(client)
    client = advanced_general_url("https://images.pexels.com/videos/6865077/pexels-photo-6865077.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=1200&w=630")
    print(client)


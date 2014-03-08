# Scrapy settings for preciosa project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'preciosa'

SPIDER_MODULES = ['preciosa.spiders']
NEWSPIDER_MODULE = 'preciosa.spiders'
DOWNLOADER_CLIENTCONTEXTFACTORY = 'preciosa.contextfactory.MyClientContextFactory'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'preciosa (+http://www.yourdomain.com)'
DOWNLOAD_DELAY = 1  # 1 seg between each request

import feedparser
from datetime import datetime, timedelta
import pytz
import pandas as pd
import argparse

def get_articles(rss_url, hours):
    # RSSフィードを解析
    feed = feedparser.parse(rss_url)

    # タイムゾーンの設定
    utc = pytz.utc
    local_tz = pytz.timezone('Asia/Tokyo')  # ここを適切なタイムゾーンに変更してください

    # hours時間前の日時を計算（現地のタイムゾーンで）
    thirty_hours_ago_local = datetime.now(local_tz) - timedelta(hours=hours)

    # hours時間以内に更新された記事のみをフィルタリング
    recent_articles = []
    for entry in feed.entries:
        # 公開日時の取得（UTCとして）
        published_time = entry.get("published_parsed", entry.get("updated_parsed", None))
        if published_time:
            published_datetime_utc = utc.localize(datetime(*published_time[:6]))
            # 公開日時を現地のタイムゾーンに変換
            published_datetime_local = published_datetime_utc.astimezone(local_tz)
            if published_datetime_local > thirty_hours_ago_local:
                # タイトル、リンク、および更新日時を追加
                recent_articles.append((entry.title, entry.link, published_datetime_local.strftime('%Y-%m-%d')))

    return recent_articles

if __name__ == "__main__":
    # RSSのURLとタグをテキストファイルから読み込む
    with open("/Users/tsutsuikana/get_rss_feed/rss_urls.txt", "r", encoding="utf-8") as file:
        rss_data = [line.strip().split(",") for line in file]
    
    parser = argparse.ArgumentParser(description='get rss feed.')
    parser.add_argument('--hours', default=26, type=int, help='hours')
    args = parser.parse_args()

    hours = args.hours

    article_tags = []
    # タイトルから判断するタグリスト
    with open('/Users/tsutsuikana/get_rss_feed/tag_list.txt', 'r', encoding='utf-8') as file:
        for line in file:
            # 末尾の改行コードを削除してリストに追加
            article_tags.append(line.rstrip('\n'))

    # 各RSSのURLから24時間以内の更新を取得して辞書に格納し、データフレームに変換する
    output_dict = {}
    tag_list = []
    update_date_list = []
    title_list = []
    link_list = []
    
    for rss_url,tag in rss_data:
        articles = get_articles(rss_url, hours)
        for title, link , update_date in articles:  
            update_date_list.append(update_date)
            title_list.append(title)
            link_list.append(link)   
            article_tag_list = [tag]
            for article_tag in article_tags:
                if (article_tag in title) and (article_tag != tag):
                    tag_appending = f'【{article_tag}】'
                    article_tag_list.append(tag_appending)
            joined_str = ''.join(article_tag_list)
            tag_list.append(joined_str)    

    output_dict['tag'] = tag_list
    output_dict['update_date'] = update_date_list
    output_dict['title'] = title_list
    output_dict['link'] = link_list
    
    df = pd.DataFrame(output_dict)
    df['update_date'] = pd.to_datetime(df['update_date'])

    df.sort_values(by=['tag','update_date'],inplace=True)
    
    # ファイル名を実行時の日付（yyyyMMdd）に設定
    filename = "/Users/tsutsuikana/Desktop/rss_feed/ITNewsPickup" + datetime.now().strftime("%Y%m%d%H%M%S")
    df.to_csv(filename + '.txt',sep=' ', index=False, header=False)


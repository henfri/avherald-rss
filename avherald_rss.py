#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import re
import datetime
import PyRSS2Gen
import hashlib
import parsedatetime.parsedatetime


# Be sure to replace the 'path_to_rss_file' with a working one
# Change the 'opt' for filters
path_to_rss_file = "/some/directory/on/local/hdd/or/server/aviationherald.xml"
opt = '0'


dtcal = parsedatetime.parsedatetime.Calendar()

# Get the source of the home page
opener = urllib2.build_opener()
# add different user agent here
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib2.install_opener(opener)
homepage = 'http://avherald.com/h?list=&opt=' + opt
req = urllib2.urlopen(homepage).read()

# Find all links to the articles
article_links = re.findall('/h\?article=[a-f0-9/]*&opt=\d', req)

# Find link to the next page
next_pages = re.findall('/h\?list=&opt=\d&offset=[0-9]*%[A-Fa-f0-9/]*', req)
next_page = 'http://avherald.com' + next_pages[0]

# open the next page
req_next = urllib2.urlopen(next_page).read()

# Find all links to the articles on next page and add them to the others
article_links = article_links + re.findall('/h\?article=[a-f0-9/]*&opt=\d', req_next)

# Initialize the rss feed
rss = PyRSS2Gen.RSS2(language = "en-US",
                     copyright = "Copyright (c) 2008-2012, by The Aviation Herald",
                     title = "Aviation Herald News",
                     link = "http://www.avherald.com/",
                     description = "Incidents and News in Aviation",
                     lastBuildDate = datetime.datetime.utcnow())


# Do the actual work!
for article_link in article_links:
    article_link = 'http://www.avherald.com' + article_link
    article_raw = urllib2.urlopen(article_link).read()
    
    
    # Title of Article
    title = re.findall('<title>.*?</title>', article_raw)[0][7:-8]
    
    # Date of Article
    date_created_updated_raw = re.findall('<span class="time_avherald">.*?</span>', article_raw)[0][28:-7].replace('  ',' ')

    # Fetch content of Article & do some formatting
    article_content = re.findall('<p align="left"><span class="sitetext">.*?<!--End Article-->', article_raw, re.DOTALL)[0][39:-18].replace('</span></td></tr></table></p>','')
    article_content = article_content.replace('<br/>','<br />')

    # Add the Date in small grey font to the Article
    article = "<font size=-1 color=\"grey\">" + date_created_updated_raw + "<br /><br /></font>" + article_content
    
    # Parse all the dates
    date_created_updated = re.findall(' [JASONFMD][aepuco][bryglnpctv].[0-9]{1,2}[r,s,t,n,d,h]{0,3}.' + '[0-9]{4}.[0-9]{2}:[0-9]{2}Z', date_created_updated_raw)
    
    # Time of Creation
    # date_created = dtcal.parse(date_created_updated[0].strip())
    # Time of Update
    date_updated = dtcal.parse(date_created_updated[1].strip())[0]
    # Year, Month, Day, Hour, Minute, Second, Weekday, Yearday, isDST
    
    # Print the stuff, so it looks cool
    print title
    print date_created_updated_raw + '\n'
    
    # Add Item to the rss feed
    rss.items.append(PyRSS2Gen.RSSItem(
                title = title,
                link = article_link,
                description = article,
                # Sometimes, articles get updated without an url change
                # thats why a checksum, isPermalink = false
                guid = PyRSS2Gen.Guid(hashlib.sha1(date_created_updated_raw).hexdigest(),0),
                # Replace guid with a hash of the article title so that the article is not considered as new if there is an update
                # guid = PyRSS2Gen.Guid(hashlib.sha1(title).hexdigest(),0),
                pubDate = datetime.datetime(date_updated[0],date_updated[1],date_updated[2],date_updated[3],date_updated[4])))

rss.write_xml(open(path_to_rss_file, "w"))

"""
RSS feed catalogue.
"""

FEEDS = [
    # AI Daily (18)
    {"url": "https://thezvi.substack.com/feed", "category": "ai_daily", "domain": "thezvi.substack.com"},
    {"url": "https://importai.substack.com/feed", "category": "ai_daily", "domain": "importai.substack.com"},
    {"url": "https://newsletter.semianalysis.com/feed", "category": "ai_daily", "domain": "newsletter.semianalysis.com"},
    {"url": "https://latent.space/feed", "category": "ai_daily", "domain": "latent.space"},
    {"url": "https://stratechery.com/feed", "category": "ai_daily", "domain": "stratechery.com"},
    {"url": "https://openai.com/news/rss.xml", "category": "ai_daily", "domain": "openai.com"},
    {"url": "https://huggingface.co/blog/feed.xml", "category": "ai_daily", "domain": "huggingface.co"},
    {"url": "https://forbes.kz/feed/", "category": "ai_daily", "domain": "forbes.kz"},
    {"url": "https://digitalbusiness.kz/feed/", "category": "ai_daily", "domain": "digitalbusiness.kz"},
    {"url": "https://kz.kursiv.media/feed/", "category": "ai_daily", "domain": "kz.kursiv.media"},
    {"url": "https://export.arxiv.org/rss/cs.AI", "category": "ai_daily", "domain": "arxiv.org"},
    {"url": "https://news.ycombinator.com/rss", "category": "ai_daily", "domain": "news.ycombinator.com"},
    {"url": "https://techcrunch.com/category/artificial-intelligence/feed/", "category": "ai_daily", "domain": "techcrunch.com"},
    {"url": "https://the-decoder.com/feed/", "category": "ai_daily", "domain": "the-decoder.com"},
    {"url": "https://venturebeat.com/category/ai/feed/", "category": "ai_daily", "domain": "venturebeat.com"},
    {"url": "https://www.forbes.com/innovation/feed/", "category": "ai_daily", "domain": "forbes.com"},
    {"url": "https://research.google/blog/rss/", "category": "ai_daily", "domain": "research.google"},
    {"url": "https://www.hyperdimensional.co/feed", "category": "ai_daily", "domain": "hyperdimensional.co"},

    # Finance Daily (26)
    {"url": "https://adamtooze.substack.com/feed", "category": "finance_daily", "domain": "adamtooze.substack.com"},
    {"url": "https://stratechery.com/feed", "category": "finance_daily", "domain": "stratechery.com"},
    {"url": "https://www.sec.gov/news/pressreleases.rss", "category": "finance_daily", "domain": "sec.gov"},
    {"url": "https://www.federalreserve.gov/feeds/press_all.xml", "category": "finance_daily", "domain": "federalreserve.gov"},
    {"url": "https://www.federalreserve.gov/feeds/speeches.xml", "category": "finance_daily", "domain": "federalreserve.gov"},
    {"url": "https://www.federalreserve.gov/feeds/h15.xml", "category": "finance_daily", "domain": "federalreserve.gov"},
    {"url": "https://www.federalreserve.gov/feeds/datadownload.xml", "category": "finance_daily", "domain": "federalreserve.gov"},
    {"url": "https://www.bls.gov/feed/bls_latest.rss", "category": "finance_daily", "domain": "bls.gov"},
    {"url": "https://www.ecb.europa.eu/rss/press.html", "category": "finance_daily", "domain": "ecb.europa.eu"},
    {"url": "https://www.bankofengland.co.uk/rss/news", "category": "finance_daily", "domain": "bankofengland.co.uk"},
    {"url": "https://www.atlanticcouncil.org/feed/", "category": "finance_daily", "domain": "atlanticcouncil.org"},
    {"url": "https://finance.yahoo.com/rss/topstories", "category": "finance_daily", "domain": "finance.yahoo.com"},
    {"url": "https://forbes.kz/feed/", "category": "finance_daily", "domain": "forbes.kz"},
    {"url": "https://digitalbusiness.kz/feed/", "category": "finance_daily", "domain": "digitalbusiness.kz"},
    {"url": "https://inbusiness.kz/ru/rss/index.rss", "category": "finance_daily", "domain": "inbusiness.kz"},
    {"url": "https://vlast.kz/feed/", "category": "finance_daily", "domain": "vlast.kz"},
    {"url": "https://astanatimes.com/feed/", "category": "finance_daily", "domain": "astanatimes.com"},
    {"url": "https://kz.kursiv.media/feed/", "category": "finance_daily", "domain": "kz.kursiv.media"},
    {"url": "https://kapital.kz/feed", "category": "finance_daily", "domain": "kapital.kz"},
    {"url": "https://profit.kz/rss", "category": "finance_daily", "domain": "profit.kz"},
    {"url": "https://www.bbc.co.uk/news/rss.xml", "category": "finance_daily", "domain": "bbc.co.uk"},
    {"url": "https://www.aljazeera.com/xml/rss/all.xml", "category": "finance_daily", "domain": "aljazeera.com"},
    {"url": "https://www.netinterest.co/feed", "category": "finance_daily", "domain": "netinterest.co"},
    {"url": "https://vc.ru/rss", "category": "finance_daily", "domain": "vc.ru"},
    {"url": "https://en.thebell.io/rss", "category": "finance_daily", "domain": "en.thebell.io"},
    {"url": "https://bankir.ru/rss", "category": "finance_daily", "domain": "bankir.ru"},

    # FinTech & Banking (24)
    {"url": "https://fintechbusinessweekly.substack.com/feed", "category": "fintech_banking", "domain": "fintechbusinessweekly.substack.com"},
    {"url": "https://newsletter.fintechtakes.com/feed", "category": "fintech_banking", "domain": "newsletter.fintechtakes.com"},
    {"url": "https://feeds.thefinanser.com/feed", "category": "fintech_banking", "domain": "thefinanser.com"},
    {"url": "https://www.bankingdive.com/feeds/news/", "category": "fintech_banking", "domain": "bankingdive.com"},
    {"url": "https://www.finextra.com/rss/headlines.aspx", "category": "fintech_banking", "domain": "finextra.com"},
    {"url": "https://www.americanbanker.com/feed?rss=true", "category": "fintech_banking", "domain": "americanbanker.com"},
    {"url": "https://thefintechtimes.com/feed/", "category": "fintech_banking", "domain": "thefintechtimes.com"},
    {"url": "https://www.fintechfutures.com/feed/", "category": "fintech_banking", "domain": "fintechfutures.com"},
    {"url": "https://www.pymnts.com/feed/", "category": "fintech_banking", "domain": "pymnts.com"},
    {"url": "https://fintechnews.sg/feed/", "category": "fintech_banking", "domain": "fintechnews.sg"},
    {"url": "https://www.crnrstone.com/feed", "category": "fintech_banking", "domain": "crnrstone.com"},
    {"url": "https://frankmedia.ru/feed", "category": "fintech_banking", "domain": "frankmedia.ru"},
    {"url": "https://www.banki.ru/xml/news.rss", "category": "fintech_banking", "domain": "banki.ru"},
    {"url": "https://www.federalreserve.gov/feeds/press_all.xml", "category": "fintech_banking", "domain": "federalreserve.gov"},
    {"url": "https://www.sec.gov/news/pressreleases.rss", "category": "fintech_banking", "domain": "sec.gov"},
    {"url": "https://www.ecb.europa.eu/rss/press.html", "category": "fintech_banking", "domain": "ecb.europa.eu"},
    {"url": "https://digitalbusiness.kz/feed/", "category": "fintech_banking", "domain": "digitalbusiness.kz"},
    {"url": "https://inbusiness.kz/ru/rss/index.rss", "category": "fintech_banking", "domain": "inbusiness.kz"},
    {"url": "https://forbes.kz/feed/", "category": "fintech_banking", "domain": "forbes.kz"},
    {"url": "https://kz.kursiv.media/feed/", "category": "fintech_banking", "domain": "kz.kursiv.media"},
    {"url": "https://kapital.kz/feed", "category": "fintech_banking", "domain": "kapital.kz"},
    {"url": "https://www.netinterest.co/feed", "category": "fintech_banking", "domain": "netinterest.co"},
    {"url": "https://vc.ru/rss", "category": "fintech_banking", "domain": "vc.ru"},
    {"url": "https://en.thebell.io/rss", "category": "fintech_banking", "domain": "en.thebell.io"},
    {"url": "https://bankir.ru/rss", "category": "fintech_banking", "domain": "bankir.ru"},

    # Cybersec & Compliance (22)
    {"url": "https://krebsonsecurity.com/feed", "category": "cybersec_compliance", "domain": "krebsonsecurity.com"},
    {"url": "https://www.bleepingcomputer.com/feed/", "category": "cybersec_compliance", "domain": "bleepingcomputer.com"},
    {"url": "https://therecord.media/feed", "category": "cybersec_compliance", "domain": "therecord.media"},
    {"url": "https://thehackernews.com/feeds/posts/default", "category": "cybersec_compliance", "domain": "thehackernews.com"},
    {"url": "https://www.darkreading.com/rss.xml", "category": "cybersec_compliance", "domain": "darkreading.com"},
    {"url": "https://news.risky.biz/rss", "category": "cybersec_compliance", "domain": "risky.biz"},
    {"url": "https://danielmiessler.com/feed.rss", "category": "cybersec_compliance", "domain": "danielmiessler.com"},
    {"url": "https://www.cisa.gov/cybersecurity-advisories/all.xml", "category": "cybersec_compliance", "domain": "cisa.gov"},
    {"url": "https://www.cisa.gov/news.xml", "category": "cybersec_compliance", "domain": "cisa.gov"},
    {"url": "https://www.sec.gov/news/pressreleases.rss", "category": "cybersec_compliance", "domain": "sec.gov"},
    {"url": "https://www.ftc.gov/feeds/press-release.xml", "category": "cybersec_compliance", "domain": "ftc.gov"},
    {"url": "https://www.nist.gov/news-events/news/rss.xml", "category": "cybersec_compliance", "domain": "nist.gov"},
    {"url": "https://www.atlanticcouncil.org/feed/", "category": "cybersec_compliance", "domain": "atlanticcouncil.org"},
    {"url": "https://inbusiness.kz/ru/rss/index.rss", "category": "cybersec_compliance", "domain": "inbusiness.kz"},
    {"url": "https://www.schneier.com/feed/atom/", "category": "cybersec_compliance", "domain": "schneier.com"},
    {"url": "https://isc.sans.edu/rssfeed.xml", "category": "cybersec_compliance", "domain": "isc.sans.edu"},
    {"url": "https://www.sans.org/blog/feed.xml", "category": "cybersec_compliance", "domain": "sans.org"},
    {"url": "https://securelist.com/feed/", "category": "cybersec_compliance", "domain": "securelist.com"},
    {"url": "https://habr.com/ru/rss/all/", "category": "cybersec_compliance", "domain": "habr.com"},
    {"url": "https://techcrunch.com/category/security/feed/", "category": "cybersec_compliance", "domain": "techcrunch.com"},
    {"url": "https://googleprojectzero.blogspot.com/feeds/posts/default", "category": "cybersec_compliance", "domain": "googleprojectzero.blogspot.com"},
    {"url": "https://security.googleblog.com/feeds/posts/default", "category": "cybersec_compliance", "domain": "security.googleblog.com"},

    # IT Leadership (15)
    {"url": "https://newsletter.pragmaticengineer.com/feed", "category": "it_leadership", "domain": "newsletter.pragmaticengineer.com"},
    {"url": "https://refactoring.fm/feed", "category": "it_leadership", "domain": "refactoring.fm"},
    {"url": "https://newsletter.eng-leadership.com/feed", "category": "it_leadership", "domain": "newsletter.eng-leadership.com"},
    {"url": "https://read.highgrowthengineer.com/feed", "category": "it_leadership", "domain": "read.highgrowthengineer.com"},
    {"url": "https://charity.wtf/feed", "category": "it_leadership", "domain": "charity.wtf"},
    {"url": "https://stratechery.com/feed", "category": "it_leadership", "domain": "stratechery.com"},
    {"url": "https://thenewstack.io/feed/", "category": "it_leadership", "domain": "thenewstack.io"},
    {"url": "https://github.blog/feed/", "category": "it_leadership", "domain": "github.blog"},
    {"url": "https://blog.cloudflare.com/rss/", "category": "it_leadership", "domain": "blog.cloudflare.com"},
    {"url": "https://www.cio.com/feed/", "category": "it_leadership", "domain": "cio.com"},
    {"url": "https://www.ciodive.com/feeds/news/", "category": "it_leadership", "domain": "ciodive.com"},
    {"url": "https://www.sequoiacap.com/feed/", "category": "it_leadership", "domain": "sequoiacap.com"},
    {"url": "https://news.ycombinator.com/rss", "category": "it_leadership", "domain": "news.ycombinator.com"},
    {"url": "https://www.allthingsdistributed.com/atom.xml", "category": "it_leadership", "domain": "allthingsdistributed.com"},
    {"url": "https://habr.com/ru/rss/all/", "category": "it_leadership", "domain": "habr.com"},
]


def unique_feed_urls():
    seen = set()
    out = []
    for f in FEEDS:
        if f["url"] in seen:
            continue
        seen.add(f["url"])
        out.append(f["url"])
    return out


def categories_for_url(url):
    return [(f["category"], f["domain"]) for f in FEEDS if f["url"] == url]

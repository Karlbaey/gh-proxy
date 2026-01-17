# -*- coding: utf-8 -*-
import re

import requests
from flask import Flask, Response, redirect, request
from requests.exceptions import (
    ChunkedEncodingError,
    ContentDecodingError,
    ConnectionError,
    StreamConsumedError,
)
from requests.utils import (
    stream_decode_response_unicode,
    iter_slices,
    CaseInsensitiveDict,
)
from urllib3.exceptions import DecodeError, ReadTimeoutError, ProtocolError
from urllib.parse import quote

# config
# 分支文件使用jsDelivr镜像的开关，0为关闭，默认关闭
jsdelivr = 0
size_limit = (
    1024 * 1024 * 20
)  # 允许的文件大小，默认999GB，相当于无限制了 https://github.com/hunshcn/gh-proxy/issues/8

"""
  先生效白名单再匹配黑名单，pass_list匹配到的会直接302到jsdelivr而忽略设置
  生效顺序 白->黑->pass，可以前往https://github.com/hunshcn/gh-proxy/issues/41 查看示例
  每个规则一行，可以封禁某个用户的所有仓库，也可以封禁某个用户的特定仓库，下方用黑名单示例，白名单同理
  user1 # 封禁user1的所有仓库
  user1/repo1 # 封禁user1的repo1
  */repo1 # 封禁所有叫做repo1的仓库
"""
white_list = """
"""
black_list = """
cirosantilli
wumaoland
codin-stuffs
cheezcharmer
gege-circle
zhaohmng-outlook-com
zaohmeing
Daravai1234
candice531033938
jk-ice-cream
jk-ice-cream-250
sky8964
pxvr-official
zpc1314521
jjzhang166
panbinibn
programthink
hello-world-1989
b0LBwZ7r5HOeh6CBMuQIhVu3-s-random-fork
thethetpvmy
wwwswitch520cc
shotoanqrob
sitempeanhkkwg
fukeluo
1206256980
curees
yuoppo
Createree
vghl
wholedata
dunjian
mksshare
abshare
tpxdat
jhdyg
changfengqj
Dujltqzv
xmq1024
golade
kdjfhd
dkjhy
junsolg
dkjiiu
faithhow
yamtioy
zugzuc
lusvont
kenyatas
koeheu
juttama
duspub
wuqdid
visxud
suyfic
qokkod
roepuo
purfob
gitprocode
ynwynw
hanguodianying
hgyw
69sm
urlapp
Augensternhx
urlweb
fuliso
nishjd
36dshipin
hapump
zhguoxmw
KoreanMovies
hanjutv
mamadepengyou
mamatouyunmuxuan
erzideqizi
wodeqizidejiejie
xiaoyizidemeng
qingyuzongheng
jiangnanerxi
hanguobiaomei
djhgy
XXOOBY
baoyu1024
kk234kkkk
15923-ORIX
wutaed
webzhibo
apptuijian
follow666
yu90892
aconteet
getmal
itxinfei
mingtiana
midoushipin
paofushipin
yinghanshipin
GTVapp
huangyouquan
devlookme
audwq
jhdgy
di6gandh
shuangyuzhibo
lvchazhibo
xiaolanshipin
bofangqi
yingtaoshipin
xiangfeizhibo
lvchaApp
luoshenzhibo
yaojizhibo
mudanzhibo
aiaizhibo
gaochaoqwe
jiolde
lsdhw
kanavdaohang
harnh
kuadaner
wapquan
laoyeer
reteres
haoersn
zhengjianzhong0107
huaaweiCode
jianjian00001
m2ak-dev
yyzwz
froginwe11
luanmenglei
xijinping0
cyqqq
qldaisd
lTbgykio
yao270161651
jt0008jt0008
15625103741
sky1234566778
chfucao
chifuyidaocao
updrmeltm
alice548
yazm000
cpnorg
tffygbu
Liberty-China
1989CCP
liulihaocai
RevolutionaryCommitteeCPC
LeiyanLu
webdao
GC4WP
tu01
ziliao1
zzs70
ff2017
guitu2017
tu2017
wm001
wnel2017
dunhlino
nelaliox
jianjian3219
giteecode
666bears
wang-buer
id681ilyg316
uhjid
usdui
uhskl
uyjks
uhskldf
itgsi5
uifskv
uhgask
igfkld
udsjd
ufodk
uigsjt
ighfrs
haivs
idrkkld
yuisju
uldydj
uyuek
tydfj
uuedif
ykwsw3
uigsi7
tyiis
ykeik
ukvdj
uyikl
ufzekg
yiksure
rhksgz
rthls
rhjaw
rehlxs
thzsgt
tdidst
eglct
tjkdyu
tjlks
tjjds
rllfs
rhkstd
yjscdr
servisee
ufsjzf
bvnbvnfgd
duliyingshi
calendi
mayeobey
QQMusic-Jay-Chou
boylovecomic
bt9527
FarmerChina
Waymon102092
baofx
biehd
moonpas
lyqilo
liliqh
hourv
xinfue
jijidianying
YuyanCai
jtdh
isdkxr
yhildyu
ykldyld
igsigk
uidekj
iufskw
udsjhf
tjkdx
rtkist
tjlsyh
euhf
rjzsht
rhkdzu
ehkkld
xzgfsw
iofgd
yufdk
ujkdub
iofgdsk
dyghikg
ugdskf
ifwaih
oigsiu
yjksku
yfdkkrf
thjsqd
yjsyhf
ydjsu6
igseyf
ujudy8
tykde
ykmdi8
yklzrf
uijdkd
yjkshc
tkajc
ykdzs
jklsx
ejldux
ifxspo
ogsvtf
ifdeu
yudfdi
ofssj
igegkx
ugfkd
ugdsk
udskts
yjlkdss
fkdryl
rtuyjsr
tus56f
yjdsd
yuet6h
ugtw
tlkxt
yesrs
ykkds
yjksu
yhyshs
xdzfby
yujzdh
znfl
kjiud
shijuezhishi
hy1980boy
ww0304
ZXCASD854
zfpdh
batiyadh
yinsedh
yyfxz
bllpooe
joodfer
qdmang
chaenet
mzsyv
kzhaoes
clnnews
kendnes
hongnews
luokez
li721-LY
itunsr
cctnews
htmle
xmmj2
younownews
445435213
seseClub
enewse
wsnewse
qsnews
soasmoughroy
adminewhat
wsermusic
molingfer
zhihues
95movies
99fuli
qnewse
tareres
hukioip
Hochoclate713
ervnme
greenleaf8888
93-days
doubanm
xhydh
fvckslvt
MDCM-FB
b08240
m3u8-ekvod
huan768468
SweeOBC
ningmengsuan7788
supperqb
idskjs
ifsird
gklksr
ifsjxr
ifskxt
ghjklsd
udsskd
tgsjk
ihgsk
ujsjk
ijhdf
fghhgks
udfae4
jujwdj
ydsdk
uyfgsj
ykkxrd
branono
hytcd
kjiuo
SaolApp
lourv
uisdlk
hutuhai
dengminna
whmnoe4j
txy9704
ufsjl
udsks
uifsjk
ygsaj
udsts
yurdek
ghklsr
ifsnx
ufskd
yujst6
ifsurjn
saoyagma
yusyrdk
uijhgr
geeeeeeeek
gfjklk
uiskv
ccccsp
rrrsp
udjxs
qiezisp
egklkd
t6korf
line915577
haijv
huaxinzhibo
haijiaofabuye
haijiaoshequ
HaijiaoCommunity
haijiao-app
fulibaike
lurmarp
entvasa
gotwib
hghkiiy121
gubcem
uijssu
yjhuk
yklsd
haijiaoWeb
winston779
tyukkst
ujsnmc
ygssk
igdkdy
qiezishiping
kjuhd
xiaogongzhuAPP
babyzhibo
yaojingzhibo
balizhibo
jiuaizhibo
liuyuezhibo
69live
asidw
kuaimaoVIP
siguaha
mizhizhibo
lihzd
caomeizhibo
36DAPP
luolisheApp
69zhibo
jiejiezhibo
k8japan
buyaoshan
dk111222
fanbaovpn
HGcrowntiyu
196tiyu
parryno
boyiscode
moonews
kim1528
tjqJ62cESiHPj6DdR6vXDAcPp
code-help-tutor
turbocanary
Ifem2BXvz4N4gh1gGn0bkR3Lp
R7w726fYrfritM7zPJCO
"""
pass_list = """
"""

HOST = "127.0.0.1"  # 监听地址，建议监听本地然后由web服务器反代
PORT = 80  # 监听端口
ASSET_URL = "https://hunshcn.github.io/gh-proxy"  # 主页

white_list = [
    tuple([x.replace(" ", "") for x in i.split("/")])
    for i in white_list.split("\n")
    if i
]
black_list = [
    tuple([x.replace(" ", "") for x in i.split("/")])
    for i in black_list.split("\n")
    if i
]
pass_list = [
    tuple([x.replace(" ", "") for x in i.split("/")])
    for i in pass_list.split("\n")
    if i
]
app = Flask(__name__)
CHUNK_SIZE = 1024 * 10
index_html = requests.get(ASSET_URL, timeout=10).text
icon_r = requests.get(ASSET_URL + "/favicon.ico", timeout=10).content
exp1 = re.compile(
    r"^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:releases|archive)/.*$"
)
exp2 = re.compile(
    r"^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:blob|raw)/.*$"
)
exp3 = re.compile(
    r"^(?:https?://)?github\.com/(?P<author>.+?)/(?P<repo>.+?)/(?:info|git-).*$"
)
exp4 = re.compile(
    r"^(?:https?://)?raw\.(?:githubusercontent|github)\.com/(?P<author>.+?)/(?P<repo>.+?)/.+?/.+$"
)
exp5 = re.compile(
    r"^(?:https?://)?gist\.(?:githubusercontent|github)\.com/(?P<author>.+?)/.+?/.+$"
)

requests.sessions.default_headers = lambda: CaseInsensitiveDict()


@app.route("/")
def index():
    if "q" in request.args:
        return redirect("/" + request.args.get("q"))  # type: ignore
    return index_html


@app.route("/favicon.ico")
def icon():
    return Response(icon_r, content_type="image/vnd.microsoft.icon")


def iter_content(self, chunk_size=1, decode_unicode=False):
    """rewrite requests function, set decode_content with False"""

    def generate():
        # Special case for urllib3.
        if hasattr(self.raw, "stream"):
            try:
                for chunk in self.raw.stream(chunk_size, decode_content=False):
                    yield chunk
            except ProtocolError as e:
                raise ChunkedEncodingError(e)
            except DecodeError as e:
                raise ContentDecodingError(e)
            except ReadTimeoutError as e:
                raise ConnectionError(e)
        else:
            # Standard file-like object.
            while True:
                chunk = self.raw.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        self._content_consumed = True

    if self._content_consumed and isinstance(self._content, bool):
        raise StreamConsumedError()
    elif chunk_size is not None and not isinstance(chunk_size, int):
        raise TypeError(
            "chunk_size must be an int, it is instead a %s." % type(chunk_size)
        )
    # simulate reading small chunks of the content
    reused_chunks = iter_slices(self._content, chunk_size)

    stream_chunks = generate()

    chunks = reused_chunks if self._content_consumed else stream_chunks

    if decode_unicode:
        chunks = stream_decode_response_unicode(chunks, self)

    return chunks


def check_url(u):
    for exp in (exp1, exp2, exp3, exp4, exp5):
        m = exp.match(u)
        if m:
            return m
    return False


@app.route("/<path:u>", methods=["GET", "POST"])
def handler(u):
    u = u if u.startswith("http") else "https://" + u
    if u.rfind("://", 3, 9) == -1:
        u = u.replace("s:/", "s://", 1)  # uwsgi会将//传递为/
    pass_by = False
    m = check_url(u)
    if m:
        m = tuple(m.groups())
        if white_list:
            for i in white_list:
                if m[: len(i)] == i or i[0] == "*" and len(m) == 2 and m[1] == i[1]:
                    break
            else:
                return Response("Forbidden by white list.", status=403)
        for i in black_list:
            if m[: len(i)] == i or i[0] == "*" and len(m) == 2 and m[1] == i[1]:
                return Response("Forbidden by black list.", status=403)
        for i in pass_list:
            if m[: len(i)] == i or i[0] == "*" and len(m) == 2 and m[1] == i[1]:
                pass_by = True
                break
    else:
        return Response("Invalid input.", status=403)

    if (jsdelivr or pass_by) and exp2.match(u):
        u = u.replace("/blob/", "@", 1).replace("github.com", "cdn.jsdelivr.net/gh", 1)
        return redirect(u)
    elif (jsdelivr or pass_by) and exp4.match(u):
        u = re.sub(r"(\.com/.*?/.+?)/(.+?/)", r"\1@\2", u, 1)
        _u = u.replace("raw.githubusercontent.com", "cdn.jsdelivr.net/gh", 1)
        u = u.replace("raw.github.com", "cdn.jsdelivr.net/gh", 1) if _u == u else _u
        return redirect(u)
    else:
        if exp2.match(u):
            u = u.replace("/blob/", "/raw/", 1)
        if pass_by:
            url = u + request.url.replace(request.base_url, "", 1)
            if url.startswith("https:/") and not url.startswith("https://"):
                url = "https://" + url[7:]
            return redirect(url)
        u = quote(u, safe="/:")
        return proxy(u)


def proxy(u, allow_redirects=False):
    headers = {}
    r_headers = dict(request.headers)
    if "Host" in r_headers:
        r_headers.pop("Host")
    try:
        url = u + request.url.replace(request.base_url, "", 1)
        if url.startswith("https:/") and not url.startswith("https://"):
            url = "https://" + url[7:]
        r = requests.request(
            method=request.method,
            url=url,
            data=request.data,
            headers=r_headers,
            stream=True,
            allow_redirects=allow_redirects,
        )
        headers = dict(r.headers)

        if (
            "Content-length" in r.headers
            and int(r.headers["Content-length"]) > size_limit
        ):
            return redirect(u + request.url.replace(request.base_url, "", 1))

        def generate():
            for chunk in iter_content(r, chunk_size=CHUNK_SIZE):
                yield chunk

        if "Location" in r.headers:
            _location = r.headers.get("Location")
            if check_url(_location):
                headers["Location"] = "/" + _location  # type: ignore
            else:
                return proxy(_location, True)

        return Response(generate(), headers=headers, status=r.status_code)  # type: ignore
    except Exception as e:
        headers["content-type"] = "text/html; charset=UTF-8"
        return Response("server error " + str(e), status=500, headers=headers)


app.debug = True
if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

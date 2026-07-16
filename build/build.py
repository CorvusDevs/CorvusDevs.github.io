# -*- coding: utf-8 -*-
import re
TEMPLATE = "build/index.src.html"; OUT = "index.html"
c = open(TEMPLATE, encoding="utf-8").read()

head_meta = c[:c.index("    <style>")]
_lw = c.index('<div class="lang-wrap"')
langwrap = c[_lw:c.index("</div>\n            </div>", _lw)+len("</div>\n            </div>")]
# drop unsupported Traditional Chinese (catalog has no zh-Hant) + self-host flag SVGs (no flagcdn.com dependency)
langwrap = re.sub(r'\s*<button data-lang="zh-Hant">.*?</button>', '', langwrap, flags=re.S)
langwrap = langwrap.replace("https://flagcdn.com/", "flags/")
assert 'flagcdn.com' not in langwrap and 'zh-Hant' not in langwrap, "langwrap transform failed"
values_block = c[c.index("    <!-- Values -->"):c.index("</footer>")+len("</footer>")]
scripts = c[c.index("</footer>")+len("</footer>"):]  # reveal/store JS + catalog + walker + </body></html>

# ---- 6 new i18n keys, translated to match the catalog's existing terms ----
NEW = {
 "en":'hero_eyebrow:"Independent Mac & Safari studio", sec_featured:"Featured", sec_featured_note:"The five we\'d install first", sec_collection:"The Collection", f_all:"All", f_free:"Free",',
 "es":'hero_eyebrow:"Estudio independiente de Mac y Safari", sec_featured:"Destacados", sec_featured_note:"Los cinco que instalaríamos primero", sec_collection:"La colección", f_all:"Todos", f_free:"Gratis",',
 "fr":'hero_eyebrow:"Studio indépendant Mac et Safari", sec_featured:"En vedette", sec_featured_note:"Les cinq à installer en premier", sec_collection:"La collection", f_all:"Tous", f_free:"Gratuit",',
 "de":'hero_eyebrow:"Unabhängiges Mac- und Safari-Studio", sec_featured:"Empfohlen", sec_featured_note:"Die fünf, die wir zuerst installieren würden", sec_collection:"Die Sammlung", f_all:"Alle", f_free:"Kostenlos",',
 "pt":'hero_eyebrow:"Estúdio independente de Mac e Safari", sec_featured:"Destaques", sec_featured_note:"Os cinco que instalaríamos primeiro", sec_collection:"A coleção", f_all:"Todos", f_free:"Grátis",',
 "it":'hero_eyebrow:"Studio indipendente Mac e Safari", sec_featured:"In evidenza", sec_featured_note:"I cinque da installare per primi", sec_collection:"La raccolta", f_all:"Tutti", f_free:"Gratis",',
 "ja":'hero_eyebrow:"Mac と Safari のインディースタジオ", sec_featured:"注目", sec_featured_note:"まず入れておきたい5つ", sec_collection:"コレクション", f_all:"すべて", f_free:"無料",',
 "zh":'hero_eyebrow:"独立的 Mac 与 Safari 工作室", sec_featured:"精选", sec_featured_note:"我们会最先安装的五个", sec_collection:"全部作品", f_all:"全部", f_free:"免费",',
 "ko":'hero_eyebrow:"독립 Mac 및 Safari 스튜디오", sec_featured:"추천", sec_featured_note:"가장 먼저 설치할 다섯 가지", sec_collection:"컴렉션", f_all:"전체", f_free:"무료",',
 "ru":'hero_eyebrow:"Независимая студия для Mac и Safari", sec_featured:"Избранное", sec_featured_note:"Пять, которые мы бы установили первыми", sec_collection:"Коллекция", f_all:"Все", f_free:"Бесплатно",',
}
NEW.update({
 "ar":'hero_eyebrow:"استوديو مستقل لتطبيقات Mac و Safari", sec_featured:"مميّزة", sec_featured_note:"الخمسة التي نثبّتها أولاً", sec_collection:"المجموعة", f_all:"الكل", f_free:"مجاني",',
 "nl":'hero_eyebrow:"Onafhankelijke Mac- en Safari-studio", sec_featured:"Uitgelicht", sec_featured_note:"De vijf die we als eerste zouden installeren", sec_collection:"De collectie", f_all:"Alle", f_free:"Gratis",',
 "tr":'hero_eyebrow:"Bağımsız Mac ve Safari stüdyosu", sec_featured:"Öne çıkanlar", sec_featured_note:"İlk kuracağımız beş uygulama", sec_collection:"Koleksiyon", f_all:"Tümü", f_free:"Ücretsiz",',
 "pl":'hero_eyebrow:"Niezależne studio Mac i Safari", sec_featured:"Polecane", sec_featured_note:"Pięć, które zainstalowalibyśmy najpierw", sec_collection:"Kolekcja", f_all:"Wszystkie", f_free:"Za darmo",',
 "sv":'hero_eyebrow:"Oberoende Mac- och Safari-studio", sec_featured:"Utvalda", sec_featured_note:"De fem vi skulle installera först", sec_collection:"Samlingen", f_all:"Alla", f_free:"Gratis",',
 "hi":'hero_eyebrow:"स्वतंत्र Mac और Safari स्टूडियो", sec_featured:"विशेष", sec_featured_note:"पाँच जिन्हें हम पहले इंस्टॉल करेंगे", sec_collection:"संग्रह", f_all:"सभी", f_free:"मुफ़्त",',
 "id":'hero_eyebrow:"Studio Mac & Safari independen", sec_featured:"Unggulan", sec_featured_note:"Lima yang akan kami pasang lebih dulu", sec_collection:"Koleksi", f_all:"Semua", f_free:"Gratis",',
 "th":'hero_eyebrow:"สตูดิโอ Mac และ Safari อิสระ", sec_featured:"แนะนำ", sec_featured_note:"ห้าแอปที่เราจะติดตั้งก่อน", sec_collection:"คอลเลกชัน", f_all:"ทั้งหมด", f_free:"ฟรี",',
 "vi":'hero_eyebrow:"Studio Mac & Safari độc lập", sec_featured:"Nổi bật", sec_featured_note:"Năm ứng dụng chúng tôi cài trước tiên", sec_collection:"Bộ sưu tập", f_all:"Tất cả", f_free:"Miễn phí",',
})
COLL={"en":"All our apps","es":"Todas nuestras apps","fr":"Toutes nos apps","de":"Alle unsere Apps",
 "pt":"Todos os nossos apps","it":"Tutte le nostre app","ja":"すべてのアプリ","zh":"全部应用",
 "ko":"모든 앱","ru":"Все наши приложения","ar":"كل تطبيقاتنا","nl":"Al onze apps",
 "tr":"Tüm uygulamalarımız","pl":"Wszystkie nasze aplikacje","sv":"Alla våra appar",
 "hi":"हमारे सभी ऐप्स","id":"Semua aplikasi kami","th":"แอปทั้งหมดของเรา","vi":"Tất cả ứng dụng của chúng tôi"}
for lang in NEW:
    NEW[lang]=re.sub(r'sec_collection:"[^"]*"','sec_collection:"'+COLL[lang]+'"',NEW[lang])
NOTE={"en":"Where we'd start","es":"Por dónde empezaríamos","fr":"Par où commencer","de":"Womit wir anfangen würden",
 "pt":"Por onde começaríamos","it":"Da dove partiremmo","ja":"まずはここから","zh":"从这里开始",
 "ko":"여기서 시작하세요","ru":"С чего бы мы начали","ar":"من أين نبدأ","nl":"Waar wij zouden beginnen",
 "tr":"Nereden başlardık","pl":"Od czego byśmy zaczęli","sv":"Här skulle vi börja",
 "hi":"हम यहाँ से शुरू करेंगे","id":"Dari sini kami mulai","th":"เริ่มจากตรงนี้","vi":"Nơi chúng tôi bắt đầu"}
for lang in NEW:
    NEW[lang]=re.sub(r'sec_featured_note:"[^"]*"','sec_featured_note:"'+NOTE[lang]+'"',NEW[lang])
for lang, keys in NEW.items():
    scripts, _n = re.subn(r'(\n        '+lang+r': \{\n)', r'\1            '+keys.replace('\\','\\\\')+'\n', scripts, count=1)
    assert _n==1, "inject failed for "+lang
# additional short UI strings (search, new/updated badges, request-an-app CTA)
EXTRA={
 "en":'f_search:"Search apps", badge_new:"New", badge_upd:"Updated", soon_req:"Have an app idea?", soon_reqlink:"Request an app",',
 "es":'f_search:"Buscar apps", badge_new:"Nuevo", badge_upd:"Actualizado", soon_req:"¿Tienes una idea de app?", soon_reqlink:"Solicitar una app",',
 "fr":'f_search:"Rechercher", badge_new:"Nouveau", badge_upd:"Mis à jour", soon_req:"Une idée d\'app ?", soon_reqlink:"Proposer une app",',
 "de":'f_search:"Apps suchen", badge_new:"Neu", badge_upd:"Aktualisiert", soon_req:"Eine App-Idee?", soon_reqlink:"App vorschlagen",',
 "pt":'f_search:"Buscar apps", badge_new:"Novo", badge_upd:"Atualizado", soon_req:"Tem uma ideia de app?", soon_reqlink:"Solicitar um app",',
 "it":'f_search:"Cerca app", badge_new:"Nuovo", badge_upd:"Aggiornato", soon_req:"Hai un\'idea per un\'app?", soon_reqlink:"Richiedi un\'app",',
 "ja":'f_search:"アプリを検索", badge_new:"新着", badge_upd:"更新", soon_req:"アプリのアイデアは?", soon_reqlink:"アプリをリクエスト",',
 "zh":'f_search:"搜索应用", badge_new:"新", badge_upd:"已更新", soon_req:"有应用点子？", soon_reqlink:"请求一个应用",',
 "ko":'f_search:"앱 검색", badge_new:"신규", badge_upd:"업데이트", soon_req:"앱 아이디어가 있나요?", soon_reqlink:"앱 요청하기",',
 "ru":'f_search:"Поиск приложений", badge_new:"Новое", badge_upd:"Обновлено", soon_req:"Есть идея приложения?", soon_reqlink:"Предложить приложение",',
 "ar":'f_search:"ابحث عن التطبيقات", badge_new:"جديد", badge_upd:"محدّث", soon_req:"لديك فكرة تطبيق؟", soon_reqlink:"اطلب تطبيقًا",',
 "nl":'f_search:"Apps zoeken", badge_new:"Nieuw", badge_upd:"Bijgewerkt", soon_req:"Heb je een app-idee?", soon_reqlink:"Vraag een app aan",',
 "tr":'f_search:"Uygulama ara", badge_new:"Yeni", badge_upd:"Güncellendi", soon_req:"Uygulama fikrin mi var?", soon_reqlink:"Uygulama iste",',
 "pl":'f_search:"Szukaj aplikacji", badge_new:"Nowość", badge_upd:"Zaktualizowano", soon_req:"Masz pomysł na aplikację?", soon_reqlink:"Zaproponuj aplikację",',
 "sv":'f_search:"Sök appar", badge_new:"Nytt", badge_upd:"Uppdaterad", soon_req:"Har du en app-idé?", soon_reqlink:"Föreslå en app",',
 "hi":'f_search:"ऐप्स खोजें", badge_new:"नया", badge_upd:"अपडेट किया गया", soon_req:"कोई ऐप आइडिया है?", soon_reqlink:"ऐप का अनुरोध करें",',
 "id":'f_search:"Cari aplikasi", badge_new:"Baru", badge_upd:"Diperbarui", soon_req:"Punya ide aplikasi?", soon_reqlink:"Minta aplikasi",',
 "th":'f_search:"ค้นหาแอป", badge_new:"ใหม่", badge_upd:"อัปเดตแล้ว", soon_req:"มีไอเดียแอปไหม?", soon_reqlink:"ขอแอป",',
 "vi":'f_search:"Tìm ứng dụng", badge_new:"Mới", badge_upd:"Đã cập nhật", soon_req:"Có ý tưởng ứng dụng?", soon_reqlink:"Yêu cầu ứng dụng",',
}
for lang, keys in EXTRA.items():
    scripts, _n = re.subn(r'(\n        '+lang+r': \{\n)', r'\1            '+keys+'\n', scripts, count=1)
    assert _n==1, "extra inject failed for "+lang
# two more "How we build software" principles (v7 pay-once, v8 actively-maintained)
V78={
 "en":'v7_t:"Pay once, keep it", v7_d:"One-time purchases and free tools. No subscriptions for the essentials.", v8_t:"Actively maintained", v8_d:"Regular updates and quick fixes. We use these apps every day too.",',
 "es":'v7_t:"Paga una vez, es tuyo", v7_d:"Compras únicas y herramientas gratis. Sin suscripciones para lo esencial.", v8_t:"Mantenimiento activo", v8_d:"Actualizaciones frecuentes y correcciones rápidas. Nosotros también las usamos a diario.",',
 "fr":'v7_t:"Payez une fois", v7_d:"Achats uniques et outils gratuits. Pas d\'abonnement pour l\'essentiel.", v8_t:"Activement maintenu", v8_d:"Mises à jour régulières et corrections rapides. Nous utilisons ces apps chaque jour.",',
 "de":'v7_t:"Einmal zahlen", v7_d:"Einmalkäufe und kostenlose Tools. Keine Abos für das Wesentliche.", v8_t:"Aktiv gepflegt", v8_d:"Regelmäßige Updates und schnelle Fixes. Wir nutzen diese Apps täglich selbst.",',
 "pt":'v7_t:"Pague uma vez", v7_d:"Compras únicas e ferramentas grátis. Sem assinaturas para o essencial.", v8_t:"Manutenção ativa", v8_d:"Atualizações frequentes e correções rápidas. Também usamos esses apps todo dia.",',
 "it":'v7_t:"Paghi una volta", v7_d:"Acquisti singoli e strumenti gratuiti. Nessun abbonamento per l\'essenziale.", v8_t:"Manutenzione attiva", v8_d:"Aggiornamenti regolari e correzioni rapide. Usiamo queste app ogni giorno anche noi.",',
 "ja":'v7_t:"買い切り", v7_d:"買い切りと無料ツール。基本機能にサブスクは不要です。", v8_t:"継続的に更新", v8_d:"定期的なアップデートと迅速な修正。私たちも毎日これらのアプリを使っています。",',
 "zh":'v7_t:"一次买断", v7_d:"一次买断和免费工具。基础功能无需订阅。", v8_t:"持续维护", v8_d:"定期更新和快速修复。我们自己也每天使用这些应用。",',
 "ko":'v7_t:"한 번만 결제", v7_d:"한 번 결제와 무료 도구. 기본 기능에 구독이 필요 없습니다.", v8_t:"지속적인 관리", v8_d:"정기 업데이트와 빠른 수정. 저희도 매일 이 앱들을 사용합니다.",',
 "ru":'v7_t:"Одна покупка", v7_d:"Разовые покупки и бесплатные инструменты. Никаких подписок за основное.", v8_t:"Активная поддержка", v8_d:"Регулярные обновления и быстрые исправления. Мы сами пользуемся этими приложениями каждый день.",',
 "ar":'v7_t:"ادفع مرة واحدة", v7_d:"مشتريات لمرة واحدة وأدوات مجانية. لا اشتراكات للأساسيات.", v8_t:"صيانة مستمرة", v8_d:"تحديثات منتظمة وإصلاحات سريعة. نحن أيضًا نستخدم هذه التطبيقات يوميًا.",',
 "nl":'v7_t:"Eenmalig betalen", v7_d:"Eenmalige aankopen en gratis tools. Geen abonnementen voor het essentiële.", v8_t:"Actief onderhouden", v8_d:"Regelmatige updates en snelle fixes. Wij gebruiken deze apps zelf ook dagelijks.",',
 "tr":'v7_t:"Bir kez öde", v7_d:"Tek seferlik satın almalar ve ücretsiz araçlar. Temel özellikler için abonelik yok.", v8_t:"Aktif bakım", v8_d:"Düzenli güncellemeler ve hızlı düzeltmeler. Bu uygulamaları biz de her gün kullanıyoruz.",',
 "pl":'v7_t:"Płać raz", v7_d:"Jednorazowe zakupy i darmowe narzędzia. Bez subskrypcji za podstawy.", v8_t:"Aktywnie rozwijane", v8_d:"Regularne aktualizacje i szybkie poprawki. Sami też codziennie używamy tych aplikacji.",',
 "sv":'v7_t:"Betala en gång", v7_d:"Engångsköp och gratis verktyg. Inga prenumerationer för det viktiga.", v8_t:"Aktivt underhållet", v8_d:"Regelbundna uppdateringar och snabba fixar. Vi använder dessa appar varje dag också.",',
 "hi":'v7_t:"एक बार भुगतान करें", v7_d:"एकमुश्त खरीद और मुफ्त टूल। बुनियादी सुविधाओं के लिए कोई सदस्यता नहीं।", v8_t:"सक्रिय रखरखाव", v8_d:"नियमित अपडेट और त्वरित सुधार। हम भी ये ऐप्स रोज़ इस्तेमाल करते हैं।",',
 "id":'v7_t:"Bayar sekali", v7_d:"Pembelian sekali dan alat gratis. Tanpa langganan untuk hal penting.", v8_t:"Dipelihara aktif", v8_d:"Pembaruan rutin dan perbaikan cepat. Kami juga memakai aplikasi ini setiap hari.",',
 "th":'v7_t:"จ่ายครั้งเดียว", v7_d:"ซื้อครั้งเดียวและเครื่องมือฟรี ไม่มีการสมัครสมาชิกสำหรับฟีเจอร์พื้นฐาน", v8_t:"ดูแลอย่างต่อเนื่อง", v8_d:"อัปเดตสม่ำเสมอและแก้ไขรวดเร็ว เราก็ใช้แอปเหล่านี้ทุกวันเช่นกัน",',
 "vi":'v7_t:"Trả một lần", v7_d:"Mua một lần và công cụ miễn phí. Không đăng ký cho các tính năng cơ bản.", v8_t:"Được duy trì tích cực", v8_d:"Cập nhật thường xuyên và sửa lỗi nhanh. Chúng tôi cũng dùng các ứng dụng này mỗi ngày.",',
}
for lang, keys in V78.items():
    scripts, _n = re.subn(r'(\n        '+lang+r': \{\n)', r'\1            '+keys+'\n', scripts, count=1)
    assert _n==1, "v78 inject failed for "+lang

# ---- app data (12), featured=5 ; store 'store' -> App Store link, 'free' -> product page ----
A = [
 ("Corvus Player","corvus-player","https://corvusdevs.github.io/Corvus-Player/","blue","p6_tag","p6_desc","mac","free",None,True),
 ("Corvus Display","corvus-display","https://corvusdevs.github.io/CorvusDisplay/","blue",None,None,"mac","free",None,True),
 ("Alien Crow","alien-crow","https://corvusdevs.github.io/Alien-Crow-For-Safari/","orange","p9_tag","p9_desc","safari","store","6769216829",True),
 ("Findbar","findbar","https://corvusdevs.github.io/Findbar-For-Safari/","purple","p8_tag","p8_desc","safari","store","6773464299",True),
 ("Corvus RSS Reader","corvus-rss","https://corvusdevs.github.io/Corvus-RSS-Reader-For-Safari/","orange","p3_tag","p3_desc","safari","store","6761442829",True),
 ("Corvus Arcade","corvus-arcade","https://corvusdevs.github.io/CorvusArcade/","purple",None,None,"mac","free",None,False),
 ("Night Crow","night-crow","https://corvusdevs.github.io/Night-Crow-For-Safari/","purple",None,None,"safari","store","6785353496",False),
 ("Ekual","ekual","https://corvusdevs.github.io/Ekual/","green","p1_tag","p1_desc","mac","free",None,False),
 ("Purple Crow","purple-crow","https://corvusdevs.github.io/Purple-Crow-For-Safari/","purple","p2_tag","p2_desc","safari","store","6761481948",True),
 ("Auto Mute Tab","auto-mute-tab","https://corvusdevs.github.io/Auto-Mute-Tab-For-Safari/","red","p4_tag","p4_desc","safari","store","6761746627",False),
 ("Red Crow","red-crow","https://corvusdevs.github.io/Red-Crow-For-Safari/","red","p7_tag","p7_desc","safari","store","6766324724",False),
 ("Tekla","tekla","https://corvusdevs.github.io/Tekla/","blue","p5_tag","p5_desc","mac","free",None,False),
]
TAG_EN = {"corvus-display":"macOS Display Control","corvus-arcade":"Windows Games on Mac","night-crow":"Safari Dark Mode"}
DESC_EN = {"corvus-display":"Brightness, color temperature and resolution for external and non-Apple displays on Apple Silicon.",
 "corvus-arcade":"Run Windows games on Apple Silicon with bundled Wine and D3DMetal. No CrossOver, no Terminal.",
 "night-crow":"A smart, native dark mode for every website in Safari. Works on macOS, iOS, and iPadOS."}
APPLE_SVG='<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>'
CHEV='<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>'

# English defaults for keyed apps (kept in the DOM as fallback + for SEO/no-JS;
# the walker overwrites per language where the key exists in the catalog).
TAGEN={"p1_tag":"macOS Loudness Equalization","p2_tag":"Twitch Extension","p3_tag":"Safari RSS Extension",
 "p4_tag":"Safari Tab Muter","p5_tag":"macOS Virtual Keyboard","p6_tag":"macOS Media Player",
 "p7_tag":"YouTube Safari Extension","p8_tag":"Safari Address-Bar Shortcuts","p9_tag":"Reddit Safari Extension"}
DESCEN={"p1_desc":"Automatic loudness equalization for macOS. Balances volume across all your apps in real time. Free 14-day trial.",
 "p2_desc":"BTTV, FFZ and 7TV emotes plus 50+ features. Auto-claim, split chat, PiP, anonymous viewing, and more.",
 "p3_desc":"Subscribe to feeds, YouTube channels and blogs, all in one place. Works on macOS, iOS, and iPadOS.",
 "p4_desc":"Automatically mutes background tabs so only the focused tab plays audio. PiP, keyboard shortcuts, and a domain whitelist.",
 "p5_desc":"Swipe-to-type virtual keyboard for macOS. Smart predictions, 14 languages, full desktop layout, 100% offline.",
 "p6_desc":"The most powerful and customizable media player for macOS. Built on mpv with GPU-accelerated playback, real-time GLSL shaders, streaming, and 200+ settings.",
 "p7_desc":"Speed control, SponsorBlock, video filters and 40+ features for YouTube. Works on macOS, iOS, and iPadOS.",
 "p8_desc":"Type a keyword in Safari's address bar and jump anywhere. 30+ built-in shortcuts, edit any of them or add your own. Works on macOS, iOS, and iPadOS.",
 "p9_desc":"Supercharge Reddit with 90+ tools: dark mode and 20+ themes, ad and nag blocking, comment upgrades, and keyboard navigation. Works on macOS, iOS, and iPadOS."}
def tagline(icon,key):
    if key: return f'<div class="c-tag" data-i18n="{key}">{TAGEN[key]}</div>'
    return f'<div class="c-tag">{TAG_EN.get(icon,"")}</div>'
def desc_html(icon,key):
    if key: return f'<p class="c-desc" data-i18n="{key}">{DESCEN[key]}</p>'
    return f'<p class="c-desc">{DESC_EN.get(icon,"")}</p>'
def plats(cat):
    return "".join(f'<span class="pchip">{p}</span>' for p in (["macOS"] if cat=="mac" else ["macOS","iOS","iPadOS"]))
def store_link(app):
    name,icon,url,color,tk,dk,cat,store,aid,feat=app
    if store=="store":
        return f'<a href="https://apps.apple.com/app/id{aid}" class="store app">{APPLE_SVG}App Store</a>'
    return f'<a href="{url}" class="store dl"><span data-i18n="f_free">Free</span></a>'
NEWB={"night-crow":("new","badge_new","New"),"purple-crow":("upd","badge_upd","Updated")}
def npill(app):
    v=NEWB.get(app[1])
    if not v: return ''
    return f'<span class="npill {"n-new" if v[0]=="new" else "n-upd"}" data-i18n="{v[1]}">{v[2]}</span>'
def price_badge(app):
    if app[7]=="store": return '<span class="badge store-b">App Store</span>'
    return '<span class="badge free-b" data-i18n="f_free">Free</span>'
# extra searchable keywords per app so search matches more than the name (e.g. "twitch" -> Purple Crow)
KEYWORDS={"purple-crow":"twitch bttv ffz 7tv emotes stream chat","alien-crow":"reddit","findbar":"address bar shortcuts keyword search bang",
 "corvus-rss":"rss feeds youtube blogs reader","night-crow":"dark mode theme night","auto-mute-tab":"mute audio sound tab volume",
 "red-crow":"youtube sponsorblock video speed","corvus-player":"media video mpv player music","corvus-display":"display monitor brightness resolution color",
 "corvus-arcade":"windows games wine gaming d3dmetal","ekual":"audio loudness volume equalizer normalize","tekla":"keyboard virtual typing swipe"}
def search_terms(app):
    name,icon,url,color,tk,dk,cat,store,aid,feat=app
    etag = TAGEN.get(tk,"") if tk else TAG_EN.get(icon,"")
    return f"{name} {etag} {KEYWORDS.get(icon,'')} {cat}".lower()

# featured cards (whole card links via a stretched name link; store button sits above it)
feat_cards=""
for app in [a for a in A if a[9]]:
    name,icon,url,color,tk,dk,cat,store,aid,feat=app
    feat_cards+=f'''
      <article class="fcard reveal" data-color="{color}">
        <div class="ftop"><img src="icons/{icon}.png" alt=""><div class="fmeta"><div class="fname"><a class="clink" href="{url}"><h3>{name}</h3></a>{npill(app)}</div>{tagline(icon,tk)}</div></div>
        {desc_html(icon,dk)}
        <div class="frow"><div class="plats">{plats(cat)}</div>{store_link(app)}</div>
      </article>'''

# collection cards
coll_cards=""
for app in A:
    name,icon,url,color,tk,dk,cat,store,aid,feat=app
    coll_cards+=f'''
      <article class="card reveal" data-color="{color}" data-cat="{cat}" data-store="{store}" data-search="{search_terms(app)}">
        <img src="icons/{icon}.png" alt="">
        <div class="cbody"><div class="chd"><span class="dot"></span><a class="clink" href="{url}"><h4>{name}</h4></a>{npill(app)}{price_badge(app)}</div>{tagline(icon,tk)}
          <div class="plats">{plats(cat)}</div></div>
      </article>'''

NAV_HERO = f'''    <!-- Nav -->
    <nav>
        <a href="/" class="nav-brand"><img src="avatar.png" alt="CorvusDevs">Corvus<span>Devs</span></a>
        <div class="nav-right">
            <button class="nav-toggle" aria-label="Menu" aria-expanded="false" onclick="var o=document.body.classList.toggle('nav-open');this.setAttribute('aria-expanded',o);event.stopPropagation();"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/></svg></button>
            <ul class="nav-links">
                <li><a href="#products" data-i18n="nav_products">Products</a></li>
                <li><a href="#about" data-i18n="nav_about">About</a></li>
                <li><a href="mailto:corvusdevs@outlook.com" data-i18n="nav_contact">Contact</a></li>
            </ul>
            {langwrap}
            <button class="themebtn" id="themeBtn" aria-label="Toggle theme" title="Toggle theme"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8z"/></svg></button>
        </div>
    </nav>

    <!-- Hero -->
    <section class="hero">
        <div class="eyebrow reveal" data-i18n="hero_eyebrow">Independent Mac &amp; Safari studio</div>
        <div class="hero-wordmark reveal">Corvus<span class="devs">Devs</span></div>
        <h1 class="reveal" data-i18n="hero_title">Software that respects your Mac.</h1>
        <p class="subtitle reveal" data-i18n="hero_sub">We build focused, privacy-first tools for macOS. No subscriptions, no telemetry, no bloat.</p>
        <a href="#products" class="hero-cta reveal"><span data-i18n="hero_cta">See our products</span>
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg></a>
    </section>

    <!-- Featured -->
    <section class="sec">
        <div class="sec-head reveal">
            <div class="sec-title" data-i18n="sec_featured">Featured</div>
            <div class="sec-note" data-i18n="sec_featured_note">Where we'd start</div>
        </div>
        <div class="feat-grid">{feat_cards}
        </div>
    </section>

    <!-- Collection -->
    <section class="sec" id="products">
        <div class="sec-head reveal">
            <div class="sec-title" data-i18n="sec_collection">All our apps</div>
            <div class="ctrls">
                <input class="search" id="search" type="search" data-i18n-ph="f_search" placeholder="Search apps" aria-label="Search apps">
                <div class="filters" id="filters" role="group" aria-label="Filter apps">
                    <button data-f="all" aria-pressed="true"><span data-i18n="f_all">All</span> <span class="c">12</span></button>
                    <button data-f="safari" aria-pressed="false">Safari <span class="c">7</span></button>
                    <button data-f="mac" aria-pressed="false">macOS <span class="c">5</span></button>
                    <button data-f="free" aria-pressed="false"><span data-i18n="f_free">Free</span> <span class="c">5</span></button>
                </div>
            </div>
        </div>
        <div class="grid" id="grid">{coll_cards}
        </div>
    </section>

'''

NEW_JS = '''
    <script>
    (function(){
      var root=document.documentElement, tb=document.getElementById("themeBtn");
      var saved=localStorage.getItem("corvus-theme"); if(saved) root.setAttribute("data-theme",saved);
      tb.addEventListener("click",function(){
        var cur=root.getAttribute("data-theme")||(matchMedia("(prefers-color-scheme:dark)").matches?"dark":"light");
        var nx=cur==="dark"?"light":"dark"; root.setAttribute("data-theme",nx); localStorage.setItem("corvus-theme",nx);
      });
      var fbar=document.getElementById("filters"), grid=document.getElementById("grid"),
          search=document.getElementById("search"), cards=grid.querySelectorAll(".card"), curF="all";
      function apply(){
        var q=(search.value||"").trim().toLowerCase();
        cards.forEach(function(cd){
          var catOk = curF==="all" || (curF==="free"? cd.dataset.store==="free" : cd.dataset.cat===curF);
          var qOk = !q || (cd.dataset.search||"").indexOf(q)>-1;
          cd.classList.toggle("chide", !(catOk&&qOk));
        });
      }
      fbar.addEventListener("click",function(e){
        var b=e.target.closest("button"); if(!b) return;
        fbar.querySelectorAll("button").forEach(function(x){x.setAttribute("aria-pressed", x===b);});
        curF=b.dataset.f; apply();
      });
      search.addEventListener("input", apply);
    })();
    </script>
'''

# localize the search placeholder through the language walker
scripts = scripts.replace(
    "el.innerHTML = s[k];\n        });",
    "el.innerHTML = s[k];\n        });\n        document.querySelectorAll(\"[data-i18n-ph]\").forEach(el => { const k = el.getAttribute(\"data-i18n-ph\"); if (s[k]) el.placeholder = s[k]; });",
    1)
# inject two more principles (v7 pay-once, v8 actively-maintained) so the grid is a symmetric 4x2
values_block = values_block.replace(
    'Email us directly.</p>\n            </div>',
    'Email us directly.</p>\n            </div>\n'
    '            <div class="value-card reveal"><div class="value-icon"><svg viewBox="0 0 24 24"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg></div><h3 data-i18n="v7_t">Pay once, keep it</h3><p data-i18n="v7_d">One-time purchases and free tools. No subscriptions for the essentials.</p></div>\n'
    '            <div class="value-card reveal"><div class="value-icon"><svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg></div><h3 data-i18n="v8_t">Actively maintained</h3><p data-i18n="v8_d">Regular updates and quick fixes. We use these apps every day too.</p></div>',
    1)
# redesign the coming-soon section (glow, placeholder tiles, accent button, request line)
_cs = values_block.index('<!-- Coming Soon -->')
_soon_old = values_block[_cs:values_block.index('</section>', _cs)+len('</section>')]
_soon_new = '''<!-- Coming Soon -->
    <section class="coming-soon">
        <div class="coming-soon-card reveal">
            <div class="soon-glow" aria-hidden="true"></div>
            <div class="soon-tiles" aria-hidden="true"><span>+</span><span>+</span><span>+</span></div>
            <h3 data-i18n="soon_t">More apps coming soon</h3>
            <p data-i18n="soon_d">We're working on new tools for macOS. Drop us a line if you want to be the first to know.</p>
            <a href="mailto:corvusdevs@outlook.com?subject=Notify me about new apps" class="notify-link" data-i18n="soon_btn">Get notified</a>
            <p class="soon-req"><span data-i18n="soon_req">Have an app idea?</span> <a href="mailto:corvusdevs@outlook.com?subject=App%20request" data-i18n="soon_reqlink">Request an app</a></p>
        </div>
    </section>'''
values_block = values_block.replace(_soon_old, _soon_new, 1)
assert 'flagcdn.com' not in langwrap and 'zh-Hant' not in langwrap and 'soon_reqlink' in values_block and 'v7_t' in values_block and 'soon-glow' in values_block, "transform failed"

STYLE = open("build/site_style.css", encoding="utf-8").read()

out = head_meta + "    <style>\n" + STYLE + "\n</style>\n</head>\n<body>\n<script>document.documentElement.classList.add('js')</script>\n" + NAV_HERO + "\n" + values_block + "\n" + NEW_JS + scripts
# long-dash cleanup (head separators -> colon / period; catalog appositives -> comma, full-width for CJK)
out=out.replace("CorvusDevs — Safari Extensions & macOS Apps","CorvusDevs: Safari Extensions & macOS Apps")
out=out.replace("and more — privacy-first software","and more. Privacy-first software")
out=out.replace("macOS apps — RSS reader","macOS apps: RSS reader")
_cjk=re.compile(r'[぀-ヿ一-鿿가-힣]')
_L=[]
for _l in out.split("\n"):
    if re.search(r'[—–―]',_l):
        _l=re.sub(r'\s*[—–―]\s*', ("，" if _cjk.search(_l) else ", "), _l)
    _L.append(_l)
out="\n".join(_L)
assert len(re.findall(r'[—–―]',out))==0, "long-dash remains"
open(OUT,"w",encoding="utf-8").write(out)
print("wrote", OUT, "|", round(len(out)/1024), "KB")
print("featured cards:", out.count('class="fcard'))
print("collection cards:", out.count('class="card reveal'))
print("new keys present (en sec_featured):", 'sec_featured:"Featured"' in out)

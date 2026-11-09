# -*- coding: utf-8 -*-
# Stranica /kontaktna-sociva/ — predporudžbina kontaktnih sočiva (SR/HU/EN/RU).
# /kontaktna-sociva/ — javna SEO stranica «online porudžbina u izradi» (linkovi, sitemap).
# /kontaktna-sociva-nacrt/ — skriveni pun nacrt (kartice + forma), noindex.
# Sočiva ispod su PRIMERI — zameniti podacima iz novih kataloga, cene upisati u price (RSD po pakovanju).
# Kad je sve gotovo: javna stranica treba da prikaže kartice i formu (ks_page preview=True bez trake «nacrt»).

KS_SLUG = "kontaktna-sociva"
KS_DRAFT = True   # (rezervisano)

# kind: "1d" jednodnevna, "2w" dvonedeljna, "1m" mesečna
# sph: (od, do) — korak 0,25 do ±6,00, dalje 0,50
# price: RSD po pakovanju ili None («cena uskoro»)
KS_LENSES = [
    dict(id="acuvue-oasys", brand="Johnson & Johnson", name="Acuvue Oasys", kind="2w", toric=False,
         pack=6, bc=["8.4", "8.8"], dia="14.0", sph=(-12, 8), price=None),
    dict(id="acuvue-oasys-ast", brand="Johnson & Johnson", name="Acuvue Oasys for Astigmatism", kind="2w", toric=True,
         pack=6, bc=["8.6"], dia="14.5", sph=(-9, 6), cyl=["-0.75", "-1.25", "-1.75", "-2.25", "-2.75"], price=None),
    dict(id="air-optix-hg", brand="Alcon", name="Air Optix plus HydraGlyde", kind="1m", toric=False,
         pack=6, bc=["8.6"], dia="14.2", sph=(-12, 8), price=None),
    dict(id="air-optix-hg-ast", brand="Alcon", name="Air Optix plus HydraGlyde for Astigmatism", kind="1m", toric=True,
         pack=6, bc=["8.7"], dia="14.5", sph=(-10, 6), cyl=["-0.75", "-1.25", "-1.75", "-2.25"], price=None),
    dict(id="dailies-total1", brand="Alcon", name="Dailies Total1", kind="1d", toric=False,
         pack=30, bc=["8.5"], dia="14.1", sph=(-12, 6), price=None),
    dict(id="biofinity", brand="CooperVision", name="Biofinity", kind="1m", toric=False,
         pack=6, bc=["8.6"], dia="14.0", sph=(-12, 8), price=None),
]

def sph_values(lo, hi):
    out, x = [], lo
    while x <= hi + 1e-9:
        out.append(round(x, 2))
        x += 0.25 if -6 <= x < 6 else 0.5
    return [f"{v:+.2f}" if v else "0.00" for v in out]

KS = {}

KS["sr"] = dict(
    title="Kontaktna sočiva — porudžbina | Optika Ginter Novi Sad",
    desc="Poručite kontaktna sočiva online i preuzmite ih u Optici Ginter, Trg Republike 25, Novi Sad. Plaćanje pri preuzimanju.",
    draft="Nacrt stranice — sočiva i cene su primeri, stranica nije javna.",
    kicker="Kontaktna sočiva",
    h1="Poručite kontaktna sočiva <em>online</em>",
    lead="Izaberite sočiva, upišite parametre i pošaljite predporudžbinu. Proverićemo dostupnost kod dobavljača i javiti vam rok — sočiva preuzimate u salonu.",
    list_kicker="Asortiman", list_h="Sočiva koja <em>poručujemo</em>",
    k_1d="Jednodnevna", k_2w="Dvonedeljna", k_1m="Mesečna", toric="Torična · astigmatizam",
    pack="Pakovanje: {n} kom", sph_range="Dioptrije od {a} do {b}", price_tbd="Cena uskoro", per_pack="po pakovanju",
    btn_pick="Poruči",
    form_kicker="Predporudžbina", form_h="Podaci za <em>porudžbinu</em>",
    hint="Parametre prepišite sa kutije sočiva ili sa recepta: SPH — dioptrija, BC — bazna krivina, CYL i AX — cilindar i osa (samo za torična sočiva).",
    f_lens="Sočiva", f_choose="— izaberite —",
    od="Desno oko (OD)", os="Levo oko (OS)",
    f_qty="Pakovanja", f_sph="SPH", f_bc="BC", f_cyl="CYL", f_ax="AX",
    qty0="nije potrebno",
    toric_note="Rok isporuke toričnih sočiva (za astigmatizam) može biti do 8 nedelja.",
    f_name="Ime i prezime", f_phone="Telefon", f_phone_ph="npr. 064 123 4567",
    f_email="E-mail (nije obavezno)", f_comment="Komentar",
    consent="Saglasan/na sam da Optika Ginter obradi moje podatke radi ove porudžbine, u skladu sa", privacy="Politikom privatnosti",
    btn_send="Pošalji predporudžbinu",
    terms_kicker="Uslovi", terms_h="Kako <em>funkcioniše</em>",
    terms=[
        ("Predporudžbina", "Ovo je predporudžbina — ništa ne plaćate unapred."),
        ("Provera i rok", "Proverićemo dostupnost sočiva kod dobavljača i javiti vam rok isporuke telefonom."),
        ("Preuzimanje", "Sočiva preuzimate lično u Optici Ginter, Trg Republike 25, Novi Sad. Ne šaljemo poštom."),
        ("Plaćanje", "Plaćate pri preuzimanju — gotovinom ili karticom."),
    ],
    ok_h="Hvala!", ok="Predporudžbina je primljena. Javićemo vam se telefonom kada proverimo dostupnost i rok.",
    e_lens="Izaberite sočiva.", e_eye="Upišite broj pakovanja bar za jedno oko.",
    e_params="Upišite dioptriju i baznu krivinu za svako oko koje poručujete.",
    e_toric="Za torična sočiva upišite i cilindar i osu.",
    e_name="Upišite ime i prezime.", e_phone="Proverite broj telefona.", e_consent="Potrebna je vaša saglasnost.",
    e_rate="Već smo primili vašu porudžbinu. Javićemo vam se uskoro.",
    e_server="Porudžbina nije poslata. Pokušajte ponovo ili nas pozovite: ",
)

KS["hu"] = dict(
    title="Kontaktlencse rendelés | Optika Ginter Újvidék",
    desc="Rendeljen kontaktlencsét online, és vegye át az Optika Ginterben, Trg Republike 25, Újvidék. Fizetés átvételkor.",
    draft="Az oldal vázlat — a lencsék és árak csak példák, az oldal nem nyilvános.",
    kicker="Kontaktlencsék",
    h1="Rendeljen kontaktlencsét <em>online</em>",
    lead="Válassza ki a lencsét, adja meg a paramétereket, és küldje el az előrendelést. Ellenőrizzük a beszállítónál, és jelezzük a határidőt — a lencsét az üzletben veheti át.",
    list_kicker="Kínálat", list_h="Rendelhető <em>lencsék</em>",
    k_1d="Napi", k_2w="Kéthetes", k_1m="Havi", toric="Tórikus · asztigmia",
    pack="Kiszerelés: {n} db", sph_range="Dioptria {a} és {b} között", price_tbd="Ár hamarosan", per_pack="dobozonként",
    btn_pick="Rendelés",
    form_kicker="Előrendelés", form_h="Rendelési <em>adatok</em>",
    hint="A paramétereket a lencse dobozáról vagy a receptről másolja át: SPH — dioptria, BC — bázisgörbület, CYL és AX — cilinder és tengely (csak tórikus lencséknél).",
    f_lens="Lencse", f_choose="— válasszon —",
    od="Jobb szem (OD)", os="Bal szem (OS)",
    f_qty="Doboz", f_sph="SPH", f_bc="BC", f_cyl="CYL", f_ax="AX",
    qty0="nem kell",
    toric_note="A tórikus (asztigmiás) lencsék szállítási ideje akár 8 hét is lehet.",
    f_name="Név", f_phone="Telefon", f_phone_ph="pl. 064 123 4567",
    f_email="E-mail (nem kötelező)", f_comment="Megjegyzés",
    consent="Hozzájárulok, hogy az Optika Ginter a rendelés céljából kezelje az adataimat, a következő szerint:", privacy="Adatvédelmi szabályzat",
    btn_send="Előrendelés küldése",
    terms_kicker="Feltételek", terms_h="Hogyan <em>működik</em>",
    terms=[
        ("Előrendelés", "Ez előrendelés — előre semmit sem kell fizetni."),
        ("Ellenőrzés és határidő", "Ellenőrizzük a lencse elérhetőségét a beszállítónál, és telefonon jelezzük a szállítási időt."),
        ("Átvétel", "A lencsét személyesen veheti át az Optika Ginterben, Trg Republike 25, Újvidék. Postán nem küldünk."),
        ("Fizetés", "Átvételkor fizet — készpénzzel vagy kártyával."),
    ],
    ok_h="Köszönjük!", ok="Az előrendelést megkaptuk. Telefonon jelentkezünk, amint ellenőriztük az elérhetőséget és a határidőt.",
    e_lens="Válasszon lencsét.", e_eye="Adja meg a dobozok számát legalább az egyik szemhez.",
    e_params="Adja meg a dioptriát és a bázisgörbületet minden rendelt szemhez.",
    e_toric="Tórikus lencséhez adja meg a cilindert és a tengelyt is.",
    e_name="Adja meg a nevét.", e_phone="Ellenőrizze a telefonszámot.", e_consent="Szükséges a hozzájárulása.",
    e_rate="Rendelését már megkaptuk. Hamarosan jelentkezünk.",
    e_server="A rendelés nem ment el. Próbálja újra, vagy hívjon minket: ",
)

KS["en"] = dict(
    title="Order contact lenses | Optika Ginter Novi Sad",
    desc="Order contact lenses online and collect them at Optika Ginter, Trg Republike 25, Novi Sad. Pay on collection.",
    draft="Draft page — lenses and prices are examples, the page is not public.",
    kicker="Contact lenses",
    h1="Order contact lenses <em>online</em>",
    lead="Choose your lenses, enter the parameters and send a pre-order. We will check availability with the supplier and let you know the lead time — you collect the lenses in our shop.",
    list_kicker="Range", list_h="Lenses we <em>order</em>",
    k_1d="Daily", k_2w="Two-weekly", k_1m="Monthly", toric="Toric · astigmatism",
    pack="Pack: {n} lenses", sph_range="Powers from {a} to {b}", price_tbd="Price coming soon", per_pack="per pack",
    btn_pick="Order",
    form_kicker="Pre-order", form_h="Order <em>details</em>",
    hint="Copy the parameters from the lens box or your prescription: SPH — power, BC — base curve, CYL and AX — cylinder and axis (toric lenses only).",
    f_lens="Lenses", f_choose="— choose —",
    od="Right eye (OD)", os="Left eye (OS)",
    f_qty="Packs", f_sph="SPH", f_bc="BC", f_cyl="CYL", f_ax="AX",
    qty0="not needed",
    toric_note="Delivery of toric lenses (for astigmatism) can take up to 8 weeks.",
    f_name="Full name", f_phone="Phone", f_phone_ph="e.g. 064 123 4567",
    f_email="E-mail (optional)", f_comment="Comment",
    consent="I agree that Optika Ginter may process my details for this order, in line with the", privacy="Privacy Policy",
    btn_send="Send pre-order",
    terms_kicker="Terms", terms_h="How it <em>works</em>",
    terms=[
        ("Pre-order", "This is a pre-order — nothing to pay in advance."),
        ("Check and lead time", "We check availability with the supplier and call you with the delivery time."),
        ("Collection", "Collect your lenses in person at Optika Ginter, Trg Republike 25, Novi Sad. We do not ship."),
        ("Payment", "Pay on collection — cash or card."),
    ],
    ok_h="Thank you!", ok="Your pre-order has been received. We will call you once we have checked availability and lead time.",
    e_lens="Please choose the lenses.", e_eye="Enter the number of packs for at least one eye.",
    e_params="Enter the power and base curve for each eye you order.",
    e_toric="For toric lenses also enter cylinder and axis.",
    e_name="Please enter your name.", e_phone="Please check the phone number.", e_consent="Your consent is required.",
    e_rate="We have already received your order. We will contact you soon.",
    e_server="The order was not sent. Please try again or call us: ",
)

KS["ru"] = dict(
    title="Заказ контактных линз | Optika Ginter Нови-Сад",
    desc="Закажите контактные линзы онлайн и заберите их в Optika Ginter, Trg Republike 25, Нови-Сад. Оплата при получении.",
    draft="Черновик страницы — линзы и цены для примера, страница не опубликована.",
    kicker="Контактные линзы",
    h1="Закажите контактные линзы <em>онлайн</em>",
    lead="Выберите линзы, укажите параметры и отправьте предварительный заказ. Мы проверим наличие у поставщика и сообщим срок — линзы вы забираете в салоне.",
    list_kicker="Ассортимент", list_h="Линзы, которые мы <em>заказываем</em>",
    k_1d="Однодневные", k_2w="Двухнедельные", k_1m="Ежемесячные", toric="Торические · астигматизм",
    pack="В упаковке: {n} шт.", sph_range="Оптическая сила от {a} до {b}", price_tbd="Цена скоро", per_pack="за упаковку",
    btn_pick="Заказать",
    form_kicker="Предварительный заказ", form_h="Данные для <em>заказа</em>",
    hint="Параметры перепишите с коробки линз или из рецепта: SPH — сфера, BC — базовая кривизна, CYL и AX — цилиндр и ось (только для торических линз).",
    f_lens="Линзы", f_choose="— выберите —",
    od="Правый глаз (OD)", os="Левый глаз (OS)",
    f_qty="Упаковок", f_sph="SPH", f_bc="BC", f_cyl="CYL", f_ax="AX",
    qty0="не нужно",
    toric_note="Срок поставки торических линз (при астигматизме) — до 8 недель.",
    f_name="Имя и фамилия", f_phone="Телефон", f_phone_ph="напр. 064 123 4567",
    f_email="E-mail (необязательно)", f_comment="Комментарий",
    consent="Я согласен(на) на обработку моих данных Optika Ginter для этого заказа в соответствии с", privacy="Политикой конфиденциальности",
    btn_send="Отправить заказ",
    terms_kicker="Условия", terms_h="Как это <em>работает</em>",
    terms=[
        ("Предварительный заказ", "Это предварительный заказ — заранее ничего платить не нужно."),
        ("Проверка и срок", "Мы проверим наличие линз у поставщика и сообщим срок поставки по телефону."),
        ("Получение", "Линзы забираете сами в Optika Ginter, Trg Republike 25, Нови-Сад. Доставки нет."),
        ("Оплата", "Оплата при получении — наличными или картой."),
    ],
    ok_h="Спасибо!", ok="Заказ принят. Мы позвоним, когда проверим наличие и срок поставки.",
    e_lens="Выберите линзы.", e_eye="Укажите количество упаковок хотя бы для одного глаза.",
    e_params="Укажите сферу и базовую кривизну для каждого заказываемого глаза.",
    e_toric="Для торических линз укажите также цилиндр и ось.",
    e_name="Укажите имя и фамилию.", e_phone="Проверьте номер телефона.", e_consent="Нужно ваше согласие.",
    e_rate="Мы уже получили ваш заказ. Скоро свяжемся с вами.",
    e_server="Заказ не отправлен. Попробуйте ещё раз или позвоните нам: ",
)

# ── Javna stranica «u izradi» (SEO) — dok online porudžbina nije gotova ──
# Pun nacrt (kartice + forma) ide na skriveni KS_PREVIEW (noindex).
KS_PREVIEW = "kontaktna-sociva-nacrt"

KS["sr"].update(
    title="Kontaktna sočiva Novi Sad — porudžbina | Optika Ginter",
    desc="Kontaktna sočiva u Novom Sadu: jednodnevna, dvonedeljna, mesečna i torična sočiva Alcon, Johnson & Johnson, CooperVision, Bausch + Lomb. Poručite u Optici Ginter, Trg Republike 25 — plaćanje pri preuzimanju.",
    nav="Kontaktna sočiva", svc_more="Poručite sočiva",
    p_h1="Kontaktna sočiva u <em>Novom Sadu</em>",
    p_lead="Poručujemo sva kontaktna sočiva dostupna u Srbiji — jednodnevna, dvonedeljna, mesečna i torična za astigmatizam. Proverimo dostupnost kod dobavljača, javimo vam rok, a sočiva preuzimate i plaćate u salonu na Trgu Republike.",
    soon_kicker="Uskoro", soon_h="Online porudžbina je <em>u izradi</em>",
    soon_p="Radimo na tome da sočiva uskoro možete da poručite direktno na sajtu. Do tada nas pozovite ili svratite u salon — porudžbinu primamo odmah.",
    btn_call="Pozovite nas", btn_map="Kako do nas",
    about_kicker="Asortiman", about_h="Sočiva za svaki <em>način nošenja</em>",
    about=[
        ("Jednodnevna", "Svaki dan novi par — najhigijenskije rešenje, bez tečnosti i održavanja."),
        ("Dvonedeljna i mesečna", "Ekonomičan izbor za svakodnevno nošenje. Air Optix obično imamo na stanju."),
        ("Torična", "Sočiva za astigmatizam. Rok isporuke može biti do 8 nedelja."),
        ("Prvi put u sočivima", "Pomoći ćemo vam da naučite da stavljate i skidate sočiva i da ih pravilno održavate."),
    ],
    faq_kicker="Pitanja", faq_h="Česta <em>pitanja</em>", crumb_home="Početna",
    faq=[
        ("Koja kontaktna sočiva možete da poručite?", "Sva kontaktna sočiva dostupna u Srbiji — Alcon, Johnson & Johnson (Acuvue), CooperVision, Bausch + Lomb: jednodnevna, dvonedeljna, mesečna i torična."),
        ("Koliko se čeka na sočiva?", "Rok zavisi od dobavljača — javićemo vam ga čim proverimo dostupnost. Torična sočiva (za astigmatizam) mogu stizati do 8 nedelja."),
        ("Da li plaćam unapred?", "Ne. Porudžbina je besplatna, a sočiva plaćate pri preuzimanju u salonu — gotovinom ili karticom."),
        ("Da li šaljete sočiva poštom?", "Ne, sočiva preuzimate lično u Optici Ginter, Trg Republike 25, Novi Sad."),
        ("Gde da nađem parametre svojih sočiva?", "Na kutiji sočiva ili u receptu: SPH (dioptrija), BC (bazna krivina), DIA (prečnik), a za torična i CYL i AX."),
        ("Nosim sočiva prvi put — šta da radim?", "Zakažite termin u salonu: proverićemo dioptriju, izabrati sočiva i naučiti vas da ih stavljate i skidate."),
    ],
)
KS["hu"].update(
    title="Kontaktlencse Újvidék — rendelés | Optika Ginter",
    desc="Kontaktlencsék Újvidéken: napi, kéthetes, havi és tórikus lencsék — Alcon, Johnson & Johnson, CooperVision, Bausch + Lomb. Rendelés az Optika Ginterben, Trg Republike 25 — fizetés átvételkor.",
    nav="Kontaktlencsék", svc_more="Lencse rendelése",
    p_h1="Kontaktlencsék <em>Újvidéken</em>",
    p_lead="Minden Szerbiában kapható kontaktlencsét megrendelünk — napi, kéthetes, havi és tórikus (asztigmiás) lencséket. Ellenőrizzük a beszállítónál, jelezzük a határidőt, a lencsét pedig az üzletben veheti át és fizetheti ki.",
    soon_kicker="Hamarosan", soon_h="Az online rendelés <em>készül</em>",
    soon_p="Dolgozunk rajta, hogy a lencséket hamarosan közvetlenül a weboldalon rendelhesse. Addig hívjon minket, vagy térjen be az üzletbe — a rendelést azonnal felvesszük.",
    btn_call="Hívjon minket", btn_map="Útvonal",
    about_kicker="Kínálat", about_h="Lencse minden <em>viselési módhoz</em>",
    about=[
        ("Napi lencsék", "Minden nap új pár — a leghigiénikusabb megoldás, folyadék és ápolás nélkül."),
        ("Kéthetes és havi", "Gazdaságos választás mindennapi viselésre. Air Optix általában raktáron van."),
        ("Tórikus", "Lencsék asztigmiára. A szállítási idő akár 8 hét is lehet."),
        ("Először visel lencsét", "Megtanítjuk a lencse be- és kivételét és a helyes ápolást."),
    ],
    faq_kicker="Kérdések", faq_h="Gyakori <em>kérdések</em>", crumb_home="Kezdőlap",
    faq=[
        ("Milyen kontaktlencséket tudnak rendelni?", "Minden Szerbiában kapható kontaktlencsét — Alcon, Johnson & Johnson (Acuvue), CooperVision, Bausch + Lomb: napi, kéthetes, havi és tórikus lencséket."),
        ("Mennyit kell várni a lencsére?", "A határidő a beszállítótól függ — amint ellenőriztük, jelezzük. A tórikus (asztigmiás) lencsék akár 8 hét alatt érkeznek."),
        ("Előre kell fizetni?", "Nem. A rendelés ingyenes, a lencsét átvételkor fizeti az üzletben — készpénzzel vagy kártyával."),
        ("Postán is küldik a lencsét?", "Nem, a lencsét személyesen veheti át az Optika Ginterben, Trg Republike 25, Újvidék."),
        ("Hol találom a lencséim paramétereit?", "A lencse dobozán vagy a recepten: SPH (dioptria), BC (bázisgörbület), DIA (átmérő), tórikusnál CYL és AX is."),
        ("Először viselek lencsét — mit tegyek?", "Foglaljon időpontot: ellenőrizzük a dioptriát, kiválasztjuk a lencsét, és megtanítjuk a be- és kivételt."),
    ],
)
KS["en"].update(
    title="Contact lenses Novi Sad — order | Optika Ginter",
    desc="Contact lenses in Novi Sad: daily, two-weekly, monthly and toric lenses from Alcon, Johnson & Johnson, CooperVision, Bausch + Lomb. Order at Optika Ginter, Trg Republike 25 — pay on collection.",
    nav="Contact lenses", svc_more="Order lenses",
    p_h1="Contact lenses in <em>Novi Sad</em>",
    p_lead="We order every contact lens available in Serbia — daily, two-weekly, monthly and toric lenses for astigmatism. We check availability with the supplier, tell you the lead time, and you collect and pay in our shop on Trg Republike.",
    soon_kicker="Coming soon", soon_h="Online ordering is <em>on its way</em>",
    soon_p="We are working to let you order lenses directly on the website very soon. Until then, call us or drop by the shop — we take your order straight away.",
    btn_call="Call us", btn_map="Directions",
    about_kicker="Range", about_h="Lenses for every <em>wearing schedule</em>",
    about=[
        ("Daily", "A fresh pair every day — the most hygienic option, no solutions or cleaning."),
        ("Two-weekly and monthly", "An economical choice for everyday wear. Air Optix is usually in stock."),
        ("Toric", "Lenses for astigmatism. Delivery can take up to 8 weeks."),
        ("First-time wearers", "We will teach you how to put in, remove and care for your lenses."),
    ],
    faq_kicker="Questions", faq_h="Frequently asked <em>questions</em>", crumb_home="Home",
    faq=[
        ("Which contact lenses can you order?", "Every contact lens available in Serbia — Alcon, Johnson & Johnson (Acuvue), CooperVision, Bausch + Lomb: daily, two-weekly, monthly and toric."),
        ("How long does delivery take?", "It depends on the supplier — we tell you the lead time as soon as we have checked. Toric lenses (for astigmatism) can take up to 8 weeks."),
        ("Do I pay in advance?", "No. Ordering is free and you pay on collection in the shop — cash or card."),
        ("Do you ship lenses?", "No, you collect your lenses in person at Optika Ginter, Trg Republike 25, Novi Sad."),
        ("Where do I find my lens parameters?", "On the lens box or your prescription: SPH (power), BC (base curve), DIA (diameter), and for toric lenses CYL and AX."),
        ("I am new to contact lenses — what should I do?", "Book an appointment: we check your prescription, choose the lenses and teach you how to put them in and take them out."),
    ],
)
KS["ru"].update(
    title="Контактные линзы Нови-Сад — заказ | Optika Ginter",
    desc="Контактные линзы в Нови-Саде: однодневные, двухнедельные, ежемесячные и торические линзы Alcon, Johnson & Johnson, CooperVision, Bausch + Lomb. Заказ в Optika Ginter, Trg Republike 25 — оплата при получении.",
    nav="Контактные линзы", svc_more="Заказать линзы",
    p_h1="Контактные линзы в <em>Нови-Саде</em>",
    p_lead="Заказываем любые контактные линзы, доступные в Сербии: однодневные, двухнедельные, ежемесячные и торические при астигматизме. Проверим наличие у поставщика, сообщим срок, а забрать и оплатить линзы можно в салоне на площади Республики.",
    soon_kicker="Скоро", soon_h="Онлайн-заказ <em>в разработке</em>",
    soon_p="Мы делаем всё, чтобы вы могли заказать линзы прямо на сайте как можно скорее. А пока позвоните нам или зайдите в салон — заказ примем сразу.",
    btn_call="Позвонить", btn_map="Как добраться",
    about_kicker="Ассортимент", about_h="Линзы для любого <em>режима ношения</em>",
    about=[
        ("Однодневные", "Каждый день новая пара — самый гигиеничный вариант, без растворов и ухода."),
        ("Двухнедельные и ежемесячные", "Экономичный выбор для ежедневного ношения. Air Optix обычно есть в наличии."),
        ("Торические", "Линзы при астигматизме. Срок поставки — до 8 недель."),
        ("Первые линзы", "Научим надевать и снимать линзы и правильно за ними ухаживать."),
    ],
    faq_kicker="Вопросы", faq_h="Частые <em>вопросы</em>", crumb_home="Главная",
    faq=[
        ("Какие контактные линзы вы заказываете?", "Любые линзы, доступные в Сербии: Alcon, Johnson & Johnson (Acuvue), CooperVision, Bausch + Lomb — однодневные, двухнедельные, ежемесячные и торические."),
        ("Сколько ждать линзы?", "Срок зависит от поставщика — сообщим, как только проверим наличие. Торические линзы (при астигматизме) могут идти до 8 недель."),
        ("Нужно ли платить заранее?", "Нет. Заказ бесплатный, оплата при получении в салоне — наличными или картой."),
        ("Отправляете ли линзы почтой?", "Нет, линзы забираете сами в Optika Ginter, Trg Republike 25, Нови-Сад."),
        ("Где найти параметры моих линз?", "На коробке линз или в рецепте: SPH (сфера), BC (базовая кривизна), DIA (диаметр), для торических — ещё CYL и AX."),
        ("Ношу линзы впервые — что делать?", "Запишитесь в салон: проверим рефракцию, подберём линзы и научим их надевать и снимать."),
    ],
)

# Stranica 404 (koren sajta, jezik po putanji)
E404 = {
    "sr": dict(h="Stranica nije pronađena", p="Možda je adresa pogrešno upisana ili je stranica premeštena. Pogledajte početnu stranu ili katalog okvira.", home="Početna", frames="Katalog okvira", call="Pozovite nas", title="Stranica nije pronađena | Optika Ginter"),
    "hu": dict(h="Az oldal nem található", p="Lehet, hogy elírta a címet, vagy az oldal elköltözött. Nézze meg a kezdőlapot vagy a keretkatalógust.", home="Kezdőlap", frames="Keretkatalógus", call="Hívjon minket", title="Az oldal nem található | Optika Ginter"),
    "en": dict(h="Page not found", p="The address may be mistyped or the page has moved. Try the home page or our frame catalogue.", home="Home", frames="Frame catalogue", call="Call us", title="Page not found | Optika Ginter"),
    "ru": dict(h="Страница не найдена", p="Возможно, адрес набран с ошибкой или страница переехала. Загляните на главную или в каталог оправ.", home="Главная", frames="Каталог оправ", call="Позвонить", title="Страница не найдена | Optika Ginter"),
}

# Service URL-ите в JSON-LD на началните страници → към страниците за услугите (за програмиста)

**Сега (проверено на живо 15.11):** на `/`, `/bg/` и `/tr/` в `LocalBusiness → OfferCatalog → Service.url` всяка услуга сочи към `services.html#web|print3d|smarthome|cameras|menu|pc` (на BG/TR вече с `/bg/` и `/tr/`, т.е. т. 4 от „Следващи стъпки“ е изпълнена наполовина).
**Защо да се смени:** от 11.11 всяка услуга има своя страница, която е индексирана и целева за „<услуга> Кърджали“. Котва в `services.html` дава на Google по-слаб сигнал от собствения URL на услугата.

**Промяна:**
1. `index.html` (EN), редове 64–69: `url` на 6-те Service:
   | котва | EN |
   |---|---|
   | #web | https://www.smartmenukj.com/web-design-kardzhali.html |
   | #print3d | https://www.smartmenukj.com/3d-printing-kardzhali.html |
   | #smarthome | https://www.smartmenukj.com/smart-home-kardzhali.html |
   | #cameras | https://www.smartmenukj.com/cctv-kardzhali.html |
   | #menu | https://www.smartmenukj.com/qr-menu-kardzhali.html |
   | #pc | https://www.smartmenukj.com/computer-repair-kardzhali.html |
2. `tools/build-langs.mjs` → `localizeJsonLd`: сега само слага `/<lang>/` пред пътя. Нужна е таблица EN→BG/TR за 6-те страници (BG/TR имат други имена):
   | EN | BG | TR |
   |---|---|---|
   | web-design-kardzhali.html | izrabotka-na-saitove-kardzhali.html | web-sitesi-kircaali.html |
   | 3d-printing-kardzhali.html | 3d-pechat-kardzhali.html | 3d-baski-kircaali.html |
   | smart-home-kardzhali.html | umen-dom-kardzhali.html | akilli-ev-kircaali.html |
   | cctv-kardzhali.html | videonablyudenie-kardzhali.html | guvenlik-kamerasi-kircaali.html |
   | qr-menu-kardzhali.html | qr-menu-kardzhali.html | qr-menu-kircaali.html |
   | computer-repair-kardzhali.html | kompyutaren-servis-kardzhali.html | bilgisayar-servisi-kircaali.html |
   (Вероятно таблицата вече я има в `build-service-pages.mjs` — да се преизползва.)
3. `node tools/build-langs.mjs`, после SEO агентът проверява на живо и с Rich Results.

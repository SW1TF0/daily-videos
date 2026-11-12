# M-1112-18 — SEO одит на smarthomekj.eu (по кода)

**Източник:** `SW1TF0/smarthomekj`, клон main, последен commit `4d90b39` (25.10.2026), Next.js 15 static export. Живият домейн (и `*.github.io`, `*.vercel.app`) не се отваря от моята среда → **всичко е по кода**; проверка на живо — след като програмистът пусне поправките (или ако мениджърът ми даде достъп до хоста).
**Какво е наред (не пипай):** robots.ts (`/admin/` забранен, линк към sitemap) · sitemap.ts (всички страници × 3 езика с hreflang) · canonical + hreflang `bg-BG / en / tr-TR / x-default` на всяка страница (`src/lib/seo.ts`) · noindex на количка, поръчка, success, отказ, data-request, `/shop/product/?p=` и корена `/` · `metadataBase` · `<html lang>` по език · title/description на основните страници са в лимита (title ≤60, description 81–157) · alt на продуктовите снимки = името на продукта · FAQPage JSON-LD на /faq · Organization + WebSite на началната.

## Топ 5 проблема (по важност) + готови поправки

### 1. Плейсхолдъри вместо фирмените данни в статичния HTML + няма град/адрес за Google
`src/lib/settings.ts` → `defaultSettings`: `legalName: "[Registered company name] EOOD"`, `address: "[Street and number]"`, `city: "[City, postcode]"`, `phone: "+359 [phone]"`, `email: "hello@smarthomekj.bg"` (домейнът е **.eu**). Истинските стойности идват от Firestore чак в браузъра, така че **предварително сглобеният HTML на всяка страница** (футър, контакти) съдържа `[ … ]`. Това вижда Google при първото четене и всеки, който отвори сайта без JS. Освен това Organization няма адрес и телефон → няма локален сигнал („умен дом Кърджали“).
**Поправка (програмистът):**
- В `defaultSettings` да стоят **истинските** данни (същите като в Admin → Settings), за да са в статичния HTML. Имейлът да е на действащ домейн — собственикът потвърждава кой (`@smarthomekj.eu`?).
- В `src/app/[locale]/page.tsx` → в `@graph` Organization става `"@type": ["Organization", "LocalBusiness"]` (по-точно `HomeAndConstructionBusiness`) с `address` (`PostalAddress`: streetAddress, addressLocality, postalCode, addressCountry "BG"), `telephone`, `email`, `areaServed`, `sameAs` (Instagram/Facebook от settings, ако не са празни), `parentOrganization: { "@type": "Organization", name: "SmartMenuKJ", url: "https://www.smartmenukj.com/" }` (на smartmenukj.com SmartHomeKJ е „нашият отдел за умен дом“).
- ❗ Адрес/телефон: **само каквото собственикът потвърди** (ако е като SmartMenuKJ: ул. „Джебелска“ 2, 6600 Кърджали, +359 88 534 8666 — не го приемам наготово).

### 2. Product JSON-LD е непълен и не показва Черния петък (−10%)
`src/components/product-detail.tsx` ред ~51: Product има само name, description, sku, Offer (price, currency, availability). Липсват `image`, `url`, `brand`, `offers.url`, `seller`, `itemCondition`, а за намалението — старата цена. `starterProducts` винаги е с `compareAtCents: null` (`src/lib/products.ts`), т.е. в статичния HTML **няма намаление**; в repo-то не намерих Черен петък (вероятно е въведен в админа → Firestore, само в браузъра).
**Поправка** (замени `jsonLd` в `product-detail.tsx`):
```ts
const url = absoluteUrl(productHref(locale, product.slug));          // от @/lib/seo и @/lib/products
const onSale = !!product.compareAtCents && product.compareAtCents > product.priceCents;
const jsonLd = {
  "@context": "https://schema.org",
  "@type": "Product",
  name: product.name,
  description: product.description || product.tagline,
  sku: product.sku,
  brand: { "@type": "Brand", name: product.name.split(" ")[0] },     // Aqara, Shelly, Philips…; по-добре поле brand в продукта
  image: product.imageUrl ? [product.imageUrl] : [absoluteUrl(`${basePath}/og.png`)],
  url,
  offers: {
    "@type": "Offer",
    url,
    priceCurrency: "EUR",
    price: (product.priceCents / 100).toFixed(2),
    itemCondition: "https://schema.org/NewCondition",
    availability: product.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
    seller: { "@type": "Organization", name: "SmartHomeKJ" },
    ...(onSale && {
      priceSpecification: [
        { "@type": "UnitPriceSpecification", price: (product.priceCents / 100).toFixed(2), priceCurrency: "EUR" },
        { "@type": "UnitPriceSpecification", priceType: "https://schema.org/StrikethroughPrice",
          price: (product.compareAtCents! / 100).toFixed(2), priceCurrency: "EUR" },
      ],
      // priceValidUntil: крайната дата на кампанията — само ако е зададена в админа; не я измисляй
    }),
  },
};
```
(`absoluteUrl` е в `lib/seo.ts`, който е `server-only` → изнеси `siteUrl/absoluteUrl` в малък файл без `server-only` или подай `url` като prop от `shop/[slug]/page.tsx`.)
Черен петък да влиза и в статичния HTML: при старта на кампанията **пресглоби сайта** (deploy), като `starterProducts` чете `compareAtCents` от seed (добави поле в `src/data/seed.ts`) — иначе Google вижда пълната цена до изпълнение на JS. По желание: `shippingDetails` (доставка 6,90 €, безплатна над 150 € — от `defaultSettings`) и `hasMerchantReturnPolicy` (14 дни отказ — текстът на сайта).

### 3. Категориите нямат собствени страници
Филтърът е `/{locale}/shop/?category=lighting` (`src/components/product-lists.tsx`), чете се само в браузъра, няма собствен title/description/h1 и не е в sitemap. Търсения като „смарт осветление“, „умен термостат“, „смарт камери“ нямат страница, на която да кацнат. Хлебната пътечка на продукта също води към `?category=`.
**Поправка:** статични страници `src/app/[locale]/shop/c/[category]/page.tsx` за 7-те `CATEGORIES` (lighting, climate, security, energy, entertainment, cleaning, hubs): `generateStaticParams` × 3 езика, `pageMetadata({ path: \`shop/c/${c}\` … })`, `<h1>` = името на категорията, 1–2 изречения въведение, `ShopGrid` с фиксирана категория. Добави ги в `sitemap.ts`, а пиловете и хлебната пътечка да сочат към тях.
Готови title/description (BG; ≤60 / ≤155; EN/TR по същия модел):
| Категория | title (+ „ · SmartHomeKJ“) | description |
|---|---|---|
| lighting | Смарт осветление: Philips Hue и сензори | Умни крушки Philips Hue, Hue Bridge и сензор за присъствие Aqara — светлина от телефона и по график. Доставка в цяла България или монтаж. |
| climate | Умен термостат и смарт климат | Умен термостат Netatmo и Shelly модули — отопление по график и от телефона. Купете онлайн с доставка в цяла България или с монтаж от нас. |
| security | Смарт камери, сензори и брави | Камери TP-Link Tapo, смарт брава и звънец Aqara, сензори за врата, движение, теч и дим. Доставка в цяла България или монтаж от нас. |
| energy | Shelly: смарт релета, контакти и електромер | Shelly релета, смарт контакт и електромер Shelly Pro 3EM за следене на тока. Купете онлайн с доставка в цяла България или с монтаж от нас. |
| entertainment | Смарт аудио: Sonos и HomePod | Тонколони Sonos Era 100 и Apple HomePod mini за музика и гласов контрол на умния дом. Купете онлайн с доставка в цяла България. |
| cleaning | — | В seed няма продукти → без страница, докато не се добавят. |
| hubs | Хъбове за умен дом и Wi-Fi: Aqara, Deco | Aqara Hub M3 (Matter, Zigbee, Thread) и Wi-Fi система TP-Link Deco — основата на умния дом. Доставка в цяла България или монтаж от нас. |
(Текстовете са по 20-те продукта в `src/data/seed.ts`; ако в Firestore има други — програмистът да ги свери. Празна категория → без страница.)

### 4. Продуктите, добавени в админа, са невидими за Google
Само 20-те продукта от `src/data/seed.ts` имат статични страници `/shop/<slug>/`. Всеки нов продукт от админа живее на `/shop/product/?p=<slug>`, който е **noindex**, не е в sitemap, а title-ът се слага с JS. Колкото по-голям става магазинът, толкова по-малка част от него е в Google.
**Поправка:** при build `generateStaticParams` на `shop/[slug]` и `sitemap.ts` да четат активните продукти от Firestore (публичните им полета, с fallback към `starterProducts`), а в админа бутон/скрипт „Пресглоби сайта“ (workflow_dispatch на `deploy.yml`) след добавяне на продукт. `/shop/product/?p=` остава само като резерва до следващия deploy.

### 5. Няма „Кърджали“/регион и няма BreadcrumbList
Title/description на всички езици казват „в България“ — добре за магазина, но за **монтаж** (оглед, проект, умен дом под ключ) хората търсят с град: „умен дом Кърджали“, „смарт дом Кърджали“. В целия repo няма нито една дума „Кърджали“. Хлебната пътечка на продукта е само визуална, без JSON-LD.
**Поправки:**
- `bg.ts` → `meta.pages.contact`: title „Безплатен оглед за умен дом в Кърджали и региона“ (48), description „Поискайте безплатен оглед или оферта за умен дом в Кърджали и региона. Отговаряме до един работен ден.“ (≈105). EN: „Free smart home visit in Kardzhali and the region“ · TR: „Kırcaali ve bölgede ücretsiz akıllı ev keşfi“. **Само ако собственикът потвърди**, че огледите/монтажът са в Кърджали и региона (както за SmartMenuKJ).
- `bg.ts` → `meta.pages.about`: description + „Базирани сме в Кърджали“ (при същото потвърждение).
- `product-detail.tsx`: добави втори JSON-LD `BreadcrumbList` (Магазин → категория → продукт) с абсолютни URL-и; след т. 3 — към страницата на категорията.

## По-дребни (по желание)
- `sitemap.ts`: `lastModified = new Date()` за всичко при всеки build → Google спира да вярва на датата. По-добре фиксирана дата на последна промяна на съдържанието (или без `lastModified`).
- Двойно хостване: deploy на GitHub Pages (`deploy.yml`) **и** Vercel (`vercel.json`). Ако и двата адреса са публични, всеки сочи canonical към себе си → дубликат на сайта. Да остане един (там, където е `smarthomekj.eu`), а другият — пренасочване или изключен. (Не мога да проверя кой обслужва домейна.)
- `meta.keywords` — Google не го ползва; не пречи.
- Линкове между двата сайта: smartmenukj.com вече линква към smarthomekj.eu (статията за умен дом); в обратна посока — линк във футъра „Част от SmartMenuKJ, Кърджали“ → https://www.smartmenukj.com/bg/ (подсилва и двата).

## Какво трябва от собственика
1. Истинските фирмени данни за SmartHomeKJ (адрес, телефон, имейл на .eu) — да са в кода, не само в админа.
2. Потвърждение: огледи/монтаж в Кърджали и региона? (за т. 5)
3. Кой хост обслужва smarthomekj.eu (Vercel или GitHub Pages) — за дубликата.
4. След пускане: smarthomekj.eu като отделно свойство в Search Console + имейлът на service account-а като потребител → `gsc.py sitemaps-submit` и `inspect-sitemap` правя аз.

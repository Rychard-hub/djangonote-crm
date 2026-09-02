# HTMX diegimo planas

## 1. Esama situacija (faktas iš kodo)

- Šablonai (`crm/templates/crm/*.html`) yra **savarankiški pilni HTML puslapiai** — nėra `base.html`, nėra `{% extends %}`, kiekvienas failas kartoja `<head>`, navigaciją ir `<style>` bloką atskirai (žr. `crm/templates/crm/lead_list.html:1-39`).
- Visi view'ai (`crm/views.py`) veikia klasikiniu POST → `redirect(...)` → pilnas puslapio perkrovimas modeliu (pvz. `task_toggle_view` `crm/views.py:399-405`, `lead_status_mark_view` `crm/views.py:420-426`, `lead_comment_add_view` `crm/views.py:362-371`).
- HTMX biblioteka šiuo metu **nenaudojama** — jos reikia įtraukti nuo nulio.
- `django-crispy-forms` jau yra `requirements.txt`, bet formos rašomos rankomis su `request.POST.get(...)`.

Tai reiškia, kad HTMX diegimas nėra „perrašymas", o laipsniškas papildymas: kiekvieną veiksmą galima migruoti atskirai, nesulaužant likusios sistemos, nes visi endpoint'ai jau egzistuoja kaip atskiri URL/view'ai.

## 2. Tikslas

Pakeisti pasirinktus veiksmus (užduoties pažymėjimas, statuso keitimas, komentaro/pastabos pridėjimas, filtravimas, kanban) taip, kad jie vyktų **be pilno puslapio perkrovimo**, išlaikant server-side rendering (jokio atskiro JS build'o, jokio JSON API sluoksnio tarp UI ir serverio).

## 3. Etapas 0 — pagrindas (būtina prieš viską kitą)

1. **Įtraukti htmx.js** — statinis failas arba CDN per `<script src="https://unpkg.com/htmx.org@2.x.x" ...>`.
   - Kadangi `django-cors-headers` ir CSP nenustatyti griežtai, paprasčiausia iš pradžių CDN, vėliau (produkcijai) atsisiųsti į `static/js/htmx.min.js` ir servinti per `STATIC_URL` (`crm_project/settings.py:149`).
2. **Sukurti `crm/templates/crm/base.html`** su bendru `<head>` (htmx `<script>`, bendras `<style>`/Tailwind), topbar navigacija ir `{% block content %}`. Tai nebūtina HTMX veikimui, bet be to kiekviename faile reikėtų dubliuoti htmx `<script>` tag'ą 15-oje šablonų — verta padaryti kartu, kad diegimas neužtruktų dvigubai.
3. **CSRF**: HTMX POST/PATCH/DELETE užklausoms reikės CSRF tokeno kiekviename request'e. Standartinis sprendimas — `hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'` ant `<body>` arba globalus JS event listener (`htmx:configRequest`), kuris prideda `X-CSRFToken` iš cookie. Įtraukti į `base.html` vieną kartą.
4. **Serverio pusėje atpažinti HTMX užklausą**: `request.headers.get('HX-Request') == 'true'`. Naudosime šitai kiekviename migruojamame view, kad grąžintume arba pilną puslapį (įprastas GET), arba tik HTML fragmentą (HTMX request).

## 4. Etapas 1 — žemos rizikos, aukštos vertės veiksmai (savaitė 1)

Tikslas: veiksmai, kurie šiuo metu daro `redirect()` po vieno lauko pakeitimo, pakeičiami į in-place atnaujinimą.

### 4.1 Task toggle (`task_toggle_view`, `crm/views.py:399-405`)
- Dabar: POST → pilnas redirect į `lead-detail`.
- Po pakeitimo: mygtukas/checkbox `lead_detail.html` gauna `hx-post="{% url 'task-toggle' task.id %}" hx-target="#task-{{ task.id }}" hx-swap="outerHTML"`.
- View grąžina tik vieno task'o `<li>`/`<tr>` fragmentą (naujas mažas template `crm/templates/crm/partials/_task_item.html`), o ne `redirect`.
- Papildomai: kadangi task'o pažymėjimas keičia ir "pending_tasks" skaitiklį `lead_detail.html`, reikia arba (a) `hx-swap-oob` fragmentui su atnaujintu skaitikliu, arba (b) tikslinti visą tasks bloką (`hx-target="#tasks-block"`).

### 4.2 Lead status mark (`lead_status_mark_view`, `crm/views.py:420-426`)
- Statuso mygtukai lead detalėse → `hx-post`, `hx-target="#lead-status-badge"`, grąžina atnaujintą badge + (out-of-band) activity log įrašą.

### 4.3 Komentaro / pastabos pridėjimas (`lead_comment_add_view`, `crm/views.py:362-371`)
- Forma `lead_detail.html` → `hx-post`, `hx-target="#comments-list"`, `hx-swap="afterbegin"`, forma po sėkmingo submit išsivalo (`hx-on::after-request="this.reset()"`).
- View grąžina tik naują `<li>` komentarui.

### 4.4 Priminimo siuntimas (`lead_reminder_send_view`, `crm/views.py:374-385`)
- Mygtukas → `hx-post`, `hx-target="#reminder-status"`, grąžina trumpą "Priminimas išsiųstas ✓" fragmentą (be redirect).

## 5. Etapas 2 — sąrašai ir filtrai (savaitė 2)

### 5.1 Leadų sąrašas (`lead_list_view`, `crm/views.py:214-260`)
- Paieškos/filtro forma (`lead_list.html:47-60`) → pridėti `hx-get="{% url 'lead-list' %}" hx-trigger="keyup changed delay:400ms, change" hx-target="#leads-table" hx-push-url="true"`.
- Reikia atskirti: jei `q`/`status`/`followup` keičiasi, atnaujinama tik lentelė, ne visas puslapis.
- View pakeitimas: jei `request.headers.get('HX-Request')`, `render(request, 'crm/partials/_lead_table.html', context)`, kitaip — visas `lead_list.html` (kuris `{% include %}` tą patį partial'ą, kad logika nedubliuotų).

### 5.2 Follow-up sąrašas (`followup_list_view`, `crm/views.py:135-155`)
- Analogiškas filtro mygtukų (`today`/`overdue`/`week`) perjungimas be perkrovimo, tas pats `HX-Request` + partial šablono principas.

## 6. Etapas 3 — Pipeline / Kanban (savaitė 3, didžiausia vertė vizualiai)

- `pipeline_view` (`crm/views.py:158-174`) jau grąžina stulpelius pagal statusą.
- HTMX drag-and-drop galimybė: naudoti [`htmx` + [`sortable.js`/`Sortable`] arba paprastesnį variantą be drag'n'drop — kiekvienas lead'o kortelė turi "perkelti į kitą stadiją" mygtukus, kurie `hx-post="{% url 'lead-status-update' lead.id %}"` su `hx-target` į patį kanban stulpelį arba visą pipeline bloką (`hx-swap="outerHTML"` ant kortelės, persikelia vizualiai perkraunant tik kortelę — realaus "drag" be JS bibliotekos HTMX savaime nepadaro, tai reikėtų arba priimti mygtukų UX, arba pridėti lengvą Sortable.js sluoksnį virš HTMX, kuris po drop tiesiog iškviečia `htmx.trigger`).
- **Sprendimas MVP etapui**: pradėti be tikro drag'n'drop — kortelėse mygtukai "→ Kita stadija" per HTMX. Tikras drag'n'drop — atskiras vėlesnis iteracijos žingsnis, jei prireiks.

## 7. Etapas 4 — formos be perkrovimo (savaitė 4, jei liks laiko)

- Lead sukūrimas/redagavimas (`lead_create_view`, `lead_edit_view`) — galima palikti kaip įprastus puslapius (formos nėra dažnai naudojamas veiksmas, rizika/nauda santykis mažesnis), **arba** migruoti į modal'ą: mygtukas "Pridėti leadą" → `hx-get` užkrauna formą į `#modal`, `hx-post` submit'ina be perkrovimo, sėkmės atveju `HX-Trigger` header'is inicijuoja lentelės perkrovimą.
- Rekomendacija: šis žingsnis **paskutinis**, nes duoda mažiausią naudą/pastangų santykį palyginus su 4-6 skyriais.

## 8. Techninis šablonas (pattern), kurį kartosime kiekvienam view

```python
@login_required(login_url='login')
def task_toggle_view(request, pk):
    task = get_object_or_404(Task, pk=pk, lead__owner=request.user)
    task.completed = not task.completed
    task.save()
    Activity.objects.create(lead=task.lead, action='task_toggled', details=task.title, created_by=request.user)

    if request.headers.get('HX-Request'):
        return render(request, 'crm/partials/_task_item.html', {'task': task})
    return redirect('lead-detail', pk=task.lead.pk)
```

- Kiekvienam migruojamam view: (1) sukurti `partials/_xxx.html` fragmentą, (2) pridėti `if request.headers.get('HX-Request')` šaką, (3) senas `redirect()` paliekamas kaip fallback ne-HTMX vartotojams (progressive enhancement — jei JS išjungtas, viskas vis tiek veikia per įprastą POST+redirect).
- Tai reiškia: **nulis rizikos regresijai** — jei kažkas nesuveikia su HTMX, sena elgsena lieka veikianti.

## 9. Testavimo / priėmimo kriterijai kiekvienam etapui

- [ ] Veiksmas suveikia be matomo puslapio "blyksnio" (network tab: tik XHR, ne pilnas document reload)
- [ ] Veikia ir be JS (senas POST+redirect fallback) — patikrinti su išjungtu JS naršyklėje
- [ ] CSRF token'as siunčiamas korektiškai (nėra 403 klaidų)
- [ ] `Activity` log įrašai vis tiek kuriami (verslo logika nepakito, tik transportas)
- [ ] Kelių vartotojų izoliacija nepažeista (owner=request.user filtrai lieka)

## 10. Kas NEKEIČIAMA

- `crm/api_urls.py`, `crm/api_views.py`, `crm/serializers.py` (DRF API) — lieka kaip yra, HTMX su jais nesikerta, nes DRF skirtas React/Skybridge/MCP sluoksniui, o HTMX dirba tiesiai su Django template view'ais.
- `crm/mcp_*.py` — MCP sąsaja nepriklauso nuo UI transporto sluoksnio.
- Duomenų modeliai (`crm/models.py`) — HTMX diegimas nereikalauja jokių migracijų.

## 11. Rekomenduojama diegimo tvarka (santrauka)

1. Etapas 0 (pagrindas: htmx.js + CSRF + `base.html`) — būtina pradžia
2. Etapas 1 (task toggle, status mark, comment add, reminder) — greičiausia matoma nauda
3. Etapas 2 (lead list + followup list filtrai)
4. Etapas 3 (pipeline/kanban mygtukai)
5. Etapas 4 (formos moduose) — tik jei liks laiko/poreikio

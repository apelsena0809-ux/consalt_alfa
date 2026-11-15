import streamlit as st
from src.integration import (
    get_recommendations, get_explanation, get_next_step,
    get_popular_materials, get_all_materials, baseline_recommend,
)

st.set_page_config(page_title="Альфа-Курс — рекомендации", page_icon="📚", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800&display=swap');
:root { --alpha-red:#EF3124; --alpha-black:#0E0E0E; --alpha-bg:#F4F5F6; }
html, body, [class*="css"] { font-family:'Montserrat',Arial,sans-serif; }
.stApp { background:var(--alpha-bg); color:var(--alpha-black); }
.block-container { padding-top:1.7rem; max-width:1220px; }
[data-testid="stSidebar"] { background:#0E0E0E; }
[data-testid="stSidebar"] * { color:#fff !important; }
[data-testid="stSidebar"] [aria-checked="true"] { background:#2a1716; border-left:4px solid var(--alpha-red); }
.hero { padding:2rem 2.2rem; border-radius:22px; color:#fff;
 background:linear-gradient(112deg,#0E0E0E 0%,#34100e 55%,#EF3124 100%);
 margin-bottom:1.35rem; box-shadow:0 12px 30px rgba(14,14,14,.12); }
.hero h1 { color:#fff; font-weight:800; letter-spacing:-.7px; margin:0 0 .45rem 0; }
.hero p { color:#f3e8e7; margin:0; }
.material { background:#fff; border:1px solid #e8e8e8; border-radius:18px;
 padding:1rem 1.2rem; margin:.55rem 0 .9rem 0; box-shadow:0 4px 14px rgba(0,0,0,.035); }
.tag { display:inline-block; padding:4px 10px; margin:2px 5px 6px 0; border-radius:20px;
 background:#f1f2f3; color:#333; font-size:.76rem; font-weight:600; }
.eyebrow { color:#EF3124; text-transform:uppercase; letter-spacing:1.3px; font-size:.72rem; font-weight:800; }
.score-wrap { text-align:center; padding:.35rem; }
.score-ring { width:76px; height:76px; border-radius:50%; display:flex; align-items:center;
 justify-content:center; margin:auto; background:conic-gradient(#EF3124 var(--score),#ececec 0);
 position:relative; font-weight:800; font-size:1.05rem; }
.score-ring:before { content:""; position:absolute; width:61px; height:61px; background:white; border-radius:50%; }
.score-ring span { position:relative; z-index:1; }
div.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
 background:#EF3124; border-color:#EF3124; color:white; border-radius:10px; font-weight:700; }
div.stButton > button, div.stLinkButton > a { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

STAGES = ["Только планирую бизнес", "Запускаю бизнес", "Веду малый/микробизнес", "Развиваю действующий бизнес"]
INDUSTRIES = ["Розничная торговля", "Услуги", "Общепит", "IT / цифровые продукты", "Производство", "Другое"]
TASKS = ["Запуск бизнеса", "Бухгалтерия и налоги", "Маркетинг и продвижение", "Продажи", "Финансы", "Управление и процессы", "Другое"]
EXPERIENCE = ["Начинающий", "Есть небольшой опыт", "Опытный предприниматель"]

@st.cache_data(show_spinner=False)
def cached_catalog():
    return get_all_materials()

def mark_studied(material_id):
    history = st.session_state.setdefault("history", [])
    if material_id not in history:
        history.append(material_id)

def init_state():
    defaults = {
        "page": "Рекомендации",
        "profile": {"stage": STAGES[0], "industry": INDUSTRIES[2],
                    "current_task": TASKS[0], "experience": EXPERIENCE[0]},
        "onboarding_done": False, "history": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)

def material_card(item, key, show_score=False, profile=None):
    title = item.get("title", "Материал")
    url = (item.get("url") or "").strip()
    score = item.get("score")
    st.markdown('<div class="material">', unsafe_allow_html=True)
    left, right = st.columns([5, 1])
    with left:
        if url:
            st.markdown(f"### [{title}]({url})")
        else:
            st.markdown(f"### {title}")
        price = "Бесплатно" if str(item.get("price","free")).lower() in ("free","бесплатно","0") else "Платный"
        st.markdown(
            f'<span class="tag">{item.get("format","Материал")}</span>'
            f'<span class="tag">{price}</span>'
            f'<span class="tag">{item.get("level","Для всех")}</span>'
            f'<span class="tag">{item.get("topic","")}</span>',
            unsafe_allow_html=True
        )
        st.write(item.get("description",""))
        if show_score and profile:
            st.write("**Почему рекомендуем:** " + get_explanation(item, profile))
            st.write("**Следующий шаг:** " + get_next_step(item))
    with right:
        if show_score and score is not None:
            pct=max(0,min(100,round(float(score)*100)))
            st.markdown(f'<div class="score-wrap"><div class="score-ring" style="--score:{pct}%"><span>{pct}%</span></div><small>Совпадение</small></div>',unsafe_allow_html=True)
        if url:
            st.link_button("Открыть материал ↗", url, use_container_width=True)
        else:
            st.caption("Ссылка не добавлена")
        st.button("Отметить изученным", key=f"studied_{key}", on_click=mark_studied,
                  args=(str(item.get("id",key)),), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

init_state()
profile=st.session_state.profile
with st.sidebar:
    st.markdown("## 📚 Альфа-Курс")
    st.caption("Знания в нужный момент")
    pages=["Рекомендации","Библиотека материалов","Мой профиль"]
    page=st.radio("Навигация",pages,index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
    st.session_state.page=page
    st.divider()
    st.caption("Персональный подбор материалов для предпринимателей")

if not st.session_state.onboarding_done:
    st.markdown('<div class="hero"><div class="eyebrow">Альфа-Курс · персональный подбор</div><h1>Найдём полезные материалы для вашего бизнеса</h1><p>Ответьте на несколько вопросов — подборка станет точнее. Онбординг можно пропустить.</p></div>',unsafe_allow_html=True)
    with st.form("onboarding"):
        stage=st.selectbox("На какой стадии ваш бизнес?",STAGES,index=STAGES.index(profile["stage"]))
        industry=st.selectbox("В какой сфере работаете?",INDUSTRIES,index=INDUSTRIES.index(profile["industry"]))
        task=st.selectbox("Какая задача сейчас важнее всего?",TASKS,index=TASKS.index(profile["current_task"]))
        experience=st.selectbox("Какой у вас опыт?",EXPERIENCE,index=EXPERIENCE.index(profile["experience"]))
        c1,c2=st.columns([1,4])
        with c1: submitted=st.form_submit_button("Сохранить профиль",type="primary",use_container_width=True)
        with c2: skipped=st.form_submit_button("Пропустить")
    if submitted:
        st.session_state.profile={"stage":stage,"industry":industry,"current_task":task,"experience":experience}
        st.session_state.onboarding_done=True
        st.rerun()
    if skipped:
        st.session_state.onboarding_done=True
        st.rerun()
    st.info("После онбординга можно изменить ответы в разделе «Мой профиль».")
    st.stop()

catalog=cached_catalog()

if page=="Рекомендации":
    st.markdown('<div class="hero"><div class="eyebrow">Ваша персональная подборка</div><h1>Полезное для следующего шага</h1><p>Подборка учитывает задачу, стадию бизнеса, сферу и историю изучения материалов.</p></div>',unsafe_allow_html=True)
    with st.expander("Уточнить задачу для рекомендаций"):
        with st.form("quick_update"):
            new_task=st.selectbox("Текущая задача",TASKS,index=TASKS.index(profile["current_task"]))
            new_stage=st.selectbox("Стадия бизнеса",STAGES,index=STAGES.index(profile["stage"]))
            new_industry=st.selectbox("Сфера",INDUSTRIES,index=INDUSTRIES.index(profile["industry"]))
            update=st.form_submit_button("Обновить подборку",type="primary")
        if update:
            profile.update({"current_task":new_task,"stage":new_stage,"industry":new_industry})
            st.session_state.profile=profile
            st.rerun()
    recommendations=get_recommendations(profile,st.session_state.history)
    st.caption(f"Найдено {len(recommendations)} рекомендаций из {len(catalog)} материалов")
    for i,item in enumerate(recommendations,1):
        material_card(item,f"recommend_{i}",True,profile)
    with st.expander("Как работает подборка"):
        st.write("Скоринг: 0,5 — совпадение задачи; 0,3 — стадии бизнеса; 0,2 — сферы; бонус 0,05 — материал уже отмечен как изученный.")
        st.write(f"Простой baseline по одной теме нашёл бы {len(baseline_recommend(profile))} материалов.")

elif page=="Библиотека материалов":
    st.markdown('<div class="hero"><div class="eyebrow">База знаний</div><h1>Библиотека материалов</h1><p>Подборка внешних инструкций, сервисов и обучающих ресурсов. Все карточки ведут на исходные сайты.</p></div>',unsafe_allow_html=True)
    topics=["Все темы"]+sorted({x.get("topic","") for x in catalog if x.get("topic")})
    c1,c2=st.columns([2,3])
    with c1: selected_topic=st.selectbox("Тема",topics)
    with c2: query=st.text_input("Поиск по материалам",placeholder="Например, налоги, маркетинг, сотрудники…")
    filtered=catalog
    if selected_topic!="Все темы":
        filtered=[x for x in filtered if x.get("topic")==selected_topic]
    if query.strip():
        q=query.casefold()
        filtered=[x for x in filtered if q in " ".join(str(x.get(k,"")) for k in ("title","description","topic","format")).casefold()]
    st.caption(f"Материалов: {len(filtered)} из {len(catalog)}")
    if not filtered: st.info("По вашему запросу ничего не найдено. Попробуйте изменить тему или поисковый запрос.")
    for i,item in enumerate(filtered,1):
        material_card(item,f"library_{i}")

elif page=="Мой профиль":
    st.markdown('<div class="hero"><div class="eyebrow">Ваши настройки</div><h1>Мой профиль</h1><p>Эти сведения используются для персонализации рекомендаций.</p></div>',unsafe_allow_html=True)
    with st.form("profile_edit"):
        stage=st.selectbox("Стадия бизнеса",STAGES,index=STAGES.index(profile["stage"]))
        industry=st.selectbox("Сфера деятельности",INDUSTRIES,index=INDUSTRIES.index(profile["industry"]))
        task=st.selectbox("Текущая задача",TASKS,index=TASKS.index(profile["current_task"]))
        experience=st.selectbox("Опыт",EXPERIENCE,index=EXPERIENCE.index(profile["experience"]))
        save=st.form_submit_button("Сохранить изменения",type="primary")
    if save:
        st.session_state.profile={"stage":stage,"industry":industry,"current_task":task,"experience":experience}
        st.success("Профиль обновлён.")
        st.rerun()
    st.subheader("История изучения")
    if st.session_state.history:
        st.write(f"Отмечено материалов: {len(st.session_state.history)}")
        by_id={str(x.get("id")):x for x in catalog}
        for mid in st.session_state.history[-20:]:
            item=by_id.get(str(mid))
            if item and item.get("url"): st.markdown(f"- [{item.get('title')}]({item.get('url')})")
            elif item: st.write("- "+item.get("title","Материал"))
    else:
        st.caption("История пока пуста. Отмечайте материалы кнопкой «Отметить изученным».")
    if st.button("Пройти онбординг заново"):
        st.session_state.onboarding_done=False
        st.rerun()

st.divider()
st.caption("Внешние ресурсы принадлежат их владельцам. Перед применением налоговых и правовых инструкций проверяйте актуальность информации на официальных сайтах.")

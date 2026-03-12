from __future__ import annotations

import asyncio
import math
import random
import struct
import wave
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import flet as ft
import flet.canvas as cv

from supabase_client import build_supabase_connection

try:
    import winsound
except ImportError:
    winsound = None

IMAGE_FIT_CONTAIN = getattr(getattr(ft, "ImageFit", None), "CONTAIN", ft.BoxFit.CONTAIN)


LIGHT_PALETTE = {
    "bg": "#F4F8FC",
    "card": "#FFFFFF",
    "line": "#D8E4F0",
    "text": "#203246",
    "muted": "#6E7C8F",
    "accent": "#FFE066",
    "accent_soft": "#FFF3B0",
    "accent_2": "#A8E6CF",
    "nav": "#6FA8DC",
    "nav_soft": "#9DC6E9",
    "nav_active": "#F7C6D9",
    "focus_soft": "#FCE4EC",
    "surface": "#F7FAFD",
    "surface_alt": "#EAF3FB",
    "hero_text": "#FFFFFF",
    "shadow": "#7E90A7",
    "good": "#A8E6CF",
    "warning": "#FFE066",
    "focus": "#F7C6D9",
    "danger": "#FFB8C6",
}

DARK_PALETTE = {
    "bg": "#0F1722",
    "card": "#162231",
    "line": "#2A394B",
    "text": "#E6EEF8",
    "muted": "#9FB0C4",
    "accent": "#E7C955",
    "accent_soft": "#62511B",
    "accent_2": "#5FC6A0",
    "nav": "#4D81C0",
    "nav_soft": "#274866",
    "nav_active": "#A77595",
    "focus_soft": "#4C3142",
    "surface": "#1B293A",
    "surface_alt": "#243547",
    "hero_text": "#F8FBFF",
    "shadow": "#04080E",
    "good": "#4AA37C",
    "warning": "#D8B84A",
    "focus": "#C18AAA",
    "danger": "#C46A78",
}

PALETTE = LIGHT_PALETTE.copy()

HOME_FEATURES = [
    "Распознавание эмоций в игровой форме.",
    "Тренировка внимания и короткой памяти.",
    "Дыхательные практики и спокойные упражнения.",
    "Подсказки для родителей и краткий скрининг.",
]

EMOTION_ITEMS = [
    {"sticker": "😄", "emotion": "Радость", "prompt": "Мальчик получил подарок и широко улыбается.", "color": "#FFF0A8"},
    {"sticker": "😢", "emotion": "Грусть", "prompt": "Девочка потеряла любимую игрушку и хочет плакать.", "color": "#D9E9FF"},
    {"sticker": "😲", "emotion": "Удивление", "prompt": "Ребенок увидел в небе большую радугу.", "color": "#FFE0B2"},
    {"sticker": "😠", "emotion": "Злость", "prompt": "У малыша забрали кубик во время игры.", "color": "#FFD3D3"},
    {"sticker": "😌", "emotion": "Спокойствие", "prompt": "Ребенок сидит у окна, дышит ровно и слушает дождь.", "color": "#D9F3E7"},
]

FOCUS_ITEMS = [
    {"label": "Солнце", "emoji": "☀️"},
    {"label": "Лист", "emoji": "🍃"},
    {"label": "Звезда", "emoji": "⭐"},
    {"label": "Облако", "emoji": "☁️"},
    {"label": "Сердце", "emoji": "💛"},
    {"label": "Капля", "emoji": "💧"},
]

MOVEMENT_TASKS = [
    {
        "title": "Потянись к солнышку",
        "steps": [
            "Подними руки вверх.",
            "Медленно потянись и посчитай до трёх.",
            "Опусти руки и улыбнись.",
        ],
        "stars": 3,
        "focus": 4,
        "emotion": 5,
    },
    {
        "title": "Крылышки бабочки",
        "steps": [
            "Сложи ладони на груди.",
            "Мягко поднимай и опускай кисти, как крылья.",
            "Сделай два спокойных вдоха.",
        ],
        "stars": 3,
        "focus": 5,
        "emotion": 4,
    },
    {
        "title": "Тихая поза",
        "steps": [
            "Сядь удобно и выпрями спину.",
            "Положи руки на колени.",
            "Сделай глубокий вдох и длинный выдох.",
        ],
        "stars": 4,
        "focus": 3,
        "emotion": 6,
    },
]

MEMORY_PAIR_ITEMS = [
    {"pair_id": "sun", "emoji": "☀️", "label": "Солнце"},
    {"pair_id": "rainbow", "emoji": "🌈", "label": "Радуга"},
    {"pair_id": "apple", "emoji": "🍎", "label": "Яблоко"},
    {"pair_id": "bear", "emoji": "🐻", "label": "Мишка"},
]

MUSIC_ITEMS = [
    {
        "id": "bells",
        "emoji": "🎐",
        "title": "Мягкие колокольчики",
        "caption": "тихая мелодия",
        "color": "#FFF0A8",
        "notes": [523.25, 659.25, 783.99, 659.25, 587.33, 659.25],
    },
    {
        "id": "moon",
        "emoji": "🌙",
        "title": "Лунная мелодия",
        "caption": "вечерний покой",
        "color": "#D9E9FF",
        "notes": [392.0, 440.0, 523.25, 440.0, 392.0, 349.23],
    },
    {
        "id": "forest",
        "emoji": "🍃",
        "title": "Тихий лес",
        "caption": "медленный ритм",
        "color": "#D9F3E7",
        "notes": [329.63, 392.0, 440.0, 392.0, 329.63, 293.66],
    },
]

MUSIC_TIMER_OPTIONS = [3, 5, 10]

DRAWING_COLORS = [
    "#203246",
    "#6FA8DC",
    "#FF8FA3",
    "#6BCB96",
    "#FFB347",
    "#A06CD5",
]

DRAWING_BRUSH_SIZES = [4, 8, 14, 22]

RELAX_ITEMS = {
    "Спокойная музыка": "Мягкие мелодии помогают снизить тревожность и легче переключиться.",
    "Звуки дождя": "Ровный звук дождя подходит для короткого отдыха и расслабления.",
    "Океан": "Шум волн поддерживает размеренное дыхание и ощущение безопасности.",
    "Короткая медитация": "Закрой глаза, назови три спокойных цвета и сделай три медленных вдоха.",
}

BREATHING_PHASES = [
    {"title": "Вдох", "prompt": "Вдыхай носом и поднимай плечи мягко.", "progress": 0.25, "color": PALETTE["good"], "seconds": 3},
    {"title": "Пауза", "prompt": "Задержи дыхание на пару секунд.", "progress": 0.5, "color": PALETTE["warning"], "seconds": 2},
    {"title": "Выдох", "prompt": "Медленно выдыхай и расслабляй плечи.", "progress": 0.85, "color": PALETTE["focus"], "seconds": 3},
    {"title": "Отдых", "prompt": "Проверь, как чувствует себя тело после цикла.", "progress": 1.0, "color": PALETTE["accent_2"], "seconds": 2},
]

BREATHING_TARGET_CYCLES = 3

SCREENING_QUESTIONS = [
    "Ребенку сложно удерживать зрительный контакт во время общения.",
    "Ребенок редко откликается на имя с первого раза.",
    "Сложно повторять простые инструкции без дополнительной помощи.",
    "Есть выраженная чувствительность к громким звукам, свету или прикосновениям.",
    "Ребенку трудно включаться в совместную игру со взрослыми или детьми.",
]

SCREENING_OPTIONS = [("Редко", 0), ("Иногда", 1), ("Часто", 2), ("Почти всегда", 3)]

PARENT_SECTIONS = [
    (
        "Что можно наблюдать",
        [
            "Зрительный контакт.",
            "Реакцию на имя и инструкции.",
            "Интерес к совместной игре.",
            "Реакцию на эмоции и смену задач.",
        ],
    ),
    (
        "Советы по взаимодействию",
        [
            "Используйте короткие и понятные фразы.",
            "Показывайте пример перед заданием.",
            "Давайте паузу после инструкции.",
            "Подкрепляйте успех спокойной похвалой.",
        ],
    ),
    (
        "Сенсорные особенности",
        [
            "Учитывайте чувствительность к шуму, свету и прикосновениям.",
            "Подбирайте спокойную среду без перегрузки.",
            "Чередуйте активные задания и расслабление.",
        ],
    ),
    (
        "Когда обратиться к специалисту",
        [
            "Если наблюдаются устойчивые трудности в коммуникации.",
            "Если есть выраженные сенсорные реакции.",
            "Если изменения поведения вызывают беспокойство.",
        ],
    ),
]

MASCOT_PHRASES = [
    "Привет. Давай играть вместе.",
    "Отличная работа. У тебя получается.",
    "Если устал, давай сделаем спокойный вдох.",
    "Ты молодец. Продолжаем маленькими шагами.",
    "Я рядом и помогу пройти задания.",
]

ROBOT_COLORS = {
    "Тёплый": "#FFB35C",
    "Мятный": "#6BB7B1",
    "Розовый": "#F39AB4",
}

PARENT_BADGES = [
    "Семейная поддержка",
    "Новый шаг",
    "Тихий успех",
]


@dataclass
class AppState:
    stars: int = 0
    completed_games: int = 0
    mascot_color: str = ROBOT_COLORS["Тёплый"]
    voice_enabled: bool = False
    screening_result: str = "Скрининг ещё не пройден."
    child_name: str = "Али"
    child_age: str = "6"
    child_strengths: str = "Любит спокойные игры, хорошо реагирует на похвалу и повторение."
    child_characteristics: str = "Лучше воспринимает короткие инструкции, паузы и визуальные подсказки."
    favorite_activity: str = "Карточки эмоций и дыхательные циклы."
    parent_goal: str = "Развивать внимание, спокойное дыхание и уверенное выполнение коротких заданий."
    badges: list[str] = field(default_factory=list)
    focus_history: list[int] = field(default_factory=lambda: [42, 48, 55])
    emotion_history: list[int] = field(default_factory=lambda: [45, 50, 58])
    recent_notes: list[str] = field(default_factory=lambda: ["Старт приложения."])

    @property
    def level(self) -> int:
        return max(1, 1 + self.stars // 12)

    def record_activity(
        self,
        *,
        stars: int = 0,
        focus_change: int = 0,
        emotion_change: int = 0,
        badge: str | None = None,
        note: str | None = None,
        completed_game: bool = False,
    ) -> None:
        self.stars += stars
        if completed_game:
            self.completed_games += 1

        focus = max(10, min(100, self.focus_history[-1] + focus_change))
        emotion = max(10, min(100, self.emotion_history[-1] + emotion_change))
        self.focus_history = (self.focus_history + [focus])[-6:]
        self.emotion_history = (self.emotion_history + [emotion])[-6:]

        if badge and badge not in self.badges:
            self.badges.append(badge)

        if note:
            stamp = datetime.now().strftime("%d.%m %H:%M")
            self.recent_notes = [f"{stamp} - {note}"] + self.recent_notes[:5]


class MobileSupportApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()
        self.supabase_connection = build_supabase_connection()
        self.supabase = self.supabase_connection.client
        self.dark_mode = False
        self.current_section = "home"
        self.child_view = "auth"
        self.child_session_profile: dict[str, str] | None = None
        self.child_username_input = ""
        self.child_password_input = ""
        self.child_auth_error = ""
        self.guidy_open = False
        self.guidy_message = ""
        self.parent_view = "auth"
        self.screening_index = 0
        self.mascot_message = random.choice(MASCOT_PHRASES)
        self.parent_note_draft = ""
        self.parent_session_user_id: str | None = None
        self.parent_session_profile: dict[str, str] | None = None
        self.parent_session_password: str | None = None
        self.parent_children: list[dict[str, str]] = []
        self.active_child_profile: dict[str, str] | None = None
        self.parent_auth_mode = "login"
        self.parent_full_name_input = ""
        self.parent_username_input = ""
        self.parent_password_input = ""
        self.parent_confirm_password_input = ""
        self.parent_auth_error = ""
        self.parent_child_name_input = ""
        self.parent_child_age_input = ""
        self.parent_child_username_input = ""
        self.parent_child_password_input = ""
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False
        self.manage_child_name_input = ""
        self.manage_child_age_input = ""
        self.manage_child_username_input = ""
        self.manage_child_password_input = ""
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False
        self.content_column = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=18)
        self.content_stack = ft.Stack(expand=True, controls=[self.content_column])
        self.root = ft.Container(
            expand=True,
            bgcolor=PALETTE["bg"],
            padding=24,
            content=self.content_stack,
        )

        self.emotion_index = 0
        self.emotion_feedback = "Выбери эмоцию по истории."
        self.emotion_streak = 0
        self.emotion_selected_answer = ""
        self.emotion_intro_visible = True

        self.focus_round = 0
        self.focus_sequence: list[dict[str, str]] = []
        self.focus_answer: list[dict[str, str]] = []
        self.focus_sequence_visible = False
        self.focus_intro_visible = True
        self.focus_preview_token = 0
        self.focus_feedback = "Сначала прочитай правила и нажми «Начать игру»."

        self.movement_index = 0
        self.movement_feedback = "Выбери задание и выполни его в спокойном темпе."

        self.memory_intro_visible = True
        self.memory_preview_visible = False
        self.memory_completed = False
        self.memory_feedback = "Сначала прочитай правила и нажми «Начать игру»."
        self.memory_cards: list[dict[str, str]] = []
        self.memory_selected_indices: list[int] = []
        self.memory_matched_ids: set[str] = set()
        self.memory_moves = 0
        self.memory_pairs_found = 0
        self.memory_locked = False
        self.memory_task_token = 0

        self.music_selected_id = MUSIC_ITEMS[0]["id"]
        self.music_timer_minutes = MUSIC_TIMER_OPTIONS[0]
        self.music_feedback = "Выбери мелодию и нажми «Старт»."
        self.music_is_playing = False
        self.music_remaining_seconds = 0
        self.music_task_token = 0
        self.music_file_paths: dict[str, str] = {}
        self.music_supported = winsound is not None
        self.drawing_selected_color = DRAWING_COLORS[0]
        self.drawing_brush_size = DRAWING_BRUSH_SIZES[1]
        self.drawing_eraser_enabled = False
        self.drawing_shapes: list[cv.Path] = []
        self.drawing_active_path: cv.Path | None = None
        self.drawing_canvas_control: cv.Canvas | None = None

        self.breath_started = False
        self.breath_intro_visible = True
        self.breath_completed = False
        self.breath_phase_index = 0
        self.breath_cycle_count = 0
        self.breath_target_cycles = BREATHING_TARGET_CYCLES
        self.breath_run_token = 0
        self.relax_choice = next(iter(RELAX_ITEMS))

        self.screening_answers = [-1] * len(SCREENING_QUESTIONS)
        self.screening_feedback = "Ответь на вопросы и нажми кнопку подсчёта."

    def configure_page(self) -> None:
        self.page.title = "Поддержка ребёнка"
        self.page.padding = 0
        self.apply_theme()

    def refresh(self) -> None:
        self.root.bgcolor = PALETTE["bg"]
        controls = []
        if self.current_section == "home":
            controls.append(self.build_home_header())
        else:
            controls.append(self.build_profile_topbar())
        controls.append(self.build_current_section())
        self.content_column.controls = controls
        self.content_stack.controls = [self.content_column]
        if self.should_show_guidy():
            self.content_stack.controls.append(self.build_guidy_overlay())
        if not self.page.controls:
            self.page.add(self.root)
        self.page.update()

    def apply_theme(self) -> None:
        palette = DARK_PALETTE if self.dark_mode else LIGHT_PALETTE
        PALETTE.clear()
        PALETTE.update(palette)
        self.page.theme_mode = ft.ThemeMode.DARK if self.dark_mode else ft.ThemeMode.LIGHT
        self.page.theme = ft.Theme(color_scheme_seed=PALETTE["nav"])
        self.page.bgcolor = PALETTE["bg"]
        self.root.bgcolor = PALETTE["bg"]

    def toggle_theme(self, _e: ft.ControlEvent) -> None:
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.refresh()

    def should_show_guidy(self) -> bool:
        return self.current_section == "child" and self.child_session_profile is not None and self.child_view != "auth"

    def current_guidy_name(self) -> str:
        if self.child_session_profile:
            return self.child_session_profile["full_name"]
        return self.state.child_name

    def current_guidy_default_message(self) -> str:
        name = self.current_guidy_name()
        if self.child_view == "hub":
            return f"Привет, {name}. Я Guidy. Могу подсказать, с чего начать."
        if self.child_view == "games":
            return "Выбери игру, а я коротко объясню, что делать."
        if self.child_view == "emotion_game":
            return "Прочитай историю и выбери, какую эмоцию чувствует герой."
        if self.child_view == "focus_game":
            return "Смотри внимательно на порядок картинок и потом повторяй его."
        if self.child_view == "memory_game":
            return "Запомни карточки и ищи одинаковые пары без спешки."
        if self.child_view == "movement_game":
            return "Повторяй шаги спокойно. Здесь не нужна скорость."
        if self.child_view == "breath_game":
            return "Дыши медленно и следуй подсказкам по шагам."
        if self.child_view == "music":
            return "Выбери спокойную мелодию, нажми старт и просто отдыхай."
        if self.child_view == "drawing":
            return "Выбери цвет и рисуй свободно. Здесь нет неправильного ответа."
        return "Я рядом и помогу тебе короткими подсказками."

    def current_guidy_reply(self, action: str) -> str:
        if action == "support":
            return "У тебя всё получится. Можно делать маленькими спокойными шагами."
        if action == "calm":
            return "Сделай медленный вдох носом и длинный мягкий выдох ртом."

        if self.child_view == "hub":
            if action == "explain":
                return "На этом экране можно открыть игры или рисование. Выбери то, что тебе сейчас больше нравится."
            return "Если хочется спокойствия, начни с музыки, дыхания или рисования."
        if self.child_view == "games":
            if action == "explain":
                return "Здесь собраны короткие игры: эмоции, фокус, пары, движение, музыка и дыхание."
            return "Если хочешь что-то тихое, выбери дыхание. Если хочешь подумать, выбери фокус или пары."
        if self.child_view == "emotion_game":
            if action == "explain":
                return "Сначала прочитай историю, потом посмотри на варианты и выбери подходящую эмоцию."
            return "Смотри на лицо героя и на слова в истории. Они подскажут правильный ответ."
        if self.child_view == "focus_game":
            if action == "explain":
                return "Сначала запоминай последовательность, а потом нажимай картинки в таком же порядке."
            return "Не торопись. Лучше запомнить две-три картинки хорошо, чем спешить."
        if self.child_view == "memory_game":
            if action == "explain":
                return "Карточки сначала открываются, потом переворачиваются. Нужно найти одинаковые пары."
            return "Запоминай, где лежали картинки. Ищи сначала самые знакомые пары."
        if self.child_view == "movement_game":
            if action == "explain":
                return "Читай шаги сверху вниз и повторяй их в удобном для себя темпе."
            return "Сделай одно движение за раз и спокойно дойди до конца задания."
        if self.child_view == "breath_game":
            if action == "explain":
                return "Нажми старт и просто следуй за фазами дыхания. Игра сама проведёт тебя по циклам."
            return "Сейчас главное дышать мягко и ровно. Спешить не нужно."
        if self.child_view == "music":
            if action == "explain":
                return "Выбери мелодию и время, потом нажми старт. Можно просто слушать и отдыхать."
            return "Сядь поудобнее, расслабь плечи и спокойно слушай музыку."
        if self.child_view == "drawing":
            if action == "explain":
                return "На белом холсте можно выбирать цвет, менять толщину кисти, включать ластик и очищать рисунок."
            return "Можно начать с простых линий или кружков, а потом добавить цвета."
        return self.current_guidy_default_message()

    def toggle_guidy(self, _e: ft.ControlEvent) -> None:
        self.guidy_open = not self.guidy_open
        if self.guidy_open:
            self.guidy_message = self.current_guidy_default_message()
        self.refresh()

    def use_guidy_action(self, action: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.guidy_open = True
            self.guidy_message = self.current_guidy_reply(action)
            self.refresh()

        return handler

    def build_guidy_overlay(self) -> ft.Container:
        panel_controls: list[ft.Control] = []
        if self.guidy_open:
            panel_controls.append(
                ft.Container(
                    width=320,
                    bgcolor=PALETTE["card"],
                    border=ft.Border.all(1, PALETTE["line"]),
                    border_radius=28,
                    padding=18,
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=22,
                            color=ft.Colors.with_opacity(0.14, PALETTE["shadow"]),
                            offset=ft.Offset(0, 10),
                        )
                    ],
                    content=ft.Column(
                        spacing=14,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Row(
                                        spacing=10,
                                        controls=[
                                            ft.Container(
                                                width=40,
                                                height=40,
                                                border_radius=20,
                                                bgcolor=PALETTE["accent"],
                                                alignment=ft.Alignment(0, 0),
                                                content=ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color=PALETTE["text"], size=22),
                                            ),
                                            ft.Column(
                                                spacing=2,
                                                controls=[
                                                    ft.Text("Guidy", size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                                    ft.Text("Помощник рядом", size=12, color=PALETTE["muted"]),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.IconButton(ft.Icons.CLOSE_ROUNDED, icon_color=PALETTE["muted"], on_click=self.toggle_guidy),
                                ],
                            ),
                            ft.Text(
                                self.guidy_message or self.current_guidy_default_message(),
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text"],
                            ),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    self.guidy_action_button("Объясни", "explain"),
                                    self.guidy_action_button("Что дальше?", "next"),
                                ],
                            ),
                            ft.Row(
                                spacing=10,
                                controls=[
                                    self.guidy_action_button("Поддержи", "support"),
                                    self.guidy_action_button("Спокойно", "calm"),
                                ],
                            ),
                        ],
                    ),
                )
            )

        panel_controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.Container(
                        bgcolor=PALETTE["surface"],
                        border=ft.Border.all(1, PALETTE["line"]),
                        border_radius=999,
                        padding=ft.Padding.symmetric(horizontal=14, vertical=10),
                        content=ft.Text("Guidy", size=13, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                    ),
                    ft.Container(
                        width=62,
                        height=62,
                        border_radius=31,
                        gradient=ft.LinearGradient(
                            colors=[PALETTE["nav"], PALETTE["accent_2"]],
                            begin=ft.Alignment(-1, -1),
                            end=ft.Alignment(1, 1),
                        ),
                        shadow=[
                            ft.BoxShadow(
                                blur_radius=20,
                                color=ft.Colors.with_opacity(0.18, PALETTE["shadow"]),
                                offset=ft.Offset(0, 8),
                            )
                        ],
                        ink=True,
                        on_click=self.toggle_guidy,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(ft.Icons.SMART_TOY_ROUNDED, color=PALETTE["hero_text"], size=30),
                    ),
                ],
            )
        )

        return ft.Container(
            right=0,
            bottom=0,
            padding=ft.Padding.only(right=6, bottom=6),
            content=ft.Column(
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=panel_controls,
            ),
        )

    def guidy_action_button(self, text: str, action: str) -> ft.Container:
        return ft.Container(
            expand=1,
            height=48,
            border_radius=16,
            bgcolor=PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            ink=True,
            on_click=self.use_guidy_action(action),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                text,
                size=14,
                weight=ft.FontWeight.W_700,
                color=PALETTE["text"],
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def theme_toggle_button(self, on_hero: bool = False) -> ft.Container:
        icon = ft.Icons.LIGHT_MODE_ROUNDED if self.dark_mode else ft.Icons.DARK_MODE_ROUNDED
        background = ft.Colors.with_opacity(0.22, ft.Colors.WHITE) if on_hero else PALETTE["card"]
        border_color = ft.Colors.with_opacity(0.18, ft.Colors.WHITE) if on_hero else PALETTE["line"]
        icon_color = PALETTE["hero_text"] if on_hero else PALETTE["text"]
        return ft.Container(
            width=52,
            height=52,
            border_radius=18,
            bgcolor=background,
            border=ft.Border.all(1, border_color),
            alignment=ft.Alignment(0, 0),
            ink=True,
            on_click=self.toggle_theme,
            content=ft.Icon(icon, color=icon_color, size=24),
        )

    def build_home_header(self) -> ft.Container:
        return ft.Container(
            border_radius=34,
            gradient=ft.LinearGradient(
                colors=[PALETTE["nav"], PALETTE["nav_soft"]],
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            padding=24,
            shadow=[
                ft.BoxShadow(
                    blur_radius=24,
                    color=ft.Colors.with_opacity(0.14, PALETTE["shadow"]),
                    offset=ft.Offset(0, 12),
                )
            ],
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        "\u041f\u043e\u0434\u0434\u0435\u0440\u0436\u043a\u0430 \u0440\u0435\u0431\u0435\u043d\u043a\u0430",
                                        size=29,
                                        weight=ft.FontWeight.W_700,
                                        color=PALETTE["hero_text"],
                                    ),
                                    ft.Text(
                                        "\u041f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 \u043f\u043e\u043c\u043e\u0433\u0430\u0435\u0442 \u0440\u0435\u0431\u0435\u043d\u043a\u0443 \u0442\u0440\u0435\u043d\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u044d\u043c\u043e\u0446\u0438\u0438, \u0432\u043d\u0438\u043c\u0430\u043d\u0438\u0435 \u0438 \u0441\u043f\u043e\u043a\u043e\u0439\u043d\u043e \u0432\u044b\u043f\u043e\u043b\u043d\u044f\u0442\u044c \u043a\u043e\u0440\u043e\u0442\u043a\u0438\u0435 \u0437\u0430\u0434\u0430\u043d\u0438\u044f.",
                                        size=14,
                                        color=PALETTE["hero_text"],
                                    ),
                                ],
                            ),
                            ft.Column(
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    self.theme_toggle_button(on_hero=True),
                                    self.art_panel("home", frame=72, image=56),
                                ],
                            ),
                        ],
                    ),
                    ft.Text(
                        "\u041d\u0430 \u0433\u043b\u0430\u0432\u043d\u043e\u043c \u044d\u043a\u0440\u0430\u043d\u0435 \u0432\u044b\u0431\u0435\u0440\u0438 \u043f\u0440\u043e\u0444\u0438\u043b\u044c \u0440\u0435\u0431\u0435\u043d\u043a\u0430 \u0438\u043b\u0438 \u0440\u043e\u0434\u0438\u0442\u0435\u043b\u044f, \u0447\u0442\u043e\u0431\u044b \u043e\u0442\u043a\u0440\u044b\u0442\u044c \u043d\u0443\u0436\u043d\u044b\u0439 \u0440\u0430\u0437\u0434\u0435\u043b.",
                        color=PALETTE["hero_text"],
                        size=14,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        self.supabase_status_text(prefix="Supabase"),
                        color=self.supabase_status_color(),
                        size=13,
                    ),
                ],
            ),
        )

    def build_header(self) -> ft.Container:
        if self.current_section == "home":
            title = "Поддержка ребёнка"
            subtitle = "Спокойный мобильный помощник для ребёнка и родителя."
            art = "home"
            chips = [
                self.hero_chip("Роли", "2"),
                self.hero_chip("Игры", "4"),
            ]
        elif self.current_section == "child":
            title = self.state.child_name
            subtitle = "Игры, дыхание и понятные короткие задания."
            art = "child"
            chips = [
                self.hero_chip("Звёзды", str(self.state.stars)),
                self.hero_chip("Уровень", str(self.state.level)),
                self.hero_chip("Игры", str(self.state.completed_games)),
            ]
        else:
            title = "Профиль родителя"
            subtitle = "Данные ребёнка, достижения и домашние заметки."
            art = "parent"
            chips = [
                self.hero_chip("Значки", str(len(self.state.badges))),
                self.hero_chip("Фокус", f"{self.state.focus_history[-1]}%"),
                self.hero_chip("Эмоции", f"{self.state.emotion_history[-1]}%"),
            ]

        return ft.Container(
            border_radius=34,
            gradient=ft.LinearGradient(
                colors=[PALETTE["nav"], PALETTE["nav_soft"]],
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            padding=24,
            shadow=[
                ft.BoxShadow(
                    blur_radius=24,
                    color=ft.Colors.with_opacity(0.14, PALETTE["shadow"]),
                    offset=ft.Offset(0, 12),
                )
            ],
            content=ft.Column(
                spacing=18,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Text(title, size=29, weight=ft.FontWeight.W_700, color=PALETTE["hero_text"]),
                                    ft.Text(subtitle, size=14, color=PALETTE["hero_text"]),
                                ],
                            ),
                            self.art_panel(art, frame=72, image=56),
                        ],
                    ),
                    ft.Text(
                        f"Робот: {self.mascot_message}",
                        color=PALETTE["hero_text"],
                        size=14,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Row(
                        wrap=True,
                        spacing=10,
                        run_spacing=10,
                        controls=chips,
                    ),
                ],
            ),
        )

    def build_profile_topbar(self) -> ft.Row:
        if self.current_section == "child":
            profile_title = "Профиль ребёнка"
        elif self.parent_view == "auth":
            profile_title = "Регистрация родителя" if self.parent_auth_mode == "register" else "Вход родителя"
        else:
            profile_title = "Профиль родителя"
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    border_radius=18,
                    bgcolor=PALETTE["card"],
                    border=ft.Border.all(1, PALETTE["line"]),
                    alignment=ft.Alignment(0, 0),
                    content=ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=PALETTE["text"], on_click=self.navigate_to("home")),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Container(
                        bgcolor=PALETTE["surface"],
                        border=ft.Border.all(1, PALETTE["line"]),
                        border_radius=999,
                        padding=ft.Padding.symmetric(horizontal=16, vertical=12),
                        content=ft.Text(profile_title, color=PALETTE["text"], size=14, weight=ft.FontWeight.W_600),
                    ),
                ),
                self.theme_toggle_button(),
            ],
        )

    def build_current_section(self) -> ft.Control:
        if self.current_section == "home":
            return self.build_home()
        if self.current_section == "child":
            return self.build_child_profile()
        return self.build_parent_profile()

    def build_home(self) -> ft.Column:
        return ft.Column(
            spacing=18,
            controls=[
                ft.Text("Выбери профиль", size=16, weight=ft.FontWeight.W_600, color=PALETTE["muted"]),
                self.role_tile("Ребёнок", "Играть и учиться", ft.Icons.MOOD, self.navigate_to("child"), [PALETTE["accent"], PALETTE["accent_soft"]], art="child"),
                self.role_tile("Родитель", "Следить за прогрессом", ft.Icons.FAMILY_RESTROOM, self.navigate_to("parent"), [PALETTE["nav_active"], PALETTE["focus_soft"]], art="parent"),
                ft.Row(
                    spacing=8,
                    controls=[
                        self.soft_chip("Спокойно"),
                        self.soft_chip("Современно"),
                        self.soft_chip("Понятно"),
                    ],
                ),
            ],
        )

    def build_child_profile(self) -> ft.Column:
        if self.child_view == "auth" or not self.child_session_profile:
            return self.build_child_auth()
        if self.child_view == "hub":
            return self.build_child_hub()
        if self.child_view == "games":
            return self.build_games_menu()
        if self.child_view == "emotion_game":
            return self.build_emotion_game()
        if self.child_view == "focus_game":
            return self.build_focus_game()
        if self.child_view == "music":
            return self.build_music_room()
        if self.child_view == "drawing":
            return self.build_drawing_room()
        if self.child_view == "memory_game":
            return self.build_memory_game()
        if self.child_view == "movement_game":
            return self.build_movement_game()
        if self.child_view == "breath_game":
            return self.build_breath_game()
        self.child_view = "hub"
        return self.build_child_hub()

    def build_child_auth(self) -> ft.Column:
        status_text = self.child_auth_error or "Войди по логину и паролю ребёнка."
        status_color = "#C95A6A" if self.child_auth_error else PALETTE["muted"]
        return ft.Column(
            spacing=14,
            controls=[
                self.card(
                    "Вход ребёнка",
                    "Регистрации здесь нет. Логин и пароль создаёт родитель.",
                    controls=[
                        ft.Container(
                            bgcolor=PALETTE["surface"],
                            border=ft.Border.all(1, PALETTE["line"]),
                            border_radius=18,
                            padding=14,
                            content=ft.Text(
                                self.supabase_status_text(prefix="Онлайн база"),
                                color=self.supabase_status_color(),
                                size=13,
                            ),
                        ),
                        self.profile_field("Логин ребёнка", self.child_username_input, self.set_child_username_input),
                        self.profile_field(
                            "Пароль ребёнка",
                            self.child_password_input,
                            self.set_child_password_input,
                            password=True,
                            can_reveal_password=True,
                            on_submit=self.submit_child_auth,
                        ),
                        ft.Text(status_text, color=status_color, size=14),
                        self.app_button("Войти", self.submit_child_auth, PALETTE["nav"], color=PALETTE["hero_text"]),
                        self.app_button("На главный экран", self.navigate_to("home"), PALETTE["surface"]),
                    ],
                )
            ],
        )

    def build_parent_profile(self) -> ft.Column:
        if self.parent_view != "auth" and not self.parent_session_user_id:
            self.reset_parent_access()
        if self.parent_view == "auth":
            return self.build_parent_auth()
        if self.parent_view == "hub":
            return self.build_parent_hub()
        if self.parent_view == "add_child":
            return ft.Column(
                spacing=12,
                controls=[
                    self.sub_back("Меню", self.set_parent_view("hub")),
                    self.build_parent_add_child_card(),
                    self.build_parent_children_card(),
                ],
            )
        if self.parent_view == "manage":
            return ft.Column(
                spacing=12,
                controls=[
                    self.sub_back("Меню", self.set_parent_view("hub")),
                    self.build_parent_management_card(),
                    self.build_parent_children_card(),
                ],
            )
        self.parent_view = "hub"
        return self.build_parent_hub()

    def build_parent_auth(self) -> ft.Column:
        status_text = self.parent_auth_error or (
            "Создай аккаунт родителя, если входишь впервые."
            if self.parent_auth_mode == "register"
            else "Войди по username и паролю, чтобы открыть раздел родителя."
        )
        status_color = "#C95A6A" if self.parent_auth_error else PALETTE["muted"]
        auth_controls: list[ft.Control] = [
            ft.Container(
                bgcolor=PALETTE["surface"],
                border=ft.Border.all(1, PALETTE["line"]),
                border_radius=18,
                padding=14,
                content=ft.Text(
                    self.supabase_status_text(prefix="Онлайн база"),
                    color=self.supabase_status_color(),
                    size=13,
                ),
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self.app_button(
                        "Вход",
                        self.set_parent_auth_mode("login"),
                        PALETTE["nav"] if self.parent_auth_mode == "login" else PALETTE["surface"],
                        color=PALETTE["hero_text"] if self.parent_auth_mode == "login" else PALETTE["text"],
                        expand=1,
                    ),
                    self.app_button(
                        "Регистрация",
                        self.set_parent_auth_mode("register"),
                        PALETTE["nav"] if self.parent_auth_mode == "register" else PALETTE["surface"],
                        color=PALETTE["hero_text"] if self.parent_auth_mode == "register" else PALETTE["text"],
                        expand=1,
                    ),
                ],
            )
        ]
        if self.parent_auth_mode == "register":
            auth_controls.extend(
                [
                    self.profile_field("ФИО", self.parent_full_name_input, self.set_parent_full_name_input),
                    self.profile_field("Username", self.parent_username_input, self.set_parent_username_input),
                    self.profile_field(
                        "Пароль",
                        self.parent_password_input,
                        self.set_parent_password_input,
                        password=True,
                        can_reveal_password=True,
                        on_submit=self.submit_parent_auth,
                    ),
                    self.profile_field(
                        "Подтверждение пароля",
                        self.parent_confirm_password_input,
                        self.set_parent_confirm_password_input,
                        password=True,
                        can_reveal_password=True,
                        on_submit=self.submit_parent_auth,
                    ),
                ]
            )
        else:
            auth_controls.extend(
                [
                    self.profile_field("Username", self.parent_username_input, self.set_parent_username_input),
                    self.profile_field(
                        "Пароль",
                        self.parent_password_input,
                        self.set_parent_password_input,
                        password=True,
                        can_reveal_password=True,
                        on_submit=self.submit_parent_auth,
                    ),
                ]
            )
        auth_controls.extend(
            [
                ft.Text(status_text, color=status_color, size=14),
                self.app_button(
                    "Зарегистрироваться" if self.parent_auth_mode == "register" else "Войти",
                    self.submit_parent_auth,
                    PALETTE["nav"],
                ),
                self.app_button("На главный экран", self.navigate_to("home"), PALETTE["surface"]),
            ]
        )
        return ft.Column(
            spacing=14,
            controls=[
                self.card(
                    "Авторизация родителя",
                    "Вход родителя работает через Supabase RPC по username и паролю.",
                    controls=auth_controls,
                )
            ],
        )

    def build_child_hub(self) -> ft.Column:
        return ft.Column(
            spacing=14,
            controls=[
                self.hero_card(
                    self.state.child_name,
                    f"{self.state.child_age} лет",
                    ft.Icons.SENTIMENT_VERY_SATISFIED,
                    [PALETTE["accent"], PALETTE["accent_2"]],
                    art="child",
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.icon_tile("Игры", "6 игр", ft.Icons.GAMES, self.set_child_view("games"), [PALETTE["accent"], PALETTE["accent_2"]], art="games"),
                        self.icon_tile("Рисование", "холст", ft.Icons.BRUSH_ROUNDED, self.set_child_view("drawing"), [PALETTE["focus"], PALETTE["surface"]], art=None),
                    ],
                ),
            ],
        )

    def build_games_menu(self) -> ft.Column:
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Профиль", self.set_child_view("hub")),
                self.hero_card(
                    "Игры",
                    "Короткие игровые задания без лишнего текста.",
                    ft.Icons.GAMES,
                    [PALETTE["nav"], PALETTE["nav_soft"]],
                    art="games",
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.icon_tile("Эмоции", "лицо", ft.Icons.PSYCHOLOGY, self.set_child_view("emotion_game"), [PALETTE["accent"], PALETTE["surface"]], art="emotions"),
                        self.icon_tile("Фокус", "память", ft.Icons.CENTER_FOCUS_STRONG, self.set_child_view("focus_game"), [PALETTE["focus"], PALETTE["surface"]], art="focus"),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.icon_tile("Пары", "найди", ft.Icons.STYLE, self.set_child_view("memory_game"), [PALETTE["warning"], PALETTE["surface"]], art=None),
                        self.icon_tile("Движение", "шаг", ft.Icons.DIRECTIONS_RUN, self.set_child_view("movement_game"), [PALETTE["accent_2"], PALETTE["surface"]], art="movement"),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.icon_tile("Музыка", "слушай", ft.Icons.MUSIC_NOTE, self.set_child_view("music"), [PALETTE["nav"], PALETTE["surface"]], art=None),
                        self.icon_tile("Дыхание", "тихо", ft.Icons.AIR, self.set_child_view("breath_game"), [PALETTE["nav_active"], PALETTE["surface"]], art="calm"),
                    ],
                ),
            ],
        )

    def build_emotion_game(self) -> ft.Column:
        emotion_item = EMOTION_ITEMS[self.emotion_index]
        if self.emotion_intro_visible:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Эмоции",
                        [
                            ft.Container(
                                width=132,
                                height=132,
                                bgcolor=emotion_item["color"],
                                border_radius=34,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text(emotion_item["sticker"], size=76, text_align=ft.TextAlign.CENTER),
                            ),
                            ft.Text(
                                "Прочитай короткую историю и выбери, какую эмоцию чувствует герой.",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Смотри на стикер, читай текст и нажимай на правильный ответ.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Начать игру", self.start_emotion_game, PALETTE["accent"]),
                        ],
                    ),
                ],
            )
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                self.game_shell(
                    "Эмоции",
                    [
                        ft.Container(
                            width=132,
                            height=132,
                            bgcolor=emotion_item["color"],
                            border_radius=34,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(emotion_item["sticker"], size=76, text_align=ft.TextAlign.CENTER),
                        ),
                        ft.Text(
                            emotion_item["prompt"],
                            size=21,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        *[
                                            self.emotion_option_tile(item, emotion_item["emotion"])
                                            for item in row_items
                                        ],
                                        *([ft.Container(expand=1)] if len(row_items) == 1 else []),
                                    ],
                                )
                                for row_items in self.chunked(EMOTION_ITEMS, 2)
                            ],
                        ),
                        ft.Text(
                            self.emotion_feedback,
                            color=self.emotion_feedback_color(),
                            size=18,
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text(
                            f"Серия правильных ответов: {self.emotion_streak}",
                            color=PALETTE["muted"],
                            size=15,
                            weight=ft.FontWeight.W_600,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        self.app_button("Дальше", self.next_emotion, PALETTE["accent"]),
                    ],
                ),
            ],
        )

    def build_focus_game(self) -> ft.Column:
        if self.focus_intro_visible:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Фокус",
                        [
                            self.svg_figure("focus", width=112, height=112),
                            ft.Text(
                                "Запомни порядок картинок. Потом они исчезнут, и нужно собрать тот же порядок.",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Сначала посмотри внимательно, потом нажимай карточки снизу в таком же порядке.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Начать игру", self.start_focus_round, PALETTE["accent"]),
                        ],
                    ),
                ],
            )

        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                self.game_shell(
                    "Фокус",
                    [
                        ft.Text(self.focus_title(), size=20, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                        ft.Container(
                            width=220,
                            height=108,
                            bgcolor=PALETTE["surface"],
                            border=ft.Border.all(1, PALETTE["line"]),
                            border_radius=28,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(self.focus_sequence_text(), size=28, text_align=ft.TextAlign.CENTER),
                        ),
                        ft.Text(self.focus_feedback, color=PALETTE["text"], size=17, weight=ft.FontWeight.W_700, text_align=ft.TextAlign.CENTER),
                        ft.Text(self.focus_answer_text(), color=PALETTE["muted"], size=16, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                        self.app_button("Новый раунд", self.start_focus_round, PALETTE["accent"]),
                        self.app_button("Очистить", self.clear_focus_answer, PALETTE["surface"]),
                        ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        self.compact_button(
                                            f"{item['emoji']} {item['label']}",
                                            lambda _e, selected=item: self.add_focus_answer(selected),
                                        )
                                        for item in row_items
                                    ],
                                )
                                for row_items in self.chunked(FOCUS_ITEMS, 2)
                            ],
                        ),
                        self.app_button("Проверить", self.check_focus_answer, PALETTE["nav"]),
                    ],
                ),
            ],
        )

    def build_memory_game(self) -> ft.Column:
        if self.memory_intro_visible:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Пары",
                        [
                            ft.Container(
                                width=112,
                                height=112,
                                border_radius=32,
                                bgcolor="#FFF1C9",
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("🃏", size=64, text_align=ft.TextAlign.CENTER),
                            ),
                            ft.Text(
                                "Карточки будут открыты 2 секунды, потом перевернутся. Запомни их и найди одинаковые пары.",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Открывай по две карточки. Если они одинаковые, пара останется открытой.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Начать игру", self.start_memory_game, PALETTE["accent"]),
                        ],
                    ),
                ],
            )

        if self.memory_completed:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Ура!",
                        [
                            ft.Container(
                                width=112,
                                height=112,
                                border_radius=32,
                                bgcolor=PALETTE["accent_2"],
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text("🎉", size=64, text_align=ft.TextAlign.CENTER),
                            ),
                            ft.Text(
                                "Ты нашёл все пары. Отличная память!",
                                size=22,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Ходов: {self.memory_moves}. Пары: {self.memory_pairs_found}.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Сыграть ещё", self.start_memory_game, PALETTE["accent"]),
                        ],
                    ),
                ],
            )

        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                self.game_shell(
                    "Пары",
                    [
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                self.soft_chip(f"Ходы: {self.memory_moves}"),
                                self.soft_chip(f"Пары: {self.memory_pairs_found}/{len(self.memory_cards) // 2 if self.memory_cards else 0}"),
                            ],
                        ),
                        ft.Text(
                            self.memory_feedback,
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Column(
                            spacing=10,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        *[
                                            self.memory_card_tile(card, index)
                                            for index, card in row_items
                                        ],
                                        *([ft.Container(expand=1)] if len(row_items) == 1 else []),
                                    ],
                                )
                                for row_items in self.chunked(list(enumerate(self.memory_cards)), 2)
                            ],
                        ),
                        self.app_button("Новая игра", self.start_memory_game, PALETTE["accent"]),
                    ],
                ),
            ],
        )

    def build_music_room(self) -> ft.Column:
        track = self.current_music_item()
        status_text = self.music_feedback
        if self.music_is_playing and self.music_remaining_seconds > 0:
            status_text = f"Сейчас играет: {track['title']}. Осталось {self.format_music_remaining()}."
        elif not self.music_supported:
            status_text = "Музыка сейчас работает только в Windows desktop-сборке."

        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                ft.Container(
                    border_radius=30,
                    gradient=ft.LinearGradient(
                        colors=[track["color"], "#FFFFFF"],
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                    ),
                    border=ft.Border.all(1, PALETTE["line"]),
                    padding=22,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("Музыка", size=16, color=PALETTE["muted"], weight=ft.FontWeight.W_600),
                                    ft.Text(track["title"], size=28, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                    ft.Text(track["caption"], size=16, color=PALETTE["text"]),
                                    self.soft_chip("Отдельный музыкальный блок"),
                                ],
                            ),
                            ft.Container(
                                width=92,
                                height=92,
                                border_radius=28,
                                bgcolor=ft.Colors.with_opacity(0.34, ft.Colors.WHITE),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Text(track["emoji"], size=54, text_align=ft.TextAlign.CENTER),
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    status_text,
                    size=17,
                    weight=ft.FontWeight.W_700,
                    color=PALETTE["text"],
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text("Выбери мелодию", size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Row(
                            spacing=10,
                            controls=[
                                *[self.music_option_tile(item) for item in row_items],
                                *([ft.Container(expand=1)] if len(row_items) == 1 else []),
                            ],
                        )
                        for row_items in self.chunked(MUSIC_ITEMS, 2)
                    ],
                ),
                ft.Text("Выбери время", size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                ft.Row(
                    spacing=10,
                    controls=[self.music_timer_chip(minutes) for minutes in MUSIC_TIMER_OPTIONS],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.app_button("Старт", self.start_music, PALETTE["accent"], expand=1),
                        self.app_button("Стоп", self.stop_music, PALETTE["surface"], expand=1),
                    ],
                ),
            ],
        )

    def build_drawing_room(self) -> ft.Column:
        canvas = cv.Canvas(shapes=self.drawing_shapes, expand=True)
        self.drawing_canvas_control = canvas

        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Профиль", self.set_child_view("hub")),
                ft.Container(
                    border_radius=30,
                    gradient=ft.LinearGradient(
                        colors=[PALETTE["focus"], "#FFFFFF"],
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                    ),
                    border=ft.Border.all(1, PALETTE["line"]),
                    padding=22,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Column(
                                spacing=8,
                                controls=[
                                    ft.Text("Рисование", size=16, color=PALETTE["muted"], weight=ft.FontWeight.W_600),
                                    ft.Text("Спокойный белый холст", size=28, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                    ft.Text("Выбирай цвет, толщину кисти и рисуй пальцем или мышью.", size=16, color=PALETTE["text"]),
                                    self.soft_chip("Отдельный блок рисования"),
                                ],
                            ),
                            ft.Container(
                                width=92,
                                height=92,
                                border_radius=28,
                                bgcolor=ft.Colors.with_opacity(0.34, ft.Colors.WHITE),
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.BRUSH_ROUNDED, size=48, color=PALETTE["text"]),
                            ),
                        ],
                    ),
                ),
                self.card(
                    "Инструменты",
                    controls=[
                        ft.Text("Цвет", size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                        ft.Row(
                            spacing=10,
                            wrap=True,
                            run_spacing=10,
                            controls=[self.drawing_color_swatch(color) for color in DRAWING_COLORS],
                        ),
                        ft.Text("Толщина кисти", size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                        ft.Row(
                            spacing=10,
                            controls=[self.drawing_brush_chip(size) for size in DRAWING_BRUSH_SIZES],
                        ),
                        ft.Row(
                            spacing=10,
                            controls=[
                                self.app_button(
                                    "Ластик",
                                    self.toggle_drawing_eraser,
                                    PALETTE["nav"] if self.drawing_eraser_enabled else PALETTE["surface"],
                                    color=PALETTE["hero_text"] if self.drawing_eraser_enabled else PALETTE["text"],
                                    expand=1,
                                ),
                                self.app_button("Очистить", self.clear_drawing_canvas, PALETTE["accent"], expand=1),
                            ],
                        ),
                    ],
                ),
                ft.Container(
                    height=430,
                    border_radius=30,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    bgcolor=ft.Colors.WHITE,
                    border=ft.Border.all(2, PALETTE["line"]),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=18,
                            color=ft.Colors.with_opacity(0.08, PALETTE["shadow"]),
                            offset=ft.Offset(0, 8),
                        )
                    ],
                    content=ft.GestureDetector(
                        expand=True,
                        drag_interval=0,
                        on_tap_up=self.draw_tap_dot,
                        on_pan_start=self.start_drawing_stroke,
                        on_pan_update=self.extend_drawing_stroke,
                        on_pan_end=self.finish_drawing_stroke,
                        content=canvas,
                    ),
                ),
            ],
        )

    def build_movement_game(self) -> ft.Column:
        task = MOVEMENT_TASKS[self.movement_index]
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                ft.Container(
                    border_radius=30,
                    gradient=ft.LinearGradient(
                        colors=[PALETTE["accent_2"], "#E6FFF4"],
                        begin=ft.Alignment(-1, -1),
                        end=ft.Alignment(1, 1),
                    ),
                    border=ft.Border.all(1, PALETTE["line"]),
                    padding=22,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Column(
                                        spacing=8,
                                        controls=[
                                            ft.Text("Движение", size=16, color=PALETTE["muted"], weight=ft.FontWeight.W_600),
                                            ft.Text(task["title"], size=28, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                            ft.Row(
                                                spacing=8,
                                                controls=[
                                                    self.soft_chip(f"Шаги: {len(task['steps'])}"),
                                                    self.soft_chip(f"Награда: {task['stars']} звезды"),
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        width=90,
                                        height=90,
                                        border_radius=26,
                                        bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.WHITE),
                                        alignment=ft.Alignment(0, 0),
                                        content=self.svg_figure("movement", width=64, height=64),
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Повтори шаги спокойно и в удобном темпе.",
                                size=16,
                                weight=ft.FontWeight.W_600,
                                color=PALETTE["text"],
                            ),
                        ],
                    ),
                ),
                ft.Column(
                    spacing=10,
                    controls=[
                        ft.Container(
                            bgcolor=PALETTE["card"],
                            border=ft.Border.all(1, PALETTE["line"]),
                            border_radius=24,
                            padding=18,
                            content=ft.Row(
                                spacing=14,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Container(
                                        width=38,
                                        height=38,
                                        border_radius=19,
                                        bgcolor=PALETTE["accent"],
                                        alignment=ft.Alignment(0, 0),
                                        content=ft.Text(str(index), size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                    ),
                                    ft.Text(step, expand=True, size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                                ],
                            ),
                        )
                        for index, step in enumerate(task["steps"], start=1)
                    ],
                ),
                self.card(
                    "Подсказка",
                    controls=[
                        ft.Text(
                            self.movement_feedback,
                            size=17,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        self.app_button("Другое задание", self.new_movement_task, PALETTE["accent"], expand=1),
                        self.app_button("Я выполнил", self.complete_movement_task, PALETTE["accent_2"], expand=1),
                    ],
                ),
            ],
        )

    def build_breath_game(self) -> ft.Column:
        if self.breath_intro_visible:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Дыхание",
                        [
                            self.svg_figure("calm", width=112, height=112),
                            ft.Text(
                                "Сейчас будет спокойное дыхание. Нажми старт, а дальше игра сама проведёт тебя по шагам.",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Будет {self.breath_target_cycles} спокойных цикла: вдох, пауза, выдох и отдых.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Старт", self.start_breathing, PALETTE["accent"]),
                        ],
                    ),
                ],
            )

        if self.breath_completed:
            return ft.Column(
                spacing=14,
                controls=[
                    self.sub_back("Игры", self.set_child_view("games")),
                    self.game_shell(
                        "Ура!",
                        [
                            self.svg_figure("calm", width=112, height=112),
                            ft.Text(
                                "Ура! Ты смог спокойно подышать и успокоиться.",
                                size=22,
                                weight=ft.FontWeight.W_700,
                                color=PALETTE["text"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                "Это было очень хорошо. Если хочешь, можно пройти дыхание ещё раз.",
                                size=16,
                                color=PALETTE["muted"],
                                text_align=ft.TextAlign.CENTER,
                            ),
                            self.app_button("Ещё раз", self.start_breathing, PALETTE["accent"]),
                        ],
                    ),
                ],
            )

        phase = BREATHING_PHASES[self.breath_phase_index]
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Игры", self.set_child_view("games")),
                self.game_shell(
                    phase["title"],
                    [
                        self.svg_figure("calm", width=96, height=96),
                        ft.Text(
                            f"Цикл {self.breath_cycle_count + 1} из {self.breath_target_cycles}",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=PALETTE["text"],
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.ProgressBar(value=phase["progress"], color=phase["color"], bgcolor=PALETTE["surface"], bar_height=10),
                        ft.Text(phase["prompt"], size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"], text_align=ft.TextAlign.CENTER),
                        ft.Text("Смотри на экран и дыши спокойно. Этапы идут автоматически.", size=15, color=PALETTE["muted"], text_align=ft.TextAlign.CENTER),
                        self.app_button("Стоп", self.stop_breathing, PALETTE["surface"]),
                    ],
                ),
            ],
        )

    def build_robot_room(self) -> ft.Column:
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Профиль", self.set_child_view("hub")),
                self.game_shell(
                    "Робот",
                    [
                        self.svg_figure("robot", width=104, height=104),
                        ft.Text("Выбери цвет", size=16, color=PALETTE["muted"]),
                        *[
                            self.app_button(name, lambda _e, c=color: self.set_mascot_color(c), color)
                            for name, color in ROBOT_COLORS.items()
                        ],
                    ],
                ),
            ],
        )

    def build_rewards_room(self) -> ft.Column:
        badges = self.state.badges[:4] if self.state.badges else ["Первая звезда"]
        return ft.Column(
            spacing=14,
            controls=[
                self.sub_back("Профиль", self.set_child_view("hub")),
                self.game_shell(
                    "Награды",
                    [
                        self.svg_figure("rewards", width=108, height=108),
                        ft.Text(f"⭐ {self.state.stars}", size=36, color=PALETTE["text"], text_align=ft.TextAlign.CENTER),
                        *[self.reward_chip(item) for item in badges],
                    ],
                ),
            ],
        )

    def build_parent_hub(self) -> ft.Column:
        active_parent = self.active_parent_user()
        parent_name = active_parent["full_name"] if active_parent else "Родитель"
        return ft.Column(
            spacing=14,
            controls=[
                self.hero_card(
                    "Родитель",
                    parent_name,
                    ft.Icons.FAMILY_RESTROOM,
                    [PALETTE["focus"], PALETTE["nav_active"]],
                    art="parent",
                ),
                self.app_button("Добавить ребёнка", self.set_parent_view("add_child"), PALETTE["nav"], color=PALETTE["hero_text"]),
                self.icon_tile("Управление", "данные", ft.Icons.TUNE, self.set_parent_view("manage"), [PALETTE["accent"], PALETTE["surface"]], art="manage"),
            ],
        )

    def build_parent_management_card(self) -> ft.Container:
        active_parent = self.active_parent_user()
        active_child = self.active_parent_child()
        return self.build_parent_account_management_content(active_parent, active_child)

    def build_parent_account_management_content(
        self,
        active_parent: dict[str, str] | None,
        active_child: dict[str, str] | None,
    ) -> ft.Container:
        return self.card(
            "Управление ребёнком",
            "Здесь можно изменить имя, возраст, логин и пароль ребёнка или удалить его аккаунт.",
            controls=[
                self.info_line("Родитель", active_parent["full_name"] if active_parent else "Не выбран"),
                self.info_line("Username", active_parent["username"] if active_parent else "-"),
                self.info_line("Активный ребёнок", active_child["full_name"] if active_child else "Пока не выбран"),
                self.info_line("Возраст", f"{active_child['age']} лет" if active_child else "-"),
                self.info_line("Логин ребёнка", active_child["username"] if active_child else "-"),
                self.app_button("Добавить или выбрать ребёнка", self.set_parent_view("add_child"), PALETTE["surface"]),
                self.profile_field("Имя ребёнка", self.manage_child_name_input, self.set_manage_child_name_input),
                self.profile_field(
                    "Возраст",
                    self.manage_child_age_input,
                    self.set_manage_child_age_input,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=2,
                ),
                self.profile_field("Логин ребёнка", self.manage_child_username_input, self.set_manage_child_username_input),
                self.profile_field(
                    "Новый пароль ребёнка",
                    self.manage_child_password_input,
                    self.set_manage_child_password_input,
                    password=True,
                    can_reveal_password=True,
                ),
                ft.Text(
                    self.manage_child_feedback or "Выбери ребёнка и затем сохрани изменения. Пароль можно оставить пустым, тогда он не изменится.",
                    color="#C95A6A" if self.manage_child_feedback_is_error else PALETTE["muted"],
                    size=14,
                ),
                self.app_button("Сохранить изменения", self.submit_parent_child_update, PALETTE["accent"]),
                self.app_button("Удалить ребёнка", self.delete_active_child, PALETTE["focus"]),
            ],
        )

    def build_parent_add_child_card(self) -> ft.Container:
        active_parent = self.active_parent_user()
        feedback_color = "#C95A6A" if self.parent_child_feedback_is_error else PALETTE["muted"]
        feedback_text = self.parent_child_feedback or "Здесь родитель создаёт для ребёнка имя, возраст, логин и пароль."
        return self.card(
            "Добавить ребёнка",
            "Данные сохраняются в Supabase и будут готовы для отдельного входа ребёнка.",
            controls=[
                self.info_line("Родитель", active_parent["full_name"] if active_parent else "Не выбран"),
                self.info_line("Логин родителя", active_parent["username"] if active_parent else "-"),
                self.profile_field("Имя ребёнка", self.parent_child_name_input, self.set_parent_child_name_input),
                self.profile_field(
                    "Возраст",
                    self.parent_child_age_input,
                    self.set_parent_child_age_input,
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=2,
                ),
                self.profile_field("Логин ребёнка", self.parent_child_username_input, self.set_parent_child_username_input),
                self.profile_field(
                    "Пароль ребёнка",
                    self.parent_child_password_input,
                    self.set_parent_child_password_input,
                    password=True,
                    can_reveal_password=True,
                    on_submit=self.submit_parent_child,
                ),
                ft.Text(feedback_text, color=feedback_color, size=14),
                self.app_button("Создать аккаунт ребёнка", self.submit_parent_child, PALETTE["accent"]),
            ],
        )

    def build_parent_children_card(self) -> ft.Container:
        controls: list[ft.Control] = []
        if not self.parent_children:
            controls.append(ft.Text("Пока ещё нет добавленных детей.", color=PALETTE["muted"], size=14))
        else:
            for child in self.parent_children:
                is_active = bool(self.active_child_profile and self.active_child_profile["id"] == child["id"])
                controls.append(
                    ft.Container(
                        bgcolor=PALETTE["surface"],
                        border=ft.Border.all(1, PALETTE["line"]),
                        border_radius=18,
                        padding=14,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                self.info_line("Имя", child["full_name"]),
                                self.info_line("Возраст", f"{child['age']} лет"),
                                self.info_line("Логин", child["username"]),
                                self.app_button(
                                    "Активный профиль" if is_active else "Выбрать",
                                    self.select_parent_child(child),
                                    PALETTE["accent_2"] if is_active else PALETTE["surface_alt"],
                                ),
                            ],
                        ),
                    )
                )
        return self.card(
            "Дети родителя",
            "Здесь можно переключать активный профиль ребёнка для игр и заметок.",
            controls=controls,
        )

    def build_parent_traits_card(self) -> ft.Container:
        return self.card(
            "Характеристики ребёнка",
            controls=[
                self.profile_field(
                    "Сильные стороны",
                    self.state.child_strengths,
                    self.bind_state_text("child_strengths"),
                    multiline=True,
                ),
                self.profile_field(
                    "Особенности и поддержка",
                    self.state.child_characteristics,
                    self.bind_state_text("child_characteristics"),
                    multiline=True,
                ),
                self.profile_field(
                    "Любимая активность",
                    self.state.favorite_activity,
                    self.bind_state_text("favorite_activity"),
                ),
                self.info_line("Мягкий голос робота", "Включён" if self.state.voice_enabled else "Выключен"),
                self.info_line("Последняя концентрация", f"{self.state.focus_history[-1]}%"),
                self.info_line("Последняя устойчивость", f"{self.state.emotion_history[-1]}%"),
            ],
        )

    def build_parent_guidance_card(self) -> ft.Container:
        tips = PARENT_SECTIONS[1][1][:3]
        return self.card(
            "Подсказки для родителя",
            "Короткие рекомендации, которые помогают держать спокойный ритм дома.",
            controls=[self.bullet(item) for item in tips],
        )

    def build_parent_screening_card(self) -> ft.Container:
        question = SCREENING_QUESTIONS[self.screening_index]
        group = ft.RadioGroup(
            value=None if self.screening_answers[self.screening_index] < 0 else str(self.screening_answers[self.screening_index]),
            on_change=lambda e, i=self.screening_index: self.set_screening_answer(i, int(e.control.value)),
            content=ft.Column(
                spacing=6,
                controls=[ft.Radio(value=str(value), label=label) for label, value in SCREENING_OPTIONS],
            ),
        )
        return self.card(
            f"Скрининг: вопрос {self.screening_index + 1} из {len(SCREENING_QUESTIONS)}",
            question,
            controls=[
                ft.ProgressBar(
                    value=(self.screening_index + 1) / len(SCREENING_QUESTIONS),
                    color=PALETTE["nav"],
                    bgcolor=PALETTE["surface"],
                    bar_height=8,
                ),
                group,
                ft.Row(
                    spacing=8,
                    controls=[
                        self.app_button("Назад", self.prev_screening_question, PALETTE["surface"], expand=1),
                        self.app_button("Дальше", self.next_screening_question, PALETTE["accent"], expand=1),
                    ],
                ),
            ],
        )

    def build_parent_screening_result_card(self) -> ft.Container:
        return self.card(
            "Результат скрининга",
            controls=[
                self.app_button("Подсчитать результат", self.calculate_screening, PALETTE["accent"]),
                self.app_button("Сбросить ответы", self.reset_screening, PALETTE["surface"]),
                ft.Text(self.screening_feedback, color=PALETTE["text"]),
            ],
        )

    def build_child(self) -> ft.Column:
        emotion_item = EMOTION_ITEMS[self.emotion_index]
        return ft.Column(
            spacing=12,
            controls=[
                self.card(
                    "Настройки робота",
                    "Можно менять цвет помощника и включать мягкий голосовой режим.",
                    [
                        ft.Text(
                            "ROBOT",
                            size=28,
                            weight=ft.FontWeight.W_700,
                            color=self.state.mascot_color,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.Text("Спокойный помощник рядом.", color=PALETTE["muted"]),
                        ft.Column(
                            spacing=8,
                            controls=[
                                self.app_button(name, lambda _e, c=color: self.set_mascot_color(c), color)
                                for name, color in ROBOT_COLORS.items()
                            ],
                        ),
                        ft.Switch(
                            label="Включить мягкий голос робота",
                            value=self.state.voice_enabled,
                            active_color=PALETTE["accent_2"],
                            on_change=self.toggle_voice,
                        ),
                    ],
                ),
                self.card(
                    "Эмоции",
                    "Выбери эмоцию по истории. Это короткая игра для тренировки понимания состояний.",
                    [
                        ft.Text(emotion_item["sticker"], size=42, text_align=ft.TextAlign.CENTER),
                        ft.Text(emotion_item["prompt"], color=PALETTE["text"], size=16),
                        ft.Column(
                            spacing=8,
                            controls=[
                                self.app_button(
                                    item["emotion"],
                                    lambda _e, emotion=item["emotion"]: self.answer_emotion(emotion),
                                    PALETTE["surface"],
                                )
                                for item in EMOTION_ITEMS
                            ],
                        ),
                        ft.Text(self.emotion_feedback, color=PALETTE["accent_2"], size=15),
                        ft.Text(f"Серия правильных ответов: {self.emotion_streak}", color=PALETTE["muted"]),
                        self.app_button("Следующая эмоция", self.next_emotion, PALETTE["accent"]),
                    ],
                ),
                self.card(
                    "Фокус",
                    "Небольшая тренировка памяти: запомни последовательность и повтори её.",
                    [
                        ft.Text(self.focus_title(), size=18, weight=ft.FontWeight.W_600),
                        ft.Text(self.focus_feedback, color=PALETTE["muted"]),
                        ft.Text(self.focus_sequence_text(), size=26, text_align=ft.TextAlign.CENTER),
                        ft.Text(self.focus_answer_text(), color=PALETTE["text"]),
                        self.app_button("Новый раунд", self.start_focus_round, PALETTE["accent"]),
                        self.app_button(
                            "Скрыть последовательность",
                            self.hide_focus_sequence,
                            PALETTE["accent_2"],
                        ),
                        self.app_button("Очистить ответ", self.clear_focus_answer, PALETTE["nav_active"]),
                        ft.Column(
                            spacing=8,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        self.compact_button(
                                            f"{item['emoji']} {item['label']}",
                                            lambda _e, selected=item: self.add_focus_answer(selected),
                                        )
                                        for item in row_items
                                    ],
                                )
                                for row_items in self.chunked(FOCUS_ITEMS, 2)
                            ],
                        ),
                        self.app_button("Проверить ответ", self.check_focus_answer, PALETTE["nav"]),
                    ],
                ),
            ],
        )

    def build_practice(self) -> ft.Column:
        movement = MOVEMENT_TASKS[self.movement_index]
        phase = BREATHING_PHASES[self.breath_phase_index]
        return ft.Column(
            spacing=12,
            controls=[
                self.card(
                    "Движения",
                    "Короткие действия помогают переключить внимание и снять напряжение.",
                    [
                        ft.Text(movement["title"], size=18, weight=ft.FontWeight.W_700),
                        ft.Column(spacing=6, controls=[self.bullet(step) for step in movement["steps"]]),
                        ft.Text(self.movement_feedback, color=PALETTE["muted"]),
                        self.app_button("Новое задание", self.new_movement_task, PALETTE["accent"]),
                        self.app_button("Я выполнил", self.complete_movement_task, PALETTE["accent_2"]),
                    ],
                ),
                self.card(
                    "Спокойствие и дыхание",
                    "Телефонный формат лучше работает с короткими шагами, поэтому цикл дыхания сделан пошаговым.",
                    [
                        ft.Text(phase["title"], size=20, weight=ft.FontWeight.W_700, color=phase["color"]),
                        ft.Text(phase["prompt"], color=PALETTE["text"]),
                        ft.ProgressBar(
                            value=phase["progress"],
                            color=phase["color"],
                            bgcolor=PALETTE["surface"],
                            bar_height=10,
                        ),
                        self.app_button("Начать дыхание", self.start_breathing, PALETTE["accent"]),
                        self.app_button("Следующий этап", self.next_breath_phase, PALETTE["accent_2"]),
                        self.app_button("Остановить", self.stop_breathing, PALETTE["nav_active"]),
                    ],
                ),
                self.card(
                    "Спокойные подсказки",
                    controls=[
                        ft.Text(self.relax_choice, size=18, weight=ft.FontWeight.W_700),
                        ft.Text(RELAX_ITEMS[self.relax_choice], color=PALETTE["muted"]),
                        ft.Column(
                            spacing=8,
                            controls=[
                                self.app_button(
                                    title,
                                    lambda _e, key=title: self.select_relax_tip(key),
                                    PALETTE["surface"],
                                )
                                for title in RELAX_ITEMS
                            ],
                        ),
                    ],
                ),
            ],
        )

    def build_parents(self) -> ft.Column:
        controls: list[ft.Control] = [
            self.card(
                "Для родителей",
                "Приложение не ставит диагноз и не заменяет консультацию специалиста.",
                [
                    self.bullet("Игры и упражнения подходят как мягкая ежедневная поддержка."),
                    self.bullet("Скрининг полезен как материал для наблюдений."),
                    self.bullet("Отчёт помогает увидеть динамику привычек и состояния."),
                ],
            )
        ]

        for title, lines in PARENT_SECTIONS:
            controls.append(self.card(title, controls=[self.bullet(line) for line in lines]))

        for index, question in enumerate(SCREENING_QUESTIONS):
            group = ft.RadioGroup(
                value=None if self.screening_answers[index] < 0 else str(self.screening_answers[index]),
                on_change=lambda e, i=index: self.set_screening_answer(i, int(e.control.value)),
                content=ft.Column(
                    spacing=4,
                    controls=[ft.Radio(value=str(value), label=label) for label, value in SCREENING_OPTIONS],
                ),
            )
            controls.append(self.card(f"Вопрос {index + 1}", question, [group]))

        controls.append(
            self.card(
                "Результат скрининга",
                controls=[
                    self.app_button("Подсчитать результат", self.calculate_screening, PALETTE["accent"]),
                    self.app_button("Сбросить ответы", self.reset_screening, PALETTE["accent_2"]),
                    ft.Text(self.screening_feedback, color=PALETTE["text"]),
                ],
            )
        )
        return ft.Column(spacing=12, controls=controls)

    def build_progress(self) -> ft.Column:
        average_focus = sum(self.state.focus_history) // len(self.state.focus_history)
        average_emotion = sum(self.state.emotion_history) // len(self.state.emotion_history)
        badges = self.state.badges or ["Пока нет значков"]

        sessions: list[ft.Control] = []
        for index, (focus, emotion) in enumerate(zip(self.state.focus_history, self.state.emotion_history), start=1):
            sessions.append(
                self.card(
                    f"Сессия {index}",
                    controls=[
                        ft.Text(f"Концентрация: {focus}%"),
                        ft.ProgressBar(value=focus / 100, color=PALETTE["nav"], bgcolor=PALETTE["surface"], bar_height=8),
                        ft.Text(f"Эмоциональная устойчивость: {emotion}%"),
                        ft.ProgressBar(
                            value=emotion / 100,
                            color=PALETTE["accent_2"],
                            bgcolor=PALETTE["surface"],
                            bar_height=8,
                        ),
                    ],
                )
            )

        return ft.Column(
            spacing=12,
            controls=[
                self.card(
                    "Ключевые показатели",
                    controls=[
                        self.info_line("Звёзды", str(self.state.stars)),
                        self.info_line("Уровень", str(self.state.level)),
                        self.info_line("Завершённые игры", str(self.state.completed_games)),
                        self.info_line("Средняя концентрация", f"{average_focus}%"),
                        self.info_line("Средняя устойчивость", f"{average_emotion}%"),
                    ],
                ),
                self.card("Значки", controls=[self.bullet(item) for item in badges]),
                self.card("Недавние заметки", controls=[self.bullet(note) for note in self.state.recent_notes]),
                self.card(
                    "Еженедельный отчёт",
                    controls=[ft.Text(f"Скрининг: {self.state.screening_result}", color=PALETTE["text"])] + sessions,
                ),
            ],
        )

    def answer_emotion(self, emotion: str) -> None:
        if self.emotion_selected_answer:
            return

        current = EMOTION_ITEMS[self.emotion_index]
        self.emotion_selected_answer = emotion
        if emotion == current["emotion"]:
            self.emotion_streak += 1
            badge = "Знаток эмоций" if self.emotion_streak >= 3 else None
            self.emotion_feedback = f"Верно. Это {emotion}."
            self.mascot_message = random.choice(MASCOT_PHRASES)
            self.state.record_activity(
                stars=2,
                focus_change=2,
                emotion_change=4,
                badge=badge,
                note=f"Угадана эмоция: {emotion}.",
                completed_game=True,
            )
        else:
            self.emotion_streak = 0
            self.emotion_feedback = f"Почти. Правильный ответ: {current['emotion']}."
            self.state.record_activity(
                focus_change=-1,
                emotion_change=-1,
                note=f"Нужна подсказка по эмоции: {current['emotion']}.",
            )
        self.refresh()

    def next_emotion(self, _e: ft.ControlEvent) -> None:
        next_index = self.emotion_index
        while next_index == self.emotion_index:
            next_index = random.randrange(len(EMOTION_ITEMS))
        self.emotion_index = next_index
        self.emotion_selected_answer = ""
        self.emotion_feedback = "Выбери эмоцию по истории."
        self.refresh()

    def start_emotion_game(self, _e: ft.ControlEvent) -> None:
        self.emotion_intro_visible = False
        self.emotion_selected_answer = ""
        self.emotion_feedback = "Выбери эмоцию по истории."
        self.refresh()

    def start_focus_round(self, _e: ft.ControlEvent) -> None:
        self.focus_intro_visible = False
        self.focus_round += 1
        length = min(5, 2 + self.focus_round)
        self.focus_sequence = [random.choice(FOCUS_ITEMS) for _ in range(length)]
        self.focus_answer = []
        self.focus_sequence_visible = True
        self.focus_preview_token += 1
        preview_token = self.focus_preview_token
        self.focus_feedback = "Запомни последовательность. Она скоро исчезнет сама."
        self.refresh()
        self.page.run_task(self.auto_hide_focus_sequence, preview_token)

    def hide_focus_sequence(self, _e: ft.ControlEvent) -> None:
        if not self.focus_sequence:
            self.focus_feedback = "Сначала начни новый раунд."
        else:
            self.focus_sequence_visible = False
            self.focus_feedback = "Теперь собери ответ в том же порядке."
        self.refresh()

    def clear_focus_answer(self, _e: ft.ControlEvent) -> None:
        self.focus_answer = []
        self.focus_feedback = "Ответ очищен. Можно ввести заново."
        self.refresh()

    def add_focus_answer(self, item: dict[str, str]) -> None:
        if not self.focus_sequence:
            self.focus_feedback = "Сначала начни новый раунд."
            self.refresh()
            return
        if self.focus_sequence_visible:
            self.focus_feedback = "Подожди немного. Последовательность скоро исчезнет сама."
            self.refresh()
            return
        if len(self.focus_answer) < len(self.focus_sequence):
            self.focus_answer.append(item)
        if len(self.focus_answer) == len(self.focus_sequence):
            self.focus_feedback = "Ответ собран. Нажми «Проверить ответ»."
        self.refresh()

    def check_focus_answer(self, _e: ft.ControlEvent) -> None:
        if not self.focus_sequence:
            self.focus_feedback = "Сначала начни новый раунд."
            self.refresh()
            return
        if len(self.focus_answer) != len(self.focus_sequence):
            self.focus_feedback = "Нужно собрать полный ответ."
            self.refresh()
            return

        expected = [item["label"] for item in self.focus_sequence]
        actual = [item["label"] for item in self.focus_answer]
        if actual == expected:
            badge = "Мастер фокуса" if self.focus_round >= 3 else None
            self.focus_feedback = "Отлично. Последовательность повторена правильно."
            self.state.record_activity(
                stars=3,
                focus_change=6,
                emotion_change=2,
                badge=badge,
                note="Успешно завершён раунд на внимание.",
                completed_game=True,
            )
            self.mascot_message = "Фокус отличный. Давай продолжим."
        else:
            self.focus_feedback = f"Не совсем так. Правильный порядок: {' '.join(item['emoji'] for item in self.focus_sequence)}"
            self.state.record_activity(
                focus_change=-2,
                note="Понадобилась повторная попытка в игре на внимание.",
            )
        self.refresh()

    async def auto_hide_focus_sequence(self, preview_token: int) -> None:
        await asyncio.sleep(max(2.4, len(self.focus_sequence) * 1.2))
        if preview_token != self.focus_preview_token or self.child_view != "focus_game":
            return
        if not self.focus_sequence_visible:
            return
        self.focus_sequence_visible = False
        self.focus_feedback = "Теперь собери ответ в том же порядке."
        self.refresh()

    def start_memory_game(self, _e: ft.ControlEvent) -> None:
        self.memory_task_token += 1
        task_token = self.memory_task_token
        selected_pairs = random.sample(MEMORY_PAIR_ITEMS, k=min(4, len(MEMORY_PAIR_ITEMS)))
        self.memory_cards = selected_pairs + [dict(item) for item in selected_pairs]
        random.shuffle(self.memory_cards)
        self.memory_intro_visible = False
        self.memory_preview_visible = True
        self.memory_completed = False
        self.memory_feedback = "Смотри внимательно. Через 2 секунды карточки перевернутся."
        self.memory_selected_indices = []
        self.memory_matched_ids = set()
        self.memory_moves = 0
        self.memory_pairs_found = 0
        self.memory_locked = True
        self.refresh()
        self.page.run_task(self.hide_memory_preview, task_token)

    async def hide_memory_preview(self, task_token: int) -> None:
        await asyncio.sleep(2)
        if task_token != self.memory_task_token or self.child_view != "memory_game":
            return
        self.memory_preview_visible = False
        self.memory_locked = False
        self.memory_feedback = "Теперь найди одинаковые карточки."
        self.refresh()

    def open_memory_card(self, index: int) -> None:
        if (
            self.memory_preview_visible
            or self.memory_locked
            or self.memory_completed
            or index in self.memory_selected_indices
            or not self.memory_cards
        ):
            return

        card = self.memory_cards[index]
        if card["pair_id"] in self.memory_matched_ids:
            return

        self.memory_selected_indices.append(index)
        if len(self.memory_selected_indices) == 1:
            self.memory_feedback = "Найди такую же карточку."
            self.refresh()
            return

        self.memory_moves += 1
        first_index, second_index = self.memory_selected_indices
        first_card = self.memory_cards[first_index]
        second_card = self.memory_cards[second_index]

        if first_card["pair_id"] == second_card["pair_id"]:
            self.memory_matched_ids.add(first_card["pair_id"])
            self.memory_pairs_found = len(self.memory_matched_ids)
            self.memory_selected_indices = []
            self.memory_feedback = f"Есть пара: {first_card['label']}."
            if self.memory_pairs_found == len(self.memory_cards) // 2:
                self.memory_completed = True
                self.memory_feedback = "Ура! Все пары найдены."
                self.state.record_activity(
                    stars=4,
                    focus_change=6,
                    emotion_change=3,
                    badge="Память и пары",
                    note="Успешно завершена игра на поиск пар.",
                    completed_game=True,
                )
                self.mascot_message = "У тебя отличная память. Все пары найдены."
            self.refresh()
            return

        self.memory_locked = True
        task_token = self.memory_task_token
        self.memory_feedback = "Почти. Запомни карточки и попробуй снова."
        self.refresh()
        self.page.run_task(self.hide_memory_mismatch, task_token, first_index, second_index)

    async def hide_memory_mismatch(self, task_token: int, first_index: int, second_index: int) -> None:
        await asyncio.sleep(0.9)
        if task_token != self.memory_task_token or self.child_view != "memory_game":
            return
        if self.memory_selected_indices == [first_index, second_index]:
            self.memory_selected_indices = []
        self.memory_locked = False
        self.memory_feedback = "Попробуй ещё. Найди одинаковые карточки."
        self.refresh()

    def current_music_item(self) -> dict[str, str]:
        return next((item for item in MUSIC_ITEMS if item["id"] == self.music_selected_id), MUSIC_ITEMS[0])

    def set_music_track(self, track_id: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.music_selected_id = track_id
            if self.music_is_playing:
                self.start_music(None)
                return
            self.music_feedback = f"Выбрана мелодия: {self.current_music_item()['title']}."
            self.refresh()

        return handler

    def set_music_timer(self, minutes: int):
        def handler(_e: ft.ControlEvent) -> None:
            self.music_timer_minutes = minutes
            if self.music_is_playing:
                self.music_feedback = f"Новый таймер {minutes} мин. применится после нового старта."
            else:
                self.music_feedback = f"Таймер: {minutes} мин."
            self.refresh()

        return handler

    def start_music(self, _e: ft.ControlEvent) -> None:
        if not self.music_supported:
            self.music_feedback = "Музыка сейчас работает только в Windows desktop-сборке."
            self.refresh()
            return

        self.stop_music_playback(reset_feedback=False)
        track = self.current_music_item()
        path = self.ensure_music_track_file(track)
        if not path:
            self.music_feedback = "Не удалось подготовить музыкальный файл."
            self.refresh()
            return

        self.music_task_token += 1
        task_token = self.music_task_token
        self.music_is_playing = True
        self.music_remaining_seconds = self.music_timer_minutes * 60
        self.music_feedback = f"Сейчас играет: {track['title']}."
        winsound.PlaySound(path, winsound.SND_ASYNC | winsound.SND_FILENAME | winsound.SND_LOOP)
        self.refresh()
        self.page.run_task(self.run_music_session, task_token)

    def stop_music(self, _e: ft.ControlEvent) -> None:
        self.stop_music_playback(reset_feedback=True)
        self.music_feedback = "Музыка остановлена."
        self.refresh()

    def stop_music_playback(self, reset_feedback: bool) -> None:
        self.music_task_token += 1
        self.music_is_playing = False
        self.music_remaining_seconds = 0
        if winsound is not None:
            winsound.PlaySound(None, winsound.SND_PURGE)
        if reset_feedback:
            self.music_feedback = "Выбери мелодию и нажми «Старт»."

    async def run_music_session(self, task_token: int) -> None:
        while self.music_remaining_seconds > 0:
            if task_token != self.music_task_token or self.child_view != "music" or not self.music_is_playing:
                return
            await asyncio.sleep(1)
            if task_token != self.music_task_token or not self.music_is_playing:
                return
            self.music_remaining_seconds -= 1
            self.refresh()

        if task_token != self.music_task_token:
            return

        completed_track = self.current_music_item()
        self.stop_music_playback(reset_feedback=False)
        self.music_feedback = f"Музыка закончилась: {completed_track['title']}. Ты хорошо отдохнул."
        self.state.record_activity(
            stars=2,
            focus_change=2,
            emotion_change=4,
            badge="Спокойная музыка",
            note=f"Прослушана спокойная музыка: {completed_track['title']}.",
            completed_game=True,
        )
        self.mascot_message = "Музыка помогла немного расслабиться."
        self.refresh()

    def ensure_music_track_file(self, track: dict[str, object]) -> str | None:
        cached = self.music_file_paths.get(track["id"])
        if cached and Path(cached).exists():
            return cached

        output_dir = Path(__file__).resolve().parent / "assets" / "generated_audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{track['id']}.wav"
        if not output_path.exists():
            self.generate_music_track(output_path, track["notes"])
        self.music_file_paths[str(track["id"])] = str(output_path)
        return str(output_path)

    def active_drawing_color(self) -> str:
        return ft.Colors.WHITE if self.drawing_eraser_enabled else self.drawing_selected_color

    def current_drawing_paint(self) -> ft.Paint:
        return ft.Paint(
            color=self.active_drawing_color(),
            stroke_width=self.drawing_brush_size,
            style=ft.PaintingStyle.STROKE,
            stroke_cap=ft.StrokeCap.ROUND,
            stroke_join=ft.StrokeJoin.ROUND,
            anti_alias=True,
        )

    def set_drawing_color(self, color: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.drawing_selected_color = color
            self.drawing_eraser_enabled = False
            self.refresh()

        return handler

    def set_drawing_brush_size(self, size: int):
        def handler(_e: ft.ControlEvent) -> None:
            self.drawing_brush_size = size
            self.refresh()

        return handler

    def toggle_drawing_eraser(self, _e: ft.ControlEvent) -> None:
        self.drawing_eraser_enabled = not self.drawing_eraser_enabled
        self.refresh()

    def clear_drawing_canvas(self, _e: ft.ControlEvent) -> None:
        self.drawing_shapes = []
        self.drawing_active_path = None
        if self.drawing_canvas_control is not None:
            self.drawing_canvas_control.shapes = self.drawing_shapes
        self.refresh()

    def update_drawing_canvas(self) -> None:
        if self.drawing_canvas_control is None:
            return
        self.drawing_canvas_control.shapes = self.drawing_shapes
        self.drawing_canvas_control.update()

    def draw_tap_dot(self, e: ft.TapEvent) -> None:
        if self.child_view != "drawing" or e.local_position is None:
            return
        x = e.local_position.x
        y = e.local_position.y
        dot = cv.Path(
            elements=[
                cv.Path.MoveTo(x, y),
                cv.Path.LineTo(x + 0.1, y + 0.1),
            ],
            paint=self.current_drawing_paint(),
        )
        self.drawing_shapes.append(dot)
        self.drawing_active_path = None
        self.update_drawing_canvas()

    def start_drawing_stroke(self, e: ft.DragStartEvent) -> None:
        if self.child_view != "drawing":
            return
        x = e.local_position.x
        y = e.local_position.y
        path = cv.Path(
            elements=[
                cv.Path.MoveTo(x, y),
                cv.Path.LineTo(x + 0.1, y + 0.1),
            ],
            paint=self.current_drawing_paint(),
        )
        self.drawing_shapes.append(path)
        self.drawing_active_path = path
        self.update_drawing_canvas()

    def extend_drawing_stroke(self, e: ft.DragUpdateEvent) -> None:
        if self.child_view != "drawing" or self.drawing_active_path is None:
            return
        self.drawing_active_path.elements.append(cv.Path.LineTo(e.local_position.x, e.local_position.y))
        self.update_drawing_canvas()

    def finish_drawing_stroke(self, _e: ft.DragEndEvent) -> None:
        self.drawing_active_path = None

    @staticmethod
    def generate_music_track(output_path: Path, notes: list[float]) -> None:
        sample_rate = 22050
        amplitude = 10000
        note_seconds = 0.56
        silence_seconds = 0.08

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            frames: list[bytes] = []
            for note in notes:
                total_samples = int(note_seconds * sample_rate)
                for sample_index in range(total_samples):
                    progress = sample_index / total_samples
                    envelope = min(progress / 0.18, 1.0, (1.0 - progress) / 0.22)
                    tone = (
                        0.72 * math.sin(2 * math.pi * note * sample_index / sample_rate)
                        + 0.18 * math.sin(2 * math.pi * note * 2 * sample_index / sample_rate)
                        + 0.1 * math.sin(2 * math.pi * note * 0.5 * sample_index / sample_rate)
                    )
                    value = int(amplitude * envelope * tone)
                    frames.append(struct.pack("<h", value))

                for _ in range(int(silence_seconds * sample_rate)):
                    frames.append(struct.pack("<h", 0))

            wav_file.writeframes(b"".join(frames))

    def format_music_remaining(self) -> str:
        minutes, seconds = divmod(max(0, self.music_remaining_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    def new_movement_task(self, _e: ft.ControlEvent) -> None:
        next_index = self.movement_index
        while next_index == self.movement_index:
            next_index = random.randrange(len(MOVEMENT_TASKS))
        self.movement_index = next_index
        self.movement_feedback = "Новое задание готово."
        self.refresh()

    def complete_movement_task(self, _e: ft.ControlEvent) -> None:
        task = MOVEMENT_TASKS[self.movement_index]
        badge = "Люблю движение" if self.state.completed_games >= 4 else None
        self.movement_feedback = "Задание отмечено как выполненное."
        self.state.record_activity(
            stars=task["stars"],
            focus_change=task["focus"],
            emotion_change=task["emotion"],
            badge=badge,
            note=f"Выполнено движение: {task['title']}.",
            completed_game=True,
        )
        self.mascot_message = "Движение получилось спокойно и уверенно."
        self.refresh()

    def start_breathing(self, _e: ft.ControlEvent) -> None:
        self.breath_run_token += 1
        run_token = self.breath_run_token
        self.breath_intro_visible = False
        self.breath_completed = False
        self.breath_started = True
        self.breath_phase_index = 0
        self.breath_cycle_count = 0
        self.mascot_message = "Начинаем дыхание. Медленно и без спешки."
        self.refresh()
        self.page.run_task(self.run_breathing_session, run_token)

    def next_breath_phase(self, _e: ft.ControlEvent) -> None:
        if not self.breath_started:
            self.start_breathing(_e)
            return
        previous = self.breath_phase_index
        self.breath_phase_index = (self.breath_phase_index + 1) % len(BREATHING_PHASES)
        if previous == len(BREATHING_PHASES) - 1:
            self.state.record_activity(
                stars=2,
                focus_change=2,
                emotion_change=4,
                badge="Спокойное дыхание",
                note="Завершён цикл дыхательной практики.",
                completed_game=True,
            )
            self.mascot_message = "Отлично. Один спокойный цикл завершён."
        self.refresh()

    def stop_breathing(self, _e: ft.ControlEvent) -> None:
        self.breath_run_token += 1
        self.breath_started = False
        self.breath_intro_visible = True
        self.breath_completed = False
        self.breath_phase_index = 0
        self.breath_cycle_count = 0
        self.mascot_message = "Можно сделать паузу и вернуться позже."
        self.refresh()

    async def run_breathing_session(self, run_token: int) -> None:
        total_steps = len(BREATHING_PHASES) * self.breath_target_cycles
        for step in range(total_steps):
            if run_token != self.breath_run_token or self.child_view != "breath_game" or not self.breath_started:
                return
            self.breath_phase_index = step % len(BREATHING_PHASES)
            self.breath_cycle_count = step // len(BREATHING_PHASES)
            self.refresh()
            await asyncio.sleep(BREATHING_PHASES[self.breath_phase_index]["seconds"])

        if run_token != self.breath_run_token or self.child_view != "breath_game":
            return

        self.breath_started = False
        self.breath_completed = True
        self.breath_phase_index = 0
        self.breath_cycle_count = self.breath_target_cycles
        self.state.record_activity(
            stars=3,
            focus_change=3,
            emotion_change=5,
            badge="Спокойное дыхание",
            note="Завершены циклы дыхательной практики.",
            completed_game=True,
        )
        self.mascot_message = "Ура! Ты смог спокойно подышать и успокоиться."
        self.refresh()

    def select_relax_tip(self, title: str) -> None:
        self.relax_choice = title
        self.refresh()

    def set_screening_answer(self, index: int, value: int) -> None:
        self.screening_answers[index] = value

    def prev_screening_question(self, _e: ft.ControlEvent) -> None:
        self.screening_index = max(0, self.screening_index - 1)
        self.refresh()

    def next_screening_question(self, _e: ft.ControlEvent) -> None:
        self.screening_index = min(len(SCREENING_QUESTIONS) - 1, self.screening_index + 1)
        self.refresh()

    def calculate_screening(self, _e: ft.ControlEvent) -> None:
        if any(value < 0 for value in self.screening_answers):
            self.screening_feedback = "Нужно выбрать вариант ответа для каждого вопроса."
            self.refresh()
            return

        total = sum(self.screening_answers)
        if total <= 4:
            conclusion = "Низкий уровень наблюдаемых индикаторов."
            recommendation = "Продолжайте спокойные развивающие занятия и периодическое наблюдение."
        elif total <= 9:
            conclusion = "Умеренный уровень наблюдаемых индикаторов."
            recommendation = "Имеет смысл обсудить наблюдения со специалистом и отслеживать динамику."
        else:
            conclusion = "Повышенный уровень наблюдаемых индикаторов."
            recommendation = "Рекомендуется очная консультация со специалистом для более точной оценки."

        result = f"{conclusion} Баллы: {total} из 15. {recommendation}"
        self.screening_feedback = result
        self.state.screening_result = result
        self.state.record_activity(
            stars=2,
            emotion_change=1,
            badge="Внимательный родитель",
            note=f"Пройден скрининг. Баллы: {total}.",
        )
        self.mascot_message = "Спасибо. Результат сохранён в отчёте."
        self.refresh()

    def reset_screening(self, _e: ft.ControlEvent) -> None:
        self.screening_answers = [-1] * len(SCREENING_QUESTIONS)
        self.screening_feedback = "Ответы очищены."
        self.refresh()

    def set_mascot_color(self, color: str) -> None:
        self.state.mascot_color = color
        self.refresh()

    def toggle_voice(self, e: ft.ControlEvent) -> None:
        self.state.voice_enabled = bool(e.control.value)
        note = "Включён мягкий голос робота." if self.state.voice_enabled else "Мягкий голос робота выключен."
        self.state.record_activity(note=note)
        self.refresh()

    def navigate_to(self, section: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.current_section = section
            if section == "child":
                self.reset_child_access()
            elif section == "parent":
                self.reset_child_access()
                self.reset_parent_access()
                self.screening_index = 0
            else:
                self.reset_child_access()
                self.reset_parent_access()
            self.refresh()

        return handler

    def set_child_view(self, view: str):
        def handler(_e: ft.ControlEvent) -> None:
            if view != "drawing":
                self.drawing_active_path = None
            if view != "focus_game":
                self.focus_preview_token += 1
            if view != "memory_game":
                self.memory_task_token += 1
                self.memory_preview_visible = False
                self.memory_locked = False
            if view != "breath_game":
                self.breath_run_token += 1
                self.breath_started = False
            if view != "music":
                self.stop_music_playback(reset_feedback=False)
            if view == "emotion_game":
                self.prepare_emotion_game()
            elif view == "focus_game":
                self.prepare_focus_game()
            elif view == "memory_game":
                self.prepare_memory_game()
            elif view == "breath_game":
                self.prepare_breath_game()
            self.child_view = view if self.child_session_profile or view == "auth" else "auth"
            self.guidy_message = self.current_guidy_default_message() if self.should_show_guidy() else ""
            self.refresh()

        return handler

    def set_parent_view(self, view: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.parent_view = view if self.parent_session_user_id or view == "auth" else "auth"
            if self.parent_view in {"manage", "add_child"} and self.parent_session_user_id:
                self.load_parent_children()
            self.refresh()

        return handler

    def prepare_emotion_game(self) -> None:
        self.emotion_intro_visible = True
        self.emotion_selected_answer = ""
        self.emotion_feedback = "Выбери эмоцию по истории."

    def prepare_focus_game(self) -> None:
        self.focus_preview_token += 1
        self.focus_round = 0
        self.focus_sequence = []
        self.focus_answer = []
        self.focus_sequence_visible = False
        self.focus_intro_visible = True
        self.focus_feedback = "Сначала прочитай правила и нажми «Начать игру»."

    def prepare_breath_game(self) -> None:
        self.breath_run_token += 1
        self.breath_started = False
        self.breath_intro_visible = True
        self.breath_completed = False
        self.breath_phase_index = 0
        self.breath_cycle_count = 0

    def prepare_memory_game(self) -> None:
        self.memory_task_token += 1
        self.memory_intro_visible = True
        self.memory_preview_visible = False
        self.memory_completed = False
        self.memory_feedback = "Сначала прочитай правила и нажми «Начать игру»."
        self.memory_cards = []
        self.memory_selected_indices = []
        self.memory_matched_ids = set()
        self.memory_moves = 0
        self.memory_pairs_found = 0
        self.memory_locked = False

    def bind_state_text(self, field_name: str):
        def handler(e: ft.ControlEvent) -> None:
            setattr(self.state, field_name, e.control.value)

        return handler

    def reset_child_access(self) -> None:
        self.child_view = "auth"
        self.child_session_profile = None
        self.child_username_input = ""
        self.child_password_input = ""
        self.child_auth_error = ""
        self.guidy_open = False
        self.guidy_message = ""
        self.drawing_selected_color = DRAWING_COLORS[0]
        self.drawing_brush_size = DRAWING_BRUSH_SIZES[1]
        self.drawing_eraser_enabled = False
        self.drawing_shapes = []
        self.drawing_active_path = None
        self.drawing_canvas_control = None
        self.emotion_intro_visible = True
        self.emotion_index = 0
        self.emotion_feedback = "Выбери эмоцию по истории."
        self.emotion_streak = 0
        self.emotion_selected_answer = ""
        self.focus_preview_token += 1
        self.memory_task_token += 1
        self.breath_run_token += 1
        self.stop_music_playback(reset_feedback=True)
        self.breath_started = False
        self.focus_intro_visible = True
        self.memory_intro_visible = True
        self.memory_preview_visible = False
        self.memory_completed = False
        self.memory_cards = []
        self.memory_selected_indices = []
        self.memory_matched_ids = set()
        self.memory_moves = 0
        self.memory_pairs_found = 0
        self.memory_locked = False
        self.breath_intro_visible = True
        self.breath_completed = False
        self.breath_phase_index = 0
        self.breath_cycle_count = 0

    def reset_parent_access(self) -> None:
        self.parent_view = "auth"
        self.parent_session_user_id = None
        self.parent_session_profile = None
        self.parent_session_password = None
        self.parent_children = []
        self.active_child_profile = None
        self.parent_auth_mode = "login"
        self.parent_full_name_input = ""
        self.parent_username_input = ""
        self.parent_password_input = ""
        self.parent_confirm_password_input = ""
        self.parent_auth_error = ""
        self.parent_child_name_input = ""
        self.parent_child_age_input = ""
        self.parent_child_username_input = ""
        self.parent_child_password_input = ""
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False

    def set_parent_auth_mode(self, mode: str):
        def handler(_e: ft.ControlEvent) -> None:
            self.parent_auth_mode = mode
            self.parent_full_name_input = ""
            self.parent_username_input = ""
            self.parent_password_input = ""
            self.parent_confirm_password_input = ""
            self.parent_auth_error = ""
            self.refresh()

        return handler

    def set_parent_full_name_input(self, e: ft.ControlEvent) -> None:
        self.parent_full_name_input = e.control.value
        self.parent_auth_error = ""

    def set_parent_username_input(self, e: ft.ControlEvent) -> None:
        self.parent_username_input = e.control.value
        self.parent_auth_error = ""

    def set_parent_password_input(self, e: ft.ControlEvent) -> None:
        self.parent_password_input = e.control.value
        self.parent_auth_error = ""

    def set_parent_confirm_password_input(self, e: ft.ControlEvent) -> None:
        self.parent_confirm_password_input = e.control.value
        self.parent_auth_error = ""

    def set_child_username_input(self, e: ft.ControlEvent) -> None:
        self.child_username_input = e.control.value
        self.child_auth_error = ""

    def set_child_password_input(self, e: ft.ControlEvent) -> None:
        self.child_password_input = e.control.value
        self.child_auth_error = ""

    def set_parent_child_name_input(self, e: ft.ControlEvent) -> None:
        self.parent_child_name_input = e.control.value
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False

    def set_parent_child_age_input(self, e: ft.ControlEvent) -> None:
        self.parent_child_age_input = e.control.value
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False

    def set_parent_child_username_input(self, e: ft.ControlEvent) -> None:
        self.parent_child_username_input = e.control.value
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False

    def set_parent_child_password_input(self, e: ft.ControlEvent) -> None:
        self.parent_child_password_input = e.control.value
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False

    def set_manage_child_name_input(self, e: ft.ControlEvent) -> None:
        self.manage_child_name_input = e.control.value
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def set_manage_child_age_input(self, e: ft.ControlEvent) -> None:
        self.manage_child_age_input = e.control.value
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def set_manage_child_username_input(self, e: ft.ControlEvent) -> None:
        self.manage_child_username_input = e.control.value
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def set_manage_child_password_input(self, e: ft.ControlEvent) -> None:
        self.manage_child_password_input = e.control.value
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def submit_child_auth(self, _e: ft.ControlEvent) -> None:
        if not self.supabase_connection.is_ready or not self.supabase:
            self.child_auth_error = "Сначала настрой подключение к Supabase."
            self.refresh()
            return

        username = self.child_username_input.strip().lower()
        password = self.child_password_input

        if len(username) < 3:
            self.child_auth_error = "Логин ребёнка должен содержать минимум 3 символа."
            self.refresh()
            return
        if len(password) < 4:
            self.child_auth_error = "Пароль ребёнка должен содержать минимум 4 символа."
            self.refresh()
            return

        try:
            response = self.supabase.rpc(
                "child_login",
                {
                    "p_username": username,
                    "p_password": password,
                },
            ).execute()
        except Exception as exc:
            self.child_auth_error = self.describe_supabase_error(exc)
            self.refresh()
            return

        child = self.extract_child_rpc_row(response)
        if not child:
            self.child_auth_error = "Неверный логин или пароль ребёнка."
            self.refresh()
            return

        self.set_child_session(child)
        self.mascot_message = f"Привет, {child['full_name']}."
        self.refresh()

    def submit_parent_auth(self, _e: ft.ControlEvent) -> None:
        if not self.supabase_connection.is_ready or not self.supabase:
            self.parent_auth_error = "Сначала настрой подключение к Supabase."
            self.refresh()
            return

        username = self.parent_username_input.strip().lower()
        password = self.parent_password_input

        if self.parent_auth_mode == "register":
            full_name = self.parent_full_name_input.strip()
            confirm = self.parent_confirm_password_input
            if len(full_name) < 3:
                self.parent_auth_error = "Укажи ФИО полностью."
            elif len(username) < 3:
                self.parent_auth_error = "Username должен содержать минимум 3 символа."
            elif len(password) < 6:
                self.parent_auth_error = "Пароль должен содержать минимум 6 символов."
            elif password != confirm:
                self.parent_auth_error = "Пароли не совпадают."
            else:
                try:
                    response = self.supabase.rpc(
                        "parent_register",
                        {
                            "p_full_name": full_name,
                            "p_username": username,
                            "p_password": password,
                        },
                    ).execute()
                except Exception as exc:
                    self.parent_auth_error = self.describe_supabase_error(exc)
                    self.refresh()
                    return

                profile = self.extract_parent_rpc_row(response)
                if not profile:
                    self.parent_auth_error = "Не удалось создать аккаунт родителя."
                else:
                    self.set_parent_session(profile, password)
                    self.mascot_message = f"Аккаунт родителя {full_name} создан."
        else:
            if len(username) < 3:
                self.parent_auth_error = "Username должен содержать минимум 3 символа."
            elif len(password) < 6:
                self.parent_auth_error = "Пароль должен содержать минимум 6 символов."
            else:
                try:
                    response = self.supabase.rpc(
                        "parent_login",
                        {
                            "p_username": username,
                            "p_password": password,
                        },
                    ).execute()
                except Exception as exc:
                    self.parent_auth_error = self.describe_supabase_error(exc)
                    self.refresh()
                    return

                profile = self.extract_parent_rpc_row(response)
                if not profile:
                    self.parent_auth_error = "Неверный username или пароль."
                else:
                    self.set_parent_session(profile, password)
                    self.mascot_message = f"Вход выполнен: {profile['full_name']}."
        self.refresh()

    def submit_parent_child(self, _e: ft.ControlEvent) -> None:
        if not self.supabase_connection.is_ready or not self.supabase:
            self.parent_child_feedback = "Сначала настрой подключение к Supabase."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        if not self.parent_session_profile or not self.parent_session_password:
            self.parent_child_feedback = "Сессия родителя недоступна. Войди заново."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        child_name = self.parent_child_name_input.strip()
        child_age_text = self.parent_child_age_input.strip()
        child_username = self.parent_child_username_input.strip().lower()
        child_password = self.parent_child_password_input

        if len(child_name) < 2:
            self.parent_child_feedback = "Имя ребёнка должно содержать минимум 2 символа."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return
        if not child_age_text.isdigit():
            self.parent_child_feedback = "Возраст нужно указать цифрами."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        child_age = int(child_age_text)
        if child_age < 1 or child_age > 18:
            self.parent_child_feedback = "Возраст ребёнка должен быть в диапазоне 1-18 лет."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return
        if len(child_username) < 3:
            self.parent_child_feedback = "Логин ребёнка должен содержать минимум 3 символа."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return
        if len(child_password) < 4:
            self.parent_child_feedback = "Пароль ребёнка должен содержать минимум 4 символа."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        try:
            response = self.supabase.rpc(
                "parent_add_child",
                {
                    "p_parent_username": self.parent_session_profile["username"],
                    "p_parent_password": self.parent_session_password,
                    "p_child_name": child_name,
                    "p_child_age": child_age,
                    "p_child_username": child_username,
                    "p_child_password": child_password,
                },
            ).execute()
        except Exception as exc:
            self.parent_child_feedback = self.describe_supabase_error(exc)
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        child = self.extract_child_rpc_row(response)
        if not child:
            self.parent_child_feedback = "Не удалось создать аккаунт ребёнка."
            self.parent_child_feedback_is_error = True
            self.refresh()
            return

        self.parent_child_name_input = ""
        self.parent_child_age_input = ""
        self.parent_child_username_input = ""
        self.parent_child_password_input = ""
        self.parent_child_feedback = f"Ребёнок {child['full_name']} добавлен."
        self.parent_child_feedback_is_error = False
        self.load_parent_children(preferred_child_id=child["id"])
        self.mascot_message = f"Для ребёнка {child['full_name']} создан отдельный вход."
        self.refresh()

    def set_parent_note_draft(self, e: ft.ControlEvent) -> None:
        self.parent_note_draft = e.control.value

    def save_parent_note(self, _e: ft.ControlEvent) -> None:
        note = self.parent_note_draft.strip()
        if not note:
            self.mascot_message = "Сначала добавь заметку родителя."
            self.refresh()
            return
        self.state.record_activity(note=f"Заметка родителя: {note}")
        self.parent_note_draft = ""
        self.mascot_message = "Заметка сохранена."
        self.refresh()

    def active_parent_user(self) -> dict[str, str] | None:
        return self.parent_session_profile

    def active_parent_child(self) -> dict[str, str] | None:
        return self.active_child_profile

    def select_parent_child(self, child: dict[str, str]):
        def handler(_e: ft.ControlEvent) -> None:
            self.set_active_child_profile(child)
            self.parent_child_feedback = f"Активный профиль: {child['full_name']}."
            self.parent_child_feedback_is_error = False
            self.refresh()

        return handler

    def clear_manage_child_inputs(self) -> None:
        self.manage_child_name_input = ""
        self.manage_child_age_input = ""
        self.manage_child_username_input = ""
        self.manage_child_password_input = ""
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def sync_manage_child_inputs(self, child: dict[str, str] | None) -> None:
        if not child:
            self.clear_manage_child_inputs()
            return
        self.manage_child_name_input = child["full_name"]
        self.manage_child_age_input = child["age"]
        self.manage_child_username_input = child["username"]
        self.manage_child_password_input = ""
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False

    def submit_parent_child_update(self, _e: ft.ControlEvent) -> None:
        active_child = self.active_parent_child()
        if not active_child:
            self.manage_child_feedback = "Сначала выбери ребёнка."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if not self.supabase_connection.is_ready or not self.supabase:
            self.manage_child_feedback = "Сначала настрой подключение к Supabase."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if not self.parent_session_profile or not self.parent_session_password:
            self.manage_child_feedback = "Сессия родителя недоступна. Войди заново."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        child_name = self.manage_child_name_input.strip()
        child_age_text = self.manage_child_age_input.strip()
        child_username = self.manage_child_username_input.strip().lower()
        child_password = self.manage_child_password_input

        if len(child_name) < 2:
            self.manage_child_feedback = "Имя ребёнка должно содержать минимум 2 символа."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if not child_age_text.isdigit():
            self.manage_child_feedback = "Возраст нужно указать цифрами."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        child_age = int(child_age_text)
        if child_age < 1 or child_age > 18:
            self.manage_child_feedback = "Возраст ребёнка должен быть в диапазоне 1-18 лет."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if len(child_username) < 3:
            self.manage_child_feedback = "Логин ребёнка должен содержать минимум 3 символа."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if child_password and len(child_password) < 4:
            self.manage_child_feedback = "Новый пароль ребёнка должен содержать минимум 4 символа."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        try:
            response = self.supabase.rpc(
                "parent_update_child",
                {
                    "p_child_id": active_child["id"],
                    "p_child_name": child_name,
                    "p_child_age": child_age,
                    "p_child_username": child_username,
                    "p_child_password": child_password,
                    "p_parent_username": self.parent_session_profile["username"],
                    "p_parent_password": self.parent_session_password,
                },
            ).execute()
        except Exception as exc:
            self.manage_child_feedback = self.describe_supabase_error(exc)
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        child = self.extract_child_rpc_row(response)
        if not child:
            self.manage_child_feedback = "Не удалось обновить данные ребёнка."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        self.manage_child_password_input = ""
        self.manage_child_feedback = f"Данные ребёнка {child['full_name']} обновлены."
        self.manage_child_feedback_is_error = False
        self.load_parent_children(preferred_child_id=child["id"])
        self.mascot_message = f"Профиль ребёнка {child['full_name']} обновлён."
        self.refresh()

    def delete_active_child(self, _e: ft.ControlEvent) -> None:
        active_child = self.active_parent_child()
        if not active_child:
            self.manage_child_feedback = "Сначала выбери ребёнка."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if not self.supabase_connection.is_ready or not self.supabase:
            self.manage_child_feedback = "Сначала настрой подключение к Supabase."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return
        if not self.parent_session_profile or not self.parent_session_password:
            self.manage_child_feedback = "Сессия родителя недоступна. Войди заново."
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        child_id = active_child["id"]
        child_name = active_child["full_name"]

        try:
            self.supabase.rpc(
                "parent_delete_child",
                {
                    "p_child_id": child_id,
                    "p_parent_username": self.parent_session_profile["username"],
                    "p_parent_password": self.parent_session_password,
                },
            ).execute()
        except Exception as exc:
            self.manage_child_feedback = self.describe_supabase_error(exc)
            self.manage_child_feedback_is_error = True
            self.refresh()
            return

        self.parent_children = [child for child in self.parent_children if child["id"] != child_id]
        if self.child_session_profile and self.child_session_profile["id"] == child_id:
            self.reset_child_access()
        if self.parent_children:
            self.set_active_child_profile(self.parent_children[0])
        else:
            self.active_child_profile = None
            self.clear_manage_child_inputs()
        self.load_parent_children()
        self.manage_child_feedback = f"Ребёнок {child_name} удалён."
        self.manage_child_feedback_is_error = False
        self.mascot_message = f"Аккаунт ребёнка {child_name} удалён."
        self.refresh()

    @staticmethod
    def describe_supabase_error(exc: Exception) -> str:
        message = str(exc)
        lowered = message.lower()
        if (
            "could not find the function public.parent_add_child" in lowered
            or "could not find the function public.parent_list_children" in lowered
            or "could not find the function public.parent_update_child" in lowered
            or "could not find the function public.parent_delete_child" in lowered
        ):
            return "В Supabase ещё не созданы функции для детей. Выполни обновлённый SQL."
        if "column \"age\" of relation \"children\" does not exist" in lowered or "column \"height_cm\" of relation \"children\" does not exist" in lowered:
            return "Таблица children создана по старой схеме. Обнови SQL для детей."
        if "could not find the function public.child_login" in lowered:
            return "В Supabase ещё не создана функция child_login. Выполни обновлённый SQL."
        if "column reference \"child_id\" is ambiguous" in lowered:
            return "Функция обновления ребёнка в Supabase создана в старой версии. Выполни обновлённый SQL."
        if "invalid parent credentials" in lowered:
            return "Сессия родителя устарела. Войди заново."
        if "invalid child credentials" in lowered:
            return "Неверный логин или пароль ребёнка."
        if "child not found or access denied" in lowered:
            return "Ребёнок не найден или нет доступа к этому профилю."
        if "child username already registered" in lowered:
            return "Такой логин ребёнка уже занят."
        if "child username must be at least 3 characters" in lowered:
            return "Логин ребёнка должен содержать минимум 3 символа."
        if "child password must be at least 4 characters" in lowered:
            return "Пароль ребёнка должен содержать минимум 4 символа."
        if "child name must be at least 2 characters" in lowered:
            return "Имя ребёнка должно содержать минимум 2 символа."
        if "child age must be between 1 and 18 years" in lowered:
            return "Возраст ребёнка должен быть в диапазоне 1-18 лет."
        if "child age must be between 1 and 18 years" in lowered:
            return "Возраст ребёнка должен быть в диапазоне 1-18 лет."
        if "username already registered" in lowered:
            return "Такой username уже зарегистрирован."
        if "duplicate key value" in lowered and "username" in lowered:
            return "Такой username уже зарегистрирован."
        if "password must be at least 6 characters" in lowered:
            return "Пароль должен содержать минимум 6 символов."
        if "username must be at least 3 characters" in lowered:
            return "Username должен содержать минимум 3 символа."
        if "full name must be at least 3 characters" in lowered:
            return "Укажи ФИО полностью."
        return f"Ошибка Supabase: {message}"

    @staticmethod
    def extract_parent_rpc_row(response) -> dict[str, str] | None:
        data = getattr(response, "data", None) or []
        if not data:
            return None
        row = data[0]
        return {
            "id": str(row.get("parent_id", "")).strip(),
            "full_name": str(row.get("full_name", "")).strip(),
            "username": str(row.get("username", "")).strip(),
        }

    @staticmethod
    def extract_child_rpc_rows(response) -> list[dict[str, str]]:
        rows = getattr(response, "data", None) or []
        children: list[dict[str, str]] = []
        for row in rows:
            children.append(
                {
                    "id": str(row.get("child_id", "")).strip(),
                    "full_name": str(row.get("child_name", "")).strip(),
                    "age": str(row.get("age", "")).strip(),
                    "username": str(row.get("username", "")).strip(),
                }
            )
        return children

    @classmethod
    def extract_child_rpc_row(cls, response) -> dict[str, str] | None:
        children = cls.extract_child_rpc_rows(response)
        return children[0] if children else None

    def set_active_child_profile(self, child: dict[str, str]) -> None:
        self.active_child_profile = child
        self.state.child_name = child["full_name"]
        self.state.child_age = child["age"]
        self.sync_manage_child_inputs(child)

    def load_parent_children(self, preferred_child_id: str | None = None) -> None:
        if not self.supabase_connection.is_ready or not self.supabase:
            return
        if not self.parent_session_profile or not self.parent_session_password:
            return

        try:
            response = self.supabase.rpc(
                "parent_list_children",
                {
                    "p_parent_username": self.parent_session_profile["username"],
                    "p_parent_password": self.parent_session_password,
                },
            ).execute()
        except Exception as exc:
            self.parent_child_feedback = self.describe_supabase_error(exc)
            self.parent_child_feedback_is_error = True
            return

        self.parent_children = self.extract_child_rpc_rows(response)
        if not self.parent_children:
            self.active_child_profile = None
            self.clear_manage_child_inputs()
            return
        selected_child = None
        if preferred_child_id:
            selected_child = next((child for child in self.parent_children if child["id"] == preferred_child_id), None)
        elif self.active_child_profile:
            selected_child = next((child for child in self.parent_children if child["id"] == self.active_child_profile["id"]), None)
        elif self.parent_children:
            selected_child = self.parent_children[0]

        if selected_child:
            self.set_active_child_profile(selected_child)

    def set_child_session(self, child: dict[str, str]) -> None:
        self.child_session_profile = child
        self.child_view = "hub"
        self.child_username_input = ""
        self.child_password_input = ""
        self.child_auth_error = ""
        self.guidy_open = False
        self.guidy_message = self.current_guidy_default_message()
        self.set_active_child_profile(child)

    def set_parent_session(self, profile: dict[str, str], password: str | None = None) -> None:
        self.parent_session_user_id = profile["id"]
        self.parent_session_profile = profile
        self.parent_session_password = password
        self.parent_view = "hub"
        self.parent_auth_error = ""
        self.parent_full_name_input = ""
        self.parent_username_input = ""
        self.parent_password_input = ""
        self.parent_confirm_password_input = ""
        self.parent_child_name_input = ""
        self.parent_child_age_input = ""
        self.parent_child_username_input = ""
        self.parent_child_password_input = ""
        self.parent_child_feedback = ""
        self.parent_child_feedback_is_error = False
        self.manage_child_name_input = ""
        self.manage_child_age_input = ""
        self.manage_child_username_input = ""
        self.manage_child_password_input = ""
        self.manage_child_feedback = ""
        self.manage_child_feedback_is_error = False
        self.load_parent_children()

    def supabase_status_text(self, prefix: str = "Supabase") -> str:
        if self.supabase_connection.is_ready:
            key_name = self.supabase_connection.key_name or "key"
            return f"{prefix}: подключен через {key_name}"
        return f"{prefix}: {self.supabase_connection.error}"

    def supabase_status_color(self) -> str:
        return PALETTE["accent_2"] if self.supabase_connection.is_ready else "#C95A6A"

    def reward_star(self, _e: ft.ControlEvent) -> None:
        self.state.record_activity(stars=1, note="Родитель добавил поощрительную звезду.")
        self.mascot_message = "Звезда добавлена в достижения."
        self.refresh()

    def reward_badge(self, _e: ft.ControlEvent) -> None:
        badge = next((item for item in PARENT_BADGES if item not in self.state.badges), PARENT_BADGES[-1])
        self.state.record_activity(
            stars=2,
            badge=badge,
            note=f"Родитель отметил достижение: {badge}.",
        )
        self.mascot_message = f"Новое достижение: {badge}."
        self.refresh()

    def focus_title(self) -> str:
        return f"Раунд {self.focus_round}" if self.focus_round else "Раунд ещё не начат"

    def focus_sequence_text(self) -> str:
        if not self.focus_sequence:
            return "Последовательность появится здесь."
        if self.focus_sequence_visible:
            return " ".join(item["emoji"] for item in self.focus_sequence)
        return "Последовательность скрыта. Введи ответ ниже."

    def focus_answer_text(self) -> str:
        if not self.focus_answer:
            return "Твой ответ: пока пусто."
        return "Твой ответ: " + " ".join(item["emoji"] for item in self.focus_answer)

    def card(
        self,
        title: str,
        subtitle: str | None = None,
        controls: list[ft.Control] | None = None,
    ) -> ft.Container:
        items: list[ft.Control] = [
            ft.Text(title, size=24, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
        ]
        if subtitle:
            items.append(ft.Text(subtitle, size=14, color=PALETTE["muted"]))
        if controls:
            items.extend(controls)
        return ft.Container(
            bgcolor=PALETTE["card"],
            border=ft.Border.all(1, PALETTE["line"]),
            border_radius=30,
            padding=22,
            shadow=[
                ft.BoxShadow(
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.1, PALETTE["shadow"]),
                    offset=ft.Offset(0, 10),
                )
            ],
            content=ft.Column(spacing=14, controls=items),
        )

    @staticmethod
    def asset_path(name: str) -> str:
        return f"illustrations/{name}.svg"

    def svg_figure(self, name: str, width: int = 76, height: int = 76) -> ft.Image:
        return ft.Image(
            src=self.asset_path(name),
            width=width,
            height=height,
            fit=IMAGE_FIT_CONTAIN,
        )

    def art_panel(self, name: str, frame: int = 78, image: int = 58) -> ft.Container:
        return ft.Container(
            width=frame,
            height=frame,
            border_radius=max(18, frame // 3),
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            alignment=ft.Alignment(0, 0),
            content=self.svg_figure(name, width=image, height=image),
        )

    def hero_card(self, title: str, subtitle: str, icon, colors: list[str], art: str | None = None) -> ft.Container:
        return ft.Container(
            height=168,
            border_radius=32,
            gradient=ft.LinearGradient(
                colors=colors,
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.16, ft.Colors.WHITE)),
            shadow=[
                ft.BoxShadow(
                    blur_radius=24,
                    color=ft.Colors.with_opacity(0.14, PALETTE["shadow"]),
                    offset=ft.Offset(0, 12),
                )
            ],
            padding=22,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=6,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(title, size=27, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                            ft.Text(subtitle, size=14, color=PALETTE["text"]),
                            self.soft_chip("Мягкий режим"),
                        ],
                    ),
                    self.art_panel(art, frame=78, image=62)
                    if art
                    else ft.Container(
                        width=78,
                        height=78,
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                        border_radius=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, size=40, color=PALETTE["text"]),
                    ),
                ],
            ),
        )

    def icon_tile(self, title: str, caption: str, icon, on_click, colors: list[str], art: str | None = None) -> ft.Container:
        return ft.Container(
            expand=1,
            height=162,
            on_click=on_click,
            ink=True,
            border_radius=28,
            gradient=ft.LinearGradient(
                colors=[colors[0], PALETTE["card"]],
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            border=ft.Border.all(1, PALETTE["line"]),
            shadow=[
                ft.BoxShadow(
                    blur_radius=18,
                    color=ft.Colors.with_opacity(0.09, PALETTE["shadow"]),
                    offset=ft.Offset(0, 8),
                )
            ],
            padding=18,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                spacing=12,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            self.art_panel(art, frame=58, image=42)
                            if art
                            else ft.Container(
                                width=58,
                                height=58,
                                bgcolor=ft.Colors.with_opacity(0.24, ft.Colors.WHITE),
                                border_radius=18,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(icon, color=PALETTE["text"], size=30),
                            ),
                            ft.Container(
                                width=34,
                                height=34,
                                bgcolor=PALETTE["surface"],
                                border=ft.Border.all(1, PALETTE["line"]),
                                border_radius=17,
                                alignment=ft.Alignment(0, 0),
                                content=ft.Icon(ft.Icons.NORTH_EAST_ROUNDED, color=PALETTE["muted"], size=18),
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=6,
                        controls=[
                            ft.Text(title, size=18, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                            ft.Text(caption, size=13, color=PALETTE["muted"]),
                        ],
                    ),
                ],
            ),
        )

    def role_tile(self, title: str, caption: str, icon, on_click, colors: list[str], art: str | None = None) -> ft.Container:
        return ft.Container(
            height=182,
            on_click=on_click,
            ink=True,
            border_radius=32,
            gradient=ft.LinearGradient(
                colors=colors,
                begin=ft.Alignment(-1, -1),
                end=ft.Alignment(1, 1),
            ),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.18, ft.Colors.WHITE)),
            shadow=[
                ft.BoxShadow(
                    blur_radius=22,
                    color=ft.Colors.with_opacity(0.12, PALETTE["shadow"]),
                    offset=ft.Offset(0, 12),
                )
            ],
            padding=24,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=8,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(title, size=30, weight=ft.FontWeight.W_700, color=PALETTE["text"]),
                            ft.Text(caption, size=16, color=PALETTE["muted"]),
                            ft.Container(
                                bgcolor=ft.Colors.with_opacity(0.24, ft.Colors.WHITE),
                                border_radius=999,
                                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                                content=ft.Text("Открыть", size=13, color=PALETTE["text"], weight=ft.FontWeight.W_600),
                            ),
                        ],
                    ),
                    self.art_panel(art, frame=78, image=60)
                    if art
                    else ft.Container(
                        width=78,
                        height=78,
                        bgcolor=ft.Colors.with_opacity(0.22, ft.Colors.WHITE),
                        border_radius=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icon, size=40, color=PALETTE["text"]),
                    ),
                ],
            ),
        )

    def game_shell(self, title: str, controls: list[ft.Control]) -> ft.Container:
        return ft.Container(
            bgcolor=PALETTE["card"],
            border=ft.Border.all(1, PALETTE["line"]),
            border_radius=30,
            padding=22,
            shadow=[
                ft.BoxShadow(
                    blur_radius=18,
                    color=ft.Colors.with_opacity(0.1, PALETTE["shadow"]),
                    offset=ft.Offset(0, 8),
                )
            ],
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.Text(title, size=30, weight=ft.FontWeight.W_700, color=PALETTE["text"])] + controls,
            ),
        )

    def memory_card_tile(self, card: dict[str, str], index: int) -> ft.Container:
        is_matched = card["pair_id"] in self.memory_matched_ids
        is_selected = index in self.memory_selected_indices
        is_open = self.memory_preview_visible or is_matched or is_selected

        if is_matched:
            background = PALETTE["good"]
            border_color = "#6BCB96"
        elif is_selected:
            background = PALETTE["warning"]
            border_color = "#E5B93D"
        else:
            background = PALETTE["surface"] if is_open else "#DCE8F5"
            border_color = PALETTE["line"]

        return ft.Container(
            expand=1,
            height=138,
            border_radius=26,
            bgcolor=background,
            border=ft.Border.all(2, border_color),
            padding=16,
            ink=True,
            on_click=lambda _e, card_index=index: self.open_memory_card(card_index),
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        f"{card['emoji']}" if is_open else "❔",
                        size=42,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        card["label"] if is_open else "Найди пару",
                        size=17,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE["text"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    def music_option_tile(self, item: dict[str, object]) -> ft.Container:
        is_active = self.music_selected_id == item["id"]
        return ft.Container(
            expand=1,
            height=138,
            border_radius=28,
            bgcolor=item["color"] if is_active else PALETTE["surface"],
            border=ft.Border.all(2, "#6FA8DC" if is_active else PALETTE["line"]),
            padding=16,
            ink=True,
            on_click=self.set_music_track(str(item["id"])),
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(str(item["emoji"]), size=42, text_align=ft.TextAlign.CENTER),
                    ft.Text(
                        str(item["title"]),
                        size=17,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE["text"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        str(item["caption"]),
                        size=13,
                        color=PALETTE["muted"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    def music_timer_chip(self, minutes: int) -> ft.Container:
        is_active = self.music_timer_minutes == minutes
        return ft.Container(
            expand=1,
            height=54,
            border_radius=18,
            bgcolor=PALETTE["accent"] if is_active else PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            ink=True,
            on_click=self.set_music_timer(minutes),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                f"{minutes} мин",
                size=15,
                weight=ft.FontWeight.W_700,
                color=PALETTE["text"],
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def drawing_color_swatch(self, color: str) -> ft.Container:
        is_active = self.drawing_selected_color == color and not self.drawing_eraser_enabled
        return ft.Container(
            width=54,
            height=54,
            border_radius=27,
            bgcolor=color,
            border=ft.Border.all(3, PALETTE["nav"] if is_active else PALETTE["line"]),
            ink=True,
            on_click=self.set_drawing_color(color),
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(ft.Icons.CHECK_ROUNDED, color=ft.Colors.WHITE, size=20) if is_active else None,
        )

    def drawing_brush_chip(self, size: int) -> ft.Container:
        is_active = self.drawing_brush_size == size
        return ft.Container(
            expand=1,
            height=56,
            border_radius=18,
            bgcolor=PALETTE["accent"] if is_active else PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            ink=True,
            on_click=self.set_drawing_brush_size(size),
            alignment=ft.Alignment(0, 0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Container(
                        width=size + 6,
                        height=size + 6,
                        border_radius=999,
                        bgcolor=PALETTE["text"],
                    ),
                    ft.Text(
                        f"{size}px",
                        size=15,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE["text"],
                    ),
                ],
            ),
        )

    def emotion_option_tile(self, item: dict[str, str], correct_emotion: str) -> ft.Container:
        is_correct = item["emotion"] == correct_emotion
        is_selected = item["emotion"] == self.emotion_selected_answer

        if not self.emotion_selected_answer:
            background = PALETTE["surface"]
            border_color = PALETTE["line"]
        elif is_correct:
            background = PALETTE["good"]
            border_color = "#6BCB96"
        elif is_selected:
            background = PALETTE["danger"]
            border_color = "#E56B7A"
        else:
            background = PALETTE["surface"]
            border_color = PALETTE["line"]

        return ft.Container(
            expand=1,
            height=122,
            bgcolor=background,
            border=ft.Border.all(2, border_color),
            border_radius=26,
            padding=16,
            ink=True,
            on_click=lambda _e, emotion=item["emotion"]: self.answer_emotion(emotion),
            content=ft.Column(
                spacing=8,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(item["sticker"], size=42, text_align=ft.TextAlign.CENTER),
                    ft.Text(
                        item["emotion"],
                        size=18,
                        weight=ft.FontWeight.W_700,
                        color=PALETTE["text"],
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    def emotion_feedback_color(self) -> str:
        if self.emotion_feedback.startswith("Верно"):
            return "#2E8B57"
        if self.emotion_feedback.startswith("Почти"):
            return "#C95A6A"
        return PALETTE["muted"]

    def sub_back(self, text: str, on_click) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Container(
                    bgcolor=PALETTE["card"],
                    border=ft.Border.all(1, PALETTE["line"]),
                    border_radius=18,
                    padding=ft.Padding.symmetric(horizontal=10, vertical=8),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.IconButton(ft.Icons.ARROW_BACK_ROUNDED, icon_color=PALETTE["text"], on_click=on_click),
                            ft.Text(text, color=PALETTE["text"], size=14, weight=ft.FontWeight.W_600),
                        ],
                    ),
                ),
            ]
        )

    def soft_chip(self, text: str) -> ft.Container:
        return ft.Container(
            bgcolor=PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            border_radius=999,
            padding=ft.Padding.symmetric(horizontal=14, vertical=8),
            content=ft.Text(text, color=PALETTE["muted"], size=13, weight=ft.FontWeight.W_600),
        )

    def hero_chip(self, title: str, value: str) -> ft.Container:
        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.18, ft.Colors.WHITE),
            border_radius=18,
            padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(title, color=PALETTE["hero_text"], size=11),
                    ft.Text(value, color=PALETTE["hero_text"], size=15, weight=ft.FontWeight.W_700),
                ],
            ),
        )

    def reward_chip(self, text: str) -> ft.Container:
        return ft.Container(
            bgcolor=PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            border_radius=18,
            padding=12,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.STAR, color="#D7A32B", size=18),
                    ft.Text(text, color=PALETTE["text"], size=14),
                ],
            ),
        )

    def bullet(self, text: str) -> ft.Text:
        return ft.Text(f"* {text}", color=PALETTE["text"], size=15)

    def info_line(self, label: str, value: str) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(label, color=PALETTE["muted"], size=14),
                ft.Text(value, color=PALETTE["text"], size=14, weight=ft.FontWeight.W_600),
            ],
        )

    def stat_pill(self, title: str, value: str) -> ft.Container:
        return ft.Container(
            bgcolor=PALETTE["surface"],
            border=ft.Border.all(1, PALETTE["line"]),
            border_radius=999,
            padding=ft.Padding.symmetric(horizontal=12, vertical=8),
            content=ft.Text(f"{title}: {value}", color=PALETTE["text"], size=13),
        )

    def profile_field(
        self,
        label: str,
        value: str,
        on_change,
        multiline: bool = False,
        password: bool = False,
        can_reveal_password: bool = False,
        keyboard_type=ft.KeyboardType.TEXT,
        max_length: int | None = None,
        on_submit=None,
    ) -> ft.TextField:
        return ft.TextField(
            label=label,
            value=value,
            on_change=on_change,
            on_submit=on_submit,
            multiline=multiline,
            min_lines=2 if multiline else None,
            max_lines=4 if multiline else None,
            password=password,
            can_reveal_password=can_reveal_password,
            keyboard_type=keyboard_type,
            max_length=max_length,
            filled=True,
            fill_color=PALETTE["surface"],
            border_color=PALETTE["line"],
            focused_border_color=PALETTE["nav"],
            border_radius=20,
            color=PALETTE["text"],
            content_padding=ft.Padding(left=18, right=18, top=16, bottom=16),
        )

    def app_button(
        self,
        text: str,
        on_click,
        bgcolor: str,
        color: str = PALETTE["text"],
        expand: int | bool | None = None,
        width: int | None = 340,
    ) -> ft.FilledButton:
        return ft.FilledButton(
            content=ft.Text(text, color=color, text_align=ft.TextAlign.CENTER),
            on_click=on_click,
            expand=expand,
            width=None if expand is not None else width,
            height=54,
            style=ft.ButtonStyle(
                bgcolor=bgcolor,
                color=color,
                side=ft.BorderSide(1, PALETTE["line"] if bgcolor == PALETTE["surface"] else bgcolor),
                padding=ft.Padding.symmetric(horizontal=20, vertical=16),
                shape=ft.RoundedRectangleBorder(radius=18),
            ),
        )

    def compact_button(self, text: str, on_click) -> ft.FilledButton:
        return ft.FilledButton(
            content=ft.Text(text, color=PALETTE["text"], text_align=ft.TextAlign.CENTER),
            on_click=on_click,
            expand=1,
            height=52,
            style=ft.ButtonStyle(
                bgcolor=PALETTE["surface"],
                side=ft.BorderSide(1, PALETTE["line"]),
                color=PALETTE["text"],
                padding=ft.Padding.symmetric(horizontal=14, vertical=12),
                shape=ft.RoundedRectangleBorder(radius=16),
            ),
        )

    @staticmethod
    def chunked(items: list[dict[str, str]], size: int) -> list[list[dict[str, str]]]:
        return [items[index : index + size] for index in range(0, len(items), size)]

    @staticmethod
    def chunked_switcher(items: list[tuple[str, str, str, object]], size: int) -> list[list[tuple[str, str, str, object]]]:
        return [items[index : index + size] for index in range(0, len(items), size)]


def main(page: ft.Page) -> None:
    app = MobileSupportApp(page)
    app.configure_page()
    app.refresh()


if __name__ == "__main__":
    ft.run(main, assets_dir="assets")

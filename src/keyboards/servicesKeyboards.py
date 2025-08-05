import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Tuple

from src.models.Service import Service
from src.utils.messages import SERVICES_CATEGORY, SERVICES, HAIR_SERVICES, COSMETOLOGY, NAILS_SERVICES, \
    HARDWARE_SERVICES, MAKEUP_SERVICES, BROWS_LASHES_SERVICES, SPA_SERVICES, KIDS_SERVICES, ALL_SERVICES

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 8


def create_paginated_keyboard(
        items: List[Tuple[str, str]],
        callback_prefix: str,
        page: int = 0,
        back_callback: str = None,
        category_key: str = None  # Добавляем ключ категории для пагинации
) -> InlineKeyboardMarkup:
    """Создает клавиатуру с пагинацией"""
    builder = InlineKeyboardBuilder()

    # Вычисляем границы страницы
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]

    # Добавляем кнопки текущей страницы
    for text, callback in page_items:
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"{callback_prefix}:{callback}"
        ))

    builder.adjust(1)  # По одной кнопке в ряд

    # Добавляем навигацию если больше одной страницы
    total_pages = (len(items) - 1) // ITEMS_PER_PAGE + 1
    if total_pages > 1:
        navigation_buttons = []

        # Кнопка "Назад"
        if page > 0:
            navigation_buttons.append(InlineKeyboardButton(
                text="⬅️ Пред",
                callback_data=f"page:{category_key}:{page - 1}"
            ))

        # Показываем текущую страницу
        navigation_buttons.append(InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data=f"current_page"
        ))

        # Кнопка "Вперед"
        if page < total_pages - 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="След ➡️",
                callback_data=f"page:{category_key}:{page + 1}"
            ))

        builder.row(*navigation_buttons)

    # Кнопка "Назад" в главное меню
    if back_callback:
        builder.add(InlineKeyboardButton(
            text="🔙 Назад",
            callback_data=back_callback
        ))

    return builder.as_markup()


def get_category_keyboard() -> InlineKeyboardMarkup:
    """Главная клавиатура с категориями услуг"""
    builder = InlineKeyboardBuilder()

    for text, callback in SERVICES_CATEGORY:
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"category:{callback}"
        ))

    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back:main_menu"
    ))

    builder.adjust(1)  # По две кнопки в ряд для лучшего использования пространства
    return builder.as_markup()

def get_hair_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для парикмахерских услуг с пагинацией"""
    return create_paginated_keyboard(
        items=HAIR_SERVICES,
        callback_prefix="service:hair",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="hair_services"
    )

def get_cosmetology_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для косметологических услуг с пагинацией"""
    return create_paginated_keyboard(
        items=COSMETOLOGY,
        callback_prefix="service:cosmetology",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="cosmetology"
    )

def get_nails_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для услуг ногтевого сервиса с пагинацией"""
    return create_paginated_keyboard(
        items=NAILS_SERVICES,
        callback_prefix="service:nails",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="nails_services"
    )

def get_hardware_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для аппаратных услуг с пагинацией"""
    return create_paginated_keyboard(
        items=HARDWARE_SERVICES,
        callback_prefix="service:hardware",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="hardware_services"
    )

def get_makeup_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для услуг визажа и макияжа с пагинацией"""
    return create_paginated_keyboard(
        items=MAKEUP_SERVICES,
        callback_prefix="service:makeup",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="makeup_services"
    )

def get_brows_lashes_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для услуг бровей и ресниц с пагинацией"""
    return create_paginated_keyboard(
        items=BROWS_LASHES_SERVICES,
        callback_prefix="service:brows_lashes",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="brows_lashes_services"
    )

def get_spa_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для SPA услуг с пагинацией"""
    return create_paginated_keyboard(
        items=SPA_SERVICES,
        callback_prefix="service:spa",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="spa_services"
    )

def get_kids_services_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Клавиатура для детских услуг с пагинацией"""
    return create_paginated_keyboard(
        items=KIDS_SERVICES,
        callback_prefix="service:kids",
        page=page,
        back_callback="back:CHOOSE_SERVICE",
        category_key="kids_services"
    )


def get_search_result_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для вывода результатов поиска """


def get_services_keyboard(service: int) -> InlineKeyboardMarkup:
    """Клавиатура услуги"""
    builder = InlineKeyboardBuilder()

    for text, callback in SERVICES:
        builder.add(InlineKeyboardButton(
            text=text,
            callback_data=f"service_select:{service}:{callback}"
        ))

    builder.add(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back:main_menu"
    ))

    builder.adjust(1)
    return builder.as_markup()

def get_booking_confirmation_keyboard(booking_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения бронирования"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="✅ Подтвердить",
            callback_data=f"booking:confirm:{booking_id}"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data=f"booking:cancel:{booking_id}"
        )
    )

    return builder.as_markup()



def create_search_results_keyboard(services: List[Service], search_query: str, page: int = 0) -> InlineKeyboardMarkup:
    """Создает клавиатуру с результатами поиска с пагинацией"""
    builder = InlineKeyboardBuilder()

    # Пагинация - 8 услуг на страницу
    items_per_page = 8
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_services = services[start_idx:end_idx]

    # Добавляем кнопки услуг
    for service in page_services:
        # Форматируем время
        duration = f"{service.duration_minutes} мин" if service.duration_minutes < 60 else f"{service.duration_minutes // 60}ч {service.duration_minutes % 60}м" if service.duration_minutes % 60 else f"{service.duration_minutes // 60}ч"

        button_text = f"{ALL_SERVICES[service.name]} • {service.price}₽"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"service:search:{service.name}"
        ))

    builder.adjust(1)  # По одной кнопке в ряд

    # Добавляем навигацию если больше одной страницы
    total_pages = (len(services) - 1) // items_per_page + 1
    if total_pages > 1:
        navigation_buttons = []

        if page > 0:
            navigation_buttons.append(InlineKeyboardButton(
                text="⬅️ Пред",
                callback_data=f"search_page:{search_query}:{page - 1}"
            ))

        navigation_buttons.append(InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        ))

        if page < total_pages - 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="След ➡️",
                callback_data=f"search_page:{search_query}:{page + 1}"
            ))

        builder.row(*navigation_buttons)

    # Кнопки управления
    builder.row(
        InlineKeyboardButton(text="🔍 Новый поиск", callback_data="MAIN:SEARCH"),
        InlineKeyboardButton(text="🔙 На главную", callback_data="back:main_menu")
    )

    return builder.as_markup()
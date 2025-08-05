# src/keyboards/masterKeyboard.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List

from src.models.users.Master import Master
from src.models.Service import Service
from src.utils.messages import ALL_SERVICES

# Количество мастеров на одной странице
ITEMS_PER_PAGE = 8

def create_masters_paginated_keyboard(
    masters: List[Master],
    page: int = 0
) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком мастеров с пагинацией.
    """
    builder = InlineKeyboardBuilder()

    # Вычисляем границы страницы
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_masters = masters[start_idx:end_idx]

    # Добавляем кнопки с именами мастеров
    for master in page_masters:
        button_text = f"👤 {master.name} - {ALL_SERVICES[master.specialization]}"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"master_info:{master.id}"
        ))

    builder.adjust(1)  # По одной кнопке в ряд

    # Добавляем навигацию, если страниц больше одной
    total_pages = (len(masters) - 1) // ITEMS_PER_PAGE + 1
    if total_pages > 1:
        navigation_buttons = []

        # Кнопка "Назад"
        if page > 0:
            navigation_buttons.append(InlineKeyboardButton(
                text="⬅️ Пред",
                callback_data=f"masters_page:{page - 1}"
            ))

        # Показываем текущую страницу
        navigation_buttons.append(InlineKeyboardButton(
            text=f"{page + 1}/{total_pages}",
            callback_data="current_page"
        ))

        # Кнопка "Вперед"
        if page < total_pages - 1:
            navigation_buttons.append(InlineKeyboardButton(
                text="След ➡️",
                callback_data=f"masters_page:{page + 1}"
            ))

        builder.row(*navigation_buttons)

    # Кнопка "Назад" в главное меню
    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data="back:main_menu"
    ))

    return builder.as_markup()

def create_master_services_keyboard( master_id: int, services: List[Service]) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком услуг конкретного мастера.
    """
    builder = InlineKeyboardBuilder()

    for service in services:
        button_text = f"{ALL_SERVICES[service.name]} - {service.price}₽"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"master_service:{master_id}:{service.id}"
        ))

    builder.adjust(1)

    # Кнопка "Назад" к списку мастеров
    builder.row(InlineKeyboardButton(
        text="🔙 К списку мастеров",
        callback_data="back:masters_list"
    ))

    return builder.as_markup()


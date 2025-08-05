from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils.messages import MAIN

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой возврата в главное меню"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text=MAIN['TO_MAIN'],
        callback_data="back:main_menu"
    ))

    return builder.as_markup()

def get_main_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главное меню"""
    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(
        text=MAIN['SEARCH'],
        callback_data="MAIN:SEARCH"
    ))
    builder.add(InlineKeyboardButton(
        text=MAIN['CATEGORY'],
        callback_data="MAIN:CATEGORY"
    ))
    builder.add(InlineKeyboardButton(
        text=MAIN['MASTERS'],
        callback_data="MASTERS"
    ))
    builder.add(InlineKeyboardButton(
        text=MAIN['INFO'],
        callback_data="MAIN:INFO"
    ))
    builder.adjust(1)
    return builder.as_markup()


import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from src.handlers.masterHandler import master_repo
from src.keyboards.mainKeyboards import get_main_keyboard, get_back_to_main_keyboard
from src.keyboards.masterKeyboard import create_masters_paginated_keyboard
from src.keyboards.servicesKeyboards import get_category_keyboard, get_services_keyboard, create_search_results_keyboard
from src.repository.ServiceRepository import ServiceRepository
from src.repository.UserRepository import UserRepository
from src.utils.messages import MAIN, MENU, ALL_SERVICES

logger = logging.getLogger(__name__)

router = Router()

# Создание репозиториев
user_repo = UserRepository()
service_repo = ServiceRepository()

class SearchStates(StatesGroup):
    waiting_for_search_query = State()

@router.message(Command("start"))
async def start_command(message: Message):
    """Обработка команды старт"""
    username = message.from_user.username
    telegram_id = message.from_user.id

    # Создание пользователя
    user, created = await user_repo.get_or_create(
        telegram_id=telegram_id,
        username=username
    )

    #Отправка приветственного сообщения
    await message.answer(
        MAIN['START'],
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("MAIN:"))
async def process_back(callback: CallbackQuery, state: FSMContext):
    """Обработка команды назад"""
    menu = callback.data.split(":")[1]

    if menu == "SEARCH":
        # Переводим пользователя в состояние ожидания поискового запроса
        await state.set_state(SearchStates.waiting_for_search_query)

        await callback.message.edit_text(
            text="🔍 <b>Поиск услуг</b>\n\n"
                 "Введите название или описание услуги, которую ищете:\n\n"
                 "<i>Например: стрижка, маникюр, массаж, окрашивание...</i>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="❌ Отмена", callback_data="back:main_menu")
            ]]),
            parse_mode="HTML"
        )
        return


    keyboards = {
        "CATEGORY": get_category_keyboard(),
        "SEARCH": get_category_keyboard(),
        "INFO": get_back_to_main_keyboard(),
    }

    if menu in keyboards:
        await callback.message.edit_text(
            text=MENU[menu],
            reply_markup=keyboards[menu]
        )

@router.callback_query(F.data.startswith("back:"))
async def process_back(callback: CallbackQuery):
    """Обработка команды назад"""
    menu = callback.data.split(":")[1]
    keyboards = {
        "CHOOSE_SERVICE": get_category_keyboard(),
        "masters_list": create_masters_paginated_keyboard(masters = await master_repo.get_all()),
        "main_menu": get_main_keyboard()
    }

    #TODO поменять для того чтобы после заказа отправлялось новое сообщение а не изменялось сообщение о подтверждении
    try:
        if menu in keyboards:
            await callback.message.answer(
                text=MENU[menu],
                reply_markup=keyboards[menu]
            )
    except Exception as e:
        await callback.message.delete()
        if menu in keyboards:
            await callback.message.answer(
                text=MENU[menu],
                reply_markup=keyboards[menu]
            )


@router.message(SearchStates.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    search_query = message.text.strip()
    logger.info(search_query)
    if len(search_query) < 2:
        await message.answer(
            text="❌ Запрос слишком короткий. Введите минимум 2 символа.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 Назад к категориям", callback_data="MAIN:CATEGORY")
            ]])
        )
        return

    try:

        # Поиск по названию
        # services_by_name = await service_repo.search_by_name(search_query)

        services_by_description = await service_repo.search_by_description(search_query)

        all_services = services_by_description
        unique_services = []
        seen_ids = set()

        for service in all_services:
            if service.id not in seen_ids:
                unique_services.append(service)
                seen_ids.add(service.id)

        # Сбрасываем состояние
        await state.clear()

        if unique_services:
            # Создаем клавиатуру с найденными услугами
            search_keyboard = create_search_results_keyboard(unique_services, search_query)

            await message.answer(
                text=f"🔍 <b>Результаты поиска по запросу:</b> \"{search_query}\"\n\n"
                     f"Найдено услуг: <b>{len(unique_services)}</b>",
                reply_markup=search_keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text=f"😔 <b>По запросу \"{search_query}\" ничего не найдено</b>\n\n"
                     f"Попробуйте:\n"
                     f"• Изменить запрос\n"
                     f"• Использовать другие ключевые слова\n"
                     f"• Выбрать услугу из категорий",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔍 Новый поиск", callback_data="MAIN:SEARCH")],
                    [InlineKeyboardButton(text="🔙 К категориям", callback_data="MAIN:CATEGORY")]
                ]),
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Ошибка при поиске: {e}")
        await state.clear()
        await message.answer(
            text="❌ Произошла ошибка при поиске. Попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="🔙 К категориям", callback_data="MAIN:CATEGORY")
            ]])
        )


# Обработчик пагинации для результатов поиска
@router.callback_query(F.data.startswith("search_page:"))
async def handle_search_pagination(callback: CallbackQuery):
    """Обработка пагинации результатов поиска"""
    try:
        _, search_query, page_str = callback.data.split(":")
        page = int(page_str)

        # Повторяем поиск
        # services_by_name = await service_repo.search_by_name(search_query)
        services_by_description = await service_repo.search_by_description(search_query)

        all_services = services_by_description
        unique_services = []
        seen_ids = set()

        for service in all_services:
            if service.id not in seen_ids:
                unique_services.append(service)
                seen_ids.add(service.id)

        if unique_services:
            search_keyboard = create_search_results_keyboard(unique_services, search_query, page)

            await callback.message.edit_text(
                text=f"🔍 <b>Результаты поиска по запросу:</b> \"{search_query}\"\n\n"
                     f"Найдено услуг: <b>{len(unique_services)}</b> (стр. {page + 1})",
                reply_markup=search_keyboard,
                parse_mode="HTML"
            )

    except Exception as e:
        logger.error(f"Ошибка при пагинации поиска: {e}")
        await callback.answer("Ошибка при загрузке страницы", show_alert=True)

    await callback.answer()


# Обработчик выбора услуги из результатов поиска
@router.callback_query(F.data.startswith("service:search:"))
async def process_search_service_selection(callback: CallbackQuery):
    """Обработка выбора услуги из результатов поиска"""
    service_name = callback.data.split(":", 2)[2]

    service_db = await service_repo.get_by_name(service_name)

    if service_db:
        # Форматируем время
        hours = service_db.duration_minutes // 60
        minutes = service_db.duration_minutes % 60

        if hours > 0 and minutes > 0:
            duration_text = f"{hours} ч {minutes} мин"
        elif hours > 0:
            duration_text = f"{hours} ч"
        else:
            duration_text = f"{minutes} мин"

        message_text = (
            f"✨ <b>Вы выбрали услугу:</b>\n\n"
            f"📋 <b>{ALL_SERVICES[service_db.name]}</b>\n\n"
            f"📝 <i>{service_db.description}</i>\n\n"
            f"💰 <b>Цена:</b> {service_db.price} ₽\n"
            f"⏱️ <b>Продолжительность:</b> {duration_text}\n\n"
            f"Что хотите сделать?"
        )

        await callback.message.edit_text(
            text=message_text,
            reply_markup=get_services_keyboard(service_name),
            parse_mode="HTML"
        )
    else:
        await callback.answer("Услуга не найдена", show_alert=True)



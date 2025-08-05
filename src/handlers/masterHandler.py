import logging
import os

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.fsm.context import FSMContext

from src.config.BotSingleton import BotSingleton
from src.keyboards.masterKeyboard import create_masters_paginated_keyboard, create_master_services_keyboard
from src.repository.MasterRepository import MasterRepository
from src.repository.ServiceRepository import ServiceRepository
from src.utils.messages import ALL_SERVICES

logger = logging.getLogger(__name__)

router_master = Router()

master_repo: MasterRepository = MasterRepository()
service_repo: ServiceRepository = ServiceRepository()

bot = BotSingleton().get_bot()


@router_master.callback_query(F.data.startswith("MASTERS"))
async def show_masters_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает первую страницу со списком всех мастеров.
    """
    await state.set_state("masters_list")

    masters = await master_repo.get_all()
    keyboard = create_masters_paginated_keyboard(masters=masters, page=0)

    message_text = "Выберите мастера, чтобы увидеть его информацию и услуги:"

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    await callback.answer()


@router_master.callback_query(F.data.startswith("masters_page:"))
async def masters_pagination_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает пагинацию списка мастеров.
    """
    page = int(callback.data.split(":")[1])

    masters = await master_repo.get_all()
    keyboard = create_masters_paginated_keyboard(masters=masters, page=page)

    message_text = "Выберите мастера, чтобы увидеть его информацию и услуги:"

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    await callback.answer()


def get_master_info_message(master):
    """
    Форматирует информацию о мастере  сообщение.
    """
    working_days_map = {
        1: "ПН", 2: "ВТ", 3: "СР", 4: "ЧТ", 5: "ПТ", 6: "СБ", 7: "ВС"
    }
    days = [working_days_map[int(day)] for day in master.working_days.split(',')]
    working_days_str = ", ".join(days)

    message = (
        f"<b>Мастер: {master.name}</b>\n"
        # f"<i>Специализация:</i> {ALL_SERVICES[master.specialization]}\n"
        f"<i>Опыт:</i> {master.experience_years} лет\n"
        f"<i>Рейтинг:</i> {'⭐' * int(master.rating)} ({master.rating:.1f}/5.0)\n\n"

        f"<b>График работы:</b>\n"
        f"<i>Часы:</i> {master.working_hours_start} - {master.working_hours_end}\n"
        f"<i>Дни:</i> {working_days_str}\n\n"
    )

    if master.phone:
        message += f"<i>Телефон:</i> {master.phone}\n"
    if master.email:
        message += f"<i>Email:</i> {master.email}\n"

    return message



@router_master.callback_query(F.data.startswith("master_info:"))
async def master_info_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает информацию о мастере и список его услуг.
    """
    master_id = int(callback.data.split(":")[1])

    master = await master_repo.get_by_id(master_id)
    if not master:
        await callback.answer("Мастер не найден.", show_alert=True)
        return

    # Получаем услуги мастера
    master_services_list = await master_repo.get_master_services(master_id)

    message_text = get_master_info_message(master)
    keyboard = create_master_services_keyboard(master_id=master_id, services=master_services_list)
    #TODO как то сохранять фото мастеров
    # photo_path = f"../images/{master.username}.jpg"
    photo_path = f"src/images/master_1.jpg"
    with open(photo_path, 'rb') as photo_file:
        photo_bytes = photo_file.read()

    if os.path.exists(photo_path):
        with open(photo_path, 'rb') as photo_file:
            photo_bytes = photo_file.read()
        logger.info("с фото")
        # Создаем объект BufferedInputFile из байтов
        photo_input = BufferedInputFile(photo_bytes, filename=f"master_1.jpg")

        await bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=photo_input,
            caption=message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        # Удаляем предыдущее сообщение, чтобы избежать дублирования
        # await callback.message.delete()

    else:
        logger.info("без фото")
        # Если изображения нет, отправляем только текст
        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    await callback.answer()


@router_master.callback_query(F.data.startswith("master_service:"))
async def master_service_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает детальную информацию о выбранной услуге мастера.
    """
    _, master_id, service_id = callback.data.split(":")
    master_id = int(master_id)
    service_id = int(service_id)

    master = await master_repo.get_by_id(master_id)
    service = await service_repo.get_by_id(service_id)

    if not master or not service:
        await callback.answer("Услуга или мастер не найдены.", show_alert=True)
        return

    # Здесь можно добавить логику перехода к бронированию
    message_text = f"<b>{ALL_SERVICES[service.name]}</b>\n\n" \
                   f"{service.description}\n\n" \
                   f"<b>Цена:</b> {service.price}₽\n" \
                   f"<b>Длительность:</b> {service.duration_minutes} мин\n\n" \
                   f"<b>Мастер:</b> {master.name}"
    try:
        await callback.message.edit_text(
            text=message_text,
            # Здесь можно добавить клавиатуру для бронирования
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗓️ Записаться", callback_data=f"ORDER:{master_id}:{service_id}")],
                [InlineKeyboardButton(text="🔙 К услугам мастера", callback_data=f"master_info:{master_id}")]
            ]),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.message.delete()
        await callback.message.answer(
            text=message_text,
            # Здесь можно добавить клавиатуру для бронирования
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🗓️ Записаться", callback_data=f"ORDER:{master_id}:{service_id}")],
                [InlineKeyboardButton(text="🔙 К услугам мастера", callback_data=f"master_info:{master_id}")]
            ]),
            parse_mode="HTML"
        )
    await callback.answer()


@router_master.callback_query(F.data == "back:masters_list")
async def back_to_masters_list_handler(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает к списку мастеров после просмотра информации о мастере.
    """
    # Предполагаем, что нужно вернуться на первую страницу
    await show_masters_handler(callback, state)


@router_master.callback_query(F.data.startswith("service_select_MASTERS"))
async def show_masters_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает первую страницу со списком всех мастеров.
    """
    await state.set_state("masters_list")

    masters = await master_repo.get_by_service()
    keyboard = create_masters_paginated_keyboard(masters=masters, page=0)

    message_text = "Выберите мастера, чтобы увидеть его информацию и услуги:"

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    await callback.answer()
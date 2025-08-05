import logging
from datetime import datetime
from typing import List

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.handlers.masterHandler import master_repo
from src.keyboards.mainKeyboards import get_back_to_main_keyboard
from src.keyboards.masterKeyboard import create_masters_paginated_keyboard
from src.keyboards.servicesKeyboards import get_nails_services_keyboard, get_hair_services_keyboard, \
    get_cosmetology_keyboard, get_hardware_services_keyboard, get_services_keyboard, get_makeup_services_keyboard, \
    get_brows_lashes_services_keyboard, get_spa_services_keyboard, get_kids_services_keyboard, get_category_keyboard
from src.models.Order import Order, OrderStatus
from src.models.users.Customer import Customer
from src.models.users.Master import Master
from src.repository.CustomerRepository import CustomerRepository
from src.repository.OrderRepository import OrderRepository
from src.repository.ServiceRepository import ServiceRepository
from src.repository.UserRepository import UserRepository
from src.states.BookingState import BookingState
from src.utils.messages import MENU, ORDER_CONFIRMATION_MESSAGE, ALL_SERVICES

logger = logging.getLogger(__name__)

services_router = Router()

# Создание репозиториев
user_repo = UserRepository()
service_repo = ServiceRepository()
order_repo = OrderRepository()
customer_repo = CustomerRepository()


@services_router.callback_query(F.data.startswith("category:"))
async def process_category(callback: CallbackQuery):
    """Функция для выбора категорий заказа"""
    category = callback.data.split(":")[1]

    keyboards = {
        "hair_services": get_hair_services_keyboard(),
        "cosmetology": get_cosmetology_keyboard(),
        "nails_services": get_nails_services_keyboard(),
        "hardware_services": get_hardware_services_keyboard(),
        "makeup_services": get_makeup_services_keyboard(),
        "brows_lashes_services": get_brows_lashes_services_keyboard(),
        "spa_services": get_spa_services_keyboard(),
        "kids_services": get_kids_services_keyboard()
    }

    category_names = {
        "hair_services": "💇‍♀️ Парикмахерские услуги",
        "cosmetology": "💆‍♀️ Косметология",
        "nails_services": "💅 Услуги ногтевого сервиса",
        "hardware_services": "🔧 Аппаратные услуги",
        "makeup_services": "💄 Визаж и макияж",
        "brows_lashes_services": "👁️ Услуги для бровей и ресниц",
        "spa_services": "🧴 SPA процедуры",
        "kids_services": "👶 Детские услуги"
    }

    if category in keyboards:
        category_name = category_names.get(category, "Услуги")
        await callback.message.edit_text(
            text=f"{category_name}\n\nВыберите услугу:",
            reply_markup=keyboards[category]
        )

    await callback.answer()


@services_router.callback_query(F.data.startswith("page:"))
async def handle_pagination(callback: CallbackQuery):
    """Обработка пагинации"""
    try:
        _, category, page = callback.data.split(":")
        page = int(page)
        logger.info(f"Pagination {category}:{page}, {callback.data}")

        keyboards = {
            "hair_services": get_hair_services_keyboard(page),
            "cosmetology": get_cosmetology_keyboard(page),
            "nails_services": get_nails_services_keyboard(page),
            "hardware_services": get_hardware_services_keyboard(page),
            "makeup_services": get_makeup_services_keyboard(page),
            "brows_lashes_services": get_brows_lashes_services_keyboard(page),
            "spa_services": get_spa_services_keyboard(page),
            "kids_services": get_kids_services_keyboard(page)
        }

        category_names = {
            "hair_services": "💇‍♀️ Парикмахерские услуги",
            "cosmetology": "💆‍♀️ Косметология",
            "nails_services": "💅 Услуги ногтевого сервиса",
            "hardware_services": "🔧 Аппаратные услуги",
            "makeup_services": "💄 Визаж и макияж",
            "brows_lashes_services": "👁️ Услуги для бровей и ресниц",
            "spa_services": "🧴 SPA процедуры",
            "kids_services": "👶 Детские услуги"
        }

        if category in keyboards:
            category_name = category_names.get(category, "Услуги")
            await callback.message.edit_text(
                text=f"{category_name} (стр. {page + 1})\n\nВыберите услугу:",
                reply_markup=keyboards[category]
            )
    except (ValueError, IndexError):
        await callback.answer("Ошибка навигации", show_alert=True)
        return

    await callback.answer()


@services_router.callback_query(F.data == "current_page")
async def current_page_handler(callback: CallbackQuery):
    """Обработчик для кнопки текущей страницы (ничего не делает)"""
    await callback.answer()


@services_router.callback_query(F.data.startswith("service:"))
async def process_service(callback: CallbackQuery):
    """Обработка выбора конкретной услуги"""
    try:
        parts = callback.data.split(":")
        if len(parts) >= 3:
            category = parts[1]
            service = parts[2]

            # получения услуги из базы данных
            service_db = await service_repo.get_by_name(service)

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

                # Формируем красивое сообщение
                message_text = (
                    f"📝 <i>{service_db.description}</i>\n\n"
                    f"💰 <b>Цена:</b> {service_db.price} ₽\n"
                    f"⏱️ <b>Продолжительность:</b> {duration_text}\n\n"
                    f"Что хотите сделать?"
                )

                await callback.message.edit_text(
                    text=message_text,
                    reply_markup=get_services_keyboard(service_db.id),
                    parse_mode="HTML"
                )
            else:
                await callback.message.edit_text(
                    text="❌ Услуга не найдена. Попробуйте еще раз.",
                    reply_markup=get_category_keyboard()
                )
    except Exception as e:
        await callback.answer("Произошла ошибка", show_alert=True)
        return

    await callback.answer()


async def create_master_select_keyboard(masters: List[Master], service_id: int):
    """Создает клавиатуру для выбора мастера при выбранной услуги"""
    builder = InlineKeyboardBuilder()

    for master in masters:
        button_text = f"👤 {master.name} - {ALL_SERVICES[master.specialization]}"
        builder.add(InlineKeyboardButton(
            text=button_text,
            callback_data=f"ORDER:{master.id}:{service_id}"
        ))

    builder.row(InlineKeyboardButton(
        text="🔙 Назад",
        callback_data=f"back:main_menu"
    ))
    builder.adjust(1)
    return builder.as_markup()


@services_router.callback_query(F.data.startswith("ORDER:"))
async def start_order_process(callback: CallbackQuery, state: FSMContext):
    """
    Инициирует процесс бронирования: сохраняет данные и запрашивает имя.
    """
    parts = callback.data.split(":")

    try:
        master_id = int(parts[1])
        service_id = int(parts[2])
    except (IndexError, ValueError):
        await callback.answer("Ошибка в данных заказа.", show_alert=True)
        return

    telegram_user_id = callback.from_user.id

    # Сохраняем данные в FSM-состоянии
    await state.update_data(
        master_id=master_id,
        service_id=service_id,
        telegram_user_id=telegram_user_id
    )

    customer = await customer_repo.get_by_telegram_id(telegram_user_id)
    master = await master_repo.get_by_id(master_id)
    service = await service_repo.get_by_id(service_id)
    appointment_datetime = datetime.now()

    if customer and customer.name and customer.phone:
        new_order = Order(
            user_id=customer.id,  # Используем ID клиента из БД
            master_id=master.id,
            service_id=service.id,
            appointment_datetime=appointment_datetime,
            duration_minutes=service.duration_minutes,
            total_price=service.price,
            status=OrderStatus.PENDING,
            client_name=customer.name,
            client_phone=customer.phone
        )

        created_order = await order_repo.create(new_order)

        # Отправляем подтверждение
        await  callback.message.edit_text(
            ORDER_CONFIRMATION_MESSAGE.format(
                order_id=created_order.id,
                master_name=master.name,
                service_name=service.name,
                price=created_order.total_price,
                duration=created_order.duration_minutes,
                datetime=created_order.appointment_datetime.strftime("%d.%m.%Y в %H:%M")
            ),
            reply_markup=get_back_to_main_keyboard(),
            parse_mode="HTML"
        )

        # Сбрасываем FSM-состояние
        await state.clear()


    else:
        # Если имени нет, запрашиваем его
        await callback.message.edit_text(
            "Для оформления заказа, пожалуйста, введите ваше имя."
        )
        await state.set_state(BookingState.waiting_for_name)

    await callback.answer()


@services_router.message(BookingState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """
    Обрабатывает введенное имя и запрашивает номер телефона.
    """
    user_name = message.text.strip()
    if len(user_name) < 2:
        await message.answer("Имя должно содержать не менее 2 символов. Пожалуйста, попробуйте еще раз.")
        return

    await state.update_data(client_name=user_name)

    await message.answer(
        "Спасибо! Теперь, пожалуйста, отправьте ваш номер телефона. "
        "Вы можете нажать на кнопку ниже, чтобы отправить его автоматически.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    await state.set_state(BookingState.waiting_for_phone)


@services_router.message(BookingState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """
    Обрабатывает номер телефона и создает заказ.
    """
    if message.contact:
        user_phone = message.contact.phone_number
    else:
        user_phone = message.text.strip()
        # Простая проверка номера телефона
        if not user_phone.replace('+', '').replace('-', '').replace('(', '').replace(')', '').isdigit() or len(
                user_phone) < 10:
            await message.answer("Пожалуйста, введите корректный номер телефона.")
            return

    await state.update_data(client_phone=user_phone)

    # Получаем все данные из FSM
    data = await state.get_data()

    master = await master_repo.get_by_id(data['master_id'])
    service = await service_repo.get_by_id(data['service_id'])

    if not master or not service:
        await message.answer("Произошла ошибка при поиске мастера или услуги.")
        await state.clear()
        return

    # TODO: Здесь по-прежнему нужна реализация выбора даты и времени
    appointment_datetime = datetime.now()

    # Ищем клиента по telegram_id. Если его нет, создаем.
    customer = await customer_repo.get_by_telegram_id(data['telegram_user_id'])
    if not customer:
        customer = Customer(
            telegram_id=data['telegram_user_id'],
            username=message.from_user.username,
            name=data.get('client_name'),
            phone=data.get('client_phone')
        )
        customer = await customer_repo.create(customer)
    else:
        # Обновляем данные существующего клиента
        customer.name = data.get('client_name') or customer.name
        customer.phone = data.get('client_phone') or customer.phone
        await customer_repo.update(customer)

    new_order = Order(
        user_id=customer.id,  # Используем ID клиента из БД
        master_id=master.id,
        service_id=service.id,
        appointment_datetime=appointment_datetime,
        duration_minutes=service.duration_minutes,
        total_price=service.price,
        status=OrderStatus.PENDING,
        client_name=customer.name,
        client_phone=customer.phone
    )

    created_order = await order_repo.create(new_order)

    # Отправляем подтверждение
    await message.answer(
        ORDER_CONFIRMATION_MESSAGE.format(
            order_id=created_order.id,
            master_name=master.name,
            service_name=service.name,
            price=created_order.total_price,
            duration=created_order.duration_minutes,
            datetime=created_order.appointment_datetime.strftime("%d.%m.%Y в %H:%M")
        ),
        reply_markup=get_back_to_main_keyboard(),
        parse_mode="HTML"
    )

    # Сбрасываем FSM-состояние
    await state.clear()

@services_router.callback_query(F.data.startswith("service_select:"))
async def process_service(callback: CallbackQuery):
    """Обработка выбора конкретной услуги"""
    try:
        parts = callback.data.split(":")
        # service = int(parts[1])                 # id TODO сделать проверку если это буковки
        select = parts[2]                       # действие

        service_id_str = parts[1]
        if not service_id_str.isdigit():
            service_from_db = await service_repo.get_by_name(service_id_str)
            service = service_from_db.id
        else:
            service = int(service_id_str)

        if (select == "MASTERS"):
            masters = await master_repo.get_by_service(service)
            logger.info(masters)
            keyboard = await create_master_select_keyboard(masters=masters, service_id=service)
            message_text = "Выберите мастера, чтобы увидеть его информацию и услуги:"

            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard
            )


        logger.info(f"Service select {service}:{select}")

            # TODO обработка действий услуги
            # order
            # masters
            # info


    except Exception as e:
        logger.error(e)
        await callback.answer("Произошла ошибка", show_alert=True)
        return

    await callback.answer()

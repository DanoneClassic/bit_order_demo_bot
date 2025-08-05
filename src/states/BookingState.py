from aiogram.fsm.state import State, StatesGroup


class BookingState(StatesGroup):
    """
    Состояния для процесса бронирования.
    """
    # Состояния для сбора данных клиента
    waiting_for_name = State()
    waiting_for_phone = State()

    # Состояния для выбора даты и времени
    waiting_for_date = State()
    waiting_for_time = State()

    # Состояние для подтверждения заказа
    waiting_for_confirmation = State()
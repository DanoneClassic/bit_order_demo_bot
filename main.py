import asyncio
import logging
import sys
from aiogram import Dispatcher
from src.config.BotSingleton import BotSingleton
from src.config.Database import db
from src.handlers.mainHandler import router
from src.handlers.masterHandler import router_master
from src.handlers.servicesHandler import services_router
from src.repository.CustomerRepository import CustomerRepository
from src.repository.UserRepository import UserRepository
from src.repository.MasterRepository import  MasterRepository
from src.repository.ServiceRepository import ServiceRepository
from src.repository.OrderRepository import OrderRepository
from src.services.MasterDataSeeder import MastersDataSeeder
from src.services.ServicesDataSeeder import ServicesDataSeeder

'''Logger config'''
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

'''Create bot'''
bot = BotSingleton().get_bot()

dp = Dispatcher()


def include_all_routes(dp: Dispatcher):
    dp.include_router(router)
    dp.include_router(services_router)
    dp.include_router(router_master)

async def init_db():
    await db.connect()

    user_repo = UserRepository()
    master_repo = MasterRepository()
    order_repo = OrderRepository()
    service_repo = ServiceRepository()
    customer_repo = CustomerRepository()

    await user_repo.create_table()
    await service_repo.create_table()
    await master_repo.create_table()
    await order_repo.create_table()
    await customer_repo.create_table()

    # # Заполненеие услуг
    # seeder = ServicesDataSeeder(service_repo)
    # await seeder.seed_all_services()
    #
    # # Заполнение мастеров
    # seederM = MastersDataSeeder(master_repo)
    # await seederM.seed_all_masters()


'''main function'''
async def main():
    await init_db()
    include_all_routes(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


'''start'''
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
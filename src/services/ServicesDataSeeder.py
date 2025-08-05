# services/ServicesDataSeeder.py
import logging
from decimal import Decimal
from typing import List, Tuple
from src.models.Service import Service
from src.repository.ServiceRepository import ServiceRepository

logger = logging.getLogger(__name__)


class ServicesDataSeeder:
    """Класс для заполнения базы данных услугами салона красоты"""

    def __init__(self, service_repository: ServiceRepository):
        self.service_repo = service_repository

    async def seed_all_services(self):
        """Добавляет все услуги в базу данных"""
        try:
            logger.info("Начинаем добавление услуг в базу данных...")

            # Получаем все услуги
            all_services = self._get_all_services_data()

            added_count = 0
            skipped_count = 0

            for service_data in all_services:
                try:
                    # Проверяем, существует ли уже такая услуга
                    existing_services = await self.service_repo.search_by_name(service_data['name'])

                    if existing_services:
                        logger.info(f"Услуга '{service_data['name']}' уже существует, пропускаем")
                        skipped_count += 1
                        continue

                    # Создаем объект услуги
                    service = Service(
                        name=service_data['name'],
                        description=service_data['description'],
                        category=service_data['category'],
                        subcategory=service_data['subcategory'],
                        price=service_data['price'],
                        duration_minutes=service_data['duration_minutes'],
                        is_active=True
                    )

                    # Добавляем в базу данных
                    created_service = await self.service_repo.create(service)
                    logger.info(f"Добавлена услуга: {created_service.name} (ID: {created_service.id})")
                    added_count += 1

                except Exception as e:
                    logger.error(f"Ошибка при добавлении услуги '{service_data['name']}': {e}")
                    continue

            logger.info(f"✅ Завершено! Добавлено: {added_count}, пропущено: {skipped_count}")

        except Exception as e:
            logger.error(f"Ошибка при заполнении услуг: {e}")
            raise

    def _get_all_services_data(self) -> List[dict]:
        """Возвращает данные всех услуг"""
        services_data = []

        # Парикмахерские услуги
        hair_services = [
            {
                'name': 'women_haircut',
                'display_name': '✂️ Женская стрижка',
                'description': 'Профессиональная женская стрижка с учетом типа лица и структуры волос. Включает мытье головы, стрижку и укладку.',
                'category': 'hair_services',
                'subcategory': 'haircuts',
                'price': Decimal('1500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'men_haircut',
                'display_name': '✂️ Мужская стрижка',
                'description': 'Стильная мужская стрижка любой сложности. Включает мытье головы, стрижку и укладку.',
                'category': 'hair_services',
                'subcategory': 'haircuts',
                'price': Decimal('800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'kids_haircut',
                'display_name': '✂️ Детская стрижка',
                'description': 'Детская стрижка в комфортной обстановке. Мастер найдет подход к каждому ребенку.',
                'category': 'hair_services',
                'subcategory': 'haircuts',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'blow_dry',
                'display_name': '💨 Укладка феном',
                'description': 'Профессиональная укладка волос феном с использованием термозащитных средств.',
                'category': 'hair_services',
                'subcategory': 'styling',
                'price': Decimal('800.00'),
                'duration_minutes': 40
            },
            {
                'name': 'festive_styling',
                'display_name': '💨 Праздничная укладка',
                'description': 'Элегантная праздничная укладка для особых случаев с использованием профессиональных средств.',
                'category': 'hair_services',
                'subcategory': 'styling',
                'price': Decimal('1200.00'),
                'duration_minutes': 60
            },
            {
                'name': 'evening_styling',
                'display_name': '💨 Вечерняя укладка',
                'description': 'Роскошная вечерняя укладка для торжественных мероприятий.',
                'category': 'hair_services',
                'subcategory': 'styling',
                'price': Decimal('1500.00'),
                'duration_minutes': 75
            },
            {
                'name': 'single_color',
                'display_name': '🎨 Окрашивание в один тон',
                'description': 'Равномерное окрашивание волос в желаемый цвет качественными красителями.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('2500.00'),
                'duration_minutes': 120
            },
            {
                'name': 'highlights',
                'display_name': '🎨 Мелирование',
                'description': 'Классическое мелирование для создания объема и игры света в волосах.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('3500.00'),
                'duration_minutes': 150
            },
            {
                'name': 'coloring',
                'display_name': '🎨 Колорирование',
                'description': 'Многоцветное окрашивание для создания уникального образа.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('4000.00'),
                'duration_minutes': 180
            },
            {
                'name': 'ombre_shatush',
                'display_name': '🎨 Омбре/Шатуш',
                'description': 'Модная техника градиентного окрашивания с плавным переходом цвета.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('4500.00'),
                'duration_minutes': 180
            },
            {
                'name': 'balayage',
                'display_name': '🎨 Балаяж',
                'description': 'Французская техника окрашивания для создания естественного эффекта выгоревших волос.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('5000.00'),
                'duration_minutes': 200
            },
            {
                'name': 'toning',
                'display_name': '🎨 Тонирование',
                'description': 'Деликатное тонирование для коррекции цвета и придания блеска.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('1800.00'),
                'duration_minutes': 60
            },
            {
                'name': 'hair_botox',
                'display_name': '💊 Ботокс для волос',
                'description': 'Восстанавливающая процедура для глубокого питания и разглаживания волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('3000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'keratin_treatment',
                'display_name': '💊 Кератиновое выпрямление',
                'description': 'Профессиональное кератиновое выпрямление для гладких и здоровых волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('5500.00'),
                'duration_minutes': 180
            },
            {
                'name': 'hair_lamination',
                'display_name': '💊 Ламинирование',
                'description': 'Ламинирование волос для создания защитной пленки и придания блеска.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('2500.00'),
                'duration_minutes': 90
            },
            {
                'name': 'treatment_masks',
                'display_name': '💊 Лечебные маски',
                'description': 'Интенсивные лечебные маски для восстановления поврежденных волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('1500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'capsule_extension',
                'display_name': '➕ Наращивание на капсулах',
                'description': 'Наращивание волос итальянскими капсулами для максимально естественного результата.',
                'category': 'hair_services',
                'subcategory': 'extensions',
                'price': Decimal('8000.00'),
                'duration_minutes': 240
            },
            {
                'name': 'tape_extension',
                'display_name': '➕ Наращивание на лентах',
                'description': 'Быстрое наращивание волос на лентах с натуральным результатом.',
                'category': 'hair_services',
                'subcategory': 'extensions',
                'price': Decimal('6000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'weft_extension',
                'display_name': '➕ Наращивание на трессах',
                'description': 'Наращивание волос на трессах для создания объема и длины.',
                'category': 'hair_services',
                'subcategory': 'extensions',
                'price': Decimal('7000.00'),
                'duration_minutes': 180
            },
            {
                'name': 'perm',
                'display_name': '🔥 Химическая завивка',
                'description': 'Химическая завивка для создания стойких локонов.',
                'category': 'hair_services',
                'subcategory': 'styling',
                'price': Decimal('3500.00'),
                'duration_minutes': 150
            },
            {
                'name': 'hair_care',
                'display_name': '🧴 Уход и восстановление',
                'description': 'Комплексная программа ухода и восстановления волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('2000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'beard_styling',
                'display_name': '💇‍♀️ Моделирование бороды',
                'description': 'Профессиональное моделирование и стрижка бороды.',
                'category': 'hair_services',
                'subcategory': 'men_services',
                'price': Decimal('800.00'),
                'duration_minutes': 30
            },
            {
                'name': 'wedding_hairstyle',
                'display_name': '🎭 Свадебная прическа',
                'description': 'Роскошная свадебная прическа для самого важного дня.',
                'category': 'hair_services',
                'subcategory': 'special_occasions',
                'price': Decimal('3000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'hollywood_curls',
                'display_name': '✨ Голливудские локоны',
                'description': 'Элегантные голливудские локоны для особых случаев.',
                'category': 'hair_services',
                'subcategory': 'styling',
                'price': Decimal('1800.00'),
                'duration_minutes': 75
            },
            {
                'name': 'creative_coloring',
                'display_name': '🌈 Креативное окрашивание',
                'description': 'Креативное окрашивание в яркие и необычные цвета.',
                'category': 'hair_services',
                'subcategory': 'coloring',
                'price': Decimal('5500.00'),
                'duration_minutes': 240
            },
            {
                'name': 'chemical_straightening',
                'display_name': '🔄 Химическое выпрямление',
                'description': 'Химическое выпрямление для непослушных и кудрявых волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('4000.00'),
                'duration_minutes': 180
            },
            {
                'name': 'hot_scissors',
                'display_name': '💎 Стрижка горячими ножницами',
                'description': 'Лечебная стрижка горячими ножницами для запаивания кончиков.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('2000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'hair_glazing',
                'display_name': '🧪 Глазирование волос',
                'description': 'Глазирование для придания волосам зеркального блеска.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('2200.00'),
                'duration_minutes': 90
            },
            {
                'name': 'hair_screening',
                'display_name': '🌟 Экранирование волос',
                'description': 'Экранирование для защиты и восстановления структуры волос.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('2800.00'),
                'duration_minutes': 100
            },
            {
                'name': 'hair_polishing',
                'display_name': '💫 Полировка волос',
                'description': 'Полировка волос специальной машинкой для удаления секущихся кончиков.',
                'category': 'hair_services',
                'subcategory': 'treatment',
                'price': Decimal('1200.00'),
                'duration_minutes': 45
            }
        ]

        # Косметология
        cosmetology_services = [
            {
                'name': 'manual_cleaning',
                'display_name': '🧼 Механическая чистка',
                'description': 'Глубокая механическая чистка лица с удалением комедонов и очищением пор.',
                'category': 'cosmetology',
                'subcategory': 'facial_cleaning',
                'price': Decimal('2500.00'),
                'duration_minutes': 90
            },
            {
                'name': 'ultrasonic_cleaning',
                'display_name': '🧼 Ультразвуковая чистка',
                'description': 'Деликатная ультразвуковая чистка лица без травмирования кожи.',
                'category': 'cosmetology',
                'subcategory': 'facial_cleaning',
                'price': Decimal('2200.00'),
                'duration_minutes': 75
            },
            {
                'name': 'vacuum_cleaning',
                'display_name': '🧼 Вакуумная чистка',
                'description': 'Вакуумная чистка для глубокого очищения пор.',
                'category': 'cosmetology',
                'subcategory': 'facial_cleaning',
                'price': Decimal('2000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'combined_cleaning',
                'display_name': '🧼 Комбинированная чистка',
                'description': 'Комплексная чистка лица, сочетающая несколько методов.',
                'category': 'cosmetology',
                'subcategory': 'facial_cleaning',
                'price': Decimal('3000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'chemical_peeling',
                'display_name': '✨ Химический пилинг',
                'description': 'Химический пилинг для обновления и омоложения кожи.',
                'category': 'cosmetology',
                'subcategory': 'peeling',
                'price': Decimal('3500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'mechanical_peeling',
                'display_name': '✨ Механический пилинг',
                'description': 'Механический пилинг для удаления ороговевших клеток.',
                'category': 'cosmetology',
                'subcategory': 'peeling',
                'price': Decimal('2500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'enzyme_peeling',
                'display_name': '✨ Энзимный пилинг',
                'description': 'Деликатный энзимный пилинг для чувствительной кожи.',
                'category': 'cosmetology',
                'subcategory': 'peeling',
                'price': Decimal('2800.00'),
                'duration_minutes': 50
            },
            {
                'name': 'gas_liquid_peeling',
                'display_name': '✨ Газожидкостный пилинг',
                'description': 'Инновационный газожидкостный пилинг для глубокого очищения.',
                'category': 'cosmetology',
                'subcategory': 'peeling',
                'price': Decimal('4000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'alginate_mask',
                'display_name': '🎭 Альгинатная маска',
                'description': 'Альгинатная маска для увлажнения и питания кожи.',
                'category': 'cosmetology',
                'subcategory': 'masks',
                'price': Decimal('1500.00'),
                'duration_minutes': 30
            },
            {
                'name': 'collagen_mask',
                'display_name': '🎭 Коллагеновая маска',
                'description': 'Коллагеновая маска для повышения упругости кожи.',
                'category': 'cosmetology',
                'subcategory': 'masks',
                'price': Decimal('2000.00'),
                'duration_minutes': 40
            },
            {
                'name': 'moisturizing_mask',
                'display_name': '🎭 Увлажняющая маска',
                'description': 'Интенсивная увлажняющая маска для сухой кожи.',
                'category': 'cosmetology',
                'subcategory': 'masks',
                'price': Decimal('1200.00'),
                'duration_minutes': 25
            },
            {
                'name': 'cleansing_mask',
                'display_name': '🎭 Очищающая маска',
                'description': 'Глубоко очищающая маска для проблемной кожи.',
                'category': 'cosmetology',
                'subcategory': 'masks',
                'price': Decimal('1000.00'),
                'duration_minutes': 20
            },
            {
                'name': 'anti_aging_mask',
                'display_name': '🎭 Антивозрастная маска',
                'description': 'Антивозрастная маска с лифтинг-эффектом.',
                'category': 'cosmetology',
                'subcategory': 'masks',
                'price': Decimal('2500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'classic_face_massage',
                'display_name': '👐 Классический массаж лица',
                'description': 'Расслабляющий классический массаж лица для улучшения кровообращения.',
                'category': 'cosmetology',
                'subcategory': 'massage',
                'price': Decimal('1800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'lymphatic_massage',
                'display_name': '👐 Лимфодренажный массаж',
                'description': 'Лимфодренажный массаж для снятия отеков и улучшения контура лица.',
                'category': 'cosmetology',
                'subcategory': 'massage',
                'price': Decimal('2200.00'),
                'duration_minutes': 60
            },
            {
                'name': 'sculptural_massage',
                'display_name': '👐 Скульптурный массаж',
                'description': 'Скульптурный массаж для коррекции овала лица.',
                'category': 'cosmetology',
                'subcategory': 'massage',
                'price': Decimal('2500.00'),
                'duration_minutes': 75
            },
            {
                'name': 'gua_sha_massage',
                'display_name': '👐 Массаж Гуаша',
                'description': 'Традиционный китайский массаж Гуаша для омоложения.',
                'category': 'cosmetology',
                'subcategory': 'massage',
                'price': Decimal('2800.00'),
                'duration_minutes': 60
            },
            {
                'name': 'moisturizing_care',
                'display_name': '🧴 Увлажняющий уход',
                'description': 'Комплексный увлажняющий уход для сухой кожи.',
                'category': 'cosmetology',
                'subcategory': 'skincare',
                'price': Decimal('3000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'rejuvenating_care',
                'display_name': '🧴 Омолаживающий уход',
                'description': 'Антивозрастной омолаживающий уход с лифтинг-эффектом.',
                'category': 'cosmetology',
                'subcategory': 'skincare',
                'price': Decimal('4000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'problem_skin_care',
                'display_name': '🧴 Уход для проблемной кожи',
                'description': 'Специализированный уход для проблемной и склонной к акне кожи.',
                'category': 'cosmetology',
                'subcategory': 'skincare',
                'price': Decimal('3500.00'),
                'duration_minutes': 105
            },
            {
                'name': 'soothing_care',
                'display_name': '🧴 Успокаивающий уход',
                'description': 'Деликатный успокаивающий уход для чувствительной кожи.',
                'category': 'cosmetology',
                'subcategory': 'skincare',
                'price': Decimal('2800.00'),
                'duration_minutes': 75
            },
            {
                'name': 'darsonvalization',
                'display_name': '⚡ Дарсонвализация',
                'description': 'Физиотерапевтическая процедура для лечения проблемной кожи.',
                'category': 'cosmetology',
                'subcategory': 'apparatus',
                'price': Decimal('1500.00'),
                'duration_minutes': 30
            },
            {
                'name': 'microcurrent_therapy',
                'display_name': '⚡ Микротоковая терапия',
                'description': 'Микротоковая терапия для омоложения и подтяжки кожи.',
                'category': 'cosmetology',
                'subcategory': 'apparatus',
                'price': Decimal('3500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'rf_lifting',
                'display_name': '⚡ RF-лифтинг',
                'description': 'Радиочастотный лифтинг для подтяжки и омоложения кожи.',
                'category': 'cosmetology',
                'subcategory': 'apparatus',
                'price': Decimal('5000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'mesotherapy',
                'display_name': '💉 Мезотерапия',
                'description': 'Инъекционная мезотерапия для омоложения и улучшения качества кожи.',
                'category': 'cosmetology',
                'subcategory': 'injections',
                'price': Decimal('6000.00'),
                'duration_minutes': 45
            },
            {
                'name': 'biorevitalization',
                'display_name': '💉 Биоревитализация',
                'description': 'Биоревитализация гиалуроновой кислотой для глубокого увлажнения.',
                'category': 'cosmetology',
                'subcategory': 'injections',
                'price': Decimal('8000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'contour_plastic',
                'display_name': '💉 Контурная пластика',
                'description': 'Контурная пластика филлерами для коррекции возрастных изменений.',
                'category': 'cosmetology',
                'subcategory': 'injections',
                'price': Decimal('12000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'cryotherapy',
                'display_name': '❄️ Криотерапия',
                'description': 'Криотерапия жидким азотом для лечения кожных новообразований.',
                'category': 'cosmetology',
                'subcategory': 'apparatus',
                'price': Decimal('2000.00'),
                'duration_minutes': 30
            },
            {
                'name': 'photorejuvenation',
                'display_name': '🌟 Фотоомоложение',
                'description': 'IPL-фотоомоложение для улучшения текстуры и цвета кожи.',
                'category': 'cosmetology',
                'subcategory': 'apparatus',
                'price': Decimal('4500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'plasma_therapy',
                'display_name': '🔬 Плазмотерапия',
                'description': 'Плазмотерапия собственной плазмой для естественного омоложения.',
                'category': 'cosmetology',
                'subcategory': 'injections',
                'price': Decimal('7000.00'),
                'duration_minutes': 75
            }
        ]

        # Услуги маникюра/педикюра
        nails_services = [
            {
                'name': 'classic_manicure',
                'display_name': '💅 Классический маникюр',
                'description': 'Классический обрезной маникюр с обработкой кутикулы и формированием ногтей.',
                'category': 'nails_services',
                'subcategory': 'manicure',
                'price': Decimal('800.00'),
                'duration_minutes': 60
            },
            {
                'name': 'european_manicure',
                'display_name': '💅 Европейский маникюр',
                'description': 'Необрезной европейский маникюр с бережным уходом за кутикулой.',
                'category': 'nails_services',
                'subcategory': 'manicure',
                'price': Decimal('900.00'),
                'duration_minutes': 75
            },
            {
                'name': 'hardware_manicure',
                'display_name': '💅 Аппаратный маникюр',
                'description': 'Современный аппаратный маникюр с использованием фрезера.',
                'category': 'nails_services',
                'subcategory': 'manicure',
                'price': Decimal('1000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'spa_manicure',
                'display_name': '💅 SPA-маникюр',
                'description': 'Расслабляющий SPA-маникюр с парафинотерапией и массажем рук.',
                'category': 'nails_services',
                'subcategory': 'manicure',
                'price': Decimal('1200.00'),
                'duration_minutes': 120
            },
            {
                'name': 'mens_manicure',
                'display_name': '💅 Мужской маникюр',
                'description': 'Мужской маникюр с акцентом на здоровье и ухоженность ногтей.',
                'category': 'nails_services',
                'subcategory': 'manicure',
                'price': Decimal('700.00'),
                'duration_minutes': 45
            },
            {
                'name': 'classic_pedicure',
                'display_name': '🦶 Классический педикюр',
                'description': 'Классический педикюр с обработкой стоп и ногтей.',
                'category': 'nails_services',
                'subcategory': 'pedicure',
                'price': Decimal('1200.00'),
                'duration_minutes': 90
            },
            {
                'name': 'hardware_pedicure',
                'display_name': '🦶 Аппаратный педикюр',
                'description': 'Аппаратный педикюр с глубокой обработкой стоп.',
                'category': 'nails_services',
                'subcategory': 'pedicure',
                'price': Decimal('1500.00'),
                'duration_minutes': 120
            },
            {
                'name': 'spa_pedicure',
                'display_name': '🦶 SPA-педикюр',
                'description': 'Роскошный SPA-педикюр с масками и массажем стоп.',
                'category': 'nails_services',
                'subcategory': 'pedicure',
                'price': Decimal('1800.00'),
                'duration_minutes': 150
            },
            {
                'name': 'medical_pedicure',
                'display_name': '🦶 Медицинский педикюр',
                'description': 'Медицинский педикюр для решения проблем со стопами и ногтями.',
                'category': 'nails_services',
                'subcategory': 'pedicure',
                'price': Decimal('2000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'gel_polish',
                'display_name': '💎 Покрытие гель-лаком',
                'description': 'Стойкое покрытие гель-лаком с длительным эффектом.',
                'category': 'nails_services',
                'subcategory': 'coating',
                'price': Decimal('600.00'),
                'duration_minutes': 45
            },
            {
                'name': 'french_manicure',
                'display_name': '💎 Френч',
                'description': 'Классический французский маникюр с белыми кончиками.',
                'category': 'nails_services',
                'subcategory': 'coating',
                'price': Decimal('800.00'),
                'duration_minutes': 60
            },
            {
                'name': 'nail_ombre',
                'display_name': '💎 Омбре на ногтях',
                'description': 'Градиентное покрытие омбре для стильного образа.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('1000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'gel_extension',
                'display_name': '✨ Наращивание гелем',
                'description': 'Наращивание ногтей гелем для создания желаемой длины.',
                'category': 'nails_services',
                'subcategory': 'extensions',
                'price': Decimal('1500.00'),
                'duration_minutes': 120
            },
            {
                'name': 'acrylic_extension',
                'display_name': '✨ Наращивание акрилом',
                'description': 'Прочное наращивание ногтей акрилом.',
                'category': 'nails_services',
                'subcategory': 'extensions',
                'price': Decimal('1400.00'),
                'duration_minutes': 120
            },
            {
                'name': 'polygel_extension',
                'display_name': '✨ Наращивание полигелем',
                'description': 'Современное наращивание полигелем - легкое и прочное.',
                'category': 'nails_services',
                'subcategory': 'extensions',
                'price': Decimal('1600.00'),
                'duration_minutes': 135
            },
            {
                'name': 'nail_art',
                'display_name': '🎨 Художественная роспись',
                'description': 'Уникальная художественная роспись ногтей.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('1200.00'),
                'duration_minutes': 90
            },
            {
                'name': 'stamping',
                'display_name': '🎨 Стемпинг',
                'description': 'Дизайн ногтей с помощью техники стемпинг.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('800.00'),
                'duration_minutes': 60
            },
            {
                'name': 'nail_molding',
                'display_name': '🎨 Литье на ногтях',
                'description': 'Объемный дизайн с использованием техники литья.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('1500.00'),
                'duration_minutes': 105
            },
            {
                'name': 'nail_decoration',
                'display_name': '💎 Стразы и декор',
                'description': 'Украшение ногтей стразами и декоративными элементами.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'hand_paraffin',
                'display_name': '🔥 Парафинотерапия рук',
                'description': 'Увлажняющая парафинотерапия для рук.',
                'category': 'nails_services',
                'subcategory': 'care',
                'price': Decimal('500.00'),
                'duration_minutes': 30
            },
            {
                'name': 'foot_paraffin',
                'display_name': '🔥 Парафинотерапия ног',
                'description': 'Расслабляющая парафинотерапия для ног.',
                'category': 'nails_services',
                'subcategory': 'care',
                'price': Decimal('600.00'),
                'duration_minutes': 40
            },
            {
                'name': 'ingrown_nail_treatment',
                'display_name': '💊 Лечение вросших ногтей',
                'description': 'Профессиональное лечение вросших ногтей.',
                'category': 'nails_services',
                'subcategory': 'medical',
                'price': Decimal('1500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'nail_strengthening',
                'display_name': '🧴 Укрепление ногтей',
                'description': 'Процедура укрепления слабых и ломких ногтей.',
                'category': 'nails_services',
                'subcategory': 'care',
                'price': Decimal('800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'shape_correction',
                'display_name': '✂️ Коррекция формы',
                'description': 'Коррекция формы ногтей и их выравнивание.',
                'category': 'nails_services',
                'subcategory': 'care',
                'price': Decimal('400.00'),
                'duration_minutes': 30
            },
            {
                'name': 'japanese_manicure',
                'display_name': '🌟 Японский маникюр',
                'description': 'Лечебный японский маникюр для восстановления ногтей.',
                'category': 'nails_services',
                'subcategory': 'care',
                'price': Decimal('1200.00'),
                'duration_minutes': 90
            },
            {
                'name': 'biogel_coating',
                'display_name': '💫 Биогель покрытие',
                'description': 'Укрепляющее покрытие биогелем.',
                'category': 'nails_services',
                'subcategory': 'coating',
                'price': Decimal('900.00'),
                'duration_minutes': 75
            },
            {
                'name': 'wedding_nail_design',
                'display_name': '🎭 Свадебный дизайн',
                'description': 'Элегантный свадебный дизайн ногтей.',
                'category': 'nails_services',
                'subcategory': 'special',
                'price': Decimal('1800.00'),
                'duration_minutes': 120
            },
            {
                'name': 'nail_gradient',
                'display_name': '🌈 Градиент на ногтях',
                'description': 'Плавный градиентный переход цветов.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('1000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'nail_inlay',
                'display_name': '💝 Инкрустация',
                'description': 'Инкрустация ногтей драгоценными элементами.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('2000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'nail_rub',
                'display_name': '🔮 Втирка',
                'description': 'Зеркальная втирка для эффектного блеска.',
                'category': 'nails_services',
                'subcategory': 'design',
                'price': Decimal('700.00'),
                'duration_minutes': 45
            }
        ]

        # Аппаратные услуги
        hardware_services = [
            {
                'name': 'laser_depilation',
                'display_name': '🔥 Лазерная депиляция',
                'description': 'Эффективная лазерная депиляция для длительного результата.',
                'category': 'hardware_services',
                'subcategory': 'hair_removal',
                'price': Decimal('3000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'photo_depilation',
                'display_name': '🔥 Фотодепиляция',
                'description': 'IPL-фотодепиляция для безболезненного удаления волос.',
                'category': 'hardware_services',
                'subcategory': 'hair_removal',
                'price': Decimal('2500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'elos_depilation',
                'display_name': '🔥 Элос-депиляция',
                'description': 'Комбинированная элос-депиляция для всех типов волос.',
                'category': 'hardware_services',
                'subcategory': 'hair_removal',
                'price': Decimal('3500.00'),
                'duration_minutes': 75
            },
            {
                'name': 'electro_epilation',
                'display_name': '⚡ Электроэпиляция',
                'description': 'Классическая электроэпиляция для навсегда.',
                'category': 'hardware_services',
                'subcategory': 'hair_removal',
                'price': Decimal('2000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'cryolipolysis',
                'display_name': '❄️ Криолиполиз',
                'description': 'Неинвазивное разрушение жировых клеток холодом.',
                'category': 'hardware_services',
                'subcategory': 'body_shaping',
                'price': Decimal('8000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'cavitation',
                'display_name': '⚡ Кавитация',
                'description': 'Ультразвуковая кавитация для коррекции фигуры.',
                'category': 'hardware_services',
                'subcategory': 'body_shaping',
                'price': Decimal('4000.00'),
                'duration_minutes': 45
            },
            {
                'name': 'pressotherapy',
                'display_name': '🌊 Прессотерапия',
                'description': 'Лимфодренажная прессотерапия против отеков.',
                'category': 'hardware_services',
                'subcategory': 'lymphatic',
                'price': Decimal('2500.00'),
                'duration_minutes': 40
            },
            {
                'name': 'myostimulation',
                'display_name': '⚡ Миостимуляция',
                'description': 'Электростимуляция мышц для подтяжки и тонуса.',
                'category': 'hardware_services',
                'subcategory': 'muscle_stimulation',
                'price': Decimal('2000.00'),
                'duration_minutes': 30
            },
            {
                'name': 'laser_rejuvenation',
                'display_name': '🔬 Лазерное омоложение',
                'description': 'Фракционное лазерное омоложение кожи.',
                'category': 'hardware_services',
                'subcategory': 'rejuvenation',
                'price': Decimal('6000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'diamond_dermabrasion',
                'display_name': '💎 Алмазная дермабразия',
                'description': 'Алмазная шлифовка кожи для обновления.',
                'category': 'hardware_services',
                'subcategory': 'resurfacing',
                'price': Decimal('4500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'carbon_peeling',
                'display_name': '🌟 Карбоновый пилинг',
                'description': 'Лазерный карбоновый пилинг для очищения пор.',
                'category': 'hardware_services',
                'subcategory': 'peeling',
                'price': Decimal('5000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'radiowave_lifting',
                'display_name': '⚡ Радиоволновой лифтинг',
                'description': 'RF-лифтинг для подтяжки кожи тела.',
                'category': 'hardware_services',
                'subcategory': 'lifting',
                'price': Decimal('5500.00'),
                'duration_minutes': 75
            },
            {
                'name': 'hydro_peeling',
                'display_name': '💧 Гидропилинг',
                'description': 'Водно-кислородная дермабразия.',
                'category': 'hardware_services',
                'subcategory': 'peeling',
                'price': Decimal('3500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'thermage',
                'display_name': '🔥 Термолифтинг',
                'description': 'Термолифтинг для глубокого прогрева тканей.',
                'category': 'hardware_services',
                'subcategory': 'lifting',
                'price': Decimal('7000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'smas_lifting',
                'display_name': '⭐ Ультразвуковой SMAS-лифтинг',
                'description': 'Ультразвуковой лифтинг глубоких слоев кожи.',
                'category': 'hardware_services',
                'subcategory': 'lifting',
                'price': Decimal('12000.00'),
                'duration_minutes': 120
            }
        ]

        # Визаж и макияж
        makeup_services = [
            {
                'name': 'day_makeup',
                'display_name': '💄 Дневной макияж',
                'description': 'Естественный дневной макияж для повседневной жизни.',
                'category': 'makeup_services',
                'subcategory': 'everyday',
                'price': Decimal('1500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'evening_makeup',
                'display_name': '💄 Вечерний макияж',
                'description': 'Яркий вечерний макияж для особых случаев.',
                'category': 'makeup_services',
                'subcategory': 'special',
                'price': Decimal('2500.00'),
                'duration_minutes': 75
            },
            {
                'name': 'wedding_makeup',
                'display_name': '💄 Свадебный макияж',
                'description': 'Романтичный свадебный макияж для невесты.',
                'category': 'makeup_services',
                'subcategory': 'wedding',
                'price': Decimal('4000.00'),
                'duration_minutes': 120
            },
            {
                'name': 'photo_makeup',
                'display_name': '💄 Фотосессионный макияж',
                'description': 'Макияж для фотосессий с HD-покрытием.',
                'category': 'makeup_services',
                'subcategory': 'photo',
                'price': Decimal('3000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'special_occasion_makeup',
                'display_name': '💄 Макияж для особых случаев',
                'description': 'Индивидуальный макияж для торжественных мероприятий.',
                'category': 'makeup_services',
                'subcategory': 'special',
                'price': Decimal('2800.00'),
                'duration_minutes': 80
            },
            {
                'name': 'makeup_lessons',
                'display_name': '💄 Обучение макияжу',
                'description': 'Индивидуальные уроки макияжа с практикой.',
                'category': 'makeup_services',
                'subcategory': 'education',
                'price': Decimal('3500.00'),
                'duration_minutes': 120
            },
            {
                'name': 'makeup_correction',
                'display_name': '💄 Коррекция макияжа',
                'description': 'Коррекция и исправление существующего макияжа.',
                'category': 'makeup_services',
                'subcategory': 'correction',
                'price': Decimal('1000.00'),
                'duration_minutes': 30
            },
            {
                'name': 'smokey_eyes',
                'display_name': '💄 Смоки айс',
                'description': 'Классическая техника смоки айс для выразительного взгляда.',
                'category': 'makeup_services',
                'subcategory': 'technique',
                'price': Decimal('2000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'nude_makeup',
                'display_name': '💄 Nude макияж',
                'description': 'Естественный nude-макияж для подчеркивания красоты.',
                'category': 'makeup_services',
                'subcategory': 'natural',
                'price': Decimal('1800.00'),
                'duration_minutes': 50
            },
            {
                'name': 'mature_makeup',
                'display_name': '💄 Возрастной макияж',
                'description': 'Деликатный макияж с учетом возрастных особенностей.',
                'category': 'makeup_services',
                'subcategory': 'age_appropriate',
                'price': Decimal('2200.00'),
                'duration_minutes': 70
            }
        ]

        # Услуги для бровей и ресниц
        # Услуги для бровей и ресниц
        brows_lashes_services = [
            {
                'name': 'brow_tweeze',
                'description': 'Классическая коррекция формы бровей пинцетом.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_shaping',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'brow_wax',
                'description': 'Быстрая коррекция бровей горячим воском.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_shaping',
                'price': Decimal('700.00'),
                'duration_minutes': 25
            },
            {
                'name': 'brow_architecture',
                'description': 'Профессиональное моделирование идеальной формы бровей.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_design',
                'price': Decimal('1200.00'),
                'duration_minutes': 60
            },
            {
                'name': 'brow_tinting',
                'description': 'Стойкое окрашивание бровей профессиональной краской.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_coloring',
                'price': Decimal('800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'brow_henna',
                'description': 'Натуральное окрашивание бровей хной с окрашиванием кожи.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_coloring',
                'price': Decimal('1000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'brow_biotattoo',
                'description': 'Долговременный биотатуаж для заполнения пробелов в бровях.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_enhancement',
                'price': Decimal('1500.00'),
                'duration_minutes': 90
            },
            {
                'name': 'brow_lamination',
                'description': 'Ламинирование для укладки и фиксации волосков бровей.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_treatment',
                'price': Decimal('1800.00'),
                'duration_minutes': 75
            },
            {
                'name': 'brow_styling',
                'description': 'Долговременная укладка непослушных волосков бровей.',
                'category': 'brows_lashes_services',
                'subcategory': 'brow_treatment',
                'price': Decimal('1600.00'),
                'duration_minutes': 60
            },
            {
                'name': 'classic_lash_extension',
                'description': 'Классическое наращивание ресниц 1:1 для естественного объема.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_extensions',
                'price': Decimal('2500.00'),
                'duration_minutes': 120
            },
            {
                'name': '2d_lash_extension',
                'description': 'Объемное наращивание 2D для более выразительного взгляда.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_extensions',
                'price': Decimal('3000.00'),
                'duration_minutes': 150
            },
            {
                'name': '3d_lash_extension',
                'description': 'Объемное наращивание 3D для максимального эффекта.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_extensions',
                'price': Decimal('3500.00'),
                'duration_minutes': 180
            },
            {
                'name': 'volume_lash_extension',
                'description': 'Объемное наращивание ресниц для драматичного эффекта.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_extensions',
                'price': Decimal('4000.00'),
                'duration_minutes': 200
            },
            {
                'name': 'hollywood_volume',
                'description': 'Максимальный голливудский объем для особых случаев.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_extensions',
                'price': Decimal('5000.00'),
                'duration_minutes': 240
            },
            {
                'name': 'lash_lamination',
                'description': 'Ламинирование собственных ресниц для подкручивания и объема.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_treatment',
                'price': Decimal('2000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'lash_botox',
                'description': 'Восстанавливающий ботокс для укрепления и питания ресниц.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_treatment',
                'price': Decimal('2200.00'),
                'duration_minutes': 60
            },
            {
                'name': 'lash_tinting',
                'description': 'Окрашивание ресниц стойкой краской для выразительности.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_coloring',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'lash_perm',
                'description': 'Химическая завивка ресниц для естественного подкручивания.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_treatment',
                'price': Decimal('1500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'lash_removal',
                'description': 'Бережное снятие наращенных ресниц специальным средством.',
                'category': 'brows_lashes_services',
                'subcategory': 'lash_service',
                'price': Decimal('500.00'),
                'duration_minutes': 30
            }
        ]

        # SPA услуги
        spa_services = [
            {
                'name': 'body_wraps',
                'description': 'Детоксицирующие и моделирующие обертывания для тела.',
                'category': 'spa_services',
                'subcategory': 'body_treatments',
                'price': Decimal('3000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'body_scrub',
                'description': 'Отшелушивающий скраб для гладкости кожи тела.',
                'category': 'spa_services',
                'subcategory': 'body_treatments',
                'price': Decimal('2000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'full_body_massage',
                'description': 'Расслабляющий массаж всего тела для снятия напряжения.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('3500.00'),
                'duration_minutes': 90
            },
            {
                'name': 'anti_cellulite_massage',
                'description': 'Интенсивный массаж против целлюлита с моделирующим эффектом.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('2800.00'),
                'duration_minutes': 75
            },
            {
                'name': 'relaxing_massage',
                'description': 'Нежный расслабляющий массаж для восстановления сил.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('2500.00'),
                'duration_minutes': 60
            },
            {
                'name': 'sports_massage',
                'description': 'Восстанавливающий спортивный массаж для активных людей.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('3000.00'),
                'duration_minutes': 75
            },
            {
                'name': 'honey_massage',
                'description': 'Детоксицирующий медовый массаж для очищения организма.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('3200.00'),
                'duration_minutes': 80
            },
            {
                'name': 'hot_stone_massage',
                'description': 'Расслабляющий массаж с использованием горячих камней.',
                'category': 'spa_services',
                'subcategory': 'massage',
                'price': Decimal('4000.00'),
                'duration_minutes': 90
            },
            {
                'name': 'hydromassage',
                'description': 'Водный массаж в специальной ванне для релаксации.',
                'category': 'spa_services',
                'subcategory': 'water_treatments',
                'price': Decimal('2500.00'),
                'duration_minutes': 45
            },
            {
                'name': 'aromatherapy',
                'description': 'Расслабляющая ароматерапия с эфирными маслами.',
                'category': 'spa_services',
                'subcategory': 'wellness',
                'price': Decimal('2000.00'),
                'duration_minutes': 60
            },
            {
                'name': 'salt_baths',
                'description': 'Лечебные солевые ванны для детоксикации и релаксации.',
                'category': 'spa_services',
                'subcategory': 'water_treatments',
                'price': Decimal('1800.00'),
                'duration_minutes': 30
            },
            {
                'name': 'herbal_baths',
                'description': 'Успокаивающие ванны с лечебными травами.',
                'category': 'spa_services',
                'subcategory': 'water_treatments',
                'price': Decimal('2000.00'),
                'duration_minutes': 40
            },
            {
                'name': 'milk_baths',
                'description': 'Питательные молочные ванны для мягкости кожи.',
                'category': 'spa_services',
                'subcategory': 'water_treatments',
                'price': Decimal('2200.00'),
                'duration_minutes': 35
            },
            {
                'name': 'spa_rituals',
                'description': 'Комплексные SPA-ритуалы для полного расслабления.',
                'category': 'spa_services',
                'subcategory': 'wellness',
                'price': Decimal('5000.00'),
                'duration_minutes': 180
            },
            {
                'name': 'decollete_treatments',
                'description': 'Специальный уход за деликатной зоной декольте.',
                'category': 'spa_services',
                'subcategory': 'body_treatments',
                'price': Decimal('2500.00'),
                'duration_minutes': 60
            }
        ]

        # Детские услуги
        kids_services = [
            {
                'name': 'kids_haircut_under5',
                'description': 'Бережная стрижка для малышей в игровой форме.',
                'category': 'kids_services',
                'subcategory': 'haircuts',
                'price': Decimal('500.00'),
                'duration_minutes': 20
            },
            {
                'name': 'kids_haircut_5to12',
                'description': 'Стильная детская стрижка с учетом пожеланий ребенка.',
                'category': 'kids_services',
                'subcategory': 'haircuts',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'teen_haircut',
                'description': 'Модная стрижка для подростков по последним трендам.',
                'category': 'kids_services',
                'subcategory': 'haircuts',
                'price': Decimal('800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'kids_styling',
                'description': 'Праздничная укладка для детей на особые случаи.',
                'category': 'kids_services',
                'subcategory': 'styling',
                'price': Decimal('600.00'),
                'duration_minutes': 30
            },
            {
                'name': 'kids_manicure',
                'description': 'Безопасный детский маникюр с яркими лаками.',
                'category': 'kids_services',
                'subcategory': 'nails',
                'price': Decimal('400.00'),
                'duration_minutes': 30
            },
            {
                'name': 'kids_body_art',
                'description': 'Безопасная роспись тела специальными красками.',
                'category': 'kids_services',
                'subcategory': 'art',
                'price': Decimal('800.00'),
                'duration_minutes': 45
            },
            {
                'name': 'hair_chalk',
                'description': 'Временное окрашивание волос цветными мелками.',
                'category': 'kids_services',
                'subcategory': 'coloring',
                'price': Decimal('300.00'),
                'duration_minutes': 15
            },
            {
                'name': 'hair_glitter',
                'description': 'Украшение прически безопасными блестками.',
                'category': 'kids_services',
                'subcategory': 'decoration',
                'price': Decimal('200.00'),
                'duration_minutes': 10
            },
            {
                'name': 'face_painting',
                'description': 'Профессиональный аквагрим для детских праздников.',
                'category': 'kids_services',
                'subcategory': 'art',
                'price': Decimal('600.00'),
                'duration_minutes': 20
            },
            {
                'name': 'kids_makeup',
                'description': 'Легкий детский макияж безопасной косметикой.',
                'category': 'kids_services',
                'subcategory': 'makeup',
                'price': Decimal('800.00'),
                'duration_minutes': 30
            }
        ]

        # Объединяем все услуги
        services_data.extend(hair_services)
        services_data.extend(cosmetology_services)
        services_data.extend(nails_services)
        services_data.extend(hardware_services)
        services_data.extend(makeup_services)
        services_data.extend(brows_lashes_services)
        services_data.extend(spa_services)
        services_data.extend(kids_services)

        return services_data